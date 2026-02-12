"""Kafka topic validation utilities for tests."""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from confluent_kafka import Consumer, KafkaError, KafkaException
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from testing.helpers.terraform_helper import TerraformHelper


class KafkaHelper:
    """Helper for reading Kafka topics to validate test data."""

    def __init__(self, cloud_provider: str, project_root: Path = None):
        """Initialize Kafka helper.

        Args:
            cloud_provider: 'aws' or 'azure'
            project_root: Project root directory (auto-detected if None)
        """
        self.cloud_provider = cloud_provider
        self.project_root = project_root or PROJECT_ROOT

        # Get Kafka credentials from terraform
        tf_helper = TerraformHelper(cloud_provider, self.project_root)
        self.kafka_creds = tf_helper.get_kafka_credentials()

        # Build consumer config
        self.consumer_config = {
            'bootstrap.servers': self.kafka_creds['bootstrap_servers'],
            'security.protocol': 'SASL_SSL',
            'sasl.mechanisms': 'PLAIN',
            'sasl.username': self.kafka_creds['kafka_api_key'],
            'sasl.password': self.kafka_creds['kafka_api_secret'],
            'group.id': 'test-consumer-group',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,
        }

    def get_topic_message_count(
        self, topic: str, timeout: int = 30, max_messages: int = 100000
    ) -> int:
        """Get approximate message count in a topic.

        Args:
            topic: Topic name
            timeout: Max time to consume in seconds (default: 30)
            max_messages: Max messages to consume (default: 100000)

        Returns:
            Number of messages consumed

        Note:
            This consumes from earliest offset and counts messages.
            For large topics, it may not read all messages within timeout.
        """
        consumer = Consumer(self.consumer_config)

        try:
            consumer.subscribe([topic])
            count = 0

            import time
            start_time = time.time()

            while True:
                # Check timeout
                if time.time() - start_time > timeout:
                    break

                # Check max messages
                if count >= max_messages:
                    break

                msg = consumer.poll(timeout=1.0)

                if msg is None:
                    # No more messages within poll timeout
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # Reached end of partition
                        continue
                    else:
                        raise KafkaException(msg.error())

                count += 1

            return count

        finally:
            consumer.close()

    def consume_messages(
        self, topic: str, max_messages: int = 10, timeout: int = 30
    ) -> List[Dict[str, Any]]:
        """Consume and return messages from a topic.

        Args:
            topic: Topic name
            max_messages: Maximum number of messages to return (default: 10)
            timeout: Max time to consume in seconds (default: 30)

        Returns:
            List of decoded message values (assuming JSON)
        """
        consumer = Consumer(self.consumer_config)
        messages = []

        try:
            consumer.subscribe([topic])

            import time
            start_time = time.time()

            while len(messages) < max_messages:
                if time.time() - start_time > timeout:
                    break

                msg = consumer.poll(timeout=1.0)

                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        raise KafkaException(msg.error())

                # Try to decode as JSON
                try:
                    value = json.loads(msg.value().decode('utf-8'))
                    messages.append(value)
                except Exception:
                    # If not JSON, store as raw string
                    messages.append({'raw': msg.value().decode('utf-8')})

            return messages

        finally:
            consumer.close()

    def check_topic_has_messages(
        self, topic: str, min_count: int = 1, timeout: int = 30
    ) -> bool:
        """Check if topic has at least min_count messages.

        Args:
            topic: Topic name
            min_count: Minimum number of messages expected (default: 1)
            timeout: Max time to check in seconds (default: 30)

        Returns:
            True if topic has >= min_count messages, False otherwise
        """
        try:
            count = self.get_topic_message_count(
                topic, timeout=timeout, max_messages=min_count
            )
            return count >= min_count
        except Exception:
            return False
