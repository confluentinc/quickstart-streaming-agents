#!/usr/bin/env python3
"""
Rate-limited document uploader with tracking for testing embeddings pipeline.

This script uploads pre-chunked documents from markdown_chunks directory
at a controlled rate to test the streaming pipeline performance.
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RateLimitedDocumentUploader:
    """Rate-limited uploader for testing document processing pipeline."""

    def __init__(self, kafka_config: Dict[str, Any], schema_registry_config: Dict[str, Any]):
        """Initialize the uploader with Kafka and Schema Registry configuration."""
        self.kafka_config = kafka_config
        self.schema_registry_config = schema_registry_config

        # Progress tracking
        self.processed_files_file = Path(__file__).parent / "processed_files.json"
        self.processed_files = self.load_processed_files()

        # Define Avro schema for documents
        self.value_schema = avro.loads(json.dumps({
            "type": "record",
            "name": "documents_value",
            "namespace": "org.apache.flink.avro.generated.record",
            "fields": [
                {"name": "document_id", "type": ["null", "string"], "default": None},
                {"name": "document_text", "type": ["null", "string"], "default": None}
            ]
        }))

        self.key_schema = avro.loads('"string"')
        self.producer = None

    def load_processed_files(self) -> set:
        """Load the list of already processed files."""
        if self.processed_files_file.exists():
            try:
                with open(self.processed_files_file, 'r') as f:
                    data = json.load(f)
                return set(data.get('processed_files', []))
            except (json.JSONDecodeError, KeyError):
                logger.warning("Could not load processed files, starting fresh")
        return set()

    def save_processed_files(self):
        """Save the list of processed files."""
        data = {
            'processed_files': list(self.processed_files),
            'last_updated': time.time()
        }
        with open(self.processed_files_file, 'w') as f:
            json.dump(data, f, indent=2)

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
        """Parse a markdown file with YAML frontmatter."""
        try:
            import yaml

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
                'metadata': frontmatter,
                'file_path': str(file_path)
            }

        except Exception as e:
            logger.error(f"Failed to parse file {file_path}: {e}")
            return None

    def publish_document(self, document: Dict[str, Any], topic: str) -> bool:
        """Publish a single document to Kafka."""
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

            # Mark as processed
            file_path = document['file_path']
            self.processed_files.add(file_path)

            logger.info(f"Published document: {Path(file_path).name} -> {document['document_id'][:100]}...")
            return True

        except Exception as e:
            logger.error(f"Failed to publish document {document.get('file_path', 'unknown')}: {e}")
            return False

    def get_unprocessed_files(self, docs_dir: Path) -> List[Path]:
        """Get list of files that haven't been processed yet."""
        all_files = list(docs_dir.glob('*.md'))
        unprocessed = [f for f in all_files if str(f) not in self.processed_files]
        return sorted(unprocessed)  # Sort for consistent ordering

    def upload_batch_with_rate_limit(self, docs_dir: Path, topic: str,
                                   docs_per_minute: int, duration_minutes: int) -> Dict[str, int]:
        """Upload documents at a controlled rate."""
        if not self.producer:
            self._init_producer()

        # Calculate timing
        interval_seconds = 60.0 / docs_per_minute
        total_docs_to_process = docs_per_minute * duration_minutes

        # Get unprocessed files
        unprocessed_files = self.get_unprocessed_files(docs_dir)

        logger.info(f"Found {len(unprocessed_files)} unprocessed files")
        logger.info(f"Will process {min(total_docs_to_process, len(unprocessed_files))} documents")
        logger.info(f"Rate: {docs_per_minute} docs/minute ({interval_seconds:.1f}s interval)")
        logger.info(f"Duration: {duration_minutes} minutes")

        results = {'success': 0, 'failed': 0, 'total': 0}
        start_time = time.time()

        for i, file_path in enumerate(unprocessed_files[:total_docs_to_process]):
            # Check if we should stop (time limit)
            elapsed_time = time.time() - start_time
            if elapsed_time >= duration_minutes * 60:
                logger.info(f"Time limit reached ({duration_minutes} minutes)")
                break

            results['total'] += 1

            logger.info(f"Processing file {i+1}/{min(total_docs_to_process, len(unprocessed_files))}: {file_path.name}")

            # Parse document
            document = self.parse_markdown_file(file_path)
            if not document:
                results['failed'] += 1
                continue

            # Publish document
            if self.publish_document(document, topic):
                results['success'] += 1

                # Flush immediately for testing
                self.producer.flush(timeout=5)

                # Save progress
                self.save_processed_files()
            else:
                results['failed'] += 1

            # Rate limiting - wait for next interval
            if i < total_docs_to_process - 1:  # Don't wait after the last document
                time.sleep(interval_seconds)

        # Final flush
        try:
            self.producer.flush(timeout=30)
            logger.info("All messages flushed successfully")
        except Exception as e:
            logger.error(f"Failed to flush messages: {e}")

        return results

    def get_progress_info(self, docs_dir: Path) -> Dict[str, int]:
        """Get current progress information."""
        all_files = list(docs_dir.glob('*.md'))
        processed_count = len([f for f in all_files if str(f) in self.processed_files])
        return {
            'total_files': len(all_files),
            'processed_files': processed_count,
            'remaining_files': len(all_files) - processed_count
        }

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
        'client.id': 'rate-limited-docs-publisher'
    }


def create_schema_registry_config(schema_registry_url: str, api_key: str, api_secret: str) -> Dict[str, Any]:
    """Create Schema Registry client configuration."""
    return {
        'url': schema_registry_url,
        'basic.auth.credentials.source': 'USER_INFO',
        'basic.auth.user.info': f'{api_key}:{api_secret}'
    }


def get_credentials():
    """Extract credentials from Terraform state files."""
    import subprocess

    # Get current directory (should be the terraform/azure/lab2-vector-search directory)
    current_dir = Path(__file__).parent

    # Paths to state files
    local_state = current_dir / "terraform.tfstate"
    core_state = current_dir / "../../core/terraform.tfstate"

    def run_terraform_output(state_path: Path) -> dict:
        """Run terraform output and return the results as a dictionary."""
        try:
            cmd = ['terraform', 'output', '-json', f'-state={state_path}']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            outputs = json.loads(result.stdout)
            # Extract values from terraform output format
            return {key: value['value'] for key, value in outputs.items()}
        except subprocess.CalledProcessError as e:
            logger.error(f"Terraform output failed: {e.stderr}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse terraform output JSON: {e}")
            raise

    # Get outputs from core state
    logger.info("Extracting outputs from core Terraform state...")
    if core_state.exists():
        core_outputs = run_terraform_output(core_state)
        logger.info(f"Core outputs available: {list(core_outputs.keys())}")
    else:
        logger.error(f"Core state file not found: {core_state}")
        sys.exit(1)

    # Extract required credentials
    try:
        credentials = {
            # Kafka connection details
            'bootstrap_servers': core_outputs['confluent_kafka_cluster_bootstrap_endpoint'],
            'kafka_api_key': core_outputs['app_manager_kafka_api_key'],
            'kafka_api_secret': core_outputs['app_manager_kafka_api_secret'],

            # Schema Registry details
            'schema_registry_url': core_outputs['confluent_schema_registry_rest_endpoint'],
            'schema_registry_api_key': core_outputs['app_manager_schema_registry_api_key'],
            'schema_registry_api_secret': core_outputs['app_manager_schema_registry_api_secret'],

            # Topic configuration
            'environment_name': core_outputs['confluent_environment_display_name'],
            'cluster_name': core_outputs['confluent_kafka_cluster_display_name'],
        }

        logger.info("Successfully extracted all required credentials")
        return credentials

    except KeyError as e:
        logger.error(f"Missing required output in Terraform state: {e}")
        logger.error("Available core outputs:")
        for key in sorted(core_outputs.keys()):
            logger.error(f"  - {key}")
        sys.exit(1)


def main():
    """Main function for testing rate-limited uploads."""
    try:
        # Extract credentials from Terraform
        credentials = get_credentials()

        # Get configuration from credentials
        kafka_config = create_kafka_config(
            credentials['bootstrap_servers'],
            credentials['kafka_api_key'],
            credentials['kafka_api_secret']
        )

        schema_registry_config = create_schema_registry_config(
            credentials['schema_registry_url'],
            credentials['schema_registry_api_key'],
            credentials['schema_registry_api_secret']
        )

        topic = 'documents'  # Use documents topic

    except Exception as e:
        logger.error(f"Failed to get credentials: {e}")
        sys.exit(1)

    # Initialize uploader
    uploader = RateLimitedDocumentUploader(kafka_config, schema_registry_config)

    try:
        # Get docs directory
        docs_dir = Path(__file__).parent / "../../../assets/lab2/flink_docs/markdown_chunks"

        if not docs_dir.exists():
            logger.error(f"Docs directory not found: {docs_dir}")
            sys.exit(1)

        # Show current progress
        progress = uploader.get_progress_info(docs_dir)
        logger.info(f"Progress: {progress['processed_files']}/{progress['total_files']} files processed, {progress['remaining_files']} remaining")

        # Parse command line arguments for rate and duration
        if len(sys.argv) >= 3:
            docs_per_minute = int(sys.argv[1])
            duration_minutes = int(sys.argv[2])
        else:
            docs_per_minute = 5  # Default rate
            duration_minutes = 3  # Default duration

        logger.info(f"Starting upload: {docs_per_minute} docs/minute for {duration_minutes} minutes")
        logger.info(f"Publishing to topic '{topic}'")

        # Upload documents
        results = uploader.upload_batch_with_rate_limit(docs_dir, topic, docs_per_minute, duration_minutes)

        logger.info(f"Upload complete: {results['success']} successful, {results['failed']} failed out of {results['total']} total")

        # Show updated progress
        progress = uploader.get_progress_info(docs_dir)
        logger.info(f"Updated progress: {progress['processed_files']}/{progress['total_files']} files processed, {progress['remaining_files']} remaining")

        if results['failed'] > 0:
            sys.exit(1)

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        sys.exit(1)
    finally:
        uploader.close()


if __name__ == '__main__':
    main()