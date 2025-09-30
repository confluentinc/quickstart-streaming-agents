#!/usr/bin/env python3
"""
Unified query publisher for quickstart-streaming-agents.

Cross-platform tool for publishing queries to Kafka topics using Avro format.
Supports both AWS and Azure deployments with automatic cloud provider detection.

Usage:
    uv run publish_queries "How do I use window functions?"   # Auto-detect
    uv run publish_queries                                    # Interactive mode
    uv run publish_queries aws "How do I join tables?"        # Specify provider
    uv run publish_queries azure "What is watermarking?"

Traditional Python:
    python scripts/lab2_publish_queries.py
"""

import argparse
import hashlib
import json
import logging
import sys
import time
import warnings
from typing import Any, Dict

# Suppress the deprecation warning for AvroProducer
warnings.filterwarnings("ignore", message="AvroProducer has been deprecated")

from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer

from .common.cloud_detection import auto_detect_cloud_provider, validate_cloud_provider, suggest_cloud_provider
from .common.terraform import extract_kafka_credentials, validate_terraform_state, get_project_root


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)


class QueryPublisher:
    """Unified query publisher for Kafka using Avro format."""

    def __init__(self, kafka_config: Dict[str, Any], schema_registry_config: Dict[str, Any], environment_id: str = None, cluster_id: str = None):
        """Initialize the publisher with Kafka and Schema Registry configuration."""
        self.kafka_config = kafka_config
        self.schema_registry_config = schema_registry_config
        self.environment_id = environment_id
        self.cluster_id = cluster_id
        self.logger = logging.getLogger(__name__)

        # Define Avro schema for queries
        self.value_schema = avro.loads(
            json.dumps({
                "type": "record",
                "name": "queries_value",
                "namespace": "org.apache.flink.avro.generated.record",
                "fields": [
                    {"name": "query", "type": ["null", "string"], "default": None}
                ],
            })
        )

        self.key_schema = avro.loads('"string"')
        self.producer = None

    def _init_producer(self) -> None:
        """Initialize the Avro producer."""
        try:
            self.producer = AvroProducer(
                self.kafka_config,
                default_key_schema=self.key_schema,
                default_value_schema=self.value_schema,
                schema_registry=avro.CachedSchemaRegistryClient(
                    self.schema_registry_config
                ),
            )
            self.logger.debug("AvroProducer initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Avro producer: {e}")
            raise

    def publish_query(self, query: str, topic: str = "queries") -> bool:
        """
        Publish a single query to Kafka.

        Args:
            query: SQL query to publish
            topic: Kafka topic name (defaults to 'queries')

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.producer:
                self._init_producer()

            # Create Avro record
            value = {"query": query}

            # Use query hash with timestamp as key for uniqueness
            key = hashlib.md5(f"{query}_{time.time()}".encode()).hexdigest()

            # Produce message
            self.logger.debug(f"Publishing query to topic '{topic}': {query[:100]}...")
            self.producer.produce(topic=topic, value=value, key=key)

            # Flush immediately to ensure delivery
            self.producer.flush(timeout=10)

            self.logger.info(f"✓ Query published successfully to topic '{topic}'")
            if self.environment_id and self.cluster_id:
                url = f"https://confluent.cloud/environments/{self.environment_id}/clusters/{self.cluster_id}/topics/{topic}/message-viewer"
                self.logger.info(f"   View messages: {url}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to publish query: {e}")
            return False

    def close(self):
        """Close the producer connection."""
        if self.producer:
            self.producer.flush()
            self.logger.debug("Producer closed")


def create_kafka_config(bootstrap_servers: str, api_key: str, api_secret: str) -> Dict[str, Any]:
    """Create Kafka client configuration."""
    return {
        "bootstrap.servers": bootstrap_servers,
        "security.protocol": "SASL_SSL",
        "sasl.mechanisms": "PLAIN",
        "sasl.username": api_key,
        "sasl.password": api_secret,
        "client.id": "unified-queries-publisher",
        "log_level": 0,  # Suppress Kafka client logs
    }


def create_schema_registry_config(schema_registry_url: str, api_key: str, api_secret: str) -> Dict[str, Any]:
    """Create Schema Registry client configuration."""
    return {
        "url": schema_registry_url,
        "basic.auth.credentials.source": "USER_INFO",
        "basic.auth.user.info": f"{api_key}:{api_secret}",
    }


def test_kafka_connection(credentials: Dict[str, str], dry_run: bool = False) -> bool:
    """
    Test Kafka connection and Schema Registry availability.

    Args:
        credentials: Extracted credentials
        dry_run: If True, only validate configuration without connecting

    Returns:
        True if connection is successful, False otherwise
    """
    logger = logging.getLogger(__name__)

    if dry_run:
        logger.info("✓ Dry run - skipping connection test")
        return True

    try:
        kafka_config = create_kafka_config(
            credentials["bootstrap_servers"],
            credentials["kafka_api_key"],
            credentials["kafka_api_secret"]
        )

        schema_registry_config = create_schema_registry_config(
            credentials["schema_registry_url"],
            credentials["schema_registry_api_key"],
            credentials["schema_registry_api_secret"]
        )

        # Create a test publisher (this will test both Kafka and Schema Registry)
        publisher = QueryPublisher(kafka_config, schema_registry_config)

        # Initialize producer (tests connection)
        publisher._init_producer()
        publisher.close()

        logger.info("✓ Kafka and Schema Registry connection test successful")
        return True

    except Exception as e:
        logger.error(f"✗ Connection test failed: {e}")
        return False


def run_interactive_mode(cloud_provider: str) -> None:
    """
    Run interactive query publishing mode.

    Args:
        cloud_provider: Target cloud provider
    """
    logger = logging.getLogger(__name__)

    try:
        project_root = get_project_root()
        credentials = extract_kafka_credentials(cloud_provider, project_root)

        kafka_config = create_kafka_config(
            credentials["bootstrap_servers"],
            credentials["kafka_api_key"],
            credentials["kafka_api_secret"]
        )

        schema_registry_config = create_schema_registry_config(
            credentials["schema_registry_url"],
            credentials["schema_registry_api_key"],
            credentials["schema_registry_api_secret"]
        )

        publisher = QueryPublisher(
            kafka_config,
            schema_registry_config,
            credentials.get("environment_id"),
            credentials.get("cluster_id")
        )

        print("Interactive query mode - Type 'quit' or 'exit' to stop")
        print("Example queries:")
        print("  What's the proper way to deduplicate a Flink table?")
        print("  What are the differences between Flink SQL API and Flink Table API?")
        print()

        try:
            while True:
                query = input("Enter your query/question: ").strip()

                if query.lower() in ['quit', 'exit', 'q']:
                    break

                if not query:
                    continue

                success = publisher.publish_query(query)
                if success:
                    print("✓ Query published to topic: 'queries'")
                    if publisher.environment_id and publisher.cluster_id:
                        url = f"https://confluent.cloud/environments/{publisher.environment_id}/clusters/{publisher.cluster_id}/topics/queries/message-viewer"
                        print(f"   View messages: {url}")
                else:
                    print("✗ Failed to publish query")
                print()

        except KeyboardInterrupt:
            print("\nExiting interactive mode...")
        except EOFError:
            print("\nExiting interactive mode...")
        finally:
            publisher.close()
            logger.info("Interactive session ended")

    except Exception as e:
        logger.error(f"Interactive mode failed: {e}")
        sys.exit(1)


def publish_single_query(
    cloud_provider: str,
    query: str,
    topic: str = "queries",
    dry_run: bool = False
) -> int:
    """
    Publish a single query to Kafka.

    Args:
        cloud_provider: Target cloud provider
        query: SQL query to publish
        topic: Kafka topic name
        dry_run: If True, validate setup but don't publish

    Returns:
        Exit code (0 for success)
    """
    logger = logging.getLogger(__name__)

    try:
        project_root = get_project_root()
        credentials = extract_kafka_credentials(cloud_provider, project_root)

        logger.info(f"Target cluster: '{credentials['cluster_name']}' in '{credentials['environment_name']}'")
        logger.info(f"Target topic: {topic}")

        if dry_run:
            logger.info("✓ Dry run successful - credentials extracted successfully")
            logger.info(f"Would publish query: {query}")
            return 0

        # Test connection
        if not test_kafka_connection(credentials):
            return 1

        # Create publisher
        kafka_config = create_kafka_config(
            credentials["bootstrap_servers"],
            credentials["kafka_api_key"],
            credentials["kafka_api_secret"]
        )

        schema_registry_config = create_schema_registry_config(
            credentials["schema_registry_url"],
            credentials["schema_registry_api_key"],
            credentials["schema_registry_api_secret"]
        )

        publisher = QueryPublisher(
            kafka_config,
            schema_registry_config,
            credentials.get("environment_id"),
            credentials.get("cluster_id")
        )

        # Publish query
        success = publisher.publish_query(query, topic)
        publisher.close()

        return 0 if success else 1

    except Exception as e:
        logger.error(f"Query publishing failed: {e}")
        return 1


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog="publish_queries",
        description="Publish SQL queries to Kafka topics using Avro format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run publish_queries "How do I use window functions?"    # Auto-detect
  uv run publish_queries                                     # Interactive mode
  uv run publish_queries aws "How do I join tables?"         # Specify provider
  uv run publish_queries "What is watermarking?" --verbose

Traditional Python:
  python scripts/lab2_publish_queries.py
        """.strip()
    )

    parser.add_argument(
        "cloud_provider",
        nargs="?",
        choices=["aws", "azure"],
        help="Target cloud provider (auto-detected if not specified)"
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="SQL query to publish (required unless using --interactive)"
    )

    parser.add_argument(
        "--topic",
        default="queries",
        help="Kafka topic to publish to (default: queries)"
    )

    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode for multiple queries"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate setup and credentials without publishing"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output and debug information"
    )

    return parser


def main() -> None:
    """Main entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()

    logger = setup_logging(args.verbose)
    logger.info("Quickstart Streaming Agents - Query Publisher")

    try:
        # Get project root
        project_root = get_project_root()
        logger.debug(f"Project root: {project_root}")

        # Determine cloud provider
        cloud_provider = args.cloud_provider
        if not cloud_provider:
            cloud_provider = auto_detect_cloud_provider()
            if not cloud_provider:
                logger.error("Could not auto-detect cloud provider")
                suggest_cloud_provider(project_root)
                sys.exit(1)
        else:
            if not validate_cloud_provider(cloud_provider):
                sys.exit(1)

        logger.info(f"Target cloud provider: {cloud_provider.upper()}")

        # Validate terraform state
        if not validate_terraform_state(cloud_provider, project_root):
            logger.error(f"Terraform state validation failed for {cloud_provider}")
            logger.error(f"Please run 'terraform apply' in {cloud_provider}/core/ and {cloud_provider}/lab2-vector-search/")
            sys.exit(1)

        # Handle interactive mode (default if no query provided)
        if args.interactive or not args.query:
            run_interactive_mode(cloud_provider)
            return

        # Publish single query
        exit_code = publish_single_query(
            cloud_provider=cloud_provider,
            query=args.query,
            topic=args.topic,
            dry_run=args.dry_run
        )

        if args.dry_run:
            logger.info("Dry run completed")
        else:
            logger.info(f"Query publishing completed with exit code {exit_code}")

        sys.exit(exit_code)

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Query publisher failed: {e}")
        if args.verbose:
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()