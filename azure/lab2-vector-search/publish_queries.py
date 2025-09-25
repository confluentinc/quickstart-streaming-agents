#!/usr/bin/env python3
"""
Simple script for publishing queries to the 'queries' Kafka topic.

Usage:
1. Set up virtual environment: cd ../../../ && uv venv && uv pip install -r requirements.txt
2. Run from this directory: ../../../.venv/bin/python publish_queries.py "your query here"
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

import warnings
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer

# Suppress the deprecation warning for AvroProducer
warnings.filterwarnings("ignore", message="AvroProducer has been deprecated")

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class QueryPublisher:
    """Simple publisher for queries to Kafka using Avro format."""

    def __init__(
        self, kafka_config: Dict[str, Any], schema_registry_config: Dict[str, Any]
    ):
        """Initialize the publisher with Kafka and Schema Registry configuration."""
        self.kafka_config = kafka_config
        self.schema_registry_config = schema_registry_config

        # Define Avro schema for queries (simple string value)
        self.value_schema = avro.loads(
            json.dumps(
                {
                    "type": "record",
                    "name": "queries_value",
                    "namespace": "org.apache.flink.avro.generated.record",
                    "fields": [
                        {"name": "query", "type": ["null", "string"], "default": None}
                    ],
                }
            )
        )

        self.key_schema = avro.loads('"string"')
        self.producer = None

    def _init_producer(self) -> None:
        """Initialize the Avro producer."""
        try:
            self.producer = AvroProducer(
                self.kafka_config,
                default_key_schema=self.key_schema,
                default_value_schema=self.value_schema,
                schema_registry=avro.CachedSchemaRegistryClient(
                    self.schema_registry_config
                ),
            )
        except Exception as e:
            logger.error(f"Failed to initialize Avro producer: {e}")
            raise

    def publish_query(self, query: str, topic: str) -> bool:
        """Publish a single query to Kafka."""
        try:
            if not self.producer:
                self._init_producer()

            # Create Avro record
            value = {"query": query}

            # Use query hash or timestamp as key
            import hashlib
            import time

            key = hashlib.md5(f"{query}_{time.time()}".encode()).hexdigest()

            # Produce message
            self.producer.produce(topic=topic, value=value, key=key)

            # Flush immediately
            self.producer.flush(timeout=10)

            return True

        except Exception as e:
            logger.error(f"Failed to publish query: {e}")
            return False

    def close(self):
        """Close the producer connection."""
        if self.producer:
            self.producer.flush()


def create_kafka_config(
    bootstrap_servers: str, api_key: str, api_secret: str
) -> Dict[str, Any]:
    """Create Kafka client configuration."""
    return {
        "bootstrap.servers": bootstrap_servers,
        "security.protocol": "SASL_SSL",
        "sasl.mechanisms": "PLAIN",
        "sasl.username": api_key,
        "sasl.password": api_secret,
        "client.id": "queries-publisher",
    }


def create_schema_registry_config(
    schema_registry_url: str, api_key: str, api_secret: str
) -> Dict[str, Any]:
    """Create Schema Registry client configuration."""
    return {
        "url": schema_registry_url,
        "basic.auth.credentials.source": "USER_INFO",
        "basic.auth.user.info": f"{api_key}:{api_secret}",
    }


def get_credentials():
    """Extract credentials from Terraform state files."""
    # Get current directory (should be the terraform/azure/lab2-vector-search directory)
    current_dir = Path(__file__).parent

    # Paths to state files
    local_state = current_dir / "terraform.tfstate"
    core_state = current_dir / "../core/terraform.tfstate"

    def run_terraform_output(state_path: Path) -> dict:
        """Run terraform output and return the results as a dictionary."""
        try:
            cmd = ["terraform", "output", "-json", f"-state={state_path}"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            outputs = json.loads(result.stdout)
            # Extract values from terraform output format
            return {key: value["value"] for key, value in outputs.items()}
        except subprocess.CalledProcessError as e:
            logger.error(f"Terraform output failed: {e.stderr}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse terraform output JSON: {e}")
            raise

    # Get outputs from core state
    if core_state.exists():
        core_outputs = run_terraform_output(core_state)
    else:
        logger.error(f"Core state file not found: {core_state}")
        sys.exit(1)

    # Extract required credentials
    try:
        credentials = {
            # Kafka connection details
            "bootstrap_servers": core_outputs[
                "confluent_kafka_cluster_bootstrap_endpoint"
            ],
            "kafka_api_key": core_outputs["app_manager_kafka_api_key"],
            "kafka_api_secret": core_outputs["app_manager_kafka_api_secret"],
            # Schema Registry details
            "schema_registry_url": core_outputs[
                "confluent_schema_registry_rest_endpoint"
            ],
            "schema_registry_api_key": core_outputs[
                "app_manager_schema_registry_api_key"
            ],
            "schema_registry_api_secret": core_outputs[
                "app_manager_schema_registry_api_secret"
            ],
            # Topic configuration
            "environment_name": core_outputs["confluent_environment_display_name"],
            "cluster_name": core_outputs["confluent_kafka_cluster_display_name"],
        }

        return credentials

    except KeyError as e:
        logger.error(f"Missing required output in Terraform state: {e}")
        logger.error("Available core outputs:")
        for key in sorted(core_outputs.keys()):
            logger.error(f"  - {key}")
        sys.exit(1)


def interactive_mode(publisher, topic):
    """Interactive mode for publishing queries."""
    logger.info("Entering interactive mode. Type 'exit', 'quit', or Ctrl+C to stop.")
    logger.info("Enter queries to publish them to the Kafka topic:")

    try:
        while True:
            try:
                query = input("\n> ").strip()

                if not query:
                    continue

                if query.lower() in ['exit', 'quit']:
                    logger.info("Exiting interactive mode...")
                    break

                logger.info("Publishing...")

                if publisher.publish_query(query, topic):
                    logger.info("Published successfully")
                else:
                    logger.error("Failed to publish query")

            except KeyboardInterrupt:
                logger.info("\nExiting interactive mode...")
                break
            except EOFError:
                logger.info("\nExiting interactive mode...")
                break

    except Exception as e:
        logger.error(f"Error in interactive mode: {e}")


def main():
    """Main function for publishing queries."""
    # Check if query provided as argument
    if len(sys.argv) >= 2:
        query = sys.argv[1]
        single_query_mode = True
    else:
        single_query_mode = False

    try:
        # Extract credentials from Terraform
        credentials = get_credentials()

        # Get configuration from credentials
        kafka_config = create_kafka_config(
            credentials["bootstrap_servers"],
            credentials["kafka_api_key"],
            credentials["kafka_api_secret"],
        )

        schema_registry_config = create_schema_registry_config(
            credentials["schema_registry_url"],
            credentials["schema_registry_api_key"],
            credentials["schema_registry_api_secret"],
        )

        topic = "queries"

    except Exception as e:
        logger.error(f"Failed to get credentials: {e}")
        sys.exit(1)

    # Initialize publisher
    publisher = QueryPublisher(kafka_config, schema_registry_config)

    try:
        if single_query_mode:
            # Single query mode
            logger.info("Publishing...")

            # Publish query
            if publisher.publish_query(query, topic):
                logger.info("Published successfully")
            else:
                logger.error("Failed to publish query")
                sys.exit(1)
        else:
            # Interactive mode
            interactive_mode(publisher, topic)

    except Exception as e:
        logger.error(f"Publishing failed: {e}")
        sys.exit(1)
    finally:
        publisher.close()


if __name__ == "__main__":
    main()