"""Flink SQL execution via Confluent CLI for test validation."""

import subprocess
import json
import re
import time
from typing import List, Dict, Any, Optional


class FlinkSQLHelper:
    """Helper for executing Flink SQL via confluent CLI commands."""

    def __init__(
        self,
        environment_id: str,
        compute_pool_id: str,
        cloud: str,
        region: str,
        database: str,
        service_account_id: str,
    ):
        """Initialize Flink SQL helper.

        Args:
            environment_id: Confluent environment ID
            compute_pool_id: Flink compute pool ID
            cloud: Cloud provider ('aws' or 'azure')
            region: Cloud region
            database: Kafka cluster name (Flink catalog database)
            service_account_id: Flink service account ID
        """
        self.environment_id = environment_id
        self.compute_pool_id = compute_pool_id
        self.cloud = cloud
        self.region = region
        self.database = database
        self.service_account_id = service_account_id
        self.created_statements = []  # Track for cleanup

    def execute_statement(
        self, name: str, sql: str, wait: bool = True
    ) -> str:
        """Execute a Flink SQL statement via confluent CLI.

        Args:
            name: Unique name for the statement (alphanumeric + hyphens)
            sql: SQL statement to execute
            wait: Whether to wait for statement to complete (default: True)

        Returns:
            Statement name

        Raises:
            subprocess.CalledProcessError: If confluent command fails
        """
        cmd = [
            "confluent",
            "flink",
            "statement",
            "create",
            name,
            "--sql",
            sql,
            "--compute-pool",
            self.compute_pool_id,
            "--environment",
            self.environment_id,
            "--cloud",
            self.cloud,
            "--region",
            self.region,
            "--database",
            self.database,
            "--service-account",
            self.service_account_id,
        ]

        if wait:
            cmd.append("--wait")

        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True
        )

        # Track for cleanup
        self.created_statements.append(name)

        return name

    def get_statement_status(self, name: str) -> str:
        """Get statement status via confluent CLI.

        Args:
            name: Statement name

        Returns:
            Status string: PENDING, RUNNING, COMPLETED, FAILING, FAILED, STOPPED, DEGRADED

        Raises:
            subprocess.CalledProcessError: If confluent command fails
        """
        cmd = [
            "confluent",
            "flink",
            "statement",
            "describe",
            name,
            "--environment",
            self.environment_id,
            "--cloud",
            self.cloud,
            "--region",
            self.region,
            "-o",
            "json",
        ]

        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True
        )

        # Parse JSON output to get status
        output = json.loads(result.stdout)
        return output.get("status", "UNKNOWN")

    def wait_for_status(
        self,
        name: str,
        target_statuses: List[str],
        timeout: int = 300,
        interval: int = 5,
    ) -> str:
        """Poll statement until it reaches target status or timeout.

        Args:
            name: Statement name
            target_statuses: List of acceptable status values (e.g., ['RUNNING', 'COMPLETED'])
            timeout: Maximum time to wait in seconds (default: 300)
            interval: Poll interval in seconds (default: 5)

        Returns:
            Final status when condition met

        Raises:
            TimeoutError: If timeout reached before target status
        """
        start_time = time.time()

        while True:
            status = self.get_statement_status(name)

            if status in target_statuses:
                return status

            # Check for failure states
            if status in ["FAILED", "STOPPED"]:
                raise RuntimeError(
                    f"Statement {name} reached terminal failure state: {status}"
                )

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Timeout waiting for {name} to reach {target_statuses} "
                    f"after {elapsed:.1f}s. Current status: {status}"
                )

            time.sleep(interval)

    def query_results(
        self, sql: str, timeout: int = 300
    ) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return parsed results.

        NOTE: Confluent CLI doesn't provide easy programmatic access to SELECT results.
        This is a placeholder - actual implementation would need to use:
        1. Confluent Flink REST API directly
        2. Kafka consumer to read from result topics
        3. Or accept that we can only validate continuous jobs are RUNNING

        For now, this raises NotImplementedError.

        Args:
            sql: SELECT query to execute
            timeout: Maximum time to wait for results in seconds (default: 300)

        Returns:
            List of row dictionaries with column names as keys

        Raises:
            NotImplementedError: This method needs proper implementation
        """
        raise NotImplementedError(
            "query_results() requires Flink REST API or Kafka consumer. "
            "Use validate_topic_count() or check_statement_running() instead."
        )

    def delete_statement(self, name: str):
        """Delete a Flink statement via confluent CLI.

        Args:
            name: Statement name to delete

        Raises:
            subprocess.CalledProcessError: If delete fails
        """
        cmd = [
            "confluent",
            "flink",
            "statement",
            "delete",
            name,
            "--environment",
            self.environment_id,
            "--cloud",
            self.cloud,
            "--region",
            self.region,
            "--force",
        ]

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            # Remove from tracked statements
            if name in self.created_statements:
                self.created_statements.remove(name)
        except subprocess.CalledProcessError:
            # Ignore errors on cleanup - statement may already be deleted
            pass

    def check_statement_running(self, name: str) -> bool:
        """Check if a statement is in RUNNING state.

        Args:
            name: Statement name

        Returns:
            True if statement is RUNNING, False otherwise
        """
        try:
            status = self.get_statement_status(name)
            return status == "RUNNING"
        except Exception:
            return False

    def cleanup_all(self):
        """Delete all statements created by this helper (for teardown).

        Continues even if individual deletes fail.
        """
        for name in list(self.created_statements):
            try:
                self.delete_statement(name)
            except Exception:
                # Continue cleanup even if some fail
                pass
