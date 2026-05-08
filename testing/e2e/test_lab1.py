"""Lab 1 E2E test: Price match pipeline with Remote MCP tool calling.

Parses SQL from LAB1-Walkthrough.md and runs the full pipeline end-to-end.
The critical assertion is that price_match_results topic has messages — asserting
only that the agent is RUNNING is insufficient because the Remote MCP server has
silently broken twice before.

Run: uv run pytest testing/e2e/test_lab1.py -v --timeout=3600
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict
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


# Email address for price match notifications in tests
_TEST_EMAIL = os.environ.get("TEST_EMAIL", "test@example.com")

# Statement name prefix to avoid collisions with Terraform-managed resources
_PREFIX = "test-lab1"


def _parse_lab1_sql(walkthrough_path: Path) -> Dict[str, str]:
    """Extract user-run SQL statements from LAB1-Walkthrough.md."""
    text = walkthrough_path.read_text()
    statements = {}

    # CREATE TABLE enriched_orders AS (strip any leading SET clause)
    match = re.search(
        r"```sql\s*(?:SET\s+'[^']+'\s*=\s*'[^']+'\s*;\s*)?(CREATE TABLE enriched_orders AS\s+SELECT.*?)```",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if match:
        statements["enriched_orders"] = match.group(1).strip()

    # CREATE TOOL lab1_remote_mcp
    match = re.search(
        r"```sql\s*(CREATE TOOL lab1_remote_mcp\b.*?)```",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if match:
        statements["create_tool"] = match.group(1).strip()

    # CREATE AGENT price_match_agent
    match = re.search(
        r"```sql\s*(CREATE AGENT price_match_agent\b.*?)```",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if match:
        statements["create_agent"] = match.group(1).strip()

    # CREATE TABLE price_match_results AS
    match = re.search(
        r"```sql\s*(CREATE TABLE price_match_results AS\s+SELECT.*?)```",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if match:
        sql = match.group(1).strip()
        # Substitute the email placeholder with the test email
        sql = sql.replace("<<YOUR-EMAIL-ADDRESS-HERE>>", _TEST_EMAIL)
        statements["price_match_results"] = sql

    return statements


def _ensure_statement(
    flink: FlinkSQLHelper, name: str, sql: str, timeout: int = 300
) -> None:
    """Create statement; skip if already RUNNING or COMPLETED (e.g. DDL/TOOL)."""
    try:
        status = flink.get_statement_status(name)
        if status in ("RUNNING", "COMPLETED"):
            return
        if status in ("FAILED", "STOPPED", "DEGRADED"):
            flink.delete_statement(name)
    except Exception:
        pass  # Statement doesn't exist yet

    try:
        flink.execute_statement(name, sql, wait=False)
        flink.wait_for_status(name, ["RUNNING", "COMPLETED"], timeout=timeout)
    except (subprocess.CalledProcessError, RuntimeError, TimeoutError):
        # CalledProcessError: CLI rejected (table/tool already exists).
        # RuntimeError: statement went to FAILED (e.g. duplicate table name).
        # TimeoutError: statement stuck in transition — may still produce output.
        # In all cases, let the subsequent topic/data assertions determine success.
        pass


@pytest.fixture(scope="class", params=["aws"])
def cloud(request):
    return request.param


class TestLab1PriceMatch:
    """Lab 1 E2E: price match pipeline from enriched_orders to price_match_results.

    Requires Lab 1 infrastructure already deployed via `uv run deploy`.
    """

    @pytest.fixture(scope="class")
    def env(self, cloud):
        """Set up helpers and parse SQL from walkthrough."""
        ensure_confluent_cli_installed()
        credentials = load_test_credentials(cloud)
        ensure_confluent_login(credentials)

        tf_helper = TerraformHelper(cloud, PROJECT_ROOT)
        flink_params = tf_helper.get_flink_params()
        flink_helper = FlinkSQLHelper(**flink_params)
        kafka_helper = KafkaHelper(cloud, PROJECT_ROOT)

        walkthrough = PROJECT_ROOT / "LAB1-Walkthrough.md"
        sql = _parse_lab1_sql(walkthrough)
        assert sql.get("enriched_orders"), "Could not parse enriched_orders SQL from LAB1-Walkthrough.md"
        assert sql.get("create_tool"), "Could not parse CREATE TOOL SQL from LAB1-Walkthrough.md"
        assert sql.get("create_agent"), "Could not parse CREATE AGENT SQL from LAB1-Walkthrough.md"
        assert sql.get("price_match_results"), "Could not parse price_match_results SQL from LAB1-Walkthrough.md"

        yield {
            "cloud": cloud,
            "flink": flink_helper,
            "kafka": kafka_helper,
            "sql": sql,
        }

        if not KEEP_STATEMENTS:
            flink_helper.cleanup_all()

    @pytest.mark.order(1)
    def test_orders_datagen(self, env):
        """orders topic has >= 1 message; run datagen if empty."""
        kafka = env["kafka"]
        has_messages = kafka.check_topic_has_messages("orders", min_count=1, timeout=15)
        if not has_messages:
            # Datagen is a long-running streaming process; launch non-blocking.
            proc = subprocess.Popen(["uv", "run", "lab1_datagen"], cwd=PROJECT_ROOT)
            has_messages = poll_until(
                getter=lambda: kafka.check_topic_has_messages("orders", min_count=1, timeout=10),
                condition=lambda r: r is True,
                timeout=120,
                interval=10,
                description="orders topic has >= 1 message after datagen",
            )
        assert has_messages, "orders topic is empty — datagen may have failed"

    @pytest.mark.order(2)
    def test_enriched_orders(self, env):
        """Create enriched_orders statement and verify output flows."""
        flink, kafka, sql = env["flink"], env["kafka"], env["sql"]
        _ensure_statement(flink, f"{_PREFIX}-enriched-orders", sql["enriched_orders"])

        has_messages = poll_until(
            getter=lambda: kafka.check_topic_has_messages("enriched_orders", min_count=1, timeout=10),
            condition=lambda r: r is True,
            timeout=300,
            interval=15,
            description="enriched_orders topic has >= 1 message",
        )
        assert has_messages, "enriched_orders topic is empty"

    @pytest.mark.order(3)
    def test_remote_mcp_tool(self, env):
        """Create the remote_mcp TOOL statement."""
        flink, sql = env["flink"], env["sql"]
        _ensure_statement(flink, f"{_PREFIX}-remote-mcp-tool", sql["create_tool"])

    @pytest.mark.order(4)
    def test_price_match_agent(self, env):
        """Create the price_match_agent AGENT statement."""
        flink, sql = env["flink"], env["sql"]
        _ensure_statement(flink, f"{_PREFIX}-price-match-agent", sql["create_agent"])

    @pytest.mark.order(5)
    def test_price_match_results(self, env):
        """Create price_match_results and verify the Remote MCP server end-to-end.

        This is the critical assertion: the agent must actually produce output.
        Asserting only that the agent is RUNNING would miss silent MCP failures.
        """
        flink, kafka, sql = env["flink"], env["kafka"], env["sql"]
        _ensure_statement(
            flink, f"{_PREFIX}-price-match-results", sql["price_match_results"], timeout=600
        )

        has_messages = poll_until(
            getter=lambda: kafka.check_topic_has_messages(
                "price_match_results", min_count=1, timeout=15
            ),
            condition=lambda r: r is True,
            timeout=1800,
            interval=30,
            description="price_match_results topic has >= 1 message",
        )
        assert has_messages, (
            "price_match_results topic is empty — Remote MCP server may be broken. "
            "Check Lambda logs in CloudWatch."
        )
