"""Terraform state extraction utilities for tests."""

import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path to import existing scripts
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.common.terraform import (
    run_terraform_output,
    extract_kafka_credentials,
    get_project_root,
)


class TerraformHelper:
    """Helper for extracting Flink/Kafka connection parameters from terraform state."""

    def __init__(self, cloud_provider: str, project_root: Path = None):
        """Initialize helper.

        Args:
            cloud_provider: 'aws' or 'azure'
            project_root: Project root directory (auto-detected if None)
        """
        self.cloud_provider = cloud_provider
        self.project_root = project_root or get_project_root()

    def get_core_outputs(self) -> Dict[str, Any]:
        """Get all terraform outputs from core environment.

        Returns:
            Dictionary of all terraform outputs (environment_id, compute_pool_id, etc.)

        Raises:
            FileNotFoundError: If core terraform.tfstate not found
            subprocess.CalledProcessError: If terraform output command fails
        """
        core_state_path = self.project_root / "terraform" / "core" / "terraform.tfstate"
        return run_terraform_output(core_state_path)

    def get_lab3_outputs(self) -> Dict[str, Any]:
        """Get all terraform outputs from lab3 environment.

        Returns:
            Dictionary of all terraform outputs

        Raises:
            FileNotFoundError: If lab3 terraform.tfstate not found
        """
        lab3_state_path = (
            self.project_root / "terraform" / "lab3-agentic-fleet-management" / "terraform.tfstate"
        )
        return run_terraform_output(lab3_state_path)

    def get_flink_params(self) -> Dict[str, str]:
        """Extract Flink SQL execution parameters from terraform state.

        Returns:
            Dictionary with:
                - environment_id: Confluent environment ID
                - compute_pool_id: Flink compute pool ID
                - database: Kafka cluster name (used as Flink catalog database)
                - service_account_id: Flink service account ID
                - cloud: Cloud provider (aws/azure)
                - region: Cloud region

        Raises:
            FileNotFoundError: If terraform state files not found
            KeyError: If required outputs missing from state
        """
        core_outputs = self.get_core_outputs()

        return {
            "environment_id": core_outputs["confluent_environment_id"],
            "compute_pool_id": core_outputs["confluent_flink_compute_pool_id"],
            "database": core_outputs["confluent_kafka_cluster_display_name"],
            "service_account_id": core_outputs["app_manager_service_account_id"],
            "cloud": self.cloud_provider,
            "region": core_outputs.get("cloud_region", "us-east-1"),
        }

    def get_kafka_credentials(self) -> Dict[str, str]:
        """Extract Kafka connection credentials from terraform state.

        Returns:
            Dictionary with bootstrap_servers, api_key, api_secret, schema_registry_*, etc.

        Raises:
            FileNotFoundError: If state files not found
            KeyError: If required outputs missing
        """
        return extract_kafka_credentials(self.cloud_provider, self.project_root)
