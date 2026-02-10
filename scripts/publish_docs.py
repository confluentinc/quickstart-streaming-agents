#!/usr/bin/env python3
"""
CLI-based document publisher for quickstart-streaming-agents.

Uses Confluent CLI instead of confluent-kafka Python library to eliminate
librdkafka and pkg-config dependencies.

Usage:
    uv run publish_docs --lab2              # Publish Lab2 Flink docs
    uv run publish_docs --lab3              # Publish Lab3 NOLA event docs
    uv run publish_docs --lab2 --dry-run    # Test without actually publishing

Traditional Python:
    python scripts/publish_docs.py --lab2
"""

import argparse
import json
import logging
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml

from .common.cloud_detection import auto_detect_cloud_provider, validate_cloud_provider, suggest_cloud_provider
from .common.login_checks import check_confluent_login
from .common.terraform import extract_kafka_credentials, validate_terraform_state, get_project_root

# Global lock to ensure only one thread checks login at a time
_login_check_lock = threading.Lock()
_login_verified = False

try:
    from .common.clear_mongodb import extract_mongodb_credentials, clear_mongodb_collection
    CLEAR_MONGODB_AVAILABLE = True
except ImportError:
    CLEAR_MONGODB_AVAILABLE = False

from .common.logging_utils import setup_logging


class FlinkDocsPublisherCLI:
    """Publisher for documentation to Kafka using Confluent CLI."""

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
        dry_run: bool = False,
        max_workers: int = 10
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
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)

        # Instance lock to prevent multiple workers from checking login simultaneously
        self._login_check_lock = threading.Lock()
        self._login_verified = False

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

    def _verify_login_once(self) -> bool:
        """
        Thread-safe login verification that only checks once across all workers.

        Returns:
            True if logged in, False otherwise
        """
        # Use instance lock to ensure only one worker checks at a time
        with self._login_check_lock:
            if self._login_verified:
                # Already verified by another worker
                return True

            # First worker to acquire lock performs the check
            if check_confluent_login():
                self._login_verified = True
                return True
            else:
                self.logger.error("Confluent CLI login session expired during publishing")
                return False

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
            # Verify login once per publisher instance (thread-safe)
            # This prevents all workers from bombarding the login endpoint
            if not self._verify_login_once():
                self.logger.error(f"Skipping document {document['document_id']}: Not logged in")
                return False

            # Create Avro record with union type formatting
            # For union types ["null", "string"], values must be wrapped as {"string": "value"}
            value = {
                "document_id": {"string": document["document_id"]},
                "document_text": {"string": document["document_text"]},
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

    def _process_single_file(self, file_path: Path, topic: str) -> Tuple[str, bool, Optional[str]]:
        """
        Process a single markdown file: parse and publish.

        Args:
            file_path: Path to the markdown file
            topic: Kafka topic name

        Returns:
            Tuple of (file_name, success, error_message)
        """
        file_name = file_path.name
        try:
            # Parse document
            document = self.parse_markdown_file(file_path)
            if not document:
                return (file_name, False, "Failed to parse markdown file")

            # Publish document
            if self.publish_document(document, topic):
                return (file_name, True, None)
            else:
                return (file_name, False, "Failed to publish document")

        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            self.logger.error(f"Error processing {file_name}: {error_msg}")
            return (file_name, False, error_msg)

    def publish_directory(self, docs_dir: Path, topic: str) -> Dict[str, int]:
        """
        Publish all markdown files in a directory to Kafka using parallel workers.

        Args:
            docs_dir: Directory containing markdown files
            topic: Kafka topic name

        Returns:
            Dictionary with success/failure counts
        """
        results = {"success": 0, "failed": 0, "total": 0}
        results_lock = threading.Lock()

        # Find all markdown files
        md_files = list(docs_dir.glob("*.md"))
        results["total"] = len(md_files)

        self.logger.info(f"Found {len(md_files)} markdown files to process")
        self.logger.info(f"Publishing with {self.max_workers} parallel workers")

        # Process files in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all files as tasks
            future_to_file = {
                executor.submit(self._process_single_file, file_path, topic): file_path
                for file_path in md_files
            }

            # Process results as they complete
            completed = 0
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                file_name, success, error_msg = future.result()

                # Update results with thread safety
                with results_lock:
                    if success:
                        results["success"] += 1
                    else:
                        results["failed"] += 1
                    completed += 1

                    # Show progress
                    if completed % 10 == 0 or completed == results["total"]:
                        self.logger.info(
                            f"Progress: {completed}/{results['total']} documents "
                            f"({results['success']} succeeded, {results['failed']} failed)"
                        )

        return results

    def close(self):
        """Clean up temporary files."""
        if self.schema_file:
            try:
                Path(self.schema_file.name).unlink(missing_ok=True)
                self.logger.debug("Temporary schema file cleaned up")
            except Exception as e:
                self.logger.debug(f"Could not clean up schema file: {e}")


def find_docs_directory(project_root: Path, lab: int, cloud_provider: str) -> Optional[Path]:
    """
    Find the documentation directory for a specific lab.

    Args:
        project_root: Project root directory
        lab: Lab number (2 or 3)
        cloud_provider: Cloud provider (aws or azure)

    Returns:
        Path to docs directory or None if not found
    """
    if lab == 2:
        # Lab2: Flink SQL documentation
        # Standard location (new structure)
        standard_path = project_root / "assets" / "lab2" / "flink_docs"
        if standard_path.exists():
            return standard_path

        # Legacy location with markdown_chunks subdirectory
        legacy_chunks_path = project_root / "assets" / "lab2" / "flink_docs" / "markdown_chunks"
        if legacy_chunks_path.exists():
            return legacy_chunks_path

        # Try cloud-specific path (legacy)
        cloud_path = project_root / cloud_provider / "lab2-vector-search" / "flink_docs"
        if cloud_path.exists():
            return cloud_path

        # Try generic path (legacy)
        generic_path = project_root / "flink_docs"
        if generic_path.exists():
            return generic_path

    elif lab == 3:
        # Lab3: New Orleans event documentation
        # Standard location
        standard_path = project_root / "assets" / "lab3" / "nola_events_docs"
        if standard_path.exists():
            return standard_path

        # Legacy location with markdown_chunks subdirectory
        legacy_chunks_path = project_root / "assets" / "lab3" / "markdown_chunks"
        if legacy_chunks_path.exists():
            return legacy_chunks_path

    return None


def prompt_clear_mongodb(cloud_provider: str, project_root: Path, logger: logging.Logger) -> bool:
    """
    Prompt user to clear MongoDB collection and perform clearing if confirmed.

    Args:
        cloud_provider: Cloud provider (aws or azure)
        project_root: Project root directory
        logger: Logger instance

    Returns:
        True if successful or skipped, False if failed
    """
    if not CLEAR_MONGODB_AVAILABLE:
        print("\nNote: MongoDB clearing functionality not available (pymongo not installed).")
        print("Proceeding with publishing documents...")
        return True

    # Ask user if they want to clear MongoDB
    print("\n" + "=" * 60)
    print("MONGODB COLLECTION MANAGEMENT")
    print("=" * 60)
    try:
        response = input("Clear existing documents from MongoDB before publishing? (y/n): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n\nSkipping MongoDB clearing.")
        return True

    if response not in ['y', 'yes']:
        print("Skipping MongoDB clearing.")
        return True

    # User wants to clear - proceed with clearing
    try:
        logger.info("Extracting MongoDB credentials...")
        mongodb_creds = extract_mongodb_credentials(cloud_provider, project_root)

        logger.info(f"Connecting to MongoDB ({mongodb_creds['database']}.{mongodb_creds['collection']})...")
        deleted_count = clear_mongodb_collection(
            connection_string=mongodb_creds['connection_string'],
            username=mongodb_creds['username'],
            password=mongodb_creds['password'],
            database=mongodb_creds['database'],
            collection=mongodb_creds['collection']
        )

        print(f"\n{'=' * 60}")
        print("MONGODB COLLECTION CLEARED")
        print(f"{'=' * 60}")
        print(f"Database:          {mongodb_creds['database']}")
        print(f"Collection:        {mongodb_creds['collection']}")
        print(f"Documents deleted: {deleted_count}")
        print(f"{'=' * 60}\n")

        return True

    except ImportError as e:
        logger.warning(f"pymongo not installed: {e}")
        print("\nNote: Could not clear MongoDB (pymongo not installed).")
        print("Proceeding with publishing documents...")
        return True
    except Exception as e:
        logger.error(f"Failed to clear MongoDB: {e}")
        print(f"\nWarning: Could not clear MongoDB collection: {e}")
        print("Proceeding with publishing documents anyway...")
        return True


def main():
    """Main entry point for the document publisher CLI."""
    parser = argparse.ArgumentParser(
        description="Publish documentation to Kafka using Confluent CLI (no librdkafka dependency)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --lab2
  %(prog)s --lab3
  %(prog)s --lab2 --dry-run
        """
    )

    # Create mutually exclusive group for lab selection
    lab_group = parser.add_mutually_exclusive_group(required=True)
    lab_group.add_argument(
        "--lab2",
        action="store_true",
        help="Publish Lab2 Flink SQL documentation"
    )
    lab_group.add_argument(
        "--lab3",
        action="store_true",
        help="Publish Lab3 New Orleans event documentation"
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
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Number of parallel workers for publishing (default: 10)"
    )

    args = parser.parse_args()

    # Set up logging
    logger = setup_logging(args.verbose)

    # Check Confluent CLI login before proceeding
    if not check_confluent_login():
        print("\n" + "=" * 60)
        print("ERROR: Not logged into Confluent Cloud")
        print("=" * 60)
        print("\nYou must be logged in to publish documents.")
        print("\nTo log in, run:")
        print("  confluent login")
        print("\nTo avoid session timeouts, save credentials with:")
        print("  confluent login --save")
        print("=" * 60 + "\n")
        return 1

    logger.info("✓ Confluent CLI logged in")

    # Determine lab number
    if args.lab2:
        lab = 2
        lab_name = "Lab2 (Flink SQL documentation)"
    else:  # args.lab3
        lab = 3
        lab_name = "Lab3 (New Orleans event documentation)"

    logger.info(f"Publishing documents for {lab_name}")

    # Auto-detect cloud provider
    cloud_provider = auto_detect_cloud_provider()
    if not cloud_provider:
        suggestion = suggest_cloud_provider()
        if suggestion:
            logger.info(f"Auto-detected cloud provider: {suggestion}")
            cloud_provider = suggestion
        else:
            logger.error("Could not auto-detect cloud provider. Please check your terraform deployment.")
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
        docs_dir = find_docs_directory(project_root, lab, cloud_provider)
        if not docs_dir:
            logger.error(f"Could not find documentation directory for Lab{lab}. Please specify --docs-dir")
            return 1
        logger.info(f"Found documentation directory: {docs_dir}")

    if not docs_dir.exists():
        logger.error(f"Documentation directory does not exist: {docs_dir}")
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

    # Prompt to clear MongoDB collection (if not in dry-run mode)
    if not args.dry_run:
        if not prompt_clear_mongodb(cloud_provider, project_root, logger):
            logger.error("MongoDB clearing failed")
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
            dry_run=args.dry_run,
            max_workers=args.workers
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
