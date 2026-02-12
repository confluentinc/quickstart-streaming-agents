"""Helper to detect if infrastructure is already deployed."""

import logging
from pathlib import Path
from typing import Dict, Optional

from testing.helpers.terraform_helper import TerraformHelper

logger = logging.getLogger(__name__)


def is_infrastructure_deployed(cloud: str, project_root: Path) -> bool:
    """Check if infrastructure is already deployed.

    Uses multi-level detection:
    1. Quick file checks (terraform state, API keys)
    2. Terraform state validation (outputs present)

    Args:
        cloud: Cloud provider ('aws' or 'azure')
        project_root: Project root directory

    Returns:
        True if infrastructure is deployed and valid, False otherwise
    """
    # Level 1: Quick file checks
    core_state = project_root / "terraform" / "core" / "terraform.tfstate"
    api_keys_file = project_root / f"API-KEYS-{cloud.upper()}.md"

    if not core_state.exists():
        logger.debug("No terraform state found - infrastructure not deployed")
        return False

    if not api_keys_file.exists():
        logger.debug("No API-KEYS file found - workshop keys not created")
        return False

    # Level 2: Terraform state validation
    try:
        tf_helper = TerraformHelper(cloud, project_root)
        outputs = tf_helper.get_core_outputs()

        # Check all required outputs are present
        required_outputs = [
            'confluent_environment_id',
            'confluent_flink_compute_pool_id',
            'confluent_kafka_cluster_display_name',
            'app_manager_service_account_id',
        ]

        missing = [k for k in required_outputs if k not in outputs]
        if missing:
            logger.warning(f"Terraform state incomplete - missing outputs: {missing}")
            return False

        logger.info("✅ Infrastructure detected: already deployed")
        return True

    except Exception as e:
        logger.debug(f"Infrastructure validation failed: {e}")
        return False


def get_deployment_info(cloud: str, project_root: Path) -> Optional[Dict]:
    """Get information about existing deployment.

    Returns deployment details if infrastructure is deployed, None otherwise.
    """
    if not is_infrastructure_deployed(cloud, project_root):
        return None

    try:
        tf_helper = TerraformHelper(cloud, project_root)
        outputs = tf_helper.get_core_outputs()

        return {
            'cloud': cloud,
            'environment_id': outputs.get('confluent_environment_id'),
            'compute_pool_id': outputs.get('confluent_flink_compute_pool_id'),
            'kafka_cluster': outputs.get('confluent_kafka_cluster_display_name'),
            'region': outputs.get('cloud_region', 'us-east-1'),
        }
    except Exception:
        return None
