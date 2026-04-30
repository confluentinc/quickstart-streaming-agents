#!/usr/bin/env python3
"""
Lab 1 data generation tool for quickstart-streaming-agents.

Generates streaming ecommerce data (customers, products, orders) and publishes
to Confluent Cloud Kafka topics using Avro serialization.

Usage:
    uv run lab1_datagen                      # Auto-detect cloud provider
    uv run lab1_datagen aws                  # Generate data for AWS environment
    uv run lab1_datagen azure                # Generate data for Azure environment
    uv run lab1_datagen --dry-run            # Validate setup without running
    uv run lab1_datagen --duration 300       # Run for 5 minutes
    uv run lab1_datagen -m 10                # Generate 10 orders per minute
    uv run lab1_datagen -m 30 --duration 120 # Generate 30 orders/min for 2 minutes

Traditional Python:
    python scripts/lab1_datagen.py
"""

import argparse
import json
import logging
import random
import sys
import time
from typing import Dict, List, Optional

from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer
from faker import Faker

from .common.cloud_detection import auto_detect_cloud_provider, validate_cloud_provider, suggest_cloud_provider
from .common.terraform import extract_kafka_credentials, validate_terraform_state, get_project_root
from .common.logging_utils import setup_logging


# ---------------------------------------------------------------------------
# Avro schemas — must match the ShadowTraffic avroSchemaHint definitions so
# Flink's schema registry expectations are met exactly.
# ---------------------------------------------------------------------------

CUSTOMERS_SCHEMA = json.dumps({
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

PRODUCTS_SCHEMA = json.dumps({
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

ORDERS_SCHEMA = json.dumps({
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

# ---------------------------------------------------------------------------
# Fixed product catalog (verbatim from generators/products.json)
# ---------------------------------------------------------------------------

PRODUCTS = [
    {"product_id": "3001", "product_name": "Apple AirPods Pro 2, Wireless Earbuds, Active Noise Cancellation, Hearing Aid Feature", "price": 245.00, "department": "electronics & technology"},
    {"product_id": "3002", "product_name": "Apple AirTag - 1 Pack, Item Tracker with Apple Find My", "price": 30.00, "department": "electronics & technology"},
    {"product_id": "3003", "product_name": "Bose QuietComfort Headphones, Bluetooth Over Ear Noise Cancelling Headphones, Black", "price": 365.00, "department": "electronics & technology"},
    {"product_id": "3004", "product_name": "Official Hasbro Games Jenga Game with Digital Die, Wood Block Party Game, Family Games, 6+", "price": 28.00, "department": "toys & games"},
    {"product_id": "3005", "product_name": "Coca-Cola Classic Soda Pop, 12 fl oz Cans, 24 Pack", "price": 15.00, "department": "food & beverages"},
    {"product_id": "3006", "product_name": "Dawn EZ-Squeeze Ultra Dish Soap Dishwashing Liquid, Original Scent, 22.0 fl oz", "price": 5.00, "department": "household cleaning & home goods"},
    {"product_id": "3007", "product_name": "JBL Flip 7 - Portable waterproof and drop-proof speaker, Bold JBL Pro Sound with AI Sound Boost, 16Hrs of Playtime, and PushLock system with interchangeable accessories (Black)", "price": 165.00, "department": "electronics & technology"},
    {"product_id": "3008", "product_name": "Monopoly Board Game, Classic Game with Storage Tray and Larger Tokens, Family Games, 8+", "price": 20.00, "department": "toys & games"},
    {"product_id": "3009", "product_name": "Panasonic Eneloop BK-4MCCA4BA Pre-Charged Nickel Metal Hydride AAA Rechargeable Batteries, 4-Battery Pack", "price": 17.00, "department": "electronics & technology"},
    {"product_id": "3010", "product_name": "Scrabble Classic Crossword Board Game for Kids and Family Ages 8 and Up, 2-4 Players", "price": 30.00, "department": "toys & games"},
    {"product_id": "3011", "product_name": "UNO Card Game for Kids, Adults & Family Game Night, Original UNO Game of Matching Colors & Numbers", "price": 10.00, "department": "toys & games"},
    {"product_id": "3012", "product_name": 'Wilson Evolution Official Game Basketball - 29.5"', "price": 100.00, "department": "sports & recreation"},
    {"product_id": "3013", "product_name": "Magic 8 Ball Kids Toy, Novelty Fortune Teller Gag Gift, Ask a Question & Turn Over for Answer", "price": 15.00, "department": "toys & games"},
    {"product_id": "3014", "product_name": "Pyrex 1-cup Measuring Cup", "price": 15.00, "department": "household cleaning & home goods"},
    {"product_id": "3015", "product_name": "Penn Championship Extra Duty Tennis Balls (1 Can, 3 balls)", "price": 8.99, "department": "sports & recreation"},
    {"product_id": "3016", "product_name": "The Grand Budapest Hotel (Blu-ray), 20th Century Fox, Comedy", "price": 16.00, "department": "movies & entertainment"},
    {"product_id": "3017", "product_name": "The Wild Robot (Blu-ray + Digital Copy), Family, DreamWorks", "price": 23.99, "department": "movies & entertainment"},
]

# Weighted state pool mirrors ShadowTraffic weightedOneOf: random(3) + CA(3) + NY(2) + TX(2) + FL(1)
_US_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "Colorado", "Connecticut",
    "Delaware", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts",
    "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska",
    "Nevada", "New Hampshire", "New Jersey", "New Mexico", "North Carolina",
    "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
    "South Carolina", "South Dakota", "Tennessee", "Utah", "Vermont", "Virginia",
    "Washington", "West Virginia", "Wisconsin", "Wyoming",
]
_STATE_WEIGHTS = (
    [(s, 3 / len(_US_STATES)) for s in _US_STATES]
    + [("California", 3), ("New York", 2), ("Texas", 2), ("Florida", 1)]
)
_STATE_POOL = [s for s, w in _STATE_WEIGHTS for _ in range(int(w * 10))] + ["California"] * 30 + ["New York"] * 20 + ["Texas"] * 20 + ["Florida"] * 10


def _random_state() -> str:
    """Return a state matching ShadowTraffic's weightedOneOf distribution."""
    # Build a weighted pool: 30 random-state slots vs 30 CA / 20 NY / 20 TX / 10 FL
    slot = random.randint(0, 109)
    if slot < 30:
        return random.choice(_US_STATES)
    elif slot < 60:
        return "California"
    elif slot < 80:
        return "New York"
    elif slot < 100:
        return "Texas"
    else:
        return "Florida"


def _now_ms() -> int:
    return int(time.time() * 1000)


def _make_order_id() -> str:
    """Replicate ShadowTraffic formula: O-{floor(now/10000) % 1000000}"""
    suffix = (_now_ms() // 10000) % 1_000_000
    return f"O-{suffix}"


# ---------------------------------------------------------------------------
# Publisher
# ---------------------------------------------------------------------------

class Lab1DataPublisher:
    """Publishes Lab 1 ecommerce data to Confluent Cloud Kafka topics."""

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
        self.fake = Faker()

        sr_conf = {
            "url": schema_registry_url,
            "basic.auth.user.info": f"{schema_registry_api_key}:{schema_registry_api_secret}",
        }
        kafka_conf_base = {
            "bootstrap.servers": bootstrap_servers,
            "sasl.mechanisms": "PLAIN",
            "security.protocol": "SASL_SSL",
            "sasl.username": kafka_api_key,
            "sasl.password": kafka_api_secret,
            "linger.ms": 10,
            "batch.size": 16384,
        }

        self._string_serializer = StringSerializer("utf_8")

        if not dry_run:
            sr_client = SchemaRegistryClient(sr_conf)

            self._customers_producer = SerializingProducer({
                **kafka_conf_base,
                "key.serializer": self._string_serializer,
                "value.serializer": AvroSerializer(sr_client, CUSTOMERS_SCHEMA),
            })
            self._products_producer = SerializingProducer({
                **kafka_conf_base,
                "key.serializer": self._string_serializer,
                "value.serializer": AvroSerializer(sr_client, PRODUCTS_SCHEMA),
            })
            self._orders_producer = SerializingProducer({
                **kafka_conf_base,
                "key.serializer": self._string_serializer,
                "value.serializer": AvroSerializer(sr_client, ORDERS_SCHEMA),
            })

    def _delivery_callback(self, err, msg):
        if err:
            self.logger.error(f"Delivery failed: {err}")
        else:
            self.logger.debug(f"Delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}")

    def publish_customers(self, count: int = 10) -> List[Dict]:
        """Stage 1: generate and publish customer records."""
        self.logger.info(f"Publishing {count} customers...")
        customers = []
        for i in range(count):
            record = {
                "customer_id": f"C-{100000 + i}",
                "customer_email": self.fake.email(),
                "customer_name": self.fake.name(),
                "state": _random_state(),
                "updated_at": _now_ms(),
            }
            customers.append(record)
            if self.dry_run:
                self.logger.info(f"  [DRY RUN] customer: {record['customer_id']} / {record['customer_name']} / {record['state']}")
            else:
                self._customers_producer.produce(
                    topic="customers",
                    key=record["customer_id"],
                    value=record,
                    on_delivery=self._delivery_callback,
                )
        if not self.dry_run:
            self._customers_producer.flush()
        self.logger.info(f"✓ Published {count} customers")
        return customers

    def publish_products(self) -> List[Dict]:
        """Stage 2: publish fixed product catalog."""
        self.logger.info(f"Publishing {len(PRODUCTS)} products...")
        products = []
        for p in PRODUCTS:
            record = {**p, "updated_at": _now_ms()}
            products.append(record)
            if self.dry_run:
                self.logger.info(f"  [DRY RUN] product: {record['product_id']} / {record['product_name']} / ${record['price']}")
            else:
                self._products_producer.produce(
                    topic="products",
                    key=record["product_id"],
                    value=record,
                    on_delivery=self._delivery_callback,
                )
        if not self.dry_run:
            self._products_producer.flush()
        self.logger.info(f"✓ Published {len(PRODUCTS)} products")
        return products

    def publish_orders(
        self,
        customers: List[Dict],
        products: List[Dict],
        max_orders: int = 17,
        throttle_ms: Optional[int] = None,
        duration: Optional[int] = None,
    ) -> int:
        """Stage 3: publish orders, throttled between each one."""
        if throttle_ms is None:
            # Default: uniform distribution 90–95 seconds (matching ShadowTraffic root.json)
            use_random_throttle = True
        else:
            use_random_throttle = False

        self.logger.info(
            f"Publishing up to {max_orders} orders"
            + (f" over {duration}s" if duration else "")
            + (f" at {60000 // throttle_ms}/min" if throttle_ms else " (~1 per 90–95s)")
        )

        start_time = time.time()
        count = 0

        for i in range(max_orders):
            if duration and (time.time() - start_time) >= duration:
                self.logger.info(f"Duration limit reached after {count} orders")
                break

            customer = random.choice(customers)
            product = random.choice(products)

            record = {
                "order_id": _make_order_id(),
                "customer_id": customer["customer_id"],
                "product_id": product["product_id"],
                "price": product["price"],
                "order_ts": _now_ms(),
            }

            if self.dry_run:
                self.logger.info(
                    f"  [DRY RUN] order {i + 1}: {record['order_id']} "
                    f"customer={record['customer_id']} product={record['product_id']} price=${record['price']}"
                )
            else:
                self._orders_producer.produce(
                    topic="orders",
                    key=record["order_id"],
                    value=record,
                    on_delivery=self._delivery_callback,
                )
                self._orders_producer.flush()
                self.logger.info(
                    f"✓ Order {i + 1}/{max_orders}: {record['order_id']} "
                    f"({record['customer_id']} → {record['product_id']} @ ${record['price']})"
                )

            count += 1

            if i < max_orders - 1:
                if use_random_throttle:
                    sleep_s = random.uniform(90, 95)
                else:
                    sleep_s = throttle_ms / 1000.0

                if not self.dry_run:
                    self.logger.info(f"  Waiting {sleep_s:.1f}s before next order...")
                    remaining = duration - (time.time() - start_time) if duration else None
                    if remaining is not None and remaining < sleep_s:
                        self.logger.info(f"  Duration will expire during wait — stopping early")
                        break
                    time.sleep(sleep_s)

        self.logger.info(f"✓ Published {count} orders")
        return count

    def close(self):
        if not self.dry_run:
            for producer in [self._customers_producer, self._products_producer, self._orders_producer]:
                producer.flush()


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def run_datagen(
    cloud_provider: str,
    duration: Optional[int] = None,
    messages_per_minute: Optional[int] = None,
    dry_run: bool = False,
    verbose: bool = False,
) -> int:
    logger = logging.getLogger(__name__)

    try:
        project_root = get_project_root()

        if cloud_provider in ["aws", "azure"]:
            if not validate_terraform_state(cloud_provider, project_root):
                logger.error(f"Terraform state validation failed for {cloud_provider}")
                logger.error("Please run 'terraform apply' in terraform/core/ and terraform/lab1-tool-calling/")
                return 1

        logger.info(f"Extracting {cloud_provider.upper()} credentials...")
        credentials = extract_kafka_credentials(cloud_provider, project_root)

        throttle_ms = None
        if messages_per_minute:
            throttle_ms = int(60_000 / messages_per_minute)
            logger.info(f"Order rate: {messages_per_minute}/min (throttle: {throttle_ms}ms)")

        publisher = Lab1DataPublisher(
            bootstrap_servers=credentials["bootstrap_servers"],
            kafka_api_key=credentials["kafka_api_key"],
            kafka_api_secret=credentials["kafka_api_secret"],
            schema_registry_url=credentials["schema_registry_url"],
            schema_registry_api_key=credentials["schema_registry_api_key"],
            schema_registry_api_secret=credentials["schema_registry_api_secret"],
            dry_run=dry_run,
        )

        try:
            customers = publisher.publish_customers(count=10)
            products = publisher.publish_products()
            publisher.publish_orders(
                customers=customers,
                products=products,
                max_orders=17,
                throttle_ms=throttle_ms,
                duration=duration,
            )
        finally:
            publisher.close()

        logger.info("Data generation complete")
        return 0

    except Exception as e:
        logger.error(f"Data generation failed: {e}")
        if verbose:
            import traceback
            logger.error(traceback.format_exc())
        return 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lab1_datagen",
        description="Generate Lab 1 ecommerce streaming data (customers, products, orders)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run lab1_datagen                      # Auto-detect cloud provider
  uv run lab1_datagen aws                  # Generate data for AWS environment
  uv run lab1_datagen azure                # Generate data for Azure environment
  uv run lab1_datagen --duration 300       # Run for 5 minutes
  uv run lab1_datagen -m 10                # Generate 10 orders per minute
  uv run lab1_datagen -m 30 --duration 120 # Generate 30 orders/min for 2 minutes
  uv run lab1_datagen --dry-run            # Validate setup only
        """.strip(),
    )

    parser.add_argument(
        "cloud_provider",
        nargs="?",
        choices=["aws", "azure", "terraform"],
        help="Target cloud provider (auto-detected if not specified)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        help="Maximum time to run order generation in seconds",
    )
    parser.add_argument(
        "--messages-per-minute", "-m",
        type=int,
        help="Orders per minute (default: ~0.65/min, one per 90–95 seconds)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate setup and show what would be published without connecting to Kafka",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed debug output",
    )
    return parser


def main() -> None:
    parser = create_argument_parser()
    args = parser.parse_args()

    logger = setup_logging(args.verbose)
    logger.info("Quickstart Streaming Agents — Lab 1 Data Generation")

    try:
        project_root = get_project_root()

        cloud_provider = args.cloud_provider
        if not cloud_provider:
            cloud_provider = auto_detect_cloud_provider()
            if not cloud_provider:
                logger.error("Could not auto-detect cloud provider")
                suggest_cloud_provider(project_root)
                sys.exit(1)
        else:
            if not validate_cloud_provider(cloud_provider):
                logger.error(f"Unsupported cloud provider: {cloud_provider}")
                sys.exit(1)

        logger.info(f"Target cloud provider: {cloud_provider.upper()}")

        exit_code = run_datagen(
            cloud_provider=cloud_provider,
            duration=args.duration,
            messages_per_minute=args.messages_per_minute,
            dry_run=args.dry_run,
            verbose=args.verbose,
        )

        sys.exit(exit_code)

    except KeyboardInterrupt:
        logger.info("Data generation interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Data generation failed: {e}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
