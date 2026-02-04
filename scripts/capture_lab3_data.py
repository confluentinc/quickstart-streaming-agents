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
import json
import logging
import select
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from .common.cloud_detection import auto_detect_cloud_provider, suggest_cloud_provider
from .common.login_checks import check_confluent_login
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
    schema_registry_url: str,
    schema_registry_api_key: str,
    schema_registry_api_secret: str,
    topic: str,
    output_file: Path,
    max_records: Optional[int] = None,
    from_beginning: bool = False,
    timeout_seconds: int = 30,
    environment_id: Optional[str] = None,
    cluster_id: Optional[str] = None,
    logger: Optional[logging.Logger] = None
) -> int:
    """
    Capture ride request data from Kafka topic using Confluent CLI.

    Args:
        bootstrap_servers: Kafka bootstrap servers
        kafka_api_key: Kafka API key
        kafka_api_secret: Kafka API secret
        schema_registry_url: Schema Registry URL
        schema_registry_api_key: Schema Registry API key
        schema_registry_api_secret: Schema Registry API secret
        topic: Kafka topic name
        output_file: Path to output JSONL file
        max_records: Maximum number of records to capture (None = unlimited)
        from_beginning: If True, start from beginning of topic
        timeout_seconds: Stop consuming after this many seconds of no new messages
        environment_id: Confluent environment ID (optional)
        cluster_id: Confluent cluster ID (optional)
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

    # Build confluent CLI consume command
    cmd = [
        "confluent", "kafka", "topic", "consume", topic,
        "--value-format", "avro",
        "--print-key",
        "--delimiter", ":",
        "--bootstrap", bootstrap_servers,
        "--api-key", kafka_api_key,
        "--api-secret", kafka_api_secret,
        "--schema-registry-endpoint", schema_registry_url,
        "--schema-registry-api-key", schema_registry_api_key,
        "--schema-registry-api-secret", schema_registry_api_secret,
    ]

    # Add environment and cluster if provided
    if environment_id:
        cmd.extend(["--environment", environment_id])
    if cluster_id:
        cmd.extend(["--cluster", cluster_id])

    # Add from-beginning if requested
    if from_beginning:
        cmd.append("--from-beginning")
        logger.info("Consuming from beginning of topic")
    else:
        logger.info("Consuming from latest offset")

    logger.debug(f"Running command: {' '.join(cmd[:5])}...")

    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Run consume command
        # Use binary mode and decode with error handling for non-UTF8 characters
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1
        )

        records_captured = 0
        records_written = []
        last_message_time = time.time()
        lines_processed = 0

        logger.info("Starting to consume messages...")
        logger.debug("Waiting for data from Confluent CLI...")

        # Read output line by line with timeout detection
        while True:
            # Check if process has data available (non-blocking)
            if process.poll() is not None:
                # Process ended
                break

            line_bytes = process.stdout.readline()
            if not line_bytes:
                # Check timeout when no data
                if time.time() - last_message_time > timeout_seconds:
                    logger.info(f"No new messages for {timeout_seconds}s, stopping capture")
                    process.terminate()
                    break
                time.sleep(0.1)
                continue

            # Decode with error handling
            try:
                line = line_bytes.decode('utf-8', errors='replace').strip()
            except Exception as e:
                logger.debug(f"Failed to decode line: {e}")
                continue

            if not line:
                continue

            # Update last message time
            last_message_time = time.time()
            lines_processed += 1

            # Log first few lines to debug format
            if lines_processed <= 3:
                logger.debug(f"Line {lines_processed}: {line[:200]}")

            try:
                # Skip lines that look like CLI headers/banners
                if line.startswith("Starting") or line.startswith("Processed"):
                    logger.debug(f"Skipping CLI header: {line[:100]}")
                    continue

                # Strip binary header bytes (Avro record metadata)
                # Find the first colon followed by JSON
                json_start = line.find(':{')
                if json_start == -1:
                    logger.debug(f"No JSON found in line: {line[:100]}")
                    continue

                # Extract just the JSON part (everything after ':')
                value_str = line[json_start + 1:].strip()

                # Ensure value looks like JSON
                if not value_str.startswith("{"):
                    logger.debug(f"Value doesn't look like JSON: {value_str[:100]}")
                    continue

                # Parse the JSON value
                value = json.loads(value_str)

                # Flatten Avro union types if present
                # Avro unions come as {"type": value}, we want just value
                flattened_record = {}
                for field, field_value in value.items():
                    if isinstance(field_value, dict) and len(field_value) == 1:
                        # This looks like an Avro union type wrapper
                        inner_type = list(field_value.keys())[0]
                        if inner_type in ["string", "int", "long", "double", "float", "boolean"]:
                            flattened_record[field] = field_value[inner_type]
                        else:
                            flattened_record[field] = field_value
                    else:
                        flattened_record[field] = field_value

                # Validate required fields
                required_fields = ["request_id", "customer_email", "pickup_zone",
                                 "drop_off_zone", "price", "number_of_passengers", "request_ts"]

                if not all(field in flattened_record for field in required_fields):
                    logger.debug(f"Skipping record with missing fields: {flattened_record}")
                    continue

                # Convert request_ts from ISO string to long (milliseconds since epoch)
                # The Avro schema expects a long, but CLI outputs ISO string
                if isinstance(flattened_record.get("request_ts"), str):
                    try:
                        dt = datetime.fromisoformat(flattened_record["request_ts"].replace('Z', '+00:00'))
                        flattened_record["request_ts"] = int(dt.timestamp() * 1000)
                    except Exception as e:
                        logger.debug(f"Failed to convert timestamp: {e}")

                records_written.append(flattened_record)
                records_captured += 1

                # Show progress
                if records_captured % 1000 == 0:
                    logger.info(f"Captured {records_captured} records...")

                # Stop if we've reached max records (if specified)
                if max_records and records_captured >= max_records:
                    logger.info(f"Reached maximum of {max_records} records")
                    process.terminate()
                    break

            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON at line {lines_processed}: {e}")
                logger.debug(f"  JSON string (first 200 chars): {value_str[:200]}")
                logger.debug(f"  Full line (first 200 chars): {line[:200]}")
                continue
            except Exception as e:
                logger.warning(f"Error processing line {lines_processed}: {e}")
                logger.debug(f"  Line (first 200 chars): {line[:200]}")
                continue

        # Wait for process to finish
        process.wait()

        # Check for errors in stderr
        if process.stderr:
            stderr_output = process.stderr.read().decode('utf-8', errors='replace')
            if stderr_output and "error" in stderr_output.lower():
                logger.warning(f"Confluent CLI stderr: {stderr_output[:500]}")

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

    except KeyboardInterrupt:
        logger.info("Capture interrupted by user")
        process.terminate()
        return records_captured
    except Exception as e:
        logger.error(f"Failed to capture data: {e}")
        return 0


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

    # Check Confluent CLI login
    if not check_confluent_login():
        print("\n" + "=" * 60)
        print("ERROR: Not logged into Confluent Cloud")
        print("=" * 60)
        print("\nYou must be logged in to capture data.")
        print("\nTo log in, run:")
        print("  confluent login")
        print("\nTo avoid session timeouts, save credentials with:")
        print("  confluent login --save")
        print("=" * 60 + "\n")
        return 1

    logger.info("✓ Confluent CLI logged in")

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
            schema_registry_url=credentials["schema_registry_url"],
            schema_registry_api_key=credentials["schema_registry_api_key"],
            schema_registry_api_secret=credentials["schema_registry_api_secret"],
            topic=args.topic,
            output_file=args.output,
            max_records=args.max_records,
            from_beginning=args.from_beginning,
            timeout_seconds=args.timeout,
            environment_id=credentials.get("environment_id"),
            cluster_id=credentials.get("cluster_id"),
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
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
