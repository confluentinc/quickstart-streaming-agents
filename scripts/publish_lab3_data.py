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
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

try:
    from confluent_kafka import Producer
    CONFLUENT_KAFKA_AVAILABLE = True
except ImportError:
    CONFLUENT_KAFKA_AVAILABLE = False

from .common.cloud_detection import auto_detect_cloud_provider, validate_cloud_provider, suggest_cloud_provider
from .common.login_checks import check_confluent_login
from .common.terraform import extract_kafka_credentials, validate_terraform_state, get_project_root


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)


class Lab3DataPublisherKafka:
    """Publisher for Lab3 ride request data to Kafka using confluent-kafka library."""

    def __init__(
        self,
        bootstrap_servers: str,
        kafka_api_key: str,
        kafka_api_secret: str,
        dry_run: bool = False,
        max_workers: int = 10
    ):
        """Initialize the publisher with Kafka configuration."""
        self.bootstrap_servers = bootstrap_servers
        self.kafka_api_key = kafka_api_key
        self.kafka_api_secret = kafka_api_secret
        self.dry_run = dry_run
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)

        # Create Kafka producer config
        self.producer_config = {
            'bootstrap.servers': bootstrap_servers,
            'sasl.mechanisms': 'PLAIN',
            'security.protocol': 'SASL_SSL',
            'sasl.username': kafka_api_key,
            'sasl.password': kafka_api_secret,
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

                # Flush periodically
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
            self.producer.flush()

        return results

    def close(self):
        """Clean up resources."""
        if self.producer:
            self.producer.flush()


class Lab3DataPublisherCLI:
    """Publisher for Lab3 ride request data to Kafka using Confluent CLI."""

    # Avro schema for ride_requests (matches Terraform schema)
    RIDE_REQUEST_VALUE_SCHEMA = {
        "type": "record",
        "name": "ride_requests_value",
        "namespace": "org.apache.flink.avro.generated.record",
        "fields": [
            {
                "name": "request_id",
                "type": ["null", "string"],
                "default": None,
            },
            {
                "name": "customer_email",
                "type": ["null", "string"],
                "default": None,
            },
            {
                "name": "pickup_zone",
                "type": ["null", "string"],
                "default": None,
            },
            {
                "name": "drop_off_zone",
                "type": ["null", "string"],
                "default": None,
            },
            {
                "name": "price",
                "type": ["null", "double"],
                "default": None,
            },
            {
                "name": "number_of_passengers",
                "type": ["null", "int"],
                "default": None,
            },
            {
                "name": "request_ts",
                "type": ["null", "long"],
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
            prefix='ride_requests_schema_'
        )
        json.dump(self.RIDE_REQUEST_VALUE_SCHEMA, self.schema_file)
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

    def parse_jsonl_line(self, line: str, line_number: int) -> Optional[Dict[str, Any]]:
        """
        Parse a single line from JSONL file.

        Args:
            line: JSON string line
            line_number: Line number for error reporting

        Returns:
            Dictionary with parsed ride request data or None if parsing fails
        """
        try:
            record = json.loads(line.strip())

            # Validate required fields exist
            required_fields = ["request_id", "customer_email", "pickup_zone", "drop_off_zone",
                             "price", "number_of_passengers", "request_ts"]
            for field in required_fields:
                if field not in record:
                    self.logger.error(f"Line {line_number}: Missing required field '{field}'")
                    return None

            return record

        except json.JSONDecodeError as e:
            self.logger.error(f"Line {line_number}: Invalid JSON: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Line {line_number}: Failed to parse: {e}")
            return None

    def publish_ride_request(self, record: Dict[str, Any], topic: str) -> bool:
        """
        Publish a single ride request to Kafka using Confluent CLI.

        Args:
            record: Ride request data
            topic: Kafka topic name (default: ride_requests)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Verify login once per publisher instance (thread-safe)
            if not self._verify_login_once():
                self.logger.error(f"Skipping record {record['request_id']}: Not logged in")
                return False

            # Create Avro record with union type formatting
            # For union types ["null", "type"], values must be wrapped as {"type": value}
            value = {
                "request_id": {"string": record["request_id"]},
                "customer_email": {"string": record["customer_email"]},
                "pickup_zone": {"string": record["pickup_zone"]},
                "drop_off_zone": {"string": record["drop_off_zone"]},
                "price": {"double": float(record["price"])},
                "number_of_passengers": {"int": int(record["number_of_passengers"])},
                "request_ts": {"long": int(record["request_ts"])},
            }

            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would publish ride request: {record['request_id']}")
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
            # Key is the request_id, value is the JSON record
            message = f"{record['request_id']}:{json.dumps(value)}\n"

            self.logger.debug(f"Publishing ride request: {record['request_id']}")

            # Run command with message as input
            result = subprocess.run(
                cmd,
                input=message,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                self.logger.error(f"Failed to publish ride request {record['request_id']}: {result.stderr}")
                return False

            self.logger.info(f"Published ride request: {record['request_id']}")
            return True

        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout while publishing ride request {record.get('request_id', 'unknown')} (60s)")
            return False
        except Exception as e:
            self.logger.error(
                f"Failed to publish ride request {record.get('request_id', 'unknown')}: {e}"
            )
            return False

    def _process_single_record(self, line: str, line_number: int, topic: str) -> Tuple[int, bool, Optional[str]]:
        """
        Process a single JSONL line: parse and publish.

        Args:
            line: JSONL line
            line_number: Line number
            topic: Kafka topic name

        Returns:
            Tuple of (line_number, success, error_message)
        """
        try:
            # Parse record
            record = self.parse_jsonl_line(line, line_number)
            if not record:
                return (line_number, False, "Failed to parse JSONL line")

            # Publish record
            if self.publish_ride_request(record, topic):
                return (line_number, True, None)
            else:
                return (line_number, False, "Failed to publish record")

        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            self.logger.error(f"Error processing line {line_number}: {error_msg}")
            return (line_number, False, error_msg)

    def publish_jsonl_file(self, jsonl_file: Path, topic: str) -> Dict[str, int]:
        """
        Publish all records from a JSONL file to Kafka using parallel workers.

        Args:
            jsonl_file: Path to JSONL file
            topic: Kafka topic name

        Returns:
            Dictionary with success/failure counts
        """
        results = {"success": 0, "failed": 0, "total": 0}
        results_lock = threading.Lock()

        # Read all lines from file
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
        except Exception as e:
            self.logger.error(f"Failed to read JSONL file {jsonl_file}: {e}")
            return results

        results["total"] = len(lines)

        self.logger.info(f"Found {len(lines)} ride requests to publish")
        self.logger.info(f"Publishing with {self.max_workers} parallel workers")

        # Process lines in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all lines as tasks
            future_to_line = {
                executor.submit(self._process_single_record, line, idx + 1, topic): idx + 1
                for idx, line in enumerate(lines)
            }

            # Process results as they complete
            completed = 0
            for future in as_completed(future_to_line):
                line_number = future_to_line[future]
                _, success, error_msg = future.result()

                # Update results with thread safety
                with results_lock:
                    if success:
                        results["success"] += 1
                    else:
                        results["failed"] += 1
                    completed += 1

                    # Show progress every 100 records or at completion
                    if completed % 100 == 0 or completed == results["total"]:
                        self.logger.info(
                            f"Progress: {completed}/{results['total']} records "
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


def detect_data_format(jsonl_file: Path) -> str:
    """
    Detect the format of the JSONL file.

    Returns:
        "base64" if data contains base64-encoded Avro data
        "decoded" if data contains plain JSON with decoded fields
    """
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
        if not first_line:
            return "unknown"

        record = json.loads(first_line)

        # Check if it's base64-encoded format (has key, value, partition, offset fields)
        if all(k in record for k in ['key', 'value', 'partition', 'offset']):
            return "base64"

        # Check if it's decoded format (has ride request fields)
        if all(k in record for k in ['request_id', 'customer_email', 'pickup_zone']):
            return "decoded"

        return "unknown"


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
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Number of parallel workers for publishing (default: 10, CLI mode only)"
    )

    args = parser.parse_args()

    # Set up logging
    logger = setup_logging(args.verbose)

    # Verify data file exists
    if not args.data_file.exists():
        logger.error(f"Data file does not exist: {args.data_file}")
        return 1

    # Detect data format
    data_format = detect_data_format(args.data_file)
    logger.info(f"Detected data format: {data_format}")

    if data_format == "unknown":
        logger.error("Could not detect data format. Expected either base64-encoded or decoded JSON format.")
        return 1

    # For base64 format, we need confluent-kafka library
    if data_format == "base64":
        if not CONFLUENT_KAFKA_AVAILABLE:
            logger.error("confluent-kafka library not available. Please install it with: uv pip install confluent-kafka")
            return 1
        logger.info("Using confluent-kafka library to publish base64-encoded Avro data")
    else:
        # For decoded format, we need Confluent CLI
        if not check_confluent_login():
            print("\n" + "=" * 60)
            print("ERROR: Not logged into Confluent Cloud")
            print("=" * 60)
            print("\nYou must be logged in to publish data.")
            print("\nTo log in, run:")
            print("  confluent login")
            print("\nTo avoid session timeouts, save credentials with:")
            print("  confluent login --save")
            print("=" * 60 + "\n")
            return 1
        logger.info("✓ Confluent CLI logged in")
        logger.info("Using Confluent CLI to publish decoded JSON data")

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

    # Initialize publisher based on data format
    try:
        if data_format == "base64":
            # Use confluent-kafka library for base64-encoded Avro data
            publisher = Lab3DataPublisherKafka(
                bootstrap_servers=credentials["bootstrap_servers"],
                kafka_api_key=credentials["kafka_api_key"],
                kafka_api_secret=credentials["kafka_api_secret"],
                dry_run=args.dry_run,
                max_workers=args.workers
            )
        else:
            # Use Confluent CLI for decoded JSON data
            publisher = Lab3DataPublisherCLI(
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
