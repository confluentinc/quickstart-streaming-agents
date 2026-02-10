#!/usr/bin/env python3
"""
CLI-based Lab3 ride requests data publisher for quickstart-streaming-agents.

Publishes pre-generated JSONL ride request data to eliminate ShadowTraffic/Docker
dependencies for workshop participants.

Usage:
    uv run publish_lab3_data --data-file assets/lab3/data/ride_requests.jsonl
    uv run publish_lab3_data --data-file assets/lab3/data/ride_requests.jsonl --dry-run

Traditional Python:
    python scripts/publish_lab3_data.py --data-file assets/lab3/data/ride_requests.jsonl
"""

import argparse
import base64
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

try:
    from confluent_kafka import Producer
    CONFLUENT_KAFKA_AVAILABLE = True
except ImportError:
    CONFLUENT_KAFKA_AVAILABLE = False

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


class Lab3DataPublisher:
    """Publisher for Lab3 ride request data to Kafka using confluent-kafka library."""

    def __init__(
        self,
        bootstrap_servers: str,
        kafka_api_key: str,
        kafka_api_secret: str,
        dry_run: bool = False
    ):
        """Initialize the publisher with Kafka configuration."""
        self.bootstrap_servers = bootstrap_servers
        self.kafka_api_key = kafka_api_key
        self.kafka_api_secret = kafka_api_secret
        self.dry_run = dry_run
        self.logger = logging.getLogger(__name__)

        # Create Kafka producer config
        self.producer_config = {
            'bootstrap.servers': bootstrap_servers,
            'sasl.mechanisms': 'PLAIN',
            'security.protocol': 'SASL_SSL',
            'sasl.username': kafka_api_key,
            'sasl.password': kafka_api_secret,
            'linger.ms': 10,
            'batch.size': 16384,
            'compression.type': 'snappy',
        }

        # Initialize producer (if not dry run)
        self.producer = None
        if not dry_run:
            self.producer = Producer(self.producer_config)

    def publish_message(self, record: Dict[str, Any], topic: str) -> bool:
        """
        Publish a single message to Kafka from base64-encoded JSONL format.

        Args:
            record: Message data with base64-encoded key/value
            topic: Kafka topic name

        Returns:
            True if successful, False otherwise
        """
        try:
            # Decode base64 key and value back to bytes
            key_bytes = base64.b64decode(record['key']) if record.get('key') else None
            value_bytes = base64.b64decode(record['value']) if record.get('value') else None

            # Decode headers if present
            headers_list = None
            if record.get('headers'):
                headers_list = [(k, base64.b64decode(v)) for k, v in record['headers'].items()]

            if self.dry_run:
                self.logger.debug(f"[DRY RUN] Would publish message to partition {record.get('partition')}, offset {record.get('offset')}")
                return True

            # Produce message
            self.producer.produce(
                topic,
                key=key_bytes,
                value=value_bytes,
                headers=headers_list
            )

            return True

        except Exception as e:
            self.logger.error(f"Failed to publish message: {e}")
            return False

    def publish_jsonl_file(self, jsonl_file: Path, topic: str) -> Dict[str, int]:
        """
        Publish all messages from a JSONL file with base64-encoded Avro data.

        Args:
            jsonl_file: Path to JSONL file
            topic: Kafka topic name

        Returns:
            Dictionary with success/failure counts
        """
        results = {"success": 0, "failed": 0, "total": 0}

        # Read all lines
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
        except Exception as e:
            self.logger.error(f"Failed to read JSONL file {jsonl_file}: {e}")
            return results

        results["total"] = len(lines)
        self.logger.info(f"Found {len(lines)} messages to publish")

        # Process messages
        for idx, line in enumerate(lines, 1):
            try:
                message_data = json.loads(line)
                if self.publish_message(message_data, topic):
                    results["success"] += 1
                else:
                    results["failed"] += 1

                # Flush periodically for better performance
                if not self.dry_run and idx % 100 == 0:
                    self.producer.poll(0)

                if not self.dry_run and idx % 1000 == 0:
                    self.producer.flush()
                    self.logger.info(f"Progress: {idx}/{results['total']} messages ({results['success']} succeeded, {results['failed']} failed)")

            except json.JSONDecodeError as e:
                self.logger.error(f"Error parsing line {idx}: {e}")
                results["failed"] += 1
            except Exception as e:
                self.logger.error(f"Error processing line {idx}: {e}")
                results["failed"] += 1

        # Final flush
        if not self.dry_run and self.producer:
            self.logger.info("Flushing remaining messages...")
            self.producer.flush()

        return results

    def close(self):
        """Clean up resources."""
        if self.producer:
            self.producer.flush()


def main():
    """Main entry point for the Lab3 data publisher CLI."""
    parser = argparse.ArgumentParser(
        description="Publish Lab3 ride request data to Kafka",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --data-file assets/lab3/data/ride_requests.jsonl
  %(prog)s --data-file assets/lab3/data/ride_requests.jsonl --dry-run
        """
    )

    parser.add_argument(
        "--data-file",
        type=Path,
        required=True,
        help="Path to JSONL data file with ride requests"
    )
    parser.add_argument(
        "--topic",
        default="ride_requests",
        help="Kafka topic name (default: ride_requests)"
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

    # Verify data file exists
    if not args.data_file.exists():
        logger.error(f"Data file does not exist: {args.data_file}")
        return 1

    # Check confluent-kafka library is available
    if not CONFLUENT_KAFKA_AVAILABLE:
        logger.error("confluent-kafka library not available. Please install it with: uv pip install confluent-kafka")
        return 1

    logger.info(f"Publishing Lab3 ride request data from {args.data_file}")

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

    # Initialize publisher
    try:
        publisher = Lab3DataPublisher(
            bootstrap_servers=credentials["bootstrap_servers"],
            kafka_api_key=credentials["kafka_api_key"],
            kafka_api_secret=credentials["kafka_api_secret"],
            dry_run=args.dry_run
        )
    except Exception as e:
        logger.error(f"Failed to initialize publisher: {e}")
        return 1

    # Publish data
    try:
        logger.info(f"Publishing ride requests to topic '{args.topic}'")
        if args.dry_run:
            logger.info("[DRY RUN MODE - No actual publishing will occur]")

        results = publisher.publish_jsonl_file(args.data_file, args.topic)

        print(f"\n{'=' * 60}")
        print("LAB3 DATA PUBLISHING SUMMARY")
        print(f"{'=' * 60}")
        print(f"Total records:    {results['total']}")
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
