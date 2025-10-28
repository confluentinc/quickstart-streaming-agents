"""
Terraform variables file (terraform.tfvars) management utilities.

Provides functions for:
- Writing terraform.tfvars files with automatic backup
- Generating formatted tfvars content for core and lab modules
- Orchestrating tfvars file creation across multiple environments
"""

import shutil
from pathlib import Path
from typing import Dict, Optional


def get_credential_value(creds: Dict[str, str], key: str) -> Optional[str]:
    """
    Get credential value, checking both TF_VAR_ prefixed and non-prefixed keys.

    Args:
        creds: Dictionary of credentials
        key: Key to look up (without TF_VAR_ prefix)

    Returns:
        Value if found, None otherwise
    """
    return creds.get(key) or creds.get(f"TF_VAR_{key}")


def write_tfvars_file(tfvars_path: Path, content: str) -> bool:
    """
    Write terraform.tfvars file with backup of existing file.

    Args:
        tfvars_path: Path to terraform.tfvars file
        content: Content to write

    Returns:
        True if successful, False otherwise
    """
    try:
        # Backup existing file
        if tfvars_path.exists():
            backup_path = tfvars_path.with_suffix(".tfvars.backup")
            shutil.copy2(tfvars_path, backup_path)

        # Ensure parent directory exists
        tfvars_path.parent.mkdir(parents=True, exist_ok=True)

        # Write new content
        with open(tfvars_path, 'w') as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"Error writing {tfvars_path}: {e}")
        return False


def generate_core_tfvars_content(
    cloud: str,
    region: str,
    api_key: str,
    api_secret: str,
    azure_sub_id: Optional[str] = None,
    owner_email: Optional[str] = None
) -> str:
    """
    Generate terraform.tfvars content for Core module.

    Args:
        cloud: Cloud provider (aws or azure)
        region: Cloud region
        api_key: Confluent Cloud API key
        api_secret: Confluent Cloud API secret
        azure_sub_id: Azure subscription ID (required for Azure)
        owner_email: Owner email for resource tagging (optional)

    Returns:
        Formatted terraform.tfvars content
    """
    content = f"""# Core Infrastructure Configuration
cloud_region = "{region}"
confluent_cloud_api_key = "{api_key}"
confluent_cloud_api_secret = "{api_secret}"
"""

    if owner_email:
        content += f'owner_email = "{owner_email}"\n'

    if cloud == "azure" and azure_sub_id:
        content += f'azure_subscription_id = "{azure_sub_id}"\n'

    return content


def generate_lab1_tfvars_content(zapier_endpoint: str) -> str:
    """
    Generate terraform.tfvars content for Lab1 module.

    Note: cloud_region is inherited from core via terraform_remote_state,
    so we don't include it here to avoid redundancy.

    Args:
        zapier_endpoint: Zapier MCP SSE endpoint URL

    Returns:
        Formatted terraform.tfvars content
    """
    return f"""# Lab1 Configuration
zapier_sse_endpoint = "{zapier_endpoint}"
"""


def generate_lab2_tfvars_content(
    mongo_conn: str,
    mongo_user: str,
    mongo_pass: str
) -> str:
    """
    Generate terraform.tfvars content for Lab2 module.

    Note: cloud_region is inherited from core via terraform_remote_state.
    MongoDB database, collection, and index settings use defaults defined
    in variables.tf, so we don't override them here.

    Args:
        mongo_conn: MongoDB connection string
        mongo_user: MongoDB username
        mongo_pass: MongoDB password

    Returns:
        Formatted terraform.tfvars content
    """
    return f"""# Lab2 Configuration
mongodb_connection_string = "{mongo_conn}"
mongodb_username = "{mongo_user}"
mongodb_password = "{mongo_pass}"
"""


def write_tfvars_for_deployment(
    root: Path,
    cloud: str,
    region: str,
    creds: Dict[str, str],
    envs_to_deploy: list
) -> None:
    """
    Write terraform.tfvars files for all environments being deployed.

    Args:
        root: Project root directory
        cloud: Cloud provider (aws or azure)
        region: Cloud region
        creds: Credentials dictionary (supports both TF_VAR_ prefixed and non-prefixed keys)
        envs_to_deploy: List of environments to deploy (core, lab1-tool-calling, lab2-vector-search)
    """
    # Core terraform.tfvars
    if "core" in envs_to_deploy:
        api_key = get_credential_value(creds, "confluent_cloud_api_key")
        api_secret = get_credential_value(creds, "confluent_cloud_api_secret")
        azure_sub_id = get_credential_value(creds, "azure_subscription_id") if cloud == "azure" else None
        owner_email = get_credential_value(creds, "owner_email")

        if api_key and api_secret:
            core_tfvars_path = root / cloud / "core" / "terraform.tfvars"
            content = generate_core_tfvars_content(cloud, region, api_key, api_secret, azure_sub_id, owner_email)
            if write_tfvars_file(core_tfvars_path, content):
                print(f"✓ Wrote {core_tfvars_path}")

    # Lab1 terraform.tfvars
    if "lab1-tool-calling" in envs_to_deploy:
        zapier_endpoint = get_credential_value(creds, "zapier_sse_endpoint")
        if zapier_endpoint:
            lab1_tfvars_path = root / cloud / "lab1-tool-calling" / "terraform.tfvars"
            content = generate_lab1_tfvars_content(zapier_endpoint)
            if write_tfvars_file(lab1_tfvars_path, content):
                print(f"✓ Wrote {lab1_tfvars_path}")

    # Lab2 terraform.tfvars
    if "lab2-vector-search" in envs_to_deploy:
        mongo_conn = get_credential_value(creds, "mongodb_connection_string")
        mongo_user = get_credential_value(creds, "mongodb_username")
        mongo_pass = get_credential_value(creds, "mongodb_password")

        if mongo_conn and mongo_user and mongo_pass:
            lab2_tfvars_path = root / cloud / "lab2-vector-search" / "terraform.tfvars"
            content = generate_lab2_tfvars_content(mongo_conn, mongo_user, mongo_pass)
            if write_tfvars_file(lab2_tfvars_path, content):
                print(f"✓ Wrote {lab2_tfvars_path}")
