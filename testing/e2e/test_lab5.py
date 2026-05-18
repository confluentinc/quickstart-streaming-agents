"""Lab 5 E2E test: IBM MQ insurance fraud detection pipeline.

Pipeline: IBM MQ → claim_mq → claims → claims_surge_windows → claims_anomalies → claims_reviewed

Run:    uv run pytest testing/e2e/test_lab5.py -v --timeout=5400
Resume: PYTEST_RESUME=true uv run pytest testing/e2e/test_lab5.py -v --timeout=5400
"""

import os
import subprocess
import sys
import warnings
from pathlib import Path

import pytest
from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from testing.conftest import (
    ensure_confluent_cli_installed,
    ensure_confluent_login,
    RESUME_MODE,
)
from testing.helpers.terraform_helper import TerraformHelper
from testing.helpers.kafka_helper import KafkaHelper
from testing.helpers.polling_helper import poll_until


EXPECTED_CLAIMS_MIN = 700  # ~715 published; tolerate <2% MQ REST failures
VALID_VERDICTS = {"APPROVE", "DENY"}
KNOWN_VERDICTS = {
    "CLM-55019": "APPROVE",
    "CLM-77093": "DENY",
    "CLM-88241": "DENY",
}


@pytest.fixture(scope="class", params=["aws"])
def cloud(request):
    return request.param


class TestLab5InsuranceFraud:
    """Lab 5 E2E: IBM MQ insurance fraud detection from MQ ingestion to agent review.

    Requires Lab 5 infrastructure deployed via `uv run deploy`.
    Data is published to IBM MQ via `uv run lab5-datagen-mq`.
    """

    @pytest.fixture(scope="class")
    def env(self, cloud):
        ensure_confluent_cli_installed()

        # credentials.env is the single source of truth — no testing/credentials.json needed.
        # Merge all vars into os.environ so subprocesses (datagen) inherit them.
        creds_env_path = PROJECT_ROOT / "credentials.env"
        if creds_env_path.exists():
            for key, val in dotenv_values(str(creds_env_path)).items():
                if key not in os.environ and val:
                    os.environ[key] = val

        # ensure_confluent_login falls back to CONFLUENT_EMAIL/PASSWORD from credentials.env.
        ensure_confluent_login({})

        # Pre-flight: skip cleanly if Lab 5 isn't deployed yet.
        lab5_state = PROJECT_ROOT / "terraform" / "lab5-insurance-fraud-watson" / "terraform.tfstate"
        if not lab5_state.exists():
            pytest.skip(
                "Lab 5 not deployed — run `uv run deploy` first to create claim_mq and downstream topics"
            )

        # Skip if Lab 4 is co-deployed: both labs write to the shared `claims` topic and
        # Lab 5's Flink surge windows process ALL claims including Lab 4's Naples spike data,
        # making Naples assertions unreliable. Deploy Lab 5 without Lab 4 for isolation.
        lab4_state = PROJECT_ROOT / "terraform" / "lab4-pubsec-fraud-agents" / "terraform.tfstate"
        if lab4_state.exists():
            pytest.skip(
                "Lab 4 is co-deployed — Lab 5 tests require an isolated environment "
                "because both labs share the `claims` topic. "
                "Run `uv run destroy` to tear down Lab 4 before testing Lab 5."
            )

        if not os.environ.get("TF_VAR_ibmmq_password", "").strip():
            pytest.skip(
                "TF_VAR_ibmmq_password not set — required for lab5-datagen-mq. "
                "Add it to credentials.env or export it in the shell before running."
            )

        kafka = KafkaHelper(cloud, PROJECT_ROOT)

        # Capture pre-datagen baselines for delta-based assertions (non-RESUME mode).
        # In RESUME_MODE we use absolute thresholds because we have no pre-datagen snapshot.
        mq_baseline = None
        claims_baseline = None
        if not RESUME_MODE:
            mq_baseline = kafka.get_topic_message_count("claim_mq", max_messages=5000)
            claims_baseline = kafka.get_topic_message_count("claims", max_messages=5000)

        yield {
            "cloud": cloud,
            "kafka": kafka,
            "mq_baseline": mq_baseline,
            "claims_baseline": claims_baseline,
        }

    @pytest.mark.order(1)
    def test_datagen_publishes_to_mq(self, env):
        """Run lab5-datagen-mq and verify claim_mq receives >= 700 new messages.

        This validates the IBM MQ source connector and queue are healthy.
        """
        kafka = env["kafka"]
        mq_baseline = env["mq_baseline"]

        if not RESUME_MODE:
            subprocess.run(
                ["uv", "run", "lab5-datagen-mq"],
                cwd=PROJECT_ROOT,
                timeout=300,
                check=True,
                env={**os.environ},
            )
            count = poll_until(
                getter=lambda: kafka.get_topic_message_count(
                    "claim_mq", max_messages=5000
                ),
                condition=lambda c: c - mq_baseline >= EXPECTED_CLAIMS_MIN,
                timeout=300,
                interval=15,
                description=f"claim_mq delta >= {EXPECTED_CLAIMS_MIN}",
            )
            delta = count - mq_baseline
            assert delta >= EXPECTED_CLAIMS_MIN, (
                f"claim_mq received only {delta} new messages (expected >= {EXPECTED_CLAIMS_MIN}) "
                f"— IBM MQ source connector or queue may be unhealthy"
            )
        else:
            count = kafka.get_topic_message_count("claim_mq", max_messages=5000)
            assert count >= EXPECTED_CLAIMS_MIN, (
                f"claim_mq has only {count} messages (expected >= {EXPECTED_CLAIMS_MIN}) "
                f"— re-run without PYTEST_RESUME=true to seed MQ first"
            )

    @pytest.mark.order(2)
    def test_claims_parsed_from_mq(self, env):
        """Verify claims topic receives >= 700 messages (Flink INSERT claim_mq → claims).

        Also spot-checks that key schema fields are present and non-empty.
        """
        kafka = env["kafka"]
        claims_baseline = env["claims_baseline"]

        if not RESUME_MODE:
            count = poll_until(
                getter=lambda: kafka.get_topic_message_count(
                    "claims", max_messages=5000
                ),
                condition=lambda c: c - claims_baseline >= EXPECTED_CLAIMS_MIN,
                timeout=600,
                interval=30,
                description=f"claims delta >= {EXPECTED_CLAIMS_MIN}",
            )
            delta = count - claims_baseline
            assert delta >= EXPECTED_CLAIMS_MIN, (
                f"claims topic has only {delta} new messages (expected >= {EXPECTED_CLAIMS_MIN}) "
                f"— Flink INSERT claim_mq_to_claims may be stopped or failing"
            )
        else:
            count = kafka.get_topic_message_count("claims", max_messages=5000)
            assert count >= EXPECTED_CLAIMS_MIN, (
                f"claims has only {count} messages (expected >= {EXPECTED_CLAIMS_MIN})"
            )

        # Spot-check schema fields
        sample = kafka.consume_messages("claims", max_messages=5, timeout=20)
        if sample:
            first = sample[0]
            for field in ("city", "claim_id", "claim_timestamp"):
                val = first.get(field) or first.get(field.upper())
                assert val, (
                    f"Expected field '{field}' missing or empty in claims message: {first}"
                )

    @pytest.mark.order(3)
    def test_claims_surge_windows_naples(self, env):
        """Verify claims_surge_windows fires for Naples (spike city).

        The spike window closes when watermarks advance past the window end after
        datagen completes — typically a few minutes with idle-source watermarking.
        """
        kafka = env["kafka"]

        windows = poll_until(
            getter=lambda: kafka.consume_messages(
                "claims_surge_windows", max_messages=5, timeout=20
            ),
            condition=lambda msgs: len(msgs) >= 1,
            timeout=900,
            interval=30,
            description="claims_surge_windows has >= 1 record",
        )
        assert windows, "claims_surge_windows is empty — surge detection has not fired"
        for w in windows:
            city = w.get("city") or w.get("CITY") or ""
            assert city == "Naples", (
                f"Unexpected surge city '{city}' — only Naples should produce an anomaly spike"
            )
            assert w.get("claim_count") or w.get("CLAIM_COUNT"), (
                f"claim_count field missing in surge window record: {w}"
            )

    @pytest.mark.order(4)
    def test_claims_anomalies(self, env):
        """Verify claims_anomalies contains Naples claims with narrative and insurance."""
        kafka = env["kafka"]

        anomalies = poll_until(
            getter=lambda: kafka.consume_messages(
                "claims_anomalies", max_messages=5, timeout=20
            ),
            condition=lambda msgs: len(msgs) >= 1,
            timeout=300,
            interval=30,
            description="claims_anomalies has >= 1 record",
        )
        assert anomalies, "claims_anomalies is empty"
        for a in anomalies:
            city = a.get("city") or a.get("CITY") or ""
            assert city == "Naples", (
                f"Unexpected anomaly city '{city}' — CTAS join should produce only Naples anomalies"
            )
            narrative = (
                a.get("claim_narrative") or a.get("CLAIM_NARRATIVE") or ""
            ).strip()
            assert narrative, (
                f"claim_narrative is empty in claims_anomalies — "
                f"anomalies should only contain narrative claims: {a}"
            )
            has_insurance = (
                a.get("has_insurance") or a.get("HAS_INSURANCE") or ""
            ).lower()
            assert has_insurance == "yes", (
                f"has_insurance != 'yes' in claims_anomalies: '{has_insurance}' "
                f"— CTAS filter should require insurance: {a}"
            )

    @pytest.mark.order(5)
    def test_claims_reviewed_verdicts(self, env):
        """Verify agent produces valid verdicts; check known demo claim verdicts."""
        kafka = env["kafka"]

        messages = poll_until(
            getter=lambda: kafka.consume_messages(
                "claims_reviewed", max_messages=100, timeout=60
            ),
            condition=lambda msgs: len(msgs) >= 1,
            timeout=900,
            interval=30,
            description="claims_reviewed has >= 1 message",
        )
        assert messages, (
            "claims_reviewed is empty — agent may not have produced verdicts yet"
        )

        for msg in messages:
            claim_id = msg.get("claim_id") or msg.get("CLAIM_ID") or "<unknown>"
            verdict = (msg.get("verdict") or msg.get("VERDICT") or "").strip()
            payment = msg.get("payment_amount") or msg.get("PAYMENT_AMOUNT") or ""
            assert verdict, f"verdict field empty in claims_reviewed: {msg}"
            assert verdict.upper() in VALID_VERDICTS, (
                f"claim {claim_id}: verdict '{verdict}' not in {VALID_VERDICTS}"
            )
            assert payment, (
                f"payment_amount empty in claims_reviewed for {claim_id}: {msg}"
            )

        # Required-if-present: validate known demo claim verdicts
        seen = {
            (msg.get("claim_id") or msg.get("CLAIM_ID") or ""): (
                msg.get("verdict") or msg.get("VERDICT") or ""
            ).strip().upper()
            for msg in messages
        }
        found_known = 0
        for claim_id, expected in KNOWN_VERDICTS.items():
            if claim_id in seen:
                found_known += 1
                assert seen[claim_id] == expected, (
                    f"Known claim {claim_id}: expected verdict '{expected}', "
                    f"got '{seen[claim_id]}'"
                )
        if found_known == 0:
            warnings.warn(
                f"None of the known demo claims {list(KNOWN_VERDICTS)} appeared in the "
                f"{len(messages)} sampled messages from claims_reviewed. "
                "Agent may not have processed them within the sample window.",
                UserWarning,
                stacklevel=2,
            )
