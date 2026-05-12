#!/usr/bin/env python3
"""
Capture Lab 1 data (orders, customers, products) from Confluent Cloud.

Consumes messages from each topic and saves them to JSONL files in
assets/lab1/data/ for distribution with the workshop repository.

Usage:
    uv run capture_lab1_data
    uv run capture_lab1_data --max-orders 500
    uv run capture_lab1_data --verbose
"""

import argparse
import base64
import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional

try:
    from confluent_kafka import Consumer, KafkaError, KafkaException
    CONFLUENT_KAFKA_AVAILABLE = True
except ImportError:
    CONFLUENT_KAFKA_AVAILABLE = False

from .common.cloud_detection import auto_detect_cloud_provider, suggest_cloud_provider
from .common.terraform import extract_kafka_credentials, get_project_root
from .common.logging_utils import setup_logging


def capture_topic(
    bootstrap_servers: str,
    kafka_api_key: str,
    kafka_api_secret: str,
    topic: str,
    output_file: Path,
    max_records: Optional[int] = None,
    timeout_seconds: int = 30,
    logger: Optional[logging.Logger] = None,
) -> int:
    if logger is None:
        logger = logging.getLogger(__name__)

    logger.info(f"Capturing topic '{topic}' → {output_file}")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    consumer_config = {
        "bootstrap.servers": bootstrap_servers,
        "sasl.mechanisms": "PLAIN",
        "security.protocol": "SASL_SSL",
        "sasl.username": kafka_api_key,
        "sasl.password": kafka_api_secret,
        "group.id": f"capture-lab1-data-{int(time.time())}",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
        "fetch.min.bytes": 1,
        "fetch.wait.max.ms": 500,
    }

    consumer = Consumer(consumer_config)
    consumer.subscribe([topic])

    records = []
    last_message_time = time.time()

    try:
        while True:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                if time.time() - last_message_time > timeout_seconds:
                    logger.info(f"No new messages for {timeout_seconds}s, stopping")
                    break
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                raise KafkaException(msg.error())

            last_message_time = time.time()
            key_bytes = msg.key()
            value_bytes = msg.value()

            record = {
                "key": base64.b64encode(key_bytes).decode("utf-8") if key_bytes else None,
                "value": base64.b64encode(value_bytes).decode("utf-8") if value_bytes else None,
                "partition": msg.partition(),
                "offset": msg.offset(),
            }
            records.append(record)

            if len(records) % 100 == 0:
                logger.info(f"  Captured {len(records)} records...")

            if max_records and len(records) >= max_records:
                logger.info(f"Reached maximum of {max_records} records")
                break

    except KeyboardInterrupt:
        logger.info("Capture interrupted")
    finally:
        consumer.close()

    if records:
        with open(output_file, "w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record) + "\n")
        logger.info(f"Wrote {len(records)} records to {output_file}")
    else:
        logger.warning(f"No records captured from '{topic}'")

    return len(records)


def main():
    parser = argparse.ArgumentParser(
        description="Capture Lab 1 data (orders, customers, products) from Confluent Cloud",
    )
    parser.add_argument(
        "--max-orders",
        type=int,
        default=500,
        help="Maximum orders to capture (default: 500; customers/products capture all)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Stop after N seconds of no new messages per topic (default: 30)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    logger = setup_logging(args.verbose)

    if not CONFLUENT_KAFKA_AVAILABLE:
        logger.error("confluent-kafka not available. Run: uv pip install confluent-kafka")
        return 1

    cloud_provider = auto_detect_cloud_provider()
    if not cloud_provider:
        cloud_provider = suggest_cloud_provider()
    if not cloud_provider:
        logger.error("Could not auto-detect cloud provider")
        return 1

    try:
        project_root = get_project_root()
        credentials = extract_kafka_credentials(cloud_provider, project_root)
    except Exception as e:
        logger.error(f"Failed to extract credentials: {e}")
        return 1

    output_dir = project_root / "assets" / "lab1" / "data"
    conn = {
        "bootstrap_servers": credentials["bootstrap_servers"],
        "kafka_api_key": credentials["kafka_api_key"],
        "kafka_api_secret": credentials["kafka_api_secret"],
    }

    topics = [
        ("customers", None),
        ("products", None),
        ("orders", args.max_orders),
    ]

    totals = {}
    for topic, max_records in topics:
        count = capture_topic(
            **conn,
            topic=topic,
            output_file=output_dir / f"{topic}.jsonl",
            max_records=max_records,
            timeout_seconds=args.timeout,
            logger=logger,
        )
        totals[topic] = count

    print(f"\n{'=' * 50}")
    print("LAB 1 CAPTURE SUMMARY")
    print(f"{'=' * 50}")
    for topic, count in totals.items():
        print(f"  {topic:<12} {count:>6} records  →  assets/lab1/data/{topic}.jsonl")
    print(f"{'=' * 50}\n")

    return 0 if all(v > 0 for v in totals.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
