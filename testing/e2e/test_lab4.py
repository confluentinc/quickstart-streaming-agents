"""Lab 4 E2E test: FEMA fraud detection pipeline.

Parses SQL from LAB4-Walkthrough.md and drives the full pipeline:
  claims → claims_anomalies_by_city → claims_to_investigate
  → claims_to_investigate_with_policies → claims_fraud_investigation_agent
  → claims_reviewed

Run: uv run pytest testing/e2e/test_lab4.py -v --timeout=5400
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


_PREFIX = "test-lab4"
_SET_RE = re.compile(r"SET\s+'([^']+)'\s*=\s*'([^']+)'\s*;\s*", re.IGNORECASE)

_VALID_VERDICTS = {
    "APPROVE",
    "APPROVE_PARTIAL",
    "REQUEST_DOCS",
    "DENY_INELIGIBLE",
    "DENY_FRAUD",
}


def _parse_lab4_sql(walkthrough_path: Path) -> Dict[str, tuple]:
    """Extract user-run SQL statements from LAB4-Walkthrough.md.

    Returns a dict mapping statement key to (sql, properties) where properties
    is a dict extracted from any leading SET clauses in the code block.
    """
    text = walkthrough_path.read_text()
    statements = {}

    # claims_anomalies_by_city — capture SET clauses then CREATE TABLE
    match = re.search(
        r"```sql\s*((?:SET\s+'[^']+'\s*=\s*'[^']+'\s*;\s*)*)(CREATE TABLE claims_anomalies_by_city AS\s+WITH\b.*?)```",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if match:
        statements["claims_anomalies_by_city"] = (
            match.group(2).strip(),
            dict(_SET_RE.findall(match.group(1))),
        )

    # claims_to_investigate — capture SET clauses then CREATE TABLE
    match = re.search(
        r"```sql\s*((?:SET\s+'[^']+'\s*=\s*'[^']+'\s*;\s*)*)(CREATE TABLE claims_to_investigate AS\s+SELECT.*?)```",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if match:
        statements["claims_to_investigate"] = (
            match.group(2).strip(),
            dict(_SET_RE.findall(match.group(1))),
        )

    # claims_to_investigate_with_policies — capture SET clauses then CREATE TABLE
    match = re.search(
        r"```sql\s*((?:SET\s+'[^']+'\s*=\s*'[^']+'\s*;\s*)*)(CREATE TABLE claims_to_investigate_with_policies AS\s+WITH\b.*?)```",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if match:
        statements["claims_to_investigate_with_policies"] = (
            match.group(2).strip(),
            dict(_SET_RE.findall(match.group(1))),
        )

    # CREATE AGENT claims_fraud_investigation_agent (no SET)
    match = re.search(
        r"```sql\s*(CREATE AGENT [`']?claims_fraud_investigation_agent[`']?\b.*?)```",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if match:
        statements["create_agent"] = (match.group(1).strip(), {})

    # claims_reviewed — capture SET clauses then CREATE TABLE
    match = re.search(
        r"```sql\s*((?:SET\s+'[^']+'\s*=\s*'[^']+'\s*;\s*)*)(CREATE TABLE claims_reviewed\b.*?)```",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if match:
        statements["claims_reviewed"] = (
            match.group(2).strip(),
            dict(_SET_RE.findall(match.group(1))),
        )

    return statements


def _ensure_statement(
    flink: FlinkSQLHelper, name: str, sql_and_props: tuple, timeout: int = 300
) -> None:
    """Create statement; skip if already RUNNING or COMPLETED (e.g. DDL/TOOL)."""
    sql, props = sql_and_props
    obj = flink._extract_sql_object(sql)
    try:
        status = flink.get_statement_status(name)
        if status in ("RUNNING", "COMPLETED"):
            if not obj or flink.verify_sql_object_exists(*obj):
                return
            flink.delete_statement(name)
        if status in ("FAILED", "STOPPED", "DEGRADED"):
            flink.delete_statement(name)
    except Exception:
        pass  # Statement doesn't exist yet

    # Pre-drop any stale SQL object so DDL/CTAS can succeed on re-runs.
    # DDL statements (CREATE AGENT/TOOL/TABLE) fail if the object already exists
    # from a previous run whose cleanup silently failed.
    if obj:
        obj_type, obj_name = obj
        try:
            drop_name = flink._unique_statement_name("pre-drop", obj_name)
            flink.execute_statement(
                drop_name, f"DROP {obj_type} IF EXISTS `{obj_name}`", wait=True
            )
            flink.delete_statement(drop_name)
        except Exception:
            pass

    try:
        flink.execute_statement(name, sql, wait=False, properties=props)
        flink.wait_for_status(name, ["RUNNING", "COMPLETED"], timeout=timeout)
    except (subprocess.CalledProcessError, RuntimeError, TimeoutError):
        # CalledProcessError: CLI rejected.
        # RuntimeError: statement went to FAILED.
        # TimeoutError: statement stuck in transition — may still produce output.
        # In all cases, let the subsequent topic/data assertions determine success.
        pass

    if obj and not flink.verify_sql_object_exists(*obj):
        obj_type, obj_name = obj
        status = flink.get_statement_status(name)
        raise AssertionError(
            f"{obj_type} {obj_name} was not created by statement {name} "
            f"(status: {status})"
        )


@pytest.fixture(scope="class", params=["aws"])
def cloud(request):
    return request.param


class TestLab4FraudDetection:
    """Lab 4 E2E: FEMA claims fraud detection from anomaly detection to agent review.

    Requires Lab 4 infrastructure already deployed via `uv run deploy`.
    ~36,000 synthetic claims are inserted by Terraform; no manual datagen needed.
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

        walkthrough = PROJECT_ROOT / "LAB4-Walkthrough.md"
        sql = _parse_lab4_sql(walkthrough)
        assert sql.get("claims_anomalies_by_city"), (
            "Could not parse claims_anomalies_by_city SQL"
        )
        assert sql.get("claims_to_investigate"), (
            "Could not parse claims_to_investigate SQL"
        )
        assert sql.get("claims_to_investigate_with_policies"), (
            "Could not parse claims_to_investigate_with_policies SQL"
        )
        assert sql.get("create_agent"), "Could not parse CREATE AGENT SQL"
        assert sql.get("claims_reviewed"), "Could not parse claims_reviewed SQL"

        yield {
            "cloud": cloud,
            "flink": flink_helper,
            "kafka": kafka_helper,
            "sql": sql,
        }

        if not KEEP_STATEMENTS:
            flink_helper.cleanup_all()

    @pytest.mark.order(16)
    def test_claims_datagen(self, env):
        """claims topic has >= 33,000 messages (datagen publishes ~33,984 FEMA claims)."""
        kafka = env["kafka"]
        count = kafka.get_topic_message_count("claims", max_messages=34000)
        if count < 33000:
            # Attempt manual fallback
            subprocess.run(
                ["uv", "run", "lab4_datagen"],
                cwd=PROJECT_ROOT,
                timeout=300,
                check=False,
            )
            count = poll_until(
                getter=lambda: kafka.get_topic_message_count(
                    "claims", max_messages=34000
                ),
                condition=lambda c: c >= 33000,
                timeout=600,
                interval=30,
                description="claims topic has >= 33,000 messages",
            )
        assert count >= 33000, (
            f"claims topic has only {count} messages (expected >= 33,000) — was Lab 4 deployed?"
        )

    @pytest.mark.order(17)
    def test_claims_anomalies_by_city(self, env):
        """Create claims_anomalies_by_city and verify only Naples anomaly fires (max 2)."""
        flink, kafka, sql = env["flink"], env["kafka"], env["sql"]
        _ensure_statement(
            flink,
            f"{_PREFIX}-anomalies-by-city",
            sql["claims_anomalies_by_city"],
            timeout=360,
        )

        def _get_city_anomalies():
            return kafka.consume_messages(
                "claims_anomalies_by_city", max_messages=3, timeout=15
            )

        anomalies = poll_until(
            getter=_get_city_anomalies,
            condition=lambda msgs: len(msgs) >= 1,
            timeout=600,
            interval=30,
            description="claims_anomalies_by_city has >= 1 message",
        )
        assert anomalies, (
            "claims_anomalies_by_city is empty — Naples anomaly not detected"
        )
        assert len(anomalies) <= 2, (
            f"claims_anomalies_by_city has {len(anomalies)} anomalies (expected <= 2): "
            f"{[m.get('city') for m in anomalies]}"
        )
        for msg in anomalies:
            city = msg.get("city") or msg.get("CITY") or ""
            assert city == "Naples", (
                f"Unexpected anomaly city '{city}' — only Naples should have a fraud spike. "
                f"Check anomaly detection parameters."
            )

    @pytest.mark.order(18)
    def test_claims_to_investigate(self, env):
        """Create claims_to_investigate and verify claims enter the investigation queue."""
        flink, kafka, sql = env["flink"], env["kafka"], env["sql"]
        _ensure_statement(
            flink,
            f"{_PREFIX}-claims-to-investigate",
            sql["claims_to_investigate"],
            timeout=360,
        )
        has_messages = poll_until(
            getter=lambda: kafka.check_topic_has_messages(
                "claims_to_investigate", min_count=1, timeout=15
            ),
            condition=lambda r: r is True,
            timeout=300,
            interval=30,
            description="claims_to_investigate has >= 1 message",
        )
        assert has_messages, (
            "claims_to_investigate is empty — claims_anomalies_by_city may have no anomalies yet"
        )

    @pytest.mark.order(19)
    def test_claims_to_investigate_with_policies(self, env):
        """Create claims_to_investigate_with_policies (RAG enrichment with FEMA policy)."""
        flink, kafka, sql = env["flink"], env["kafka"], env["sql"]
        name = f"{_PREFIX}-claims-with-policies"
        _ensure_statement(
            flink,
            name,
            sql["claims_to_investigate_with_policies"],
            timeout=600,
        )
        status = flink.get_statement_status(name)
        if status not in ("RUNNING", "COMPLETED"):
            # Bounded CTAS may complete and be GC'd; verify the output topic has data
            has_data = kafka.check_topic_has_messages(
                "claims_to_investigate_with_policies", min_count=1, timeout=120
            )
            assert has_data, (
                f"claims_to_investigate_with_policies statement is in state '{status}' "
                "and topic has no messages — check Confluent Cloud for failure details"
            )

    @pytest.mark.order(20)
    def test_claims_fraud_investigation_agent(self, env):
        """Create the claims_fraud_investigation_agent AGENT statement."""
        flink, sql = env["flink"], env["sql"]
        _ensure_statement(
            flink, f"{_PREFIX}-fraud-agent", sql["create_agent"], timeout=360
        )
        assert flink.verify_sql_object_exists(
            "AGENT", "claims_fraud_investigation_agent"
        ), (
            "claims_fraud_investigation_agent was not created — check Confluent Cloud for the statement failure"
        )

    @pytest.mark.order(21)
    def test_claims_reviewed(self, env):
        """Create claims_reviewed and verify agent produces fraud verdicts."""
        flink, kafka, sql = env["flink"], env["kafka"], env["sql"]
        _ensure_statement(
            flink, f"{_PREFIX}-claims-reviewed", sql["claims_reviewed"], timeout=600
        )

        def _get_reviewed():
            return kafka.consume_messages("claims_reviewed", max_messages=3, timeout=20)

        messages = poll_until(
            getter=_get_reviewed,
            condition=lambda msgs: len(msgs) >= 1,
            timeout=1800,
            interval=30,
            description="claims_reviewed has >= 1 message",
        )
        assert messages, (
            "claims_reviewed topic is empty — claims_to_investigate pipeline may have no data"
        )

        first = messages[0]
        verdict = first.get("verdict") or first.get("VERDICT") or ""
        assert verdict and verdict.strip(), (
            f"verdict field is empty in claims_reviewed: {first}"
        )
        assert verdict.upper() in _VALID_VERDICTS, (
            f"verdict '{verdict}' is not a valid verdict. "
            f"Expected one of: {_VALID_VERDICTS}. Message: {first}"
        )
