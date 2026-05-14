#!/usr/bin/env python3
"""
Publish pre-generated Lab 1 data (customers, products, orders) to Confluent Cloud.

Reads CSV files from assets/lab1/data/, rebases order_ts to end ~2 minutes before
now, re-serializes each record with AvroSerializer, and publishes to the
customers, products, and orders Kafka topics.

Publish order: customers → products → orders
(lookup tables first so Flink joins succeed when orders arrive)

Usage:
    uv run publish_lab1_data
    uv run publish_lab1_data --dry-run
"""

import argparse
import csv
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

try:
    from confluent_kafka import Producer
    from confluent_kafka.schema_registry import SchemaRegistryClient
    from confluent_kafka.schema_registry.avro import AvroSerializer
    from confluent_kafka.serialization import SerializationContext, MessageField

    CONFLUENT_KAFKA_AVAILABLE = True
except ImportError:
    CONFLUENT_KAFKA_AVAILABLE = False

from .common.cloud_detection import (
    auto_detect_cloud_provider,
    validate_cloud_provider,
    suggest_cloud_provider,
)
from .common.terraform import (
    extract_kafka_credentials,
    validate_terraform_state,
    get_project_root,
)
from .common.logging_utils import setup_logging


CUSTOMERS_VALUE_SCHEMA_STR = json.dumps(
    {
        "type": "record",
        "name": "customers_value",
        "namespace": "org.apache.flink.avro.generated.record",
        "fields": [
            {"name": "customer_id", "type": "string"},
            {"name": "customer_email", "type": "string"},
            {"name": "customer_name", "type": "string"},
            {"name": "state", "type": "string"},
            {
                "name": "updated_at",
                "type": {"type": "long", "logicalType": "timestamp-millis"},
            },
        ],
    }
)

PRODUCTS_VALUE_SCHEMA_STR = json.dumps(
    {
        "type": "record",
        "name": "products_value",
        "namespace": "org.apache.flink.avro.generated.record",
        "fields": [
            {"name": "product_id", "type": "string"},
            {"name": "product_name", "type": "string"},
            {"name": "price", "type": "double"},
            {"name": "department", "type": "string"},
            {
                "name": "updated_at",
                "type": {"type": "long", "logicalType": "timestamp-millis"},
            },
        ],
    }
)

ORDERS_VALUE_SCHEMA_STR = json.dumps(
    {
        "type": "record",
        "name": "orders_value",
        "namespace": "org.apache.flink.avro.generated.record",
        "fields": [
            {"name": "order_id", "type": "string"},
            {"name": "customer_id", "type": "string"},
            {"name": "product_id", "type": "string"},
            {"name": "price", "type": "double"},
            {
                "name": "order_ts",
                "type": {"type": "long", "logicalType": "timestamp-millis"},
            },
        ],
    }
)

SCHEMAS = {
    "customers": CUSTOMERS_VALUE_SCHEMA_STR,
    "products": PRODUCTS_VALUE_SCHEMA_STR,
    "orders": ORDERS_VALUE_SCHEMA_STR,
}

TS_FIELD = {"orders": "order_ts"}

ORDERS_PUBLISH_INTERVAL_SECONDS = 120


def _parse_iso_ms(s: str) -> int:
    return int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() * 1000)


def _coerce_row(topic: str, row: dict, now_ms: int = 0) -> dict:
    record = dict(row)
    if "price" in record:
        record["price"] = float(record["price"])
    if "updated_at" in record:
        record["updated_at"] = now_ms
    if "order_ts" in record:
        record["order_ts"] = _parse_iso_ms(record["order_ts"])
    return record


def compute_orders_ts_offset(csv_file: Path) -> int:
    """Compute ms offset to rebase order_ts so the latest order lands 2 minutes before now."""
    max_ts = 0
    with open(csv_file, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ts = _parse_iso_ms(row["order_ts"])
            if ts > max_ts:
                max_ts = ts
    if max_ts == 0:
        return 0
    target_ms = int(time.time() * 1000) - (2 * 60 * 1000)
    return target_ms - max_ts


class Lab1DataPublisher:
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

        sr_conf = {
            "url": schema_registry_url,
            "basic.auth.user.info": f"{schema_registry_api_key}:{schema_registry_api_secret}",
        }
        sr_client = SchemaRegistryClient(sr_conf)

        self.serializers = {
            topic: AvroSerializer(sr_client, schema_str)
            for topic, schema_str in SCHEMAS.items()
        }

        producer_conf = {
            "bootstrap.servers": bootstrap_servers,
            "sasl.mechanisms": "PLAIN",
            "security.protocol": "SASL_SSL",
            "sasl.username": kafka_api_key,
            "sasl.password": kafka_api_secret,
            "linger.ms": 10,
            "batch.size": 16384,
            "compression.type": "snappy",
        }
        self._producer_conf = producer_conf
        self.producer = None if dry_run else Producer(producer_conf)

    def purge_topic(self, topic: str) -> None:
        from confluent_kafka.admin import AdminClient, OffsetSpec
        from confluent_kafka import TopicPartition as AdminTP

        self.logger.info(f"Purging '{topic}'...")
        admin = AdminClient(
            {
                k: v
                for k, v in self._producer_conf.items()
                if k
                in (
                    "bootstrap.servers",
                    "sasl.mechanisms",
                    "security.protocol",
                    "sasl.username",
                    "sasl.password",
                )
            }
        )
        try:
            meta = admin.list_topics(topic=topic, timeout=10)
            if topic not in meta.topics:
                return
            tps = [AdminTP(topic, p) for p in meta.topics[topic].partitions]
            futures = admin.list_offsets({tp: OffsetSpec.latest() for tp in tps})
            delete_offsets = {
                tp: AdminTP(tp.topic, tp.partition, fut.result().offset)
                for tp, fut in futures.items()
                if fut.result().offset > 0
            }
            if delete_offsets:
                for fut in admin.delete_records(delete_offsets).values():
                    fut.result()
                self.logger.info(
                    f"Purged {len(delete_offsets)} partition(s) in '{topic}'"
                )
            else:
                self.logger.info(f"'{topic}' already empty")
        except Exception as e:
            self.logger.warning(f"Could not purge '{topic}': {e} — continuing")

    def publish_topic(
        self, topic: str, csv_file: Path, ts_offset_ms: int = 0
    ) -> Dict[str, int]:
        results = {"success": 0, "failed": 0, "total": 0}
        ts_field = TS_FIELD.get(topic)
        serializer = self.serializers[topic]

        try:
            with open(csv_file, newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
        except Exception as e:
            self.logger.error(f"Could not read {csv_file}: {e}")
            return results

        results["total"] = len(rows)
        self.logger.info(f"Publishing {len(rows)} records to '{topic}'")

        if not self.dry_run:
            self.purge_topic(topic)

        now_ms = int(time.time() * 1000)
        for idx, row in enumerate(rows, 1):
            try:
                value_dict = _coerce_row(topic, row, now_ms=now_ms)

                if topic == "orders":
                    value_dict["order_ts"] = int(time.time() * 1000)
                elif ts_field and ts_offset_ms and ts_field in value_dict:
                    value_dict[ts_field] += ts_offset_ms

                if self.dry_run:
                    self.logger.debug(f"[DRY RUN] {topic}: {value_dict}")
                    results["success"] += 1
                    continue

                ctx = SerializationContext(topic, MessageField.VALUE)
                serialized = serializer(value_dict, ctx)
                self.producer.produce(topic, value=serialized, partition=0)
                results["success"] += 1

                if topic == "orders":
                    self.producer.flush()
                    self.logger.info(
                        f"Published order {idx}/{len(rows)}: {value_dict['order_id']}"
                    )
                    if idx < len(rows):
                        self.logger.info(
                            f"Waiting {ORDERS_PUBLISH_INTERVAL_SECONDS}s before next order..."
                        )
                        time.sleep(ORDERS_PUBLISH_INTERVAL_SECONDS)
                elif idx % 100 == 0:
                    self.producer.poll(0)

            except Exception as e:
                self.logger.error(f"Error on row {idx} of {topic}: {e}")
                results["failed"] += 1

        if not self.dry_run and self.producer:
            self.producer.flush()

        return results

    def close(self):
        if self.producer:
            self.producer.flush()


def main():
    parser = argparse.ArgumentParser(
        description="Publish pre-generated Lab 1 data to Confluent Cloud",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Directory containing customers.csv, products.csv, orders.csv "
        "(default: assets/lab1/data/)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logger = setup_logging(args.verbose)

    if not CONFLUENT_KAFKA_AVAILABLE:
        logger.error(
            "confluent-kafka not available. Run: uv pip install confluent-kafka[avro,schema-registry]"
        )
        return 1

    cloud_provider = auto_detect_cloud_provider()
    if not cloud_provider:
        cloud_provider = suggest_cloud_provider()
    if not cloud_provider:
        logger.error("Could not auto-detect cloud provider")
        return 1
    if not validate_cloud_provider(cloud_provider):
        logger.error(f"Invalid cloud provider: {cloud_provider}")
        return 1

    try:
        project_root = get_project_root()
        validate_terraform_state(cloud_provider, project_root)
        credentials = extract_kafka_credentials(cloud_provider, project_root)
    except Exception as e:
        logger.error(f"Credential extraction failed: {e}")
        return 1

    data_dir = args.data_dir or (project_root / "assets" / "lab1" / "data")
    for topic in ("customers", "products", "orders"):
        f = data_dir / f"{topic}.csv"
        if not f.exists():
            logger.error(
                f"Data file not found: {f} — ensure you are on the mcp-lambda branch and files are present in assets/lab1/data/"
            )
            return 1

    publisher = Lab1DataPublisher(
        bootstrap_servers=credentials["bootstrap_servers"],
        kafka_api_key=credentials["kafka_api_key"],
        kafka_api_secret=credentials["kafka_api_secret"],
        schema_registry_url=credentials["schema_registry_url"],
        schema_registry_api_key=credentials["schema_registry_api_key"],
        schema_registry_api_secret=credentials["schema_registry_api_secret"],
        dry_run=args.dry_run,
    )

    try:
        if args.dry_run:
            logger.info("[DRY RUN MODE]")

        logger.info(
            f"Orders will be published one every {ORDERS_PUBLISH_INTERVAL_SECONDS}s "
            f"with order_ts set to publish time"
        )

        all_results = {}
        for topic in ("customers", "products", "orders"):
            results = publisher.publish_topic(topic, data_dir / f"{topic}.csv", 0)
            all_results[topic] = results

        print(f"\n{'=' * 55}")
        print("LAB 1 DATA PUBLISHING SUMMARY")
        print(f"{'=' * 55}")
        for topic, r in all_results.items():
            print(
                f"  {topic:<12}  published: {r['success']:>4}  failed: {r['failed']:>3}  total: {r['total']:>4}"
            )
        print(f"{'=' * 55}")
        if args.dry_run:
            print("\n[DRY RUN — no messages actually published]")

        total_failed = sum(r["failed"] for r in all_results.values())
        return 0 if total_failed == 0 else 1

    finally:
        publisher.close()


if __name__ == "__main__":
    sys.exit(main())
