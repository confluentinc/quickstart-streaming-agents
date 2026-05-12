#!/usr/bin/env python3
"""
Publish pre-captured Lab 1 data (customers, products, orders) to Confluent Cloud.

Replays captured JSONL files without requiring ShadowTraffic or Docker.
Decodes raw Avro bytes and re-serializes with AvroSerializer so schemas are
properly registered in the user's Schema Registry.

Orders timestamps (order_ts) are rebased to end ~2 minutes before now so
the enriched_orders Flink pipeline sees fresh data. customers and products
are published as-is (no timestamp rebasing needed for lookup tables).

Publish order: customers → products → orders
(lookup tables first so joins succeed when orders arrive)

Usage:
    uv run publish_lab1_data
    uv run publish_lab1_data --dry-run
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
from typing import Any, Dict, List, Optional

try:
    from confluent_kafka import Producer
    from confluent_kafka.schema_registry import SchemaRegistryClient
    from confluent_kafka.schema_registry.avro import AvroSerializer
    from confluent_kafka.serialization import SerializationContext, MessageField
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


CUSTOMERS_VALUE_SCHEMA_STR = json.dumps({
    "type": "record",
    "name": "customers_value",
    "namespace": "org.apache.flink.avro.generated.record",
    "fields": [
        {"name": "customer_id", "type": "string"},
        {"name": "customer_email", "type": "string"},
        {"name": "customer_name", "type": "string"},
        {"name": "state", "type": "string"},
        {"name": "updated_at", "type": {"type": "long", "logicalType": "timestamp-millis"}},
    ],
})

PRODUCTS_VALUE_SCHEMA_STR = json.dumps({
    "type": "record",
    "name": "products_value",
    "namespace": "org.apache.flink.avro.generated.record",
    "fields": [
        {"name": "product_id", "type": "string"},
        {"name": "product_name", "type": "string"},
        {"name": "price", "type": "double"},
        {"name": "department", "type": "string"},
        {"name": "updated_at", "type": {"type": "long", "logicalType": "timestamp-millis"}},
    ],
})

ORDERS_VALUE_SCHEMA_STR = json.dumps({
    "type": "record",
    "name": "orders_value",
    "namespace": "org.apache.flink.avro.generated.record",
    "fields": [
        {"name": "order_id", "type": "string"},
        {"name": "customer_id", "type": "string"},
        {"name": "product_id", "type": "string"},
        {"name": "price", "type": "double"},
        {"name": "order_ts", "type": {"type": "long", "logicalType": "timestamp-millis"}},
    ],
})

SCHEMAS = {
    "customers": CUSTOMERS_VALUE_SCHEMA_STR,
    "products": PRODUCTS_VALUE_SCHEMA_STR,
    "orders": ORDERS_VALUE_SCHEMA_STR,
}

# Field used for timestamp rebasing (orders only)
TS_FIELD = {"orders": "order_ts"}


def decode_avro_value(raw_bytes: bytes, schema_str: str) -> Any:
    """Decode Confluent wire-format Avro (magic byte + 4-byte schema ID + payload)."""
    if len(raw_bytes) < 5:
        raise ValueError(f"Avro payload too short ({len(raw_bytes)} bytes)")
    if raw_bytes[0] != 0:
        raise ValueError(f"Invalid Avro magic byte: {raw_bytes[0]}")
    schema = avro.schema.parse(schema_str)
    reader = avro.io.DatumReader(schema)
    result = reader.read(avro.io.BinaryDecoder(io.BytesIO(raw_bytes[5:])))
    if isinstance(result, dict):
        for k, v in result.items():
            if isinstance(v, datetime.datetime):
                result[k] = int(v.timestamp() * 1000)
    return result


def compute_orders_ts_offset(lines: List[str]) -> int:
    """Compute ms offset to rebase order_ts so the latest order is 2 minutes before now."""
    schema = avro.schema.parse(ORDERS_VALUE_SCHEMA_STR)
    max_ts = 0
    for line in lines:
        record = json.loads(line)
        raw = base64.b64decode(record["value"]) if record.get("value") else None
        if raw and len(raw) >= 5:
            val = avro.io.DatumReader(schema).read(avro.io.BinaryDecoder(io.BytesIO(raw[5:])))
            ts = val.get("order_ts", 0)
            if isinstance(ts, datetime.datetime):
                ts = int(ts.timestamp() * 1000)
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
        admin = AdminClient({k: v for k, v in self._producer_conf.items()
                             if k in ("bootstrap.servers", "sasl.mechanisms",
                                      "security.protocol", "sasl.username", "sasl.password")})
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
                self.logger.info(f"Purged {len(delete_offsets)} partition(s) in '{topic}'")
            else:
                self.logger.info(f"'{topic}' already empty")
        except Exception as e:
            self.logger.warning(f"Could not purge '{topic}': {e} — continuing")

    def publish_topic(
        self, topic: str, jsonl_file: Path, ts_offset_ms: int = 0
    ) -> Dict[str, int]:
        results = {"success": 0, "failed": 0, "total": 0}
        schema_str = SCHEMAS[topic]
        ts_field = TS_FIELD.get(topic)
        serializer = self.serializers[topic]

        try:
            lines = [l.strip() for l in jsonl_file.read_text().splitlines() if l.strip()]
        except Exception as e:
            self.logger.error(f"Could not read {jsonl_file}: {e}")
            return results

        results["total"] = len(lines)
        self.logger.info(f"Publishing {len(lines)} records to '{topic}'")

        if not self.dry_run:
            self.purge_topic(topic)

        for idx, line in enumerate(lines, 1):
            try:
                record = json.loads(line)
                raw_value = base64.b64decode(record["value"]) if record.get("value") else None
                if raw_value is None:
                    results["failed"] += 1
                    continue

                value_dict = decode_avro_value(raw_value, schema_str)

                if ts_field and ts_offset_ms and ts_field in value_dict:
                    value_dict[ts_field] += ts_offset_ms

                if self.dry_run:
                    self.logger.debug(f"[DRY RUN] {topic}: {value_dict}")
                    results["success"] += 1
                    continue

                ctx = SerializationContext(topic, MessageField.VALUE)
                serialized = serializer(value_dict, ctx)
                self.producer.produce(topic, value=serialized, partition=0)
                results["success"] += 1

                if idx % 100 == 0:
                    self.producer.poll(0)
                if idx % 500 == 0:
                    self.producer.flush()
                    self.logger.info(f"  {idx}/{results['total']} published")

            except Exception as e:
                self.logger.error(f"Error on line {idx} of {topic}: {e}")
                results["failed"] += 1

        if not self.dry_run and self.producer:
            self.producer.flush()

        return results

    def close(self):
        if self.producer:
            self.producer.flush()


def main():
    parser = argparse.ArgumentParser(
        description="Publish pre-captured Lab 1 data to Confluent Cloud",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Directory containing customers.jsonl, products.jsonl, orders.jsonl "
             "(default: assets/lab1/data/)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logger = setup_logging(args.verbose)

    if not CONFLUENT_KAFKA_AVAILABLE:
        logger.error("confluent-kafka not available. Run: uv pip install confluent-kafka[avro,schema-registry]")
        return 1
    if not AVRO_AVAILABLE:
        logger.error("avro-python3 not available. Run: uv pip install avro-python3")
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
        f = data_dir / f"{topic}.jsonl"
        if not f.exists():
            logger.error(f"Data file not found: {f} — run 'uv run capture_lab1_data' first")
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

        # Compute order_ts offset before publishing anything
        orders_file = data_dir / "orders.jsonl"
        orders_lines = [l.strip() for l in orders_file.read_text().splitlines() if l.strip()]
        ts_offset_ms = compute_orders_ts_offset(orders_lines)
        offset_minutes = ts_offset_ms / 60000
        logger.info(f"Rebasing order_ts by {offset_minutes:+.1f} minutes")

        all_results = {}

        # Publish lookup tables first, then orders
        for topic in ("customers", "products", "orders"):
            offset = ts_offset_ms if topic == "orders" else 0
            results = publisher.publish_topic(topic, data_dir / f"{topic}.jsonl", offset)
            all_results[topic] = results

        print(f"\n{'=' * 55}")
        print("LAB 1 DATA PUBLISHING SUMMARY")
        print(f"{'=' * 55}")
        for topic, r in all_results.items():
            print(f"  {topic:<12}  published: {r['success']:>4}  failed: {r['failed']:>3}  total: {r['total']:>4}")
        print(f"{'=' * 55}")
        if args.dry_run:
            print("\n[DRY RUN — no messages actually published]")

        total_failed = sum(r["failed"] for r in all_results.values())
        return 0 if total_failed == 0 else 1

    finally:
        publisher.close()


if __name__ == "__main__":
    sys.exit(main())
