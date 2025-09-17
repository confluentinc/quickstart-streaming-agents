#!/usr/bin/env python3
"""
AWS Lab2 Document Publisher
Publishes Flink documentation files to Confluent Kafka topic in AVRO format
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from confluent_kafka import Producer
from confluent_kafka.avro import AvroProducer
from confluent_kafka.avro.serializer import SerializerError

def get_terraform_output(key):
    """Get terraform output value"""
    try:
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            check=True
        )
        outputs = json.loads(result.stdout)
        return outputs[key]["value"]
    except (subprocess.CalledProcessError, KeyError, json.JSONDecodeError) as e:
        print(f"Error getting terraform output {key}: {e}")
        sys.exit(1)

def get_core_terraform_output(key):
    """Get core terraform output value"""
    try:
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=Path(__file__).parent / "../../core",
            capture_output=True,
            text=True,
            check=True
        )
        outputs = json.loads(result.stdout)
        return outputs[key]["value"]
    except (subprocess.CalledProcessError, KeyError, json.JSONDecodeError) as e:
        print(f"Error getting core terraform output {key}: {e}")
        sys.exit(1)

def main():
    print("Starting AWS Lab2 Document Publisher...")

    # Get Confluent Cloud credentials and endpoints from terraform
    try:
        kafka_bootstrap_endpoint = get_core_terraform_output("confluent_kafka_cluster_bootstrap_endpoint")
        schema_registry_endpoint = get_core_terraform_output("confluent_schema_registry_rest_endpoint")
        environment_name = get_core_terraform_output("confluent_environment_display_name")
        cluster_name = get_core_terraform_output("confluent_kafka_cluster_display_name")

        kafka_api_key = get_core_terraform_output("app_manager_kafka_api_key")
        kafka_api_secret = get_core_terraform_output("app_manager_kafka_api_secret")
        sr_api_key = get_core_terraform_output("app_manager_schema_registry_api_key")
        sr_api_secret = get_core_terraform_output("app_manager_schema_registry_api_secret")

        print(f"Environment: {environment_name}")
        print(f"Cluster: {cluster_name}")
        print(f"Bootstrap endpoint: {kafka_bootstrap_endpoint}")

    except Exception as e:
        print(f"Error getting terraform outputs: {e}")
        sys.exit(1)

    # Topic name (without environment/cluster prefix since we'll use the full topic name)
    topic_name = f"{environment_name}.{cluster_name}.documents"

    # AVRO schema for documents
    value_schema = {
        "type": "record",
        "name": "Document",
        "fields": [
            {"name": "document_id", "type": "string"},
            {"name": "document_text", "type": "string"}
        ]
    }

    # Producer configuration
    producer_config = {
        'bootstrap.servers': kafka_bootstrap_endpoint,
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': kafka_api_key,
        'sasl.password': kafka_api_secret,
        'schema.registry.url': schema_registry_endpoint,
        'schema.registry.basic.auth.user.info': f"{sr_api_key}:{sr_api_secret}",
    }

    # Create AVRO producer
    try:
        producer = AvroProducer(
            producer_config,
            default_value_schema=json.dumps(value_schema)
        )
        print(f"Created AVRO producer for topic: {topic_name}")
    except Exception as e:
        print(f"Error creating AVRO producer: {e}")
        sys.exit(1)

    # Path to flink_docs directory
    docs_path = Path(__file__).parent / "../../../assets/lab2/flink_docs"

    if not docs_path.exists():
        print(f"Error: Documentation directory not found: {docs_path}")
        sys.exit(1)

    # Process all markdown files
    md_files = list(docs_path.glob("*.md"))
    print(f"Found {len(md_files)} markdown files to process")

    successful_messages = 0
    failed_messages = 0

    for md_file in md_files:
        try:
            # Read file content
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Create message
            document_id = md_file.name  # Just the filename like "flink_changelog.md"

            message_value = {
                "document_id": document_id,
                "document_text": content
            }

            # Produce message
            producer.produce(
                topic=topic_name,
                key=document_id,
                value=message_value
            )

            print(f"✓ Produced: {document_id} ({len(content)} chars)")
            successful_messages += 1

        except Exception as e:
            print(f"✗ Failed to process {md_file.name}: {e}")
            failed_messages += 1

    # Flush producer
    try:
        producer.flush()
        print(f"\n📊 Summary:")
        print(f"  ✓ Successfully published: {successful_messages} documents")
        print(f"  ✗ Failed: {failed_messages} documents")
        print(f"  📡 Topic: {topic_name}")
    except Exception as e:
        print(f"Error flushing producer: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()