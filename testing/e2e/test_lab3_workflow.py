"""Lab 3 E2E test: Full deployment through agent execution workflow."""

import os
import subprocess
import sys
import re
import time
import logging
from pathlib import Path
from typing import Dict
from contextlib import contextmanager
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.common.sql_extractors import extract_sql_from_lab_walkthroughs
from testing.conftest import (
    ensure_confluent_cli_installed,
    ensure_confluent_login,
    load_test_credentials,
    write_credentials_to_project_root,
    remove_credentials_from_project_root,
)
from testing.helpers.terraform_helper import TerraformHelper
from testing.helpers.flink_sql_helper import FlinkSQLHelper
from testing.helpers.kafka_helper import KafkaHelper
from testing.helpers.polling_helper import poll_until
from testing.helpers.deployment_state_helper import is_infrastructure_deployed, get_deployment_info


# Configure logging
LOG_FILE = PROJECT_ROOT / "testing" / "reports" / "test_run.log"
LOG_FILE.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@contextmanager
def timer(description: str):
    """Context manager to time operations and log results."""
    logger.info(f"⏱️  Starting: {description}")
    start = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)
        logger.info(f"✅ Completed: {description} - {mins}m {secs}s")


def parse_sql_statements(extracted_markdown: str) -> Dict[str, str]:
    """Parse extracted markdown to get individual SQL statements.

    Args:
        extracted_markdown: Output from extract_sql_from_lab_walkthroughs()

    Returns:
        Dictionary mapping statement names to SQL code:
            - anomalies_per_zone
            - anomalies_enriched
            - create_tool
            - create_agent
            - completed_actions
    """
    statements = {}

    # Extract CREATE TABLE anomalies_per_zone
    match = re.search(
        r'```sql\s*(CREATE TABLE anomalies_per_zone.*?)```',
        extracted_markdown,
        re.DOTALL | re.IGNORECASE
    )
    if match:
        statements['anomalies_per_zone'] = match.group(1).strip()

    # Extract CREATE TABLE anomalies_enriched
    match = re.search(
        r'```sql\s*(CREATE TABLE anomalies_enriched.*?)```',
        extracted_markdown,
        re.DOTALL | re.IGNORECASE
    )
    if match:
        statements['anomalies_enriched'] = match.group(1).strip()

    # Extract CREATE TOOL zapier
    match = re.search(
        r'```sql\s*(CREATE TOOL zapier.*?)```',
        extracted_markdown,
        re.DOTALL | re.IGNORECASE
    )
    if match:
        statements['create_tool'] = match.group(1).strip()

    # Extract CREATE AGENT boat_dispatch_agent
    match = re.search(
        r'```sql\s*(CREATE AGENT `?boat_dispatch_agent`?.*?)```',
        extracted_markdown,
        re.DOTALL | re.IGNORECASE
    )
    if match:
        statements['create_agent'] = match.group(1).strip()

    # Extract CREATE TABLE completed_actions
    match = re.search(
        r'```sql\s*(CREATE TABLE completed_actions.*?)```',
        extracted_markdown,
        re.DOTALL | re.IGNORECASE
    )
    if match:
        statements['completed_actions'] = match.group(1).strip()

    return statements


@pytest.mark.parametrize("cloud", ["aws"], scope="class")  # Start with AWS only
class TestLab3Workflow:
    """Complete Lab 3 E2E test with automatic setup/teardown.

    Run: uv run pytest testing/e2e/test_lab3_workflow.py -k aws -v --timeout=5400
    """

    @pytest.fixture(scope="class")
    def deployed_environment(self, cloud, request):
        """Full lifecycle: generate credentials.json -> deploy -> yield -> destroy -> cleanup."""
        test_start_time = time.time()

        # Check if resuming from existing deployment
        resume_mode = os.getenv("PYTEST_RESUME", "false").lower() == "true"
        skip_teardown = os.getenv("PYTEST_SKIP_TEARDOWN", "false").lower() == "true"
        destroy_on_failure = os.getenv("PYTEST_DESTROY_ON_FAILURE", "false").lower() == "true"
        was_already_deployed = is_infrastructure_deployed(cloud, PROJECT_ROOT)

        if resume_mode and was_already_deployed:
            logger.info(f"\n{'='*70}")
            logger.info("🔄 RESUMING: Using existing infrastructure")
            logger.info(f"{'='*70}\n")

            # Show deployment info
            info = get_deployment_info(cloud, PROJECT_ROOT)
            if info:
                logger.info(f"Environment: {info['environment_id']}")
                logger.info(f"Kafka Cluster: {info['kafka_cluster']}")
                logger.info(f"Region: {info['region']}")

            # Load existing credentials
            credentials = load_test_credentials(cloud)
            ensure_confluent_login(credentials)

            # Skip workshop keys creation (already exists)
            # Skip deployment (already deployed)

            # Extract SQL and initialize helpers (still needed)
            with timer("SQL extraction from walkthrough"):
                logger.info("\n=== Extracting SQL from LAB3-Walkthrough.md ===")
                walkthrough_path = PROJECT_ROOT / "LAB3-Walkthrough.md"
                extracted_markdown = extract_sql_from_lab_walkthroughs(walkthrough_path)
                sql_statements = parse_sql_statements(extracted_markdown)

                # Verify all required statements extracted
                required_statements = [
                    'anomalies_per_zone',
                    'anomalies_enriched',
                    'create_tool',
                    'create_agent',
                    'completed_actions'
                ]
                missing = [s for s in required_statements if s not in sql_statements]
                if missing:
                    pytest.fail(f"Failed to extract SQL statements: {', '.join(missing)}")

            # Initialize helpers
            logger.info("\n=== Initializing test helpers ===")
            tf_helper = TerraformHelper(cloud, PROJECT_ROOT)
            flink_params = tf_helper.get_flink_params()
            flink_helper = FlinkSQLHelper(**flink_params)
            kafka_helper = KafkaHelper(cloud, PROJECT_ROOT)

            yield {
                'flink': flink_helper,
                'kafka': kafka_helper,
                'sql': sql_statements,
                'cloud': cloud,
                'test_start_time': test_start_time,
                'was_resumed': True
            }

            # TEARDOWN - only clean up Flink statements, keep infrastructure
            logger.info("\n🔄 RESUME MODE: Skipping infrastructure teardown")
            try:
                with timer("Flink statement cleanup"):
                    if 'flink_helper' in locals():
                        flink_helper.cleanup_all()
            except Exception as e:
                logger.warning(f"Flink cleanup error: {e}")

            # Don't destroy infrastructure
            # Don't destroy workshop keys
            # Don't remove credentials

            total_elapsed = time.time() - test_start_time
            total_mins = int(total_elapsed // 60)
            total_secs = int(total_elapsed % 60)
            logger.info(f"\n{'='*70}")
            logger.info(f"🏁 TOTAL TEST TIME (resume mode): {total_mins}m {total_secs}s")
            logger.info(f"{'='*70}\n")
            logger.info(f"📋 Full log saved to: {LOG_FILE}")
            logger.info(f"\n💡 Infrastructure still deployed. To clean up:")
            logger.info(f"   uv run destroy --testing")

            return

        # Normal mode: full deployment
        if was_already_deployed:
            logger.warning("\n⚠️  Infrastructure already deployed but PYTEST_RESUME not set")
            logger.warning("Will tear down and redeploy. Use PYTEST_RESUME=true to reuse.")
            logger.warning(f"{'='*70}\n")

        # Ensure CLI installed
        ensure_confluent_cli_installed()

        # Load test credentials
        credentials = load_test_credentials(cloud)

        # Ensure Confluent CLI is logged in
        ensure_confluent_login(credentials)

        # Write credentials to project root for deploy.py --testing
        write_credentials_to_project_root(credentials)

        # Track if we created keys vs. they pre-existed
        keys_pre_existed = False

        try:
            # Step 1: Create workshop keys (or validate existing)
            api_keys_file = PROJECT_ROOT / f"API-KEYS-{cloud.upper()}.md"

            if api_keys_file.exists():
                keys_pre_existed = True
                logger.info(f"\n{'='*70}")
                logger.info(f"✅ WORKSHOP KEYS ALREADY EXIST FOR {cloud.upper()}")
                logger.info(f"{'='*70}\n")
                logger.info(f"Using existing file: {api_keys_file.name}")
                logger.info("💡 To test fresh creation, run 'uv run destroy' first")
            else:
                with timer(f"Workshop keys creation ({cloud.upper()})"):
                    logger.info(f"\n{'='*70}")
                    logger.info(f"CREATING WORKSHOP KEYS FOR {cloud.upper()}")
                    logger.info(f"{'='*70}\n")

                    result = subprocess.run(
                        ["uv", "run", "workshop-keys", "create", cloud],
                        cwd=PROJECT_ROOT,
                        timeout=300,
                        capture_output=True,
                        text=True
                    )

                    if result.returncode != 0:
                        # Check if failed due to AWS key limits
                        if "already has 2 access keys" in result.stderr:
                            pytest.fail(
                                f"Workshop keys creation failed: AWS IAM user has reached key limit (2 keys max).\n\n"
                                f"To fix this:\n"
                                f"1. List keys: aws iam list-access-keys --user-name workshop-bedrock-user\n"
                                f"2. Delete old key: aws iam delete-access-key --user-name workshop-bedrock-user --access-key-id <KEY_ID>\n"
                                f"3. Rerun tests\n\n"
                                f"Or run 'uv run destroy' to clean up all workshop resources."
                            )
                        else:
                            pytest.fail(f"Workshop keys creation failed: {result.stderr}")

                    # Verify API-KEYS file created
                    if not api_keys_file.exists():
                        pytest.fail(f"API-KEYS-{cloud.upper()}.md not created")

            # Step 2: Deploy all labs
            with timer(f"Infrastructure deployment ({cloud.upper()})"):
                logger.info(f"\n{'='*70}")
                logger.info(f"DEPLOYING ALL LABS FOR {cloud.upper()}")
                logger.info(f"{'='*70}\n")

                result = subprocess.run(
                    ["uv", "run", "deploy", "--testing"],
                    cwd=PROJECT_ROOT,
                    timeout=1800  # 30 minutes
                )

                if result.returncode != 0:
                    pytest.fail(f"Deployment failed")

            # Step 3: Extract SQL statements from walkthrough
            with timer("SQL extraction from walkthrough"):
                logger.info("\n=== Extracting SQL from LAB3-Walkthrough.md ===")
                walkthrough_path = PROJECT_ROOT / "LAB3-Walkthrough.md"
                extracted_markdown = extract_sql_from_lab_walkthroughs(walkthrough_path)
                sql_statements = parse_sql_statements(extracted_markdown)

                # Verify all required statements extracted
                required_statements = [
                    'anomalies_per_zone',
                    'anomalies_enriched',
                    'create_tool',
                    'create_agent',
                    'completed_actions'
                ]
                missing = [s for s in required_statements if s not in sql_statements]
                if missing:
                    pytest.fail(f"Failed to extract SQL statements: {', '.join(missing)}")

            # Step 4: Initialize helpers
            logger.info("\n=== Initializing test helpers ===")
            tf_helper = TerraformHelper(cloud, PROJECT_ROOT)
            flink_params = tf_helper.get_flink_params()
            flink_helper = FlinkSQLHelper(**flink_params)
            kafka_helper = KafkaHelper(cloud, PROJECT_ROOT)

            # Yield to tests
            yield {
                'flink': flink_helper,
                'kafka': kafka_helper,
                'sql': sql_statements,
                'cloud': cloud,
                'test_start_time': test_start_time,
                'was_resumed': False
            }

        finally:
            # TEARDOWN (runs even on test failure)
            # Check if any tests failed
            test_failed = request.session.testsfailed > 0

            # Decision logic:
            # 1. If skip_teardown flag set → always skip
            # 2. If tests failed and NOT destroy_on_failure → skip (keep for debugging)
            # 3. Otherwise → destroy
            should_skip_teardown = skip_teardown or (test_failed and not destroy_on_failure)

            if should_skip_teardown:
                reason = "PYTEST_SKIP_TEARDOWN flag" if skip_teardown else "test failure (keeping for debugging)"
                logger.info(f"\n{'='*70}")
                logger.info(f"🚫 SKIP TEARDOWN: Infrastructure will be kept ({reason})")
                logger.info(f"{'='*70}\n")

                try:
                    # Still clean up Flink statements
                    with timer("Flink statement cleanup"):
                        if 'flink_helper' in locals():
                            flink_helper.cleanup_all()
                except Exception as e:
                    logger.warning(f"Flink cleanup error: {e}")

                # Log total test time
                total_elapsed = time.time() - test_start_time
                total_mins = int(total_elapsed // 60)
                total_secs = int(total_elapsed % 60)
                logger.info(f"\n{'='*70}")
                logger.info(f"🏁 TOTAL TEST TIME (no teardown): {total_mins}m {total_secs}s")
                logger.info(f"{'='*70}\n")
                logger.info(f"📋 Full log saved to: {LOG_FILE}")

                if test_failed:
                    logger.info(f"\n{'='*70}")
                    logger.info(f"❌ Tests failed - Infrastructure preserved for debugging")
                    logger.info(f"{'='*70}")
                    logger.info(f"\n💡 Next steps:")
                    logger.info(f"   1. Fix the issue")
                    logger.info(f"   2. Resume tests: uv run tests --resume")
                    logger.info(f"   3. (Optional) Clean up: uv run destroy --testing")
                    logger.info(f"\n💡 To force destroy on failure:")
                    logger.info(f"   PYTEST_DESTROY_ON_FAILURE=true uv run tests")
                else:
                    logger.info(f"\n💡 Infrastructure still deployed. To clean up:")
                    logger.info(f"   uv run destroy --testing")
                    logger.info(f"\n💡 To rerun tests with existing infrastructure:")
                    logger.info(f"   uv run tests --resume")

                return

            # Normal teardown
            logger.info(f"\n{'='*70}")
            logger.info(f"TEARDOWN: Cleaning up {cloud.upper()} resources")
            logger.info(f"{'='*70}\n")

            try:
                # Clean up Flink statements
                with timer("Flink statement cleanup"):
                    if 'flink_helper' in locals():
                        flink_helper.cleanup_all()
            except Exception as e:
                logger.warning(f"Flink cleanup error: {e}")

            # Destroy infrastructure
            try:
                with timer("Infrastructure teardown"):
                    result = subprocess.run(
                        ["uv", "run", "destroy", "--testing"],
                        cwd=PROJECT_ROOT,
                        timeout=1200  # 20 minutes
                    )
                    if result.returncode != 0:
                        logger.warning("Destroy command failed")
            except Exception as e:
                logger.warning(f"Destroy error: {e}")

            # Destroy workshop keys (only if we created them)
            if keys_pre_existed:
                logger.info("ℹ️  Skipping workshop keys cleanup (keys existed before test)")
            else:
                try:
                    with timer("Workshop keys cleanup"):
                        result = subprocess.run(
                            ["uv", "run", "workshop-keys", "destroy", cloud, "--keep-user"],
                            cwd=PROJECT_ROOT,
                            timeout=300
                        )
                        if result.returncode != 0:
                            logger.warning("Workshop keys destroy failed")

                        # Verify API-KEYS file removed
                        api_keys_file = PROJECT_ROOT / f"API-KEYS-{cloud.upper()}.md"
                        if api_keys_file.exists():
                            api_keys_file.unlink()
                            logger.info(f"Removed {api_keys_file}")
                except Exception as e:
                    logger.warning(f"Workshop keys destroy error: {e}")

            # Remove credentials.json from project root
            remove_credentials_from_project_root()

            # Log total test time
            total_elapsed = time.time() - test_start_time
            total_mins = int(total_elapsed // 60)
            total_secs = int(total_elapsed % 60)
            logger.info(f"\n{'='*70}")
            logger.info(f"🏁 TOTAL TEST TIME: {total_mins}m {total_secs}s")
            logger.info(f"{'='*70}\n")
            logger.info(f"📋 Full log saved to: {LOG_FILE}")

    @pytest.mark.order(1)
    def test_data_generation(self, deployed_environment):
        """Generate ride_requests data and validate count >= 28,000."""
        flink = deployed_environment['flink']
        kafka = deployed_environment['kafka']
        cloud = deployed_environment['cloud']

        with timer("TEST 1: Data generation"):
            logger.info(f"\n{'='*70}")
            logger.info(f"TEST 1: Data generation for {cloud.upper()}")
            logger.info(f"{'='*70}\n")

            # Run data generator
            with timer("Data generator execution"):
                result = subprocess.run(
                    ["uv", "run", "lab3_datagen", "--local"],
                    cwd=PROJECT_ROOT,
                    timeout=60  # Should complete in < 30 seconds
                )

                assert result.returncode == 0, f"Data generation failed"

            # Validate record count via Kafka consumer
            with timer("Data validation (count >= 28,000)"):
                logger.info("Polling for ride_requests count >= 28,000...")

                def get_count():
                    try:
                        return kafka.get_topic_message_count("ride_requests", timeout=30, max_messages=30000)
                    except Exception as e:
                        logger.warning(f"Error getting count: {e}")
                        return 0

                count = poll_until(
                    getter=get_count,
                    condition=lambda c: c >= 28000,
                    timeout=120,  # 2 minutes max
                    interval=10,
                    description="ride_requests count >= 28,000"
                )

                logger.info(f"✅ ride_requests count: {count}")
                assert count >= 28000, f"Expected >= 28,000 records, got {count}"

    @pytest.mark.order(2)
    def test_anomaly_detection(self, deployed_environment):
        """Create anomaly detection table and validate 1-2 anomalies."""
        flink = deployed_environment['flink']
        kafka = deployed_environment['kafka']
        sql = deployed_environment['sql']

        with timer("TEST 2: Anomaly detection"):
            logger.info(f"\n{'='*70}")
            logger.info("TEST 2: Anomaly detection")
            logger.info(f"{'='*70}\n")

            # Execute CREATE TABLE anomalies_per_zone
            with timer("Create anomalies_per_zone table"):
                logger.info("Creating anomalies_per_zone table...")
                flink.execute_statement(
                    "test-anomalies-per-zone",
                    sql['anomalies_per_zone'],
                    wait=True
                )

                # Wait for statement to be RUNNING
                flink.wait_for_status(
                    "test-anomalies-per-zone",
                    ["RUNNING"],
                    timeout=120
                )

            # Wait for anomaly detection and check topic
            with timer("Anomaly detection (5-min window + processing)"):
                logger.info("Waiting for anomaly detection...")

                def get_anomalies():
                    try:
                        messages = kafka.consume_messages("anomalies_per_zone", max_messages=5, timeout=30)
                        return messages
                    except Exception as e:
                        logger.debug(f"Polling for anomalies: {e}")
                        return []

                rows = poll_until(
                    getter=get_anomalies,
                    condition=lambda r: len(r) >= 1,
                    timeout=360,  # 6 minutes (5-min window + 1-min processing)
                    interval=30,
                    description="anomalies_per_zone has >= 1 record"
                )

                logger.info(f"✅ Detected {len(rows)} anomaly/anomalies")
                assert 1 <= len(rows) <= 2, f"Expected 1-2 anomalies, got {len(rows)}"

    @pytest.mark.order(3)
    def test_rag_enrichment(self, deployed_environment):
        """Create enrichment table and validate no NULLs in key columns."""
        flink = deployed_environment['flink']
        kafka = deployed_environment['kafka']
        sql = deployed_environment['sql']

        with timer("TEST 3: RAG enrichment"):
            logger.info(f"\n{'='*70}")
            logger.info("TEST 3: RAG enrichment")
            logger.info(f"{'='*70}\n")

            # Execute CREATE TABLE anomalies_enriched
            with timer("Create anomalies_enriched table"):
                logger.info("Creating anomalies_enriched table...")
                flink.execute_statement(
                    "test-anomalies-enriched",
                    sql['anomalies_enriched'],
                    wait=True
                )

                # Wait for statement to be RUNNING
                flink.wait_for_status(
                    "test-anomalies-enriched",
                    ["RUNNING"],
                    timeout=120
                )

            # Wait for enrichment processing and check topic
            with timer("RAG enrichment processing"):
                logger.info("Waiting for enrichment...")

                def get_enriched():
                    try:
                        messages = kafka.consume_messages("anomalies_enriched", max_messages=5, timeout=30)
                        return messages
                    except Exception as e:
                        logger.debug(f"Polling for enriched anomalies: {e}")
                        return []

                rows = poll_until(
                    getter=get_enriched,
                    condition=lambda r: len(r) >= 1,
                    timeout=180,  # 3 minutes
                    interval=15,
                    description="anomalies_enriched has >= 1 record"
                )

            # Validate no NULLs in key columns
            with timer("Validate enrichment data"):
                logger.info(f"Validating {len(rows)} enriched record(s)...")
                for i, row in enumerate(rows):
                    # Check RAG enrichment column
                    anomaly_reason = row.get('anomaly_reason')
                    assert anomaly_reason is not None, \
                        f"Row {i}: anomaly_reason is NULL"
                    assert str(anomaly_reason).strip() != "", \
                        f"Row {i}: anomaly_reason is empty string"

                    # Check vector search columns
                    for col in ['top_chunk_1', 'top_chunk_2', 'top_chunk_3']:
                        assert row.get(col) is not None, \
                            f"Row {i}: {col} is NULL — vector search may have failed"

                logger.info("✅ All enrichment columns populated correctly")

    @pytest.mark.order(4)
    def test_agent_execution(self, deployed_environment):
        """Create agent tools, agent, and completed_actions. Validate successful dispatch."""
        flink = deployed_environment['flink']
        kafka = deployed_environment['kafka']
        sql = deployed_environment['sql']

        with timer("TEST 4: Agent execution"):
            logger.info(f"\n{'='*70}")
            logger.info("TEST 4: Agent execution")
            logger.info(f"{'='*70}\n")

            # Execute CREATE TOOL
            with timer("Create MCP tool"):
                logger.info("Creating MCP tool...")
                flink.execute_statement(
                    "test-create-tool",
                    sql['create_tool'],
                    wait=True
                )

            # Execute CREATE AGENT
            with timer("Create agent"):
                logger.info("Creating boat dispatch agent...")
                flink.execute_statement(
                    "test-create-agent",
                    sql['create_agent'],
                    wait=True
                )

            # Execute CREATE TABLE completed_actions
            with timer("Create completed_actions table"):
                logger.info("Creating completed_actions table...")
                flink.execute_statement(
                    "test-completed-actions",
                    sql['completed_actions'],
                    wait=True
                )

                # Wait for statement to be RUNNING
                flink.wait_for_status(
                    "test-completed-actions",
                    ["RUNNING"],
                    timeout=120
                )

            # Wait for agent to process and check topic
            with timer("Agent execution & validation"):
                logger.info("Waiting for agent execution...")

                def get_actions():
                    try:
                        messages = kafka.consume_messages("completed_actions", max_messages=5, timeout=30)
                        return messages
                    except Exception as e:
                        logger.debug(f"Polling for actions: {e}")
                        return []

                rows = poll_until(
                    getter=get_actions,
                    condition=lambda r: len(r) >= 1,
                    timeout=180,  # 3 minutes
                    interval=15,
                    description="completed_actions has >= 1 record"
                )

                logger.info(f"✅ Agent executed {len(rows)} action(s)")
                assert 1 <= len(rows) <= 2, f"Expected 1-2 actions, got {len(rows)}"

                # Validate dispatch results
                logger.info("Validating dispatch results...")
                for i, row in enumerate(rows):
                    # Check dispatch_summary doesn't indicate failure
                    summary = row.get('dispatch_summary', '')
                    assert summary is not None, f"Row {i}: dispatch_summary is NULL"

                    failure_phrases = [
                        "unable to dispatch",
                        "failed to",
                        "could not",
                        "error"
                    ]
                    for phrase in failure_phrases:
                        assert phrase.lower() not in str(summary).lower(), \
                            f"Row {i}: dispatch_summary contains failure indicator '{phrase}': {summary}"

                    # Check api_response is present (agent actually called the API)
                    api_response = row.get('api_response', '')
                    assert api_response is not None and str(api_response).strip() != "", \
                        f"Row {i}: api_response is NULL or empty — agent may not have executed the API call"

                logger.info("✅ Agent dispatch successful")
