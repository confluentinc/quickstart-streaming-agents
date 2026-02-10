#!/usr/bin/env python3
"""
Capture ride_requests data from Confluent Cloud Kafka cluster.

Consumes messages from the ride_requests topic and saves them to a JSONL file
for distribution with the workshop repository.

Usage:
    uv run capture_lab3_data --output assets/lab3/data/ride_requests.jsonl
    uv run capture_lab3_data --from-beginning
    uv run capture_lab3_data --max-records 50000  # Optional: limit records
"""

import argparse
import base64
import json
import logging
import sys
import time
import traceback
from pathlib import Path
from typing import Optional

try:
    from confluent_kafka import Consumer, KafkaError, KafkaException
    CONFLUENT_KAFKA_AVAILABLE = True
except ImportError:
    CONFLUENT_KAFKA_AVAILABLE = False

from .common.cloud_detection import auto_detect_cloud_provider, suggest_cloud_provider
from .common.terraform import extract_kafka_credentials, get_project_root


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)


def capture_ride_requests(
    bootstrap_servers: str,
    kafka_api_key: str,
    kafka_api_secret: str,
    topic: str,
    output_file: Path,
    max_records: Optional[int] = None,
    from_beginning: bool = False,
    timeout_seconds: int = 30,
    logger: Optional[logging.Logger] = None
) -> int:
    """
    Capture ride request data from Kafka topic using confluent-kafka library.

    Args:
        bootstrap_servers: Kafka bootstrap servers
        kafka_api_key: Kafka API key
        kafka_api_secret: Kafka API secret
        topic: Kafka topic name
        output_file: Path to output JSONL file
        max_records: Maximum number of records to capture (None = unlimited)
        from_beginning: If True, start from beginning of topic
        timeout_seconds: Stop consuming after this many seconds of no new messages
        logger: Logger instance

    Returns:
        Number of records captured
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    if max_records:
        logger.info(f"Capturing up to {max_records} records from topic '{topic}'")
    else:
        logger.info(f"Capturing ALL records from topic '{topic}' (no limit)")
        logger.info(f"Will stop after {timeout_seconds}s of no new messages")

    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Configure Kafka consumer
    consumer_config = {
        'bootstrap.servers': bootstrap_servers,
        'sasl.mechanisms': 'PLAIN',
        'security.protocol': 'SASL_SSL',
        'sasl.username': kafka_api_key,
        'sasl.password': kafka_api_secret,
        'group.id': f'capture-lab3-data-{int(time.time())}',
        'auto.offset.reset': 'earliest' if from_beginning else 'latest',
        'enable.auto.commit': False,
        'fetch.min.bytes': 1,
        'fetch.wait.max.ms': 500,
    }

    consumer = Consumer(consumer_config)
    consumer.subscribe([topic])

    logger.info(f"Subscribed to topic '{topic}'")
    if from_beginning:
        logger.info("Consuming from beginning of topic")
    else:
        logger.info("Consuming from latest offset")

    records_captured = 0
    records_written = []
    last_message_time = time.time()

    try:
        logger.info("Starting to consume messages...")

        while True:
            # Poll for messages
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                # No message received - check timeout
                if time.time() - last_message_time > timeout_seconds:
                    logger.info(f"No new messages for {timeout_seconds}s, stopping capture")
                    break
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.debug(f"Reached end of partition {msg.partition()}")
                    continue
                else:
                    raise KafkaException(msg.error())

            # Update last message time
            last_message_time = time.time()

            # Get key and value as base64-encoded strings
            key_bytes = msg.key()
            value_bytes = msg.value()
            headers = msg.headers() or []

            # Encode to base64 for storage
            record = {
                'key': base64.b64encode(key_bytes).decode('utf-8') if key_bytes else None,
                'value': base64.b64encode(value_bytes).decode('utf-8') if value_bytes else None,
                'partition': msg.partition(),
                'offset': msg.offset(),
            }

            # Add headers if present
            if headers:
                record['headers'] = {k: base64.b64encode(v).decode('utf-8') for k, v in headers}

            records_written.append(record)
            records_captured += 1

            # Show progress
            if records_captured % 1000 == 0:
                logger.info(f"Captured {records_captured} records...")

            # Stop if we've reached max records
            if max_records and records_captured >= max_records:
                logger.info(f"Reached maximum of {max_records} records")
                break

    except KeyboardInterrupt:
        logger.info("Capture interrupted by user")
    except Exception as e:
        logger.error(f"Error during consumption: {e}")
        raise
    finally:
        # Close consumer
        consumer.close()
        logger.debug("Consumer closed")

    # Write all records to file
    if records_written:
        logger.info(f"Writing {len(records_written)} records to {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            for record in records_written:
                f.write(json.dumps(record) + "\n")

        logger.info(f"Successfully captured {records_captured} records to {output_file}")
    else:
        logger.warning("No records were captured")

    return records_captured


def main():
    """Main entry point for the capture script."""
    parser = argparse.ArgumentParser(
        description="Capture ride_requests data from Confluent Cloud Kafka cluster",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --output assets/lab3/data/ride_requests.jsonl
  %(prog)s --from-beginning
  %(prog)s --topic ride_requests --output data.jsonl --max-records 50000
        """
    )

    parser.add_argument(
        "--topic",
        default="ride_requests",
        help="Kafka topic to consume from (default: ride_requests)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("assets/lab3/data/ride_requests.jsonl"),
        help="Output JSONL file path (default: assets/lab3/data/ride_requests.jsonl)"
    )
    parser.add_argument(
        "--max-records",
        type=int,
        default=None,
        help="Maximum number of records to capture (default: unlimited)"
    )
    parser.add_argument(
        "--from-beginning",
        action="store_true",
        help="Consume from beginning of topic (default: from latest)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Stop after N seconds of no new messages (default: 30)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set up logging
    logger = setup_logging(args.verbose)

    # Check confluent-kafka library is available
    if not CONFLUENT_KAFKA_AVAILABLE:
        logger.error("confluent-kafka library not available. Please install it with: uv pip install confluent-kafka")
        return 1

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

    # Get project root
    try:
        project_root = get_project_root()
    except Exception as e:
        logger.error(f"Could not find project root: {e}")
        return 1

    # Extract Kafka credentials
    try:
        logger.info(f"Extracting credentials for {cloud_provider.upper()}...")
        credentials = extract_kafka_credentials(cloud_provider, project_root)
    except Exception as e:
        logger.error(f"Failed to extract Kafka credentials: {e}")
        return 1

    # Capture data
    try:
        records_captured = capture_ride_requests(
            bootstrap_servers=credentials["bootstrap_servers"],
            kafka_api_key=credentials["kafka_api_key"],
            kafka_api_secret=credentials["kafka_api_secret"],
            topic=args.topic,
            output_file=args.output,
            max_records=args.max_records,
            from_beginning=args.from_beginning,
            timeout_seconds=args.timeout,
            logger=logger
        )

        print(f"\n{'=' * 60}")
        print("DATA CAPTURE SUMMARY")
        print(f"{'=' * 60}")
        print(f"Topic:            {args.topic}")
        print(f"Records captured: {records_captured}")
        print(f"Output file:      {args.output}")
        print(f"{'=' * 60}\n")

        return 0 if records_captured > 0 else 1

    except Exception as e:
        logger.error(f"Capture failed: {e}")
        if args.verbose:
            logger.error(f"Stack trace: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
