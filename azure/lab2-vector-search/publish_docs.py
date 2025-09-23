#!/usr/bin/env python3
"""
Usage:
1. Set up virtual environment: cd ../../../ && uv venv && uv pip install -r requirements.txt
2. Run from this directory: ../../../.venv/bin/python publish_docs.py
"""
"""
Azure-specific wrapper script for publishing Flink docs to Kafka.

This script extracts credentials from Azure Terraform state and runs the main publisher.
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_terraform_output(state_path: Path) -> dict:
    """
    Run terraform output and return the results as a dictionary.

    Args:
        state_path: Path to the terraform state file

    Returns:
        Dictionary of terraform outputs
    """
    try:
        cmd = ["terraform", "output", "-json", f"-state={state_path}"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        outputs = json.loads(result.stdout)

        # Extract values from terraform output format
        return {key: value["value"] for key, value in outputs.items()}
    except subprocess.CalledProcessError as e:
        logger.error(f"Terraform output failed: {e.stderr}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse terraform output JSON: {e}")
        raise


def get_credentials():
    """Extract credentials from Terraform state files."""
    # Get current directory (should be the terraform/azure/lab2-vector-search directory)
    current_dir = Path(__file__).parent

    # Paths to state files
    local_state = current_dir / "terraform.tfstate"
    core_state = current_dir / "../core/terraform.tfstate"

    # Get outputs from local state
    logger.info("Extracting outputs from local Terraform state...")
    if local_state.exists():
        local_outputs = run_terraform_output(local_state)
        logger.info(f"Local outputs available: {list(local_outputs.keys())}")
    else:
        logger.warning(f"Local state file not found: {local_state}")
        local_outputs = {}

    # Get outputs from core state
    logger.info("Extracting outputs from core Terraform state...")
    if core_state.exists():
        core_outputs = run_terraform_output(core_state)
        logger.info(f"Core outputs available: {list(core_outputs.keys())}")
    else:
        logger.error(f"Core state file not found: {core_state}")
        sys.exit(1)

    # Extract required credentials
    try:
        credentials = {
            # Kafka connection details
            "bootstrap_servers": core_outputs[
                "confluent_kafka_cluster_bootstrap_endpoint"
            ],
            "kafka_api_key": core_outputs["app_manager_kafka_api_key"],
            "kafka_api_secret": core_outputs["app_manager_kafka_api_secret"],
            # Schema Registry details
            "schema_registry_url": core_outputs[
                "confluent_schema_registry_rest_endpoint"
            ],
            "schema_registry_api_key": core_outputs[
                "app_manager_schema_registry_api_key"
            ],
            "schema_registry_api_secret": core_outputs[
                "app_manager_schema_registry_api_secret"
            ],
            # Topic configuration
            "environment_name": core_outputs["confluent_environment_display_name"],
            "cluster_name": core_outputs["confluent_kafka_cluster_display_name"],
        }

        logger.info("Successfully extracted all required credentials")
        return credentials

    except KeyError as e:
        logger.error(f"Missing required output in Terraform state: {e}")
        logger.error("Available core outputs:")
        for key in sorted(core_outputs.keys()):
            logger.error(f"  - {key}")
        sys.exit(1)


def run_publisher(credentials: dict):
    """Run the main publisher script with extracted credentials."""
    # Path to the main publisher script
    main_script = (
        Path(__file__).parent / "../../../assets/lab2/flink_docs/publish_docs.py"
    )

    if not main_script.exists():
        logger.error(f"Main publisher script not found: {main_script}")
        sys.exit(1)

    # Set environment variables for the main script
    env = os.environ.copy()
    env.update(
        {
            "KAFKA_BOOTSTRAP_SERVERS": credentials["bootstrap_servers"],
            "KAFKA_API_KEY": credentials["kafka_api_key"],
            "KAFKA_API_SECRET": credentials["kafka_api_secret"],
            "SCHEMA_REGISTRY_URL": credentials["schema_registry_url"],
            "SCHEMA_REGISTRY_API_KEY": credentials["schema_registry_api_key"],
            "SCHEMA_REGISTRY_API_SECRET": credentials["schema_registry_api_secret"],
            "KAFKA_TOPIC": "documents",  # Use simple topic name as it exists
        }
    )

    logger.info(f"Running main publisher script: {main_script}")
    logger.info(
        f"Publishing to topic 'documents' in cluster '{credentials['cluster_name']}'"
    )

    try:
        # Use uv virtual environment python
        venv_python = Path(__file__).parent / "../../../.venv/bin/python"
        if not venv_python.exists():
            logger.error(f"Virtual environment python not found: {venv_python}")
            logger.error("Please run 'uv venv' from the project root directory")
            sys.exit(1)

        # Run the main script
        result = subprocess.run(
            [str(venv_python), str(main_script)], env=env, check=True
        )
        logger.info("Publisher completed successfully")
        return result.returncode
    except subprocess.CalledProcessError as e:
        logger.error(f"Publisher failed with exit code {e.returncode}")
        return e.returncode


def main():
    """Main function."""
    logger.info("Azure Flink Docs Publisher - Starting...")

    try:
        # Extract credentials from Terraform
        credentials = get_credentials()

        # Run the publisher
        exit_code = run_publisher(credentials)

        logger.info(
            f"Azure Flink Docs Publisher - Completed with exit code {exit_code}"
        )
        sys.exit(exit_code)

    except Exception as e:
        logger.error(f"Azure Flink Docs Publisher failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
