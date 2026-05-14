"""Lab 3 E2E test: Agentic fleet management pipeline.

Parses SQL from LAB3-Walkthrough.md and drives the full pipeline:
  ride_requests → anomalies_per_zone → anomalies_enriched
  → boat_dispatch_agent → completed_actions

Run: uv run pytest testing/e2e/test_lab3.py -v --timeout=5400
"""

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


_PREFIX = "test-lab3"


def _parse_lab3_sql(walkthrough_path: Path) -> Dict[str, str]:
    """Extract user-run SQL statements from LAB3-Walkthrough.md."""
    text = walkthrough_path.read_text()
    statements = {}

    # CREATE TABLE anomalies_per_zone AS (WITH CTE, TUMBLE window)
    match = re.search(
        r"```sql\s*(CREATE TABLE anomalies_per_zone AS\s+WITH\b.*?)```",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if match:
        statements["anomalies_per_zone"] = match.group(1).strip()

    # CREATE TABLE anomalies_enriched
    match = re.search(
        r"```sql\s*(CREATE TABLE anomalies_enriched\b.*?)```",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if match:
        statements["anomalies_enriched"] = match.group(1).strip()

    # CREATE TOOL lab3_remote_mcp
    match = re.search(
        r"```sql\s*(CREATE TOOL lab3_remote_mcp\b.*?)```",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if match:
        statements["create_tool"] = match.group(1).strip()

    # CREATE AGENT boat_dispatch_agent
    match = re.search(
        r"```sql\s*(CREATE AGENT [`']?boat_dispatch_agent[`']?\b.*?)```",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if match:
        statements["create_agent"] = match.group(1).strip()

    # CREATE TABLE completed_actions
    match = re.search(
        r"```sql\s*(CREATE TABLE completed_actions\b.*?)```",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if match:
        statements["completed_actions"] = match.group(1).strip()

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


class TestLab3FleetManagement:
    """Lab 3 E2E: ride-request surge detection through boat dispatch.

    Requires Lab 3 infrastructure already deployed via `uv run deploy`.
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

        walkthrough = PROJECT_ROOT / "LAB3-Walkthrough.md"
        sql = _parse_lab3_sql(walkthrough)
        assert sql.get("anomalies_per_zone"), "Could not parse anomalies_per_zone SQL"
        assert sql.get("anomalies_enriched"), "Could not parse anomalies_enriched SQL"
        assert sql.get("create_tool"), "Could not parse CREATE TOOL SQL"
        assert sql.get("create_agent"), "Could not parse CREATE AGENT SQL"
        assert sql.get("completed_actions"), "Could not parse completed_actions SQL"

        yield {
            "cloud": cloud,
            "flink": flink_helper,
            "kafka": kafka_helper,
            "sql": sql,
        }

        if not KEEP_STATEMENTS:
            flink_helper.cleanup_all()

    @pytest.mark.order(1)
    def test_ride_requests_datagen(self, env):
        """ride_requests topic has >= 28,000 messages; run datagen if under threshold."""
        kafka = env["kafka"]
        count = kafka.get_topic_message_count("ride_requests", timeout=60, max_messages=28001)
        if count < 28000:
            # Datagen is a long-running streaming process; launch non-blocking.
            proc = subprocess.Popen(["uv", "run", "lab3_datagen", "--local"], cwd=PROJECT_ROOT)
            count = poll_until(
                getter=lambda: kafka.get_topic_message_count(
                    "ride_requests", timeout=60, max_messages=28001
                ),
                condition=lambda c: c >= 28000,
                timeout=600,
                interval=30,
                description="ride_requests >= 28,000 messages",
            )
        assert count >= 28000, f"ride_requests has only {count} messages (expected >= 28,000)"

    @pytest.mark.order(2)
    def test_anomalies_per_zone(self, env):
        """Create anomalies_per_zone and verify only French Quarter surges (max 2 anomalies)."""
        flink, kafka, sql = env["flink"], env["kafka"], env["sql"]
        _ensure_statement(flink, f"{_PREFIX}-anomalies-per-zone", sql["anomalies_per_zone"], timeout=360)

        def _get_anomalies():
            return kafka.consume_messages("anomalies_per_zone", max_messages=3, timeout=15)

        messages = poll_until(
            getter=_get_anomalies,
            condition=lambda msgs: len(msgs) >= 1,
            timeout=600,
            interval=30,
            description="anomalies_per_zone has >= 1 message",
        )
        assert messages, "anomalies_per_zone topic is empty after 10 minutes"
        assert len(messages) <= 2, (
            f"anomalies_per_zone has {len(messages)} anomalies (expected <= 2): "
            f"{[m.get('pickup_zone') for m in messages]}"
        )
        for msg in messages:
            zone = msg.get("pickup_zone") or msg.get("PICKUP_ZONE") or ""
            assert zone == "French Quarter", (
                f"Unexpected anomaly zone '{zone}' — only French Quarter should surge. "
                f"Check anomaly detection threshold or datagen."
            )

    @pytest.mark.order(3)
    def test_anomalies_enriched(self, env):
        """Create anomalies_enriched and verify top_chunk_content is populated."""
        flink, kafka, sql = env["flink"], env["kafka"], env["sql"]
        _ensure_statement(flink, f"{_PREFIX}-anomalies-enriched", sql["anomalies_enriched"], timeout=360)

        def _get_enriched():
            return kafka.consume_messages("anomalies_enriched", max_messages=3, timeout=15)

        messages = poll_until(
            getter=_get_enriched,
            condition=lambda msgs: len(msgs) >= 1,
            timeout=600,
            interval=30,
            description="anomalies_enriched has >= 1 message",
        )
        assert messages, "anomalies_enriched topic is empty"

        first = messages[0]
        # Schema uses top_chunk_1/2/3, not top_chunk_content
        chunk = (
            first.get("top_chunk_1") or first.get("top_chunk_2")
            or first.get("TOP_CHUNK_1") or first.get("TOP_CHUNK_2") or ""
        )
        assert chunk and chunk.strip(), (
            f"top_chunk_1/2 are null/empty in anomalies_enriched: {list(first.keys())}"
        )

    @pytest.mark.order(4)
    def test_boat_dispatch_tool(self, env):
        """Create the remote_mcp TOOL statement."""
        flink, sql = env["flink"], env["sql"]
        _ensure_statement(flink, f"{_PREFIX}-remote-mcp-tool", sql["create_tool"])

    @pytest.mark.order(5)
    def test_boat_dispatch_agent(self, env):
        """Create the boat_dispatch_agent AGENT statement."""
        flink, sql = env["flink"], env["sql"]
        _ensure_statement(flink, f"{_PREFIX}-boat-dispatch-agent", sql["create_agent"])

    @pytest.mark.order(6)
    def test_completed_actions(self, env):
        """Create completed_actions and verify dispatch summaries are valid."""
        flink, kafka, sql = env["flink"], env["kafka"], env["sql"]
        _ensure_statement(
            flink, f"{_PREFIX}-completed-actions", sql["completed_actions"], timeout=600
        )

        def _get_actions():
            return kafka.consume_messages("completed_actions", max_messages=3, timeout=20)

        messages = poll_until(
            getter=_get_actions,
            condition=lambda msgs: len(msgs) >= 1,
            timeout=1800,
            interval=60,
            description="completed_actions has >= 1 message",
        )
        assert messages, "completed_actions topic is empty after 30 minutes"

        first = messages[0]
        summary = first.get("dispatch_summary") or first.get("DISPATCH_SUMMARY") or ""
        failure_markers = ("unable to dispatch", "failed to", "error:", "could not")
        for marker in failure_markers:
            assert marker not in summary.lower(), (
                f"dispatch_summary contains failure marker '{marker}': {summary!r}"
            )
