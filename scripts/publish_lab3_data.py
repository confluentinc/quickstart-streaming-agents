#!/usr/bin/env python3
"""
CLI-based Lab3 ride requests data publisher for quickstart-streaming-agents.

Publishes pre-generated JSONL ride request data to eliminate ShadowTraffic/Docker
dependencies for workshop participants.

Decodes captured Avro bytes and re-serializes using AvroSerializer so that
schemas are properly registered in the user's Schema Registry. Timestamps
are rebased so the data ends at the current time, producing ~24 hours of
data with the anomaly spike landing near "now".

Usage:
    uv run publish_lab3_data --data-file assets/lab3/data/ride_requests.jsonl
    uv run publish_lab3_data --data-file assets/lab3/data/ride_requests.jsonl --dry-run

Traditional Python:
    python scripts/publish_lab3_data.py --data-file assets/lab3/data/ride_requests.jsonl
"""

import argparse
import base64
import datetime
import io
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

try:
    from confluent_kafka import Producer
    from confluent_kafka.schema_registry import SchemaRegistryClient
    from confluent_kafka.schema_registry.avro import AvroSerializer
    from confluent_kafka.serialization import (
        SerializationContext,
        MessageField,
        StringSerializer,
    )
    CONFLUENT_KAFKA_AVAILABLE = True
except ImportError:
    CONFLUENT_KAFKA_AVAILABLE = False

try:
    import avro.io
    import avro.schema
    AVRO_AVAILABLE = True
except ImportError:
    AVRO_AVAILABLE = False

from .common.cloud_detection import auto_detect_cloud_provider, validate_cloud_provider, suggest_cloud_provider
from .common.terraform import extract_kafka_credentials, validate_terraform_state, get_project_root
from .common.logging_utils import setup_logging


# Avro schema for ride_requests value (matches ShadowTraffic avroSchemaHint)
VALUE_SCHEMA_STR = json.dumps({
    "type": "record",
    "name": "ride_requests_value",
    "namespace": "org.apache.flink.avro.generated.record",
    "fields": [
        {"name": "request_id", "type": "string"},
        {"name": "customer_email", "type": "string"},
        {"name": "pickup_zone", "type": "string"},
        {"name": "drop_off_zone", "type": "string"},
        {"name": "price", "type": "double"},
        {"name": "number_of_passengers", "type": "int"},
        {"name": "request_ts", "type": {"type": "long", "logicalType": "timestamp-millis"}},
    ],
})

# Avro schema for ride_requests key (simple string)
KEY_SCHEMA_STR = json.dumps({
    "type": "string",
})


def decode_avro_bytes(raw_bytes: bytes, schema_str: str) -> Any:
    """
    Decode Confluent wire-format Avro bytes (magic byte + 4-byte schema ID + payload).

    Returns the deserialized Python object.
    """
    if len(raw_bytes) < 5:
        raise ValueError(f"Avro payload too short ({len(raw_bytes)} bytes)")

    magic = raw_bytes[0]
    if magic != 0:
        raise ValueError(f"Invalid Avro magic byte: {magic}")

    # Skip 5-byte header (1 magic + 4 schema ID)
    avro_payload = raw_bytes[5:]
    schema = avro.schema.parse(schema_str)
    reader = avro.io.DatumReader(schema)
    decoder = avro.io.BinaryDecoder(io.BytesIO(avro_payload))
    result = reader.read(decoder)

    # Convert datetime objects back to epoch millis for AvroSerializer
    if isinstance(result, dict):
        for key, val in result.items():
            if isinstance(val, datetime.datetime):
                result[key] = int(val.timestamp() * 1000)

    return result


WINDOW_SIZE_MS = 5 * 60 * 1000  # 5-minute tumbling windows


def _extract_ts(line: str, schema) -> int:
    """Extract request_ts (epoch ms) from a JSONL line."""
    record = json.loads(line)
    raw_value = base64.b64decode(record["value"]) if record.get("value") else None
    if raw_value is None or len(raw_value) < 5:
        return 0
    reader = avro.io.DatumReader(schema)
    decoder = avro.io.BinaryDecoder(io.BytesIO(raw_value[5:]))
    val = reader.read(decoder)
    ts = val["request_ts"]
    if isinstance(ts, datetime.datetime):
        ts = int(ts.timestamp() * 1000)
    return ts


def compute_timestamp_offset(lines: List[str]) -> tuple:
    """
    Scan all JSONL lines to find the max request_ts, then compute an offset
    that rebases the data so the last few messages land 10s past aligned_end.
    This advances the Flink watermark past aligned_end, closing all 288
    windows. With minTrainingSize=287, only the last closed window (288th)
    is eligible for anomaly detection. Returns (offset_ms, aligned_start_ms).
    """
    schema = avro.schema.parse(VALUE_SCHEMA_STR)
    max_ts = 0

    for line in lines:
        ts = _extract_ts(line, schema)
        if ts > max_ts:
            max_ts = ts

    # Round "now" down to the nearest 5-minute boundary
    now_ms = int(time.time() * 1000)
    aligned_end = (now_ms // WINDOW_SIZE_MS) * WINDOW_SIZE_MS
    num_windows = 288
    aligned_start = aligned_end - (num_windows * WINDOW_SIZE_MS)

    # Shift max_ts to 10s past aligned_end so the last few real messages
    # land in a 289th window and advance the watermark past aligned_end,
    # closing the 288th window (the spike window).
    watermark_buffer_ms = 10_000
    offset_ms = (aligned_end + watermark_buffer_ms) - max_ts
    return offset_ms, aligned_start


class Lab3DataPublisher:
    """Publisher for Lab3 ride request data using AvroSerializer for proper Schema Registry integration."""

    def __init__(
        self,
        bootstrap_servers: str,
        kafka_api_key: str,
        kafka_api_secret: str,
        schema_registry_url: str,
        schema_registry_api_key: str,
        schema_registry_api_secret: str,
        dry_run: bool = False,
    ):
        self.dry_run = dry_run
        self.logger = logging.getLogger(__name__)

        # Schema Registry client
        sr_conf = {
            "url": schema_registry_url,
            "basic.auth.user.info": f"{schema_registry_api_key}:{schema_registry_api_secret}",
        }
        sr_client = SchemaRegistryClient(sr_conf)

        # Serializers
        self.value_serializer = AvroSerializer(sr_client, VALUE_SCHEMA_STR)
        self.key_serializer = StringSerializer("utf_8")

        # Kafka producer
        self.producer_config = {
            "bootstrap.servers": bootstrap_servers,
            "sasl.mechanisms": "PLAIN",
            "security.protocol": "SASL_SSL",
            "sasl.username": kafka_api_key,
            "sasl.password": kafka_api_secret,
            "linger.ms": 10,
            "batch.size": 16384,
            "compression.type": "snappy",
        }

        self.producer = None
        if not dry_run:
            self.producer = Producer(self.producer_config)

    def publish_message(
        self, record: Dict[str, Any], topic: str,
        ts_offset_ms: int = 0, start_ms: int = 0,
    ) -> str:
        """
        Decode a captured Avro message, rebase its timestamp, and re-publish.

        Returns "ok", "skipped" (outside time window), or "error".
        """
        try:
            raw_key = base64.b64decode(record["key"]) if record.get("key") else None
            raw_value = base64.b64decode(record["value"]) if record.get("value") else None

            if raw_value is None:
                self.logger.warning("Skipping message with null value")
                return "error"

            value_dict = decode_avro_bytes(raw_value, VALUE_SCHEMA_STR)
            key_str = decode_avro_bytes(raw_key, KEY_SCHEMA_STR) if raw_key else None

            # Rebase timestamp to current time
            if ts_offset_ms and "request_ts" in value_dict:
                value_dict["request_ts"] += ts_offset_ms

            # Drop messages before the 24-hour window start
            rebased_ts = value_dict.get("request_ts", 0)
            if start_ms and rebased_ts < start_ms:
                return "skipped"

            if self.dry_run:
                self.logger.debug(f"[DRY RUN] Would publish: key={key_str}, value={value_dict}")
                return "ok"

            # Re-serialize with AvroSerializer (registers schema in user's SR)
            ctx_value = SerializationContext(topic, MessageField.VALUE)
            serialized_value = self.value_serializer(value_dict, ctx_value)

            serialized_key = None
            if key_str is not None:
                ctx_key = SerializationContext(topic, MessageField.KEY)
                serialized_key = self.key_serializer(key_str, ctx_key)

            self.producer.produce(
                topic,
                key=serialized_key,
                value=serialized_value,
            )
            return "ok"

        except Exception as e:
            self.logger.error(f"Failed to publish message: {e}")
            return "error"

    def publish_jsonl_file(self, jsonl_file: Path, topic: str) -> Dict[str, int]:
        """Publish all messages from a JSONL file, re-serializing with AvroSerializer."""
        results = {"success": 0, "failed": 0, "skipped": 0, "total": 0}

        try:
            with open(jsonl_file, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
        except Exception as e:
            self.logger.error(f"Failed to read JSONL file {jsonl_file}: {e}")
            return results

        results["total"] = len(lines)
        self.logger.info(f"Found {len(lines)} messages to publish")

        # Compute timestamp offset so data ends at "now" aligned to 5-min boundary
        self.logger.info("Scanning timestamps to rebase data to current time...")
        ts_offset_ms, start_ms = compute_timestamp_offset(lines)
        offset_hours = ts_offset_ms / (1000 * 60 * 60)
        end_ms = start_ms + (288 * WINDOW_SIZE_MS)
        start_dt = datetime.datetime.fromtimestamp(start_ms / 1000, tz=datetime.timezone.utc)
        end_dt = datetime.datetime.fromtimestamp(end_ms / 1000, tz=datetime.timezone.utc)
        self.logger.info(f"Rebasing timestamps by {offset_hours:+.1f} hours")
        self.logger.info(f"Time window: {start_dt.strftime('%Y-%m-%d %H:%M')} to {end_dt.strftime('%Y-%m-%d %H:%M')} UTC (288 x 5-min windows)")

        for idx, line in enumerate(lines, 1):
            try:
                message_data = json.loads(line)
                status = self.publish_message(message_data, topic, ts_offset_ms, start_ms)
                if status == "ok":
                    results["success"] += 1
                elif status == "skipped":
                    results["skipped"] += 1
                else:
                    results["failed"] += 1

                if not self.dry_run and idx % 100 == 0:
                    self.producer.poll(0)

                if not self.dry_run and idx % 1000 == 0:
                    self.producer.flush()
                    self.logger.info(
                        f"Progress: {idx}/{results['total']} messages "
                        f"({results['success']} succeeded, {results['failed']} failed)"
                    )

            except json.JSONDecodeError as e:
                self.logger.error(f"Error parsing line {idx}: {e}")
                results["failed"] += 1
            except Exception as e:
                self.logger.error(f"Error processing line {idx}: {e}")
                results["failed"] += 1

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
        help="Path to JSONL data file with ride requests",
    )
    parser.add_argument(
        "--topic",
        default="ride_requests",
        help="Kafka topic name (default: ride_requests)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Test without actually publishing")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    logger = setup_logging(args.verbose)

    if not args.data_file.exists():
        logger.error(f"Data file does not exist: {args.data_file}")
        return 1

    if not CONFLUENT_KAFKA_AVAILABLE:
        logger.error(
            "confluent-kafka library not available. "
            "Please install it with: uv pip install confluent-kafka[avro,schema-registry]"
        )
        return 1

    if not AVRO_AVAILABLE:
        logger.error(
            "avro-python3 library not available. "
            "Please install it with: uv pip install avro-python3"
        )
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

    if not validate_cloud_provider(cloud_provider):
        logger.error(f"Invalid cloud provider: {cloud_provider}")
        return 1

    try:
        project_root = get_project_root()
    except Exception as e:
        logger.error(f"Could not find project root: {e}")
        return 1

    try:
        validate_terraform_state(cloud_provider, project_root)
    except Exception as e:
        logger.error(f"Terraform validation failed: {e}")
        return 1

    try:
        credentials = extract_kafka_credentials(cloud_provider, project_root)
    except Exception as e:
        logger.error(f"Failed to extract Kafka credentials: {e}")
        return 1

    try:
        publisher = Lab3DataPublisher(
            bootstrap_servers=credentials["bootstrap_servers"],
            kafka_api_key=credentials["kafka_api_key"],
            kafka_api_secret=credentials["kafka_api_secret"],
            schema_registry_url=credentials["schema_registry_url"],
            schema_registry_api_key=credentials["schema_registry_api_key"],
            schema_registry_api_secret=credentials["schema_registry_api_secret"],
            dry_run=args.dry_run,
        )
    except Exception as e:
        logger.error(f"Failed to initialize publisher: {e}")
        return 1

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
        print(f"Skipped (trim):   {results['skipped']}")
        print(f"Failed:           {results['failed']}")
        print(f"{'=' * 60}")

        if args.dry_run:
            print("\n[DRY RUN COMPLETE - No messages were actually published]")

        return 0 if results["failed"] == 0 else 1
    finally:
        publisher.close()


if __name__ == "__main__":
    sys.exit(main())
