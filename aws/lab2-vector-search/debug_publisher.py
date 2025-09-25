#!/usr/bin/env python3
"""
Debug version of publish_docs.py that shows detailed information about what's being published.
"""

import json
import logging
import subprocess
import sys
from pathlib import Path

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_credentials():
    """Extract credentials from Terraform state files."""
    current_dir = Path(__file__).parent
    core_state = current_dir / "../core/terraform.tfstate"

    def run_terraform_output(state_path: Path) -> dict:
        """Run terraform output and return the results as a dictionary."""
        try:
            cmd = ["terraform", "output", "-json", f"-state={state_path}"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            outputs = json.loads(result.stdout)
            return {key: value["value"] for key, value in outputs.items()}
        except subprocess.CalledProcessError as e:
            logger.error(f"Terraform output failed: {e.stderr}")
            raise

    if core_state.exists():
        core_outputs = run_terraform_output(core_state)
    else:
        logger.error(f"Core state file not found: {core_state}")
        sys.exit(1)

    return {
        "bootstrap_servers": core_outputs["confluent_kafka_cluster_bootstrap_endpoint"],
        "kafka_api_key": core_outputs["app_manager_kafka_api_key"],
        "kafka_api_secret": core_outputs["app_manager_kafka_api_secret"],
        "schema_registry_url": core_outputs["confluent_schema_registry_rest_endpoint"],
        "schema_registry_api_key": core_outputs["app_manager_schema_registry_api_key"],
        "schema_registry_api_secret": core_outputs["app_manager_schema_registry_api_secret"],
        "environment_name": core_outputs["confluent_environment_display_name"],
        "cluster_name": core_outputs["confluent_kafka_cluster_display_name"],
    }


def debug_topic_info(credentials):
    """Debug topic information and Kafka cluster details."""
    logger.info("=== DEBUGGING KAFKA TOPIC INFORMATION ===")
    logger.info(f"Kafka Bootstrap Servers: {credentials['bootstrap_servers']}")
    logger.info(f"Environment: {credentials['environment_name']}")
    logger.info(f"Cluster: {credentials['cluster_name']}")
    logger.info(f"Schema Registry: {credentials['schema_registry_url']}")

    # Try different topic name formats
    topic_formats = [
        "documents",
        f"{credentials['environment_name']}.{credentials['cluster_name']}.documents",
        f"documents",  # Simple name
    ]

    logger.info("Possible topic name formats:")
    for i, topic in enumerate(topic_formats, 1):
        logger.info(f"  {i}. {topic}")


def debug_chunks_directory():
    """Debug markdown chunks directory."""
    chunks_dir = Path(__file__).parent.parent.parent / "assets/lab2/flink_docs/markdown_chunks"
    logger.info("=== DEBUGGING CHUNKS DIRECTORY ===")
    logger.info(f"Chunks directory: {chunks_dir}")
    logger.info(f"Directory exists: {chunks_dir.exists()}")

    if chunks_dir.exists():
        md_files = list(chunks_dir.glob("*.md"))
        logger.info(f"Number of markdown files: {len(md_files)}")

        if md_files:
            # Show first few files
            logger.info("First 5 chunk files:")
            for i, file in enumerate(md_files[:5], 1):
                logger.info(f"  {i}. {file.name}")

            # Show a sample chunk content
            sample_file = md_files[0]
            logger.info(f"\nSample content from {sample_file.name}:")
            try:
                with open(sample_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    logger.info(f"File size: {len(content)} characters")
                    logger.info(f"First 200 characters: {content[:200]}...")
            except Exception as e:
                logger.error(f"Error reading sample file: {e}")


def test_simple_kafka_publish(credentials):
    """Test a simple Kafka message publish to verify connectivity."""
    try:
        from confluent_kafka import Producer

        logger.info("=== TESTING SIMPLE KAFKA PUBLISH ===")

        # Simple producer config
        config = {
            'bootstrap.servers': credentials['bootstrap_servers'],
            'security.protocol': 'SASL_SSL',
            'sasl.mechanisms': 'PLAIN',
            'sasl.username': credentials['kafka_api_key'],
            'sasl.password': credentials['kafka_api_secret'],
        }

        producer = Producer(config)

        # Test message
        test_message = {
            'document_id': 'debug-test-001',
            'document_text': 'This is a debug test message to verify Kafka connectivity.'
        }

        topic = 'documents'

        def delivery_report(err, msg):
            if err is not None:
                logger.error(f'Message delivery failed: {err}')
            else:
                logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')

        # Produce test message
        logger.info(f"Sending test message to topic: {topic}")
        producer.produce(
            topic,
            key='debug-test',
            value=json.dumps(test_message),
            callback=delivery_report
        )

        producer.flush(timeout=10)
        logger.info("Simple Kafka test completed")
        return True

    except Exception as e:
        logger.error(f"Simple Kafka test failed: {e}")
        return False


def main():
    """Main debug function."""
    logger.info("=== STARTING KAFKA PUBLISHING DEBUG ===")

    try:
        # Get credentials
        credentials = get_credentials()
        logger.info("✓ Successfully extracted credentials")

        # Debug topic info
        debug_topic_info(credentials)

        # Debug chunks directory
        debug_chunks_directory()

        # Test simple Kafka publish
        if test_simple_kafka_publish(credentials):
            logger.info("✓ Basic Kafka connectivity works")
        else:
            logger.error("✗ Basic Kafka connectivity failed")

    except Exception as e:
        logger.error(f"Debug failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()