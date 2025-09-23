#!/usr/bin/env python3
# Note: Run with uv virtual environment: ../../.venv/bin/python publish_docs.py
"""
Main script to publish Flink documentation files to Kafka in Avro format.

This script reads Markdown files with YAML frontmatter and publishes them
to a Kafka topic using Confluent's Avro producer.
"""

import os
import sys
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FlinkDocsPublisher:
    """Publisher for Flink documentation to Kafka using Avro format."""

    def __init__(self, kafka_config: Dict[str, Any], schema_registry_config: Dict[str, Any]):
        """
        Initialize the publisher with Kafka and Schema Registry configuration.

        Args:
            kafka_config: Kafka client configuration
            schema_registry_config: Schema Registry configuration
        """
        self.kafka_config = kafka_config
        self.schema_registry_config = schema_registry_config

        # Define Avro schema for documents (compatible with existing schema)
        self.value_schema = avro.loads(json.dumps({
            "type": "record",
            "name": "documents_value",
            "namespace": "org.apache.flink.avro.generated.record",
            "fields": [
                {"name": "document_id", "type": ["null", "string"], "default": None},
                {"name": "document_text", "type": ["null", "string"], "default": None}
            ]
        }))

        # Define Avro schema for keys (simple string)
        self.key_schema = avro.loads('"string"')

        # Initialize producer
        self.producer = None

    def _init_producer(self) -> None:
        """Initialize the Avro producer."""
        try:
            self.producer = AvroProducer(
                self.kafka_config,
                default_key_schema=self.key_schema,
                default_value_schema=self.value_schema,
                schema_registry=avro.CachedSchemaRegistryClient(self.schema_registry_config)
            )
            logger.info("Avro producer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Avro producer: {e}")
            raise

    def parse_markdown_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse a markdown file with YAML frontmatter.

        Args:
            file_path: Path to the markdown file

        Returns:
            Dictionary with parsed content or None if parsing fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split frontmatter and content
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    markdown_content = parts[2].strip()
                else:
                    frontmatter = {}
                    markdown_content = content
            else:
                frontmatter = {}
                markdown_content = content

            # Use source_url from frontmatter as document_id, fallback to filename
            document_id = frontmatter.get('source_url', file_path.name)

            # Combine title and content for document_text
            title = frontmatter.get('title', '')
            if title:
                document_text = f"# {title}\n\n{markdown_content}"
            else:
                document_text = markdown_content

            return {
                'document_id': document_id,
                'document_text': document_text,
                'metadata': frontmatter
            }

        except Exception as e:
            logger.error(f"Failed to parse file {file_path}: {e}")
            return None

    def publish_document(self, document: Dict[str, Any], topic: str) -> bool:
        """
        Publish a single document to Kafka.

        Args:
            document: Document data with document_id and document_text
            topic: Kafka topic name

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.producer:
                self._init_producer()

            # Create Avro record
            value = {
                'document_id': document['document_id'],
                'document_text': document['document_text']
            }

            # Produce message
            self.producer.produce(
                topic=topic,
                value=value,
                key=document['document_id']
            )

            logger.info(f"Published document: {document['document_id']}")
            return True

        except Exception as e:
            logger.error(f"Failed to publish document {document.get('document_id', 'unknown')}: {e}")
            return False

    def publish_directory(self, docs_dir: Path, topic: str) -> Dict[str, int]:
        """
        Publish all markdown files in a directory to Kafka.

        Args:
            docs_dir: Directory containing markdown files
            topic: Kafka topic name

        Returns:
            Dictionary with success/failure counts
        """
        if not self.producer:
            self._init_producer()

        results = {'success': 0, 'failed': 0, 'total': 0}

        # Find all markdown files
        md_files = list(docs_dir.glob('*.md'))
        results['total'] = len(md_files)

        logger.info(f"Found {len(md_files)} markdown files to process")

        for file_path in md_files:
            logger.info(f"Processing: {file_path.name}")

            # Parse document
            document = self.parse_markdown_file(file_path)
            if not document:
                results['failed'] += 1
                continue

            # Publish document
            if self.publish_document(document, topic):
                results['success'] += 1
            else:
                results['failed'] += 1

        # Flush all messages
        try:
            self.producer.flush(timeout=30)
            logger.info("All messages flushed successfully")
        except Exception as e:
            logger.error(f"Failed to flush messages: {e}")

        return results

    def close(self):
        """Close the producer connection."""
        if self.producer:
            self.producer.flush()


def create_kafka_config(bootstrap_servers: str, api_key: str, api_secret: str) -> Dict[str, Any]:
    """Create Kafka client configuration."""
    return {
        'bootstrap.servers': bootstrap_servers,
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': api_key,
        'sasl.password': api_secret,
        'client.id': 'flink-docs-publisher'
    }


def create_schema_registry_config(schema_registry_url: str, api_key: str, api_secret: str) -> Dict[str, Any]:
    """Create Schema Registry client configuration."""
    return {
        'url': schema_registry_url,
        'basic.auth.credentials.source': 'USER_INFO',
        'basic.auth.user.info': f'{api_key}:{api_secret}'
    }


def main():
    """Main function when script is run directly."""
    # This function expects environment variables to be set by wrapper scripts
    required_env_vars = [
        'KAFKA_BOOTSTRAP_SERVERS',
        'KAFKA_API_KEY',
        'KAFKA_API_SECRET',
        'SCHEMA_REGISTRY_URL',
        'SCHEMA_REGISTRY_API_KEY',
        'SCHEMA_REGISTRY_API_SECRET',
        'KAFKA_TOPIC'
    ]

    # Check for required environment variables
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        sys.exit(1)

    # Get configuration from environment
    kafka_config = create_kafka_config(
        os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
        os.getenv('KAFKA_API_KEY'),
        os.getenv('KAFKA_API_SECRET')
    )

    schema_registry_config = create_schema_registry_config(
        os.getenv('SCHEMA_REGISTRY_URL'),
        os.getenv('SCHEMA_REGISTRY_API_KEY'),
        os.getenv('SCHEMA_REGISTRY_API_SECRET')
    )

    topic = os.getenv('KAFKA_TOPIC')

    # Initialize publisher
    publisher = FlinkDocsPublisher(kafka_config, schema_registry_config)

    try:
        # Get docs directory (script should be run from flink_docs directory)
        docs_dir = Path(__file__).parent

        logger.info(f"Publishing documents from {docs_dir} to topic '{topic}'")

        # Publish all documents
        results = publisher.publish_directory(docs_dir, topic)

        logger.info(f"Publishing complete: {results['success']} successful, {results['failed']} failed out of {results['total']} total")

        if results['failed'] > 0:
            sys.exit(1)

    except Exception as e:
        logger.error(f"Publishing failed: {e}")
        sys.exit(1)
    finally:
        publisher.close()


if __name__ == '__main__':
    main()
