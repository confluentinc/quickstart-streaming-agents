"""Lab 2 E2E test: Vector search / RAG pipeline.

All infrastructure is Terraform-managed. Tests assert that deployed statements
are RUNNING and that data flows through the full pipeline.

Run: uv run pytest testing/e2e/test_lab2.py -v
"""

import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from testing.conftest import (
    ensure_confluent_cli_installed,
    ensure_confluent_login,
    load_test_credentials,
    RESUME_MODE,
    KEEP_STATEMENTS,
)
from testing.helpers.terraform_helper import TerraformHelper
from testing.helpers.flink_sql_helper import FlinkSQLHelper
from testing.helpers.kafka_helper import KafkaHelper
from testing.helpers.polling_helper import poll_until


# Terraform-deployed statement names (from terraform/lab2-vector-search/main.tf)
_TERRAFORM_STATEMENTS = [
    "mongodb-connection-create",
    "create-table-queries",
    "create-table-queries-embed",
    "queries-insert-sample",
    "documents-vectordb-create-table",
    "queries-embed-insert-into",
    "search-results-create-table",
    "search-results-response-create-table",
]


@pytest.fixture(scope="class", params=["aws"])
def cloud(request):
    return request.param


class TestLab2VectorSearch:
    """Lab 2 E2E: vector search and RAG assertions.

    Requires Lab 2 infrastructure already deployed via `uv run deploy`.
    No datagen step — Terraform inserts a sample query during deploy.
    """

    @pytest.fixture(scope="class")
    def env(self, cloud):
        """Set up Flink + Kafka helpers from Terraform state."""
        ensure_confluent_cli_installed()
        credentials = load_test_credentials(cloud)
        ensure_confluent_login(credentials)

        tf_helper = TerraformHelper(cloud, PROJECT_ROOT)
        flink_params = tf_helper.get_flink_params()
        flink_helper = FlinkSQLHelper(**flink_params)
        kafka_helper = KafkaHelper(cloud, PROJECT_ROOT)

        yield {
            "cloud": cloud,
            "flink": flink_helper,
            "kafka": kafka_helper,
        }
        # Lab 2 has no test-created statements to clean up

    @pytest.mark.order(1)
    def test_sample_query_inserted(self, env):
        """queries topic has >= 1 message (Terraform inserted sample on deploy)."""
        has_messages = env["kafka"].check_topic_has_messages(
            "queries", min_count=1, timeout=30
        )
        assert has_messages, "queries topic has no messages — was Lab 2 deployed?"

    @pytest.mark.order(2)
    def test_embeddings_pipeline_running(self, env):
        """Embedding pipeline is active: continuous INSERT is RUNNING and queries_embed has data."""
        flink, kafka = env["flink"], env["kafka"]
        # queries-embed-insert-into is the continuous INSERT that must stay RUNNING.
        assert flink.check_statement_running("queries-embed-insert-into"), (
            "Statement 'queries-embed-insert-into' is not RUNNING — check Confluent Cloud UI"
        )
        # queries_embed topic having messages proves the DDL ran and embeddings are flowing.
        # (The DDL statement 'create-table-queries-embed' completes and is GC'd by Confluent
        # Cloud; checking its status is fragile. Checking the topic is the durable assertion.)
        has_messages = kafka.check_topic_has_messages(
            "queries_embed", min_count=1, timeout=30
        )
        assert has_messages, (
            "queries_embed topic has no messages — embedding pipeline may not be running"
        )

    @pytest.mark.order(3)
    def test_search_results(self, env):
        """search_results topic has >= 1 message within 10 minutes."""
        kafka = env["kafka"]
        count = poll_until(
            getter=lambda: kafka.get_topic_message_count("search_results", timeout=10),
            condition=lambda c: c >= 1,
            timeout=600,
            interval=30,
            description="search_results has >= 1 message",
        )
        assert count >= 1

    @pytest.mark.order(4)
    def test_rag_response(self, env):
        """search_results_response has >= 1 message with non-empty response field."""
        kafka = env["kafka"]

        def _get_messages():
            return kafka.consume_messages(
                "search_results_response", max_messages=5, timeout=15
            )

        messages = poll_until(
            getter=_get_messages,
            condition=lambda msgs: len(msgs) >= 1,
            timeout=600,
            interval=30,
            description="search_results_response has >= 1 message",
        )

        assert messages, "No messages in search_results_response"
        first = messages[0]
        response = first.get("response") or first.get("RESPONSE") or ""
        assert response and response.strip(), (
            f"response field is empty in search_results_response message: {first}"
        )
