#!/usr/bin/env python3
"""
CLI-based document publisher for quickstart-streaming-agents.

Uses Confluent CLI instead of confluent-kafka Python library to eliminate
librdkafka and pkg-config dependencies.

Usage:
    uv run publish_docs_cli              # Auto-detect cloud provider
    uv run publish_docs_cli aws          # Publish to AWS environment
    uv run publish_docs_cli azure        # Publish to Azure environment
    uv run publish_docs_cli --dry-run    # Test without actually publishing

Traditional Python:
    python scripts/lab2_publish_docs_cli.py
"""

import argparse
import json
import logging
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

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


class FlinkDocsPublisherCLI:
    """Publisher for Flink documentation to Kafka using Confluent CLI."""

    # Avro schema for documents
    DOCUMENT_VALUE_SCHEMA = {
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

    def __init__(
        self,
        bootstrap_servers: str,
        kafka_api_key: str,
        kafka_api_secret: str,
        schema_registry_url: str,
        schema_registry_api_key: str,
        schema_registry_api_secret: str,
        environment_id: str = None,
        cluster_id: str = None,
        dry_run: bool = False
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
        self.dry_run = dry_run
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
            prefix='documents_schema_'
        )
        json.dump(self.DOCUMENT_VALUE_SCHEMA, self.schema_file)
        self.schema_file.flush()
        self.logger.debug(f"Created schema file: {self.schema_file.name}")

    def parse_markdown_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse a markdown file with YAML frontmatter.

        Args:
            file_path: Path to the markdown file

        Returns:
            Dictionary with parsed content or None if parsing fails
        """
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
            self.logger.error(f"Failed to parse file {file_path}: {e}")
            return None

    def publish_document(self, document: Dict[str, Any], topic: str) -> bool:
        """
        Publish a single document to Kafka using Confluent CLI.

        Args:
            document: Document data with document_id and document_text
            topic: Kafka topic name

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create Avro record
            value = {
                "document_id": document["document_id"],
                "document_text": document["document_text"],
            }

            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would publish document: {document['document_id']}")
                self.logger.debug(f"[DRY RUN] Content length: {len(document['document_text'])} chars")
                return True

            # Prepare confluent CLI command
            cmd = [
                "confluent", "kafka", "topic", "produce", topic,
                "--value-format", "avro",
                "--schema", self.schema_file.name,
                "--parse-key",
                "--delimiter", ":",
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

            # Create message with key:value format
            # Key is the document_id, value is the JSON record
            message = f"{document['document_id']}:{json.dumps(value)}\n"

            self.logger.debug(f"Publishing document: {document['document_id']}")

            # Run command with message as input
            result = subprocess.run(
                cmd,
                input=message,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                self.logger.error(f"Failed to publish document {document['document_id']}: {result.stderr}")
                return False

            self.logger.info(f"Published document: {document['document_id']}")
            return True

        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout while publishing document {document.get('document_id', 'unknown')} (60s)")
            return False
        except Exception as e:
            self.logger.error(
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
        results = {"success": 0, "failed": 0, "total": 0}

        # Find all markdown files
        md_files = list(docs_dir.glob("*.md"))
        results["total"] = len(md_files)

        self.logger.info(f"Found {len(md_files)} markdown files to process")

        for file_path in md_files:
            self.logger.info(f"Processing: {file_path.name}")

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

        return results

    def close(self):
        """Clean up temporary files."""
        if self.schema_file:
            try:
                Path(self.schema_file.name).unlink(missing_ok=True)
                self.logger.debug("Temporary schema file cleaned up")
            except Exception as e:
                self.logger.debug(f"Could not clean up schema file: {e}")


def find_flink_docs_directory(project_root: Path, cloud_provider: str) -> Optional[Path]:
    """
    Find the Flink documentation directory.

    Args:
        project_root: Project root directory
        cloud_provider: Cloud provider (aws or azure)

    Returns:
        Path to Flink docs directory or None if not found
    """
    # Try cloud-specific path first
    cloud_path = project_root / cloud_provider / "lab2-vector-search" / "flink_docs"
    if cloud_path.exists():
        return cloud_path

    # Try generic path
    generic_path = project_root / "flink_docs"
    if generic_path.exists():
        return generic_path

    return None


def main():
    """Main entry point for the document publisher CLI."""
    parser = argparse.ArgumentParser(
        description="Publish Flink documentation to Kafka using Confluent CLI (no librdkafka dependency)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s aws
  %(prog)s azure --dry-run
        """
    )

    parser.add_argument(
        "cloud_provider",
        nargs="?",
        choices=["aws", "azure"],
        help="Cloud provider (aws or azure). If not specified, will auto-detect."
    )
    parser.add_argument(
        "--topic",
        default="documents",
        help="Kafka topic name (default: documents)"
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        help="Directory containing markdown files (auto-detected if not specified)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test without actually publishing"
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
    cloud_provider = args.cloud_provider
    if not cloud_provider:
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

    # Find docs directory
    docs_dir = args.docs_dir
    if not docs_dir:
        docs_dir = find_flink_docs_directory(project_root, cloud_provider)
        if not docs_dir:
            logger.error(f"Could not find Flink documentation directory. Please specify --docs-dir")
            return 1
        logger.info(f"Found documentation directory: {docs_dir}")

    if not docs_dir.exists():
        logger.error(f"Documentation directory does not exist: {docs_dir}")
        return 1

    # Validate terraform state
    try:
        validate_terraform_state(project_root, cloud_provider)
    except Exception as e:
        logger.error(f"Terraform validation failed: {e}")
        return 1

    # Extract Kafka credentials
    try:
        credentials = extract_kafka_credentials(project_root, cloud_provider)
    except Exception as e:
        logger.error(f"Failed to extract Kafka credentials: {e}")
        return 1

    # Initialize publisher
    try:
        publisher = FlinkDocsPublisherCLI(
            bootstrap_servers=credentials["bootstrap_servers"],
            kafka_api_key=credentials["kafka_api_key"],
            kafka_api_secret=credentials["kafka_api_secret"],
            schema_registry_url=credentials["schema_registry_url"],
            schema_registry_api_key=credentials["schema_registry_api_key"],
            schema_registry_api_secret=credentials["schema_registry_api_secret"],
            environment_id=credentials.get("environment_id"),
            cluster_id=credentials.get("cluster_id"),
            dry_run=args.dry_run
        )
    except Exception as e:
        logger.error(f"Failed to initialize publisher: {e}")
        return 1

    # Publish documents
    try:
        logger.info(f"Publishing documents from {docs_dir} to topic '{args.topic}'")
        if args.dry_run:
            logger.info("[DRY RUN MODE - No actual publishing will occur]")

        results = publisher.publish_directory(docs_dir, args.topic)

        print(f"\n{'=' * 60}")
        print("PUBLISHING SUMMARY")
        print(f"{'=' * 60}")
        print(f"Total files:      {results['total']}")
        print(f"Published:        {results['success']}")
        print(f"Failed:           {results['failed']}")
        print(f"{'=' * 60}")

        if args.dry_run:
            print("\n[DRY RUN COMPLETE - No messages were actually published]")

        return 0 if results['failed'] == 0 else 1
    finally:
        publisher.close()


if __name__ == "__main__":
    sys.exit(main())
