#!/usr/bin/env python3
"""
Alternate Lab4 claims data publisher with timestamp rebasing.

Reads the same CSV data as lab4_datagen but rebases timestamps so that:
- Non-narrative claims (steady state) are spread evenly from ~24h ago to now
- Narrative claims (the spike) are concentrated in the last 1 hour

Also publishes Claims Investigation System (CIS) reference data to a
separate topic for use in fraud detection agent queries.

Claims are sorted by rebased timestamp and published in perfect chronological
order, following the pattern established by publish_lab3_data.

Usage:
    uv run lab4_datagen_alternate
    uv run lab4_datagen_alternate --dry-run
    uv run lab4_datagen_alternate --cloud-provider aws
"""

import argparse
import csv
import json
import logging
import random
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    from confluent_kafka import SerializingProducer
    from confluent_kafka.schema_registry import SchemaRegistryClient
    from confluent_kafka.schema_registry.avro import AvroSerializer
    from confluent_kafka.serialization import StringSerializer
    CONFLUENT_KAFKA_AVAILABLE = True
except ImportError:
    CONFLUENT_KAFKA_AVAILABLE = False

from .common.cloud_detection import auto_detect_cloud_provider, validate_cloud_provider, suggest_cloud_provider
from .common.terraform import extract_kafka_credentials, validate_terraform_state, get_project_root
from .common.logging_utils import setup_logging


# Total time window: 24 hours of data
TOTAL_WINDOW_HOURS = 24
# Spike window: last 1 hour
SPIKE_WINDOW_HOURS = 1
# Steady-state rate: ~25-30 claims per hour (we use 27 for ~23 hours = 621 claims)
STEADY_STATE_PER_HOUR = 27
# Extra non-narrative claims mixed into the spike hour alongside the 47 narrative claims
SPIKE_EXTRA_NORMAL = 47


def rebase_timestamps(
    claims: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Rebase claim timestamps so data ends at 'now'.

    - A small number of non-narrative claims (~27/hr) fill the first 23 hours
      (steady state).
    - The last 1 hour contains all 47 narrative claims plus 47 additional
      non-narrative claims (94 total) — the spike.
    - Remaining claims from the CSV are discarded.

    All claims are returned sorted by their new timestamp.
    """
    logger = logging.getLogger(__name__)

    now = datetime.now(timezone.utc)
    window_start = now - timedelta(hours=TOTAL_WINDOW_HOURS)
    spike_start = now - timedelta(hours=SPIKE_WINDOW_HOURS)

    # Separate claims by whether they have a narrative
    narrative_claims = [c for c in claims if c.get("claim_narrative", "").strip()]
    normal_claims = [c for c in claims if not c.get("claim_narrative", "").strip()]

    # Select subsets
    steady_state_hours = TOTAL_WINDOW_HOURS - SPIKE_WINDOW_HOURS
    steady_state_count = STEADY_STATE_PER_HOUR * steady_state_hours
    total_normal_needed = steady_state_count + SPIKE_EXTRA_NORMAL

    if len(normal_claims) < total_normal_needed:
        logger.warning(
            f"Only {len(normal_claims)} non-narrative claims available, "
            f"need {total_normal_needed}"
        )
        total_normal_needed = len(normal_claims)
        steady_state_count = total_normal_needed - SPIKE_EXTRA_NORMAL

    steady_state_claims = normal_claims[:steady_state_count]
    spike_normal_claims = normal_claims[steady_state_count:steady_state_count + SPIKE_EXTRA_NORMAL]

    total_emitted = len(steady_state_claims) + len(spike_normal_claims) + len(narrative_claims)
    logger.info(f"Steady state: {len(steady_state_claims)} claims over {steady_state_hours}h (~{STEADY_STATE_PER_HOUR}/hr)")
    logger.info(f"Spike hour: {len(narrative_claims)} narrative + {len(spike_normal_claims)} normal = {len(narrative_claims) + len(spike_normal_claims)} claims")
    logger.info(f"Total to publish: {total_emitted} (discarding {len(claims) - total_emitted} from CSV)")

    rebased = []

    # Spread steady-state claims over the first 23 hours with jitter.
    # Generate random offsets within the window, then sort them to maintain
    # chronological order while producing natural per-hour count variation.
    if steady_state_claims:
        total_seconds = steady_state_hours * 3600
        offsets = sorted(random.uniform(0, total_seconds) for _ in steady_state_claims)
        for claim, offset in zip(steady_state_claims, offsets):
            new_ts = window_start + timedelta(seconds=offset)
            claim = claim.copy()
            claim["claim_timestamp"] = new_ts.strftime("%Y-%m-%dT%H:%M:%S+00:00")
            rebased.append(claim)

    # Combine narrative + extra normal claims for the spike hour
    spike_claims = narrative_claims + spike_normal_claims
    if spike_claims:
        spike_seconds = SPIKE_WINDOW_HOURS * 3600
        interval = spike_seconds / (len(spike_claims) + 1)
        for i, claim in enumerate(spike_claims):
            new_ts = spike_start + timedelta(seconds=(i + 1) * interval)
            claim = claim.copy()
            claim["claim_timestamp"] = new_ts.strftime("%Y-%m-%dT%H:%M:%S+00:00")
            rebased.append(claim)

    # Sort ALL claims by rebased timestamp for chronological publishing
    rebased.sort(key=lambda c: c["claim_timestamp"])

    logger.info(
        f"Rebased time window: "
        f"{window_start.strftime('%Y-%m-%d %H:%M')} to "
        f"{now.strftime('%Y-%m-%d %H:%M')} UTC"
    )
    logger.info(
        f"Spike window: "
        f"{spike_start.strftime('%Y-%m-%d %H:%M')} to "
        f"{now.strftime('%Y-%m-%d %H:%M')} UTC"
    )

    return rebased


CLAIMS_VALUE_SCHEMA_STR = json.dumps({
    "type": "record",
    "name": "claims_value",
    "namespace": "org.apache.flink.avro.generated.record",
    "fields": [
        {"name": "claim_id", "type": "string"},
        {"name": "applicant_name", "type": ["null", "string"], "default": None},
        {"name": "city", "type": "string"},
        {"name": "is_primary_residence", "type": ["null", "string"], "default": None},
        {"name": "damage_assessed", "type": ["null", "string"], "default": None},
        {"name": "claim_amount", "type": "string"},
        {"name": "has_insurance", "type": ["null", "string"], "default": None},
        {"name": "insurance_amount", "type": ["null", "string"], "default": None},
        {"name": "claim_narrative", "type": ["null", "string"], "default": None},
        {"name": "assessment_date", "type": ["null", "string"], "default": None},
        {"name": "disaster_date", "type": ["null", "string"], "default": None},
        {"name": "previous_claims_count", "type": ["null", "string"], "default": None},
        {"name": "last_claim_date", "type": ["null", "string"], "default": None},
        {"name": "assessment_source", "type": ["null", "string"], "default": None},
        {"name": "shared_account", "type": ["null", "string"], "default": None},
        {"name": "shared_phone", "type": ["null", "string"], "default": None},
        {"name": "claim_timestamp", "type": {"type": "long", "logicalType": "timestamp-millis"}},
    ],
})

# CIS value schema — claim_id is the Kafka message KEY (not in value),
# matching what Flink's PRIMARY KEY (claim_id) NOT ENFORCED produces.
CIS_VALUE_SCHEMA_STR = json.dumps({
    "type": "record",
    "name": "claims_investigation_value",
    "namespace": "org.apache.flink.avro.generated.record",
    "fields": [
        {"name": "policy_owner_name", "type": "string"},
        {"name": "policy_coverage_amount", "type": "string"},
        {"name": "policy_status", "type": "string"},
        {"name": "policy_history", "type": "string"},
        {"name": "clue_history", "type": ["null", "string"], "default": None},
        {"name": "ip_country", "type": "string"},
        {"name": "bank_account_country", "type": "string"},
        {"name": "identity_verified", "type": "string"},
        {"name": "ssn_matches_policyholder", "type": "string"},
        {"name": "identity_theft_history", "type": "string"},
    ],
})


class Lab4AlternatePublisher:
    """Publisher for Lab4 claims with rebased timestamps, plus CIS reference data."""

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

        schema_registry_conf = {
            "url": schema_registry_url,
            "basic.auth.user.info": f"{schema_registry_api_key}:{schema_registry_api_secret}",
        }

        self.string_serializer = StringSerializer("utf_8")
        self.schema_registry_client = None
        self.claims_avro_serializer = None
        self.cis_avro_serializer = None

        if not dry_run:
            self.schema_registry_client = SchemaRegistryClient(schema_registry_conf)

            def claim_to_avro(claim, ctx):
                """Convert claim dict - only convert timestamp to millis."""
                claim_copy = claim.copy()
                if "claim_timestamp" in claim_copy and isinstance(claim_copy["claim_timestamp"], str):
                    dt = datetime.fromisoformat(claim_copy["claim_timestamp"]).replace(tzinfo=timezone.utc)
                    claim_copy["claim_timestamp"] = int(dt.timestamp() * 1000)
                return claim_copy

            self.claims_avro_serializer = AvroSerializer(
                self.schema_registry_client,
                CLAIMS_VALUE_SCHEMA_STR,
                claim_to_avro,
            )

            self.cis_avro_serializer = AvroSerializer(
                self.schema_registry_client,
                CIS_VALUE_SCHEMA_STR,
            )

        self.producer_config = base_producer_config = {
            "bootstrap.servers": bootstrap_servers,
            "sasl.mechanisms": "PLAIN",
            "security.protocol": "SASL_SSL",
            "sasl.username": kafka_api_key,
            "sasl.password": kafka_api_secret,
            "linger.ms": 10,
            "batch.size": 16384,
            "compression.type": "snappy",
        }

        self.claims_producer = None
        self.cis_producer = None
        if not dry_run:
            self.claims_producer = SerializingProducer({
                **base_producer_config,
                "key.serializer": self.string_serializer,
                "value.serializer": self.claims_avro_serializer,
            })
            self.cis_producer = SerializingProducer({
                **base_producer_config,
                "key.serializer": self.string_serializer,
                "value.serializer": self.cis_avro_serializer,
            })

    def purge_topic(self, topic: str) -> None:
        """Delete all existing records from a topic before publishing fresh data."""
        from confluent_kafka.admin import AdminClient, OffsetSpec
        from confluent_kafka import TopicPartition as AdminTopicPartition

        self.logger.info(f"Purging existing records from topic '{topic}'...")
        admin = AdminClient({
            "bootstrap.servers": self.producer_config["bootstrap.servers"],
            "sasl.mechanisms": self.producer_config["sasl.mechanisms"],
            "security.protocol": self.producer_config["security.protocol"],
            "sasl.username": self.producer_config["sasl.username"],
            "sasl.password": self.producer_config["sasl.password"],
        })

        try:
            metadata = admin.list_topics(topic=topic, timeout=10)
            if topic not in metadata.topics:
                self.logger.info(f"Topic '{topic}' not found — skipping purge")
                return
            partition_ids = list(metadata.topics[topic].partitions.keys())
            tps = [AdminTopicPartition(topic, p) for p in partition_ids]

            futures = admin.list_offsets({tp: OffsetSpec.latest() for tp in tps})
            delete_offsets = {}
            for tp, future in futures.items():
                result = future.result()
                if result.offset > 0:
                    delete_offsets[tp] = AdminTopicPartition(tp.topic, tp.partition, result.offset)

            if delete_offsets:
                del_futures = admin.delete_records(delete_offsets)
                for tp, future in del_futures.items():
                    future.result()
                self.logger.info(f"Purged {len(delete_offsets)} partition(s) in '{topic}'")
            else:
                self.logger.info(f"Topic '{topic}' already empty")
        except Exception as e:
            self.logger.warning(f"Could not purge topic '{topic}': {e} — continuing without purge")

    def delivery_callback(self, err, msg):
        if err:
            self.logger.error(f"Message delivery failed: {err}")
        else:
            self.logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    def publish_claim(self, claim: Dict[str, Any], topic: str) -> bool:
        try:
            claim_id = claim["claim_id"]

            if self.dry_run:
                self.logger.debug(f"[DRY RUN] Would publish claim {claim_id} to {topic}")
                return True

            self.claims_producer.produce(
                topic=topic,
                key=claim_id,
                value=claim,
                on_delivery=self.delivery_callback,
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to publish claim {claim.get('claim_id', 'unknown')}: {e}")
            import traceback
            self.logger.error(f"Full traceback:\n{traceback.format_exc()}")
            return False

    def publish_claims(
        self,
        claims: List[Dict[str, Any]],
        topic: str,
    ) -> Dict[str, int]:
        """
        Publish pre-sorted claims in order.

        Claims must already be sorted by timestamp (from rebase_timestamps).
        """
        results = {"success": 0, "failed": 0, "total": len(claims)}
        self.logger.info(f"Publishing {len(claims)} claims in chronological order")

        for idx, claim in enumerate(claims, 1):
            if self.publish_claim(claim, topic):
                results["success"] += 1
            else:
                results["failed"] += 1

            if not self.dry_run and idx % 100 == 0:
                self.claims_producer.poll(0)

            if not self.dry_run and idx % 1000 == 0:
                self.claims_producer.flush()
                self.logger.info(
                    f"Progress: {idx}/{results['total']} claims "
                    f"({results['success']} succeeded, {results['failed']} failed)"
                )

        if not self.dry_run and self.claims_producer:
            self.logger.info("Flushing remaining messages...")
            self.claims_producer.flush()

        return results

    def publish_cis(
        self,
        cis_records: List[Dict[str, Any]],
        topic: str,
    ) -> Dict[str, int]:
        """Publish Claims Investigation System reference data."""
        results = {"success": 0, "failed": 0, "total": len(cis_records)}
        self.logger.info(f"Publishing {len(cis_records)} CIS records to '{topic}'")

        for record in cis_records:
            try:
                if self.dry_run:
                    self.logger.debug(f"[DRY RUN] Would publish CIS record {record['claim_id']}")
                    results["success"] += 1
                    continue

                # claim_id goes in the key only (not in value schema)
                value = {k: v for k, v in record.items() if k != "claim_id"}
                self.cis_producer.produce(
                    topic=topic,
                    key=record["claim_id"],
                    value=value,
                    on_delivery=self.delivery_callback,
                )
                results["success"] += 1
            except Exception as e:
                self.logger.error(f"Failed to publish CIS record {record.get('claim_id', 'unknown')}: {e}")
                results["failed"] += 1

        if not self.dry_run and self.cis_producer:
            self.cis_producer.flush()

        return results

    def close(self):
        if self.claims_producer:
            self.claims_producer.flush()
        if self.cis_producer:
            self.cis_producer.flush()


def main():
    """Main entry point for the Lab4 alternate data publisher CLI."""
    parser = argparse.ArgumentParser(
        description="Publish Lab4 claims with rebased timestamps (steady state + spike) and CIS reference data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                      # Publish claims only (no CIS)
  %(prog)s --cis                                # Publish claims + CIS reference data
  %(prog)s --cloud-provider aws                 # Specify AWS
  %(prog)s --dry-run                            # Test without publishing
        """,
    )

    parser.add_argument(
        "--cloud-provider",
        choices=["aws", "azure"],
        help="Target cloud provider (auto-detected if not specified)",
    )
    parser.add_argument(
        "--data-file",
        type=Path,
        help="Path to CSV data file (default: auto-detect in assets directory)",
    )
    parser.add_argument(
        "--cis-file",
        type=Path,
        help="Path to CIS CSV data file (default: auto-detect in assets directory)",
    )
    parser.add_argument(
        "--topic",
        default="claims",
        help="Kafka topic name for claims (default: claims)",
    )
    parser.add_argument(
        "--cis-topic",
        default="claims_investigation",
        help="Kafka topic name for CIS data (default: claims_investigation)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Test without actually publishing")
    parser.add_argument("--cis", action="store_true", help="Also publish CIS reference data to claims_investigation topic")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    logger = setup_logging(args.verbose)

    if not CONFLUENT_KAFKA_AVAILABLE:
        logger.error("confluent-kafka library not available. Please install it with: uv pip install confluent-kafka")
        return 1

    try:
        project_root = get_project_root()
    except Exception as e:
        logger.error(f"Could not find project root: {e}")
        return 1

    # Find data files
    if args.data_file:
        data_file = args.data_file
    else:
        data_file = project_root / "assets" / "lab4" / "data" / "fema_claims_synthetic.csv"

    if args.cis_file:
        cis_file = args.cis_file
    else:
        cis_file = project_root / "assets" / "lab4" / "data" / "claims_investigation.csv"

    if not data_file.exists():
        logger.error(f"Data file does not exist: {data_file}")
        return 1

    if args.cis and not cis_file.exists():
        logger.error(f"CIS data file does not exist: {cis_file}")
        return 1

    logger.info("Lab4 Alternate Data Publisher (steady state + spike pattern)")
    logger.info(f"Reading claims from {data_file}")
    if args.cis:
        logger.info(f"Reading CIS data from {cis_file}")
    else:
        logger.info("CIS publishing disabled (pass --cis to enable)")

    # Read claims CSV
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            claims = list(reader)
    except Exception as e:
        logger.error(f"Failed to read CSV file {data_file}: {e}")
        return 1

    # Read CIS CSV (only if --cis flag is set)
    cis_records = []
    if args.cis:
        try:
            with open(cis_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                cis_records = list(reader)
            logger.info(f"Loaded {len(cis_records)} CIS records")
        except Exception as e:
            logger.error(f"Failed to read CIS file {cis_file}: {e}")
            return 1

    # Rebase timestamps and sort chronologically
    logger.info("Rebasing timestamps (steady state + 1-hour spike)...")
    sorted_claims = rebase_timestamps(claims)

    # Determine cloud provider
    cloud_provider = args.cloud_provider
    if not cloud_provider:
        cloud_provider = auto_detect_cloud_provider()
        if not cloud_provider:
            suggestion = suggest_cloud_provider(project_root)
            if suggestion:
                logger.info(f"Auto-detected cloud provider: {suggestion}")
                cloud_provider = suggestion
            else:
                logger.error("Could not auto-detect cloud provider. Please check your terraform deployment.")
                return 1

    logger.info(f"Target cloud provider: {cloud_provider.upper()}")

    if not validate_cloud_provider(cloud_provider):
        logger.error(f"Invalid cloud provider: {cloud_provider}")
        return 1

    try:
        if not validate_terraform_state(cloud_provider, project_root):
            logger.error("Terraform validation failed")
            return 1
    except Exception as e:
        logger.error(f"Terraform validation failed: {e}")
        return 1

    try:
        credentials = extract_kafka_credentials(cloud_provider, project_root)
    except Exception as e:
        logger.error(f"Failed to extract Kafka credentials: {e}")
        return 1

    try:
        publisher = Lab4AlternatePublisher(
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
        if args.dry_run:
            logger.info("[DRY RUN MODE - No actual publishing will occur]")

        # Purge old data before publishing
        if not args.dry_run:
            publisher.purge_topic(args.topic)
            if args.cis:
                publisher.purge_topic(args.cis_topic)

        # Publish CIS reference data first (only if --cis)
        cis_results = {"success": 0, "failed": 0, "total": 0}
        if args.cis:
            logger.info(f"Publishing CIS data to topic '{args.cis_topic}'")
            cis_results = publisher.publish_cis(cis_records, args.cis_topic)

        # Publish claims
        logger.info(f"Publishing claims to topic '{args.topic}'")
        claims_results = publisher.publish_claims(sorted_claims, args.topic)

        print(f"\n{'=' * 60}")
        print("LAB4 ALTERNATE DATA PUBLISHING SUMMARY")
        print(f"{'=' * 60}")
        print(f"Claims published: {claims_results['success']}/{claims_results['total']}")
        print(f"Claims failed:    {claims_results['failed']}")
        if args.cis:
            print(f"CIS published:    {cis_results['success']}/{cis_results['total']}")
            print(f"CIS failed:       {cis_results['failed']}")
        else:
            print("CIS:              skipped (use --cis to publish)")
        print(f"{'=' * 60}")

        if args.dry_run:
            print("\n[DRY RUN COMPLETE - No messages were actually published]")
        else:
            env_name = credentials.get("environment_name")
            if env_name:
                print(f"\n✅ Published to environment: {env_name}")
            print(f"✅ {claims_results['success']} claims -> '{args.topic}'")
            if args.cis:
                print(f"✅ {cis_results['success']} CIS records -> '{args.cis_topic}'")
            print("Steady state + spike pattern applied. Ready for Flink anomaly detection!")

        failed = claims_results["failed"] + (cis_results["failed"] if args.cis else 0)
        return 0 if failed == 0 else 1
    finally:
        publisher.close()


if __name__ == "__main__":
    sys.exit(main())
