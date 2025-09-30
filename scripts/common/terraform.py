"""
Terraform utilities for credential extraction and state file handling.

Provides cross-platform functions for:
- Reading terraform state files from AWS/Azure deployments
- Extracting required credentials for Kafka and Schema Registry
- Validating terraform outputs and providing helpful error messages
"""

import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def run_terraform_output(state_path: Path) -> Dict[str, any]:
    """
    Run terraform output and return the results as a dictionary.

    Args:
        state_path: Path to the terraform state file

    Returns:
        Dictionary of terraform outputs

    Raises:
        subprocess.CalledProcessError: If terraform command fails
        json.JSONDecodeError: If output is not valid JSON
        FileNotFoundError: If terraform binary is not found
    """
    try:
        cmd = ["terraform", "output", "-json", f"-state={state_path}"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        outputs = json.loads(result.stdout)

        # Extract values from terraform output format
        return {key: value["value"] for key, value in outputs.items()}
    except FileNotFoundError:
        logger.error("Terraform binary not found. Please install terraform.")
        logger.error("Visit: https://developer.hashicorp.com/terraform/install")
        raise
    except subprocess.CalledProcessError as e:
        logger.error(f"Terraform output failed: {e.stderr}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse terraform output JSON: {e}")
        raise


def find_state_files(cloud_provider: str, base_dir: Path) -> Tuple[Path, Path]:
    """
    Find terraform state files for the given cloud provider.

    Args:
        cloud_provider: 'aws' or 'azure'
        base_dir: Base directory to search from (usually project root)

    Returns:
        Tuple of (core_state_path, local_state_path)

    Raises:
        FileNotFoundError: If required state files are not found
    """
    provider_dir = base_dir / cloud_provider
    core_state = provider_dir / "core" / "terraform.tfstate"
    local_state = provider_dir / "lab2-vector-search" / "terraform.tfstate"

    if not core_state.exists():
        logger.error(f"Core terraform state not found: {core_state}")
        logger.error(f"Please run 'terraform apply' in: {core_state.parent}")
        raise FileNotFoundError(f"Core state file not found: {core_state}")

    return core_state, local_state


def extract_kafka_credentials(
    cloud_provider: str, project_root: Optional[Path] = None
) -> Dict[str, str]:
    """
    Extract Kafka and Schema Registry credentials from terraform state.

    Args:
        cloud_provider: 'aws' or 'azure'
        project_root: Project root directory (defaults to auto-detection)

    Returns:
        Dictionary with all required credentials for Kafka connection

    Raises:
        FileNotFoundError: If state files or terraform binary not found
        KeyError: If required outputs are missing from state
        ValueError: If cloud_provider is not supported
    """
    if cloud_provider not in ["aws", "azure"]:
        raise ValueError(f"Unsupported cloud provider: {cloud_provider}")

    if project_root is None:
        project_root = Path(__file__).parent.parent.parent

    logger.info(f"Extracting {cloud_provider.upper()} credentials from terraform state...")

    # Find state files
    core_state, local_state = find_state_files(cloud_provider, project_root)

    # Get outputs from core state (required)
    logger.info("Reading core terraform state...")
    core_outputs = run_terraform_output(core_state)
    logger.info(f"Core outputs available: {sorted(core_outputs.keys())}")

    # Get outputs from local state (optional)
    local_outputs = {}
    if local_state.exists():
        logger.info("Reading local terraform state...")
        local_outputs = run_terraform_output(local_state)
        logger.info(f"Local outputs available: {sorted(local_outputs.keys())}")
    else:
        logger.warning(f"Local state file not found (optional): {local_state}")

    # Extract required credentials
    required_keys = {
        "confluent_kafka_cluster_bootstrap_endpoint": "bootstrap_servers",
        "app_manager_kafka_api_key": "kafka_api_key",
        "app_manager_kafka_api_secret": "kafka_api_secret",
        "confluent_schema_registry_rest_endpoint": "schema_registry_url",
        "app_manager_schema_registry_api_key": "schema_registry_api_key",
        "app_manager_schema_registry_api_secret": "schema_registry_api_secret",
        "confluent_environment_display_name": "environment_name",
        "confluent_kafka_cluster_display_name": "cluster_name",
        "confluent_environment_id": "environment_id",
        "confluent_kafka_cluster_id": "cluster_id",
    }

    credentials = {}
    missing_keys = []

    for tf_key, cred_key in required_keys.items():
        if tf_key in core_outputs:
            credentials[cred_key] = core_outputs[tf_key]
        elif tf_key in local_outputs:
            credentials[cred_key] = local_outputs[tf_key]
        else:
            missing_keys.append(tf_key)

    if missing_keys:
        logger.error(f"Missing required terraform outputs: {missing_keys}")
        logger.error("Available core outputs:")
        for key in sorted(core_outputs.keys()):
            logger.error(f"  - {key}")
        if local_outputs:
            logger.error("Available local outputs:")
            for key in sorted(local_outputs.keys()):
                logger.error(f"  - {key}")
        raise KeyError(f"Missing required terraform outputs: {missing_keys}")

    logger.info("Successfully extracted all required credentials")
    logger.info(
        f"Connecting to cluster '{credentials['cluster_name']}' "
        f"in environment '{credentials['environment_name']}'"
    )

    return credentials


def validate_terraform_state(cloud_provider: str, project_root: Optional[Path] = None) -> bool:
    """
    Validate that terraform state files exist and contain required outputs.

    Args:
        cloud_provider: 'aws' or 'azure'
        project_root: Project root directory (defaults to auto-detection)

    Returns:
        True if state is valid, False otherwise
    """
    try:
        extract_kafka_credentials(cloud_provider, project_root)
        return True
    except (FileNotFoundError, KeyError, ValueError) as e:
        logger.error(f"Terraform state validation failed: {e}")
        return False


def get_project_root() -> Path:
    """
    Find the project root directory by looking for pyproject.toml.

    Returns:
        Path to project root

    Raises:
        FileNotFoundError: If project root cannot be found
    """
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return parent

    raise FileNotFoundError(
        "Could not find project root (pyproject.toml not found in any parent directory)"
    )