#!/usr/bin/env python3
"""
CLI-based query publisher for quickstart-streaming-agents.

Uses Confluent CLI instead of confluent-kafka Python library to eliminate
librdkafka and pkg-config dependencies.

Usage:
    uv run publish_queries "How do I use window functions?"
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
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict

from .common.cloud_detection import auto_detect_cloud_provider, validate_cloud_provider, suggest_cloud_provider
from .common.terraform import extract_kafka_credentials, validate_terraform_state, get_project_root


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)


class QueryPublisherCLI:
    """Query publisher using Confluent CLI instead of Python Kafka client."""

    # Avro schema for queries
    QUERY_VALUE_SCHEMA = {
        "type": "record",
        "name": "queries_value",
        "namespace": "org.apache.flink.avro.generated.record",
        "fields": [
            {"name": "query", "type": ["null", "string"], "default": None}
        ],
    }

    def __init__(
        self,
        bootstrap_servers: str,
        kafka_api_key: str,
        kafka_api_secret: str,
        schema_registry_url: str,
        schema_registry_api_key: str,
        schema_registry_api_secret: str,
        environment_id: str = None,
        cluster_id: str = None
    ):
        """Initialize the publisher with Kafka and Schema Registry configuration."""
        self.bootstrap_servers = bootstrap_servers
        self.kafka_api_key = kafka_api_key
        self.kafka_api_secret = kafka_api_secret
        self.schema_registry_url = schema_registry_url
        self.schema_registry_api_key = schema_registry_api_key
        self.schema_registry_api_secret = schema_registry_api_secret
        self.environment_id = environment_id
        self.cluster_id = cluster_id
        self.logger = logging.getLogger(__name__)

        # Create temporary schema file
        self.schema_file = None
        self._create_schema_file()

    def _create_schema_file(self) -> None:
        """Create temporary Avro schema file."""
        self.schema_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.avsc',
            delete=False,
            prefix='queries_schema_'
        )
        json.dump(self.QUERY_VALUE_SCHEMA, self.schema_file)
        self.schema_file.flush()
        self.logger.debug(f"Created schema file: {self.schema_file.name}")

    def publish_query(self, query: str, topic: str = "queries") -> bool:
        """
        Publish a single query to Kafka using Confluent CLI.

        Args:
            query: SQL query to publish
            topic: Kafka topic name (defaults to 'queries')

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create Avro record with union type formatting
            # For union types ["null", "string"], values must be wrapped as {"string": "value"}
            value = {"query": {"string": query}}

            # Prepare confluent CLI command
            cmd = [
                "confluent", "kafka", "topic", "produce", topic,
                "--value-format", "avro",
                "--schema", self.schema_file.name,
                "--bootstrap", self.bootstrap_servers,
                "--api-key", self.kafka_api_key,
                "--api-secret", self.kafka_api_secret,
                "--schema-registry-endpoint", self.schema_registry_url,
                "--schema-registry-api-key", self.schema_registry_api_key,
                "--schema-registry-api-secret", self.schema_registry_api_secret,
            ]

            # Add environment and cluster if provided
            if self.environment_id:
                cmd.extend(["--environment", self.environment_id])
            if self.cluster_id:
                cmd.extend(["--cluster", self.cluster_id])

            self.logger.debug(f"Publishing query to topic '{topic}': {query[:100]}...")

            # Run command with JSON message as input
            result = subprocess.run(
                cmd,
                input=json.dumps(value) + "\n",
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                self.logger.error(f"Failed to publish query: {result.stderr}")
                return False

            self.logger.info(f"✓ Query published successfully to topic '{topic}'")
            if self.environment_id and self.cluster_id:
                url = f"https://confluent.cloud/environments/{self.environment_id}/clusters/{self.cluster_id}/topics/{topic}/message-viewer"
                self.logger.info(f"   View messages:  {url}")
                response_url = f"https://confluent.cloud/environments/{self.environment_id}/clusters/{self.cluster_id}/topics/search_results_response/message-viewer"
                self.logger.info(f"   View responses: {response_url}")

            return True

        except subprocess.TimeoutExpired:
            self.logger.error("Timeout while publishing query (30s)")
            return False
        except Exception as e:
            self.logger.error(f"Failed to publish query: {e}")
            return False

    def close(self):
        """Clean up temporary files."""
        if self.schema_file:
            try:
                Path(self.schema_file.name).unlink(missing_ok=True)
                self.logger.debug("Temporary schema file cleaned up")
            except Exception as e:
                self.logger.debug(f"Could not clean up schema file: {e}")


def main():
    """Main entry point for the query publisher CLI."""
    parser = argparse.ArgumentParser(
        description="Publish queries to Kafka using Confluent CLI (no librdkafka dependency)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "How do I use window functions?"
  %(prog)s aws "What is watermarking?"
  %(prog)s azure --verbose
        """
    )

    parser.add_argument(
        "cloud_provider",
        nargs="?",
        choices=["aws", "azure"],
        help="Cloud provider (aws or azure). If not specified, will auto-detect."
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Query to publish. If not provided, interactive mode will be used."
    )
    parser.add_argument(
        "--topic",
        default="queries",
        help="Kafka topic name (default: queries)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set up logging
    logger = setup_logging(args.verbose)

    # Determine cloud provider
    if args.cloud_provider:
        cloud_provider = args.cloud_provider
        logger.debug(f"Using specified cloud provider: {cloud_provider}")
    else:
        # If query is "aws" or "azure", treat it as cloud provider
        if args.query in ["aws", "azure"]:
            cloud_provider = args.query
            args.query = None
            logger.debug(f"Interpreted first argument as cloud provider: {cloud_provider}")
        else:
            cloud_provider = auto_detect_cloud_provider()
            if not cloud_provider:
                suggestion = suggest_cloud_provider()
                if suggestion:
                    logger.info(f"Auto-detected cloud provider: {suggestion}")
                    cloud_provider = suggestion
                else:
                    logger.error("Could not auto-detect cloud provider. Please specify 'aws' or 'azure'.")
                    return 1

    # Validate cloud provider
    if not validate_cloud_provider(cloud_provider):
        logger.error(f"Invalid cloud provider: {cloud_provider}")
        return 1

    # Get project root
    try:
        project_root = get_project_root()
    except Exception as e:
        logger.error(f"Could not find project root: {e}")
        return 1

    # Validate terraform state
    try:
        validate_terraform_state(cloud_provider, project_root)
    except Exception as e:
        logger.error(f"Terraform validation failed: {e}")
        return 1

    # Extract Kafka credentials
    try:
        credentials = extract_kafka_credentials(cloud_provider, project_root)
    except Exception as e:
        logger.error(f"Failed to extract Kafka credentials: {e}")
        return 1

    # Get query from user if not provided
    query = args.query
    if not query:
        print("\nEnter your query (press Ctrl+D or Ctrl+Z when done):")
        query = sys.stdin.read().strip()
        if not query:
            logger.error("No query provided")
            return 1

    # Initialize publisher
    try:
        publisher = QueryPublisherCLI(
            bootstrap_servers=credentials["bootstrap_servers"],
            kafka_api_key=credentials["kafka_api_key"],
            kafka_api_secret=credentials["kafka_api_secret"],
            schema_registry_url=credentials["schema_registry_url"],
            schema_registry_api_key=credentials["schema_registry_api_key"],
            schema_registry_api_secret=credentials["schema_registry_api_secret"],
            environment_id=credentials.get("environment_id"),
            cluster_id=credentials.get("cluster_id")
        )
    except Exception as e:
        logger.error(f"Failed to initialize publisher: {e}")
        return 1

    # Publish query
    try:
        success = publisher.publish_query(query, args.topic)
        if not success:
            return 1

        print(f"\n✓ Query published successfully!")
        print(f"  Topic: {args.topic}")
        print(f"  Query: {query[:100]}{'...' if len(query) > 100 else ''}")

        return 0
    finally:
        publisher.close()


if __name__ == "__main__":
    sys.exit(main())
