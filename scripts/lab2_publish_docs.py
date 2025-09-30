#!/usr/bin/env python3
"""
Unified document publisher for quickstart-streaming-agents.

Cross-platform tool for publishing Flink documentation to Kafka topics.
Supports both AWS and Azure deployments with automatic cloud provider detection.

Usage:
    uv run publish_docs              # Auto-detect cloud provider
    uv run publish_docs aws          # Publish to AWS environment
    uv run publish_docs azure        # Publish to Azure environment
    uv run publish_docs --dry-run    # Test without actually publishing

Traditional Python:
    python scripts/lab2_publish_docs.py
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer

from .common.cloud_detection import auto_detect_cloud_provider, validate_cloud_provider, suggest_cloud_provider
from .common.terraform import extract_kafka_credentials, validate_terraform_state, get_project_root


class FlinkDocsPublisher:
    """Publisher for Flink documentation to Kafka using Avro format."""

    def __init__(
        self, kafka_config: Dict[str, Any], schema_registry_config: Dict[str, Any]
    ):
        """
        Initialize the publisher with Kafka and Schema Registry configuration.

        Args:
            kafka_config: Kafka client configuration
            schema_registry_config: Schema Registry configuration
        """
        self.kafka_config = kafka_config
        self.schema_registry_config = schema_registry_config

        # Define Avro schema for documents (compatible with existing schema)
        self.value_schema = avro.loads(
            json.dumps(
                {
                    "type": "record",
                    "name": "documents_value",
                    "namespace": "org.apache.flink.avro.generated.record",
                    "fields": [
                        {
                            "name": "document_id",
                            "type": ["null", "string"],
                            "default": None,
                        },
                        {
                            "name": "document_text",
                            "type": ["null", "string"],
                            "default": None,
                        },
                    ],
                }
            )
        )

        # Define Avro schema for keys (simple string)
        self.key_schema = avro.loads('"string"')

        # Initialize producer
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
            logger = logging.getLogger(__name__)
            logger.info("Avro producer initialized successfully")
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to initialize Avro producer: {e}")
            raise

    def parse_markdown_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse a markdown file with YAML frontmatter.

        Args:
            file_path: Path to the markdown file

        Returns:
            Dictionary with parsed content or None if parsing fails
        """
        logger = logging.getLogger(__name__)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Split frontmatter and content
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    markdown_content = parts[2].strip()
                else:
                    frontmatter = {}
                    markdown_content = content
            else:
                frontmatter = {}
                markdown_content = content

            # Use filename as document_id for uniqueness, with optional frontmatter document_id override
            document_id = frontmatter.get("document_id", file_path.name)

            # Combine title and content for document_text
            title = frontmatter.get("title", "")
            if title:
                document_text = f"# {title}\n\n{markdown_content}"
            else:
                document_text = markdown_content

            return {
                "document_id": document_id,
                "document_text": document_text,
                "metadata": frontmatter,
            }

        except Exception as e:
            logger.error(f"Failed to parse file {file_path}: {e}")
            return None

    def publish_document(self, document: Dict[str, Any], topic: str) -> bool:
        """
        Publish a single document to Kafka.

        Args:
            document: Document data with document_id and document_text
            topic: Kafka topic name

        Returns:
            True if successful, False otherwise
        """
        logger = logging.getLogger(__name__)
        try:
            if not self.producer:
                self._init_producer()

            # Create Avro record
            value = {
                "document_id": document["document_id"],
                "document_text": document["document_text"],
            }

            # Produce message
            self.producer.produce(topic=topic, value=value, key=document["document_id"])

            logger.info(f"Published document: {document['document_id']}")
            return True

        except Exception as e:
            logger.error(
                f"Failed to publish document {document.get('document_id', 'unknown')}: {e}"
            )
            return False

    def publish_directory(self, docs_dir: Path, topic: str) -> Dict[str, int]:
        """
        Publish all markdown files in a directory to Kafka.

        Args:
            docs_dir: Directory containing markdown files
            topic: Kafka topic name

        Returns:
            Dictionary with success/failure counts
        """
        logger = logging.getLogger(__name__)
        if not self.producer:
            self._init_producer()

        results = {"success": 0, "failed": 0, "total": 0}

        # Find all markdown files
        md_files = list(docs_dir.glob("*.md"))
        results["total"] = len(md_files)

        logger.info(f"Found {len(md_files)} markdown files to process")

        for file_path in md_files:
            logger.info(f"Processing: {file_path.name}")

            # Parse document
            document = self.parse_markdown_file(file_path)
            if not document:
                results["failed"] += 1
                continue

            # Publish document
            if self.publish_document(document, topic):
                results["success"] += 1
            else:
                results["failed"] += 1

        # Flush all messages
        try:
            self.producer.flush(timeout=30)
            logger.info("All messages flushed successfully")
        except Exception as e:
            logger.error(f"Failed to flush messages: {e}")

        return results

    def close(self):
        """Close the producer connection."""
        if self.producer:
            self.producer.flush()


def create_kafka_config(
    bootstrap_servers: str, api_key: str, api_secret: str
) -> Dict[str, Any]:
    """Create Kafka client configuration."""
    return {
        "bootstrap.servers": bootstrap_servers,
        "security.protocol": "SASL_SSL",
        "sasl.mechanisms": "PLAIN",
        "sasl.username": api_key,
        "sasl.password": api_secret,
        "client.id": "flink-docs-publisher",
    }


def create_schema_registry_config(
    schema_registry_url: str, api_key: str, api_secret: str
) -> Dict[str, Any]:
    """Create Schema Registry client configuration."""
    return {
        "url": schema_registry_url,
        "basic.auth.credentials.source": "USER_INFO",
        "basic.auth.user.info": f"{api_key}:{api_secret}",
    }


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)




def test_dependencies() -> bool:
    """
    Test that all required dependencies are available.

    Returns:
        True if dependencies are available, False otherwise
    """
    logger = logging.getLogger(__name__)
    logger.info("Testing required dependencies...")

    try:
        # Test imports directly since we're in the same process
        import yaml
        import confluent_kafka.avro
        import requests

        logger.info("✓ All required dependencies are available")
        return True
    except ImportError as e:
        logger.error("✗ Missing required dependencies!")
        logger.error(f"Import test failed: {e}")
        logger.error("To install required packages:")
        logger.error("  uv pip install -r requirements.txt")
        logger.error("  # Or with traditional Python:")
        logger.error("  pip install -r requirements.txt")
        return False




def run_publisher(
    cloud_provider: str,
    project_root: Path,
    dry_run: bool = False,
    verbose: bool = False
) -> int:
    """
    Run the document publisher with extracted credentials.

    Args:
        cloud_provider: Target cloud provider (aws/azure)
        project_root: Project root directory
        dry_run: If True, validate setup but don't publish
        verbose: If True, show detailed output

    Returns:
        Exit code (0 for success)
    """
    logger = logging.getLogger(__name__)

    try:
        # Extract credentials from terraform state
        credentials = extract_kafka_credentials(cloud_provider, project_root)

        # Test dependencies first
        if not test_dependencies():
            return 1

        if dry_run:
            logger.info("✓ Dry run successful - all dependencies and credentials are ready")
            logger.info(f"Would publish to topic 'documents' in cluster '{credentials['cluster_name']}'")
            logger.info(f"Environment: {credentials['environment_name']}")
            logger.info(f"Bootstrap servers: {credentials['bootstrap_servers']}")
            return 0

        # Create Kafka and Schema Registry configurations
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

        logger.info(f"Publishing to topic 'documents' in cluster '{credentials['cluster_name']}'")

        # Initialize publisher
        publisher = FlinkDocsPublisher(kafka_config, schema_registry_config)

        try:
            # Use markdown_chunks directory instead of full docs
            docs_dir = project_root / "assets/lab2/flink_docs/markdown_chunks"

            if not docs_dir.exists():
                logger.error(f"Markdown chunks directory not found: {docs_dir}")
                return 1

            logger.info(f"Publishing document chunks from {docs_dir} to topic 'documents'")

            # Publish all documents
            results = publisher.publish_directory(docs_dir, "documents")

            logger.info(
                f"Publishing complete: {results['success']} successful, {results['failed']} failed out of {results['total']} total"
            )

            if results["failed"] > 0:
                logger.error("✗ Some documents failed to publish")
                return 1
            else:
                logger.info("✓ Document publishing completed successfully")
                return 0

        finally:
            publisher.close()

    except Exception as e:
        logger.error(f"Publisher failed: {e}")
        if verbose:
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
        return 1


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog="publish_docs",
        description="Publish Flink documentation to Kafka topics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run publish_docs              # Auto-detect cloud provider
  uv run publish_docs aws          # Publish to AWS environment
  uv run publish_docs azure        # Publish to Azure environment
  uv run publish_docs --dry-run --verbose

Traditional Python:
  python scripts/lab2_publish_docs.py
        """.strip()
    )

    parser.add_argument(
        "cloud_provider",
        nargs="?",
        choices=["aws", "azure"],
        help="Target cloud provider (auto-detected if not specified)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate setup and credentials without publishing documents"
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
    logger.info("Quickstart Streaming Agents - Document Publisher")

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

        # Run the publisher
        exit_code = run_publisher(
            cloud_provider=cloud_provider,
            project_root=project_root,
            dry_run=args.dry_run,
            verbose=args.verbose
        )

        if args.dry_run:
            logger.info("Dry run completed")
        else:
            logger.info(f"Document publishing completed with exit code {exit_code}")

        sys.exit(exit_code)

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Document publisher failed: {e}")
        if args.verbose:
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()