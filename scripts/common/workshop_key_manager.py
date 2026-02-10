#!/usr/bin/env python3
"""
Unified Workshop Key Manager - Create and manage AWS/Azure credentials for workshop mode.

This script helps workshop organizers create properly-scoped credentials for participants
to use AI models without requiring full cloud infrastructure permissions.

Usage:
    uv run workshop-keys create           # Interactive cloud selection
    uv run workshop-keys create aws       # Create AWS Bedrock credentials
    uv run workshop-keys create azure     # Create Azure OpenAI credentials
    uv run workshop-keys destroy          # Interactive cloud selection
    uv run workshop-keys destroy aws      # Destroy AWS credentials
    uv run workshop-keys destroy azure    # Destroy Azure credentials

    # With options:
    uv run workshop-keys create aws --verbose
    uv run workshop-keys destroy azure --keep-resource-group

Examples:
    # Day before workshop - interactive
    uv run workshop-keys create
    # → Prompts for AWS or Azure, then creates credentials

    # Day before workshop - direct
    uv run workshop-keys create aws
    # → Creates WORKSHOP_KEYS_AWS.md

    uv run workshop-keys create azure
    # → Creates WORKSHOP_CREDENTIALS_AZURE.md

    # After workshop - interactive
    uv run workshop-keys destroy
    # → Prompts for AWS or Azure, then destroys credentials

    # After workshop - direct
    uv run workshop-keys destroy aws
    uv run workshop-keys destroy azure
"""

import argparse
import json
import logging
import random
import string
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

# AWS imports
try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

# Azure imports
try:
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
    from azure.mgmt.cognitiveservices.models import (
        Account,
        AccountProperties,
        Deployment,
        DeploymentModel,
        DeploymentProperties,
        Sku as CognitiveServicesSku,
    )
    from azure.mgmt.resource import ResourceManagementClient
    from azure.mgmt.resource.resources.models import ResourceGroup
    from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
    AZURE_SDK_AVAILABLE = True
except ImportError:
    AZURE_SDK_AVAILABLE = False

from dotenv import dotenv_values, set_key

from .terraform import get_project_root
from .ui import prompt_choice, prompt_with_default


# ============================================================================
# CONSTANTS
# ============================================================================

PROJECT_URL = "https://github.com/confluentinc/quickstart-streaming-agents"

# AWS Constants
AWS_IAM_USERNAME = "workshop-bedrock-user"
AWS_POLICY_NAME = "BedrockInvokeOnly"
AWS_STATE_FILE = ".workshop-keys-state-aws.json"
AWS_CREDENTIALS_FILE = "WORKSHOP_KEYS_AWS.md"

# Azure Constants
AZURE_RESOURCE_GROUP_PREFIX = "rg-workshop-openai"
AZURE_COGNITIVE_ACCOUNT_PREFIX = "workshop-openai"
AZURE_STATE_FILE = ".workshop-keys-state-azure.json"
AZURE_CREDENTIALS_FILE = "WORKSHOP_CREDENTIALS_AZURE.md"

# Azure model deployment configurations
AZURE_DEPLOYMENTS = {
    "gpt-5-mini": {
        "model": "gpt-5-mini",
        "version": "2025-08-07",
        "capacity": 50
    },
    "text-embedding-ada-002": {
        "model": "text-embedding-ada-002",
        "version": "2",
        "capacity": 120
    }
}


# ============================================================================
# COMMON UTILITIES
# ============================================================================

def setup_logging(verbose: bool = False) -> logging.Logger:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Suppress verbose Azure SDK logging unless --verbose is used
    if not verbose:
        # Suppress Azure HTTP request/response logging
        logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
        logging.getLogger("azure.identity").setLevel(logging.WARNING)
        logging.getLogger("azure.mgmt").setLevel(logging.WARNING)
        # Suppress urllib3 connection pool messages
        logging.getLogger("urllib3").setLevel(logging.WARNING)

    return logging.getLogger(__name__)


def get_tags(project_root: Path, owner_email: str) -> Dict[str, str]:
    """Build resource tags matching Terraform pattern."""
    return {
        "Owner": owner_email,
        "Project": PROJECT_URL,
        "Environment": "workshop",
        "ManagedBy": "workshop-key-manager",
        "LocalPath": str(project_root)
    }


def get_owner_email(project_root: Path) -> str:
    """Get owner email from credentials.env or prompt user."""
    creds_file = project_root / "credentials.env"

    # Try to load from credentials.env
    if creds_file.exists():
        creds = dotenv_values(creds_file)
        if "TF_VAR_owner_email" in creds and creds["TF_VAR_owner_email"]:
            return creds["TF_VAR_owner_email"].strip("'\"")

    # Prompt user
    return prompt_with_default(
        "Enter owner email (for resource tagging)",
        default=""
    )


def prompt_cloud_provider() -> str:
    """Prompt user to select cloud provider."""
    print("\n" + "=" * 70)
    print("WORKSHOP KEY MANAGER")
    print("=" * 70)
    print("\nSelect cloud provider for workshop credentials:")

    choice = prompt_choice(
        "Cloud Provider",
        ["AWS (Bedrock)", "Azure (OpenAI)"]
    )

    if "AWS" in choice:
        return "aws"
    else:
        return "azure"


# ============================================================================
# AWS-SPECIFIC FUNCTIONS
# ============================================================================

def get_bedrock_policy() -> Dict:
    """Get the IAM policy document for Bedrock model invocation."""
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                "Resource": "*"
            }
        ]
    }


def get_aws_region(project_root: Path) -> str:
    """Get AWS region from credentials.env or prompt user."""
    creds_file = project_root / "credentials.env"

    # Try to load from credentials.env
    if creds_file.exists():
        creds = dotenv_values(creds_file)
        if "TF_VAR_cloud_region" in creds and creds["TF_VAR_cloud_region"]:
            return creds["TF_VAR_cloud_region"].strip("'\"")

    # Prompt user with common defaults
    print("\nSelect AWS region:")
    regions = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]
    return prompt_choice("AWS Region", regions)


def create_or_get_iam_user(iam_client, tags: Dict[str, str], logger: logging.Logger) -> bool:
    """Create IAM user if it doesn't exist, or get existing user."""
    try:
        # Check if user exists
        iam_client.get_user(UserName=AWS_IAM_USERNAME)
        logger.info(f"IAM user '{AWS_IAM_USERNAME}' already exists")
        return False
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            # User doesn't exist, create it
            logger.info(f"Creating IAM user '{AWS_IAM_USERNAME}'...")
            tag_list = [{"Key": k, "Value": v} for k, v in tags.items()]
            iam_client.create_user(
                UserName=AWS_IAM_USERNAME,
                Tags=tag_list
            )
            logger.info(f"✓ Created IAM user '{AWS_IAM_USERNAME}'")
            return True
        else:
            raise


def attach_bedrock_policy(iam_client, logger: logging.Logger) -> None:
    """Attach inline Bedrock policy to IAM user."""
    logger.info(f"Attaching Bedrock policy '{AWS_POLICY_NAME}'...")

    policy_doc = get_bedrock_policy()

    iam_client.put_user_policy(
        UserName=AWS_IAM_USERNAME,
        PolicyName=AWS_POLICY_NAME,
        PolicyDocument=json.dumps(policy_doc)
    )

    logger.info(f"✓ Attached inline policy '{AWS_POLICY_NAME}'")


def create_access_key(iam_client, logger: logging.Logger) -> Tuple[str, str]:
    """Create new access key for IAM user."""
    # Check existing keys
    response = iam_client.list_access_keys(UserName=AWS_IAM_USERNAME)
    existing_keys = response.get('AccessKeyMetadata', [])

    if len(existing_keys) >= 2:
        raise Exception(
            f"User '{AWS_IAM_USERNAME}' already has 2 access keys (AWS limit). "
            f"Please delete an old key before creating a new one."
        )

    logger.info("Generating new access key...")

    response = iam_client.create_access_key(UserName=AWS_IAM_USERNAME)
    access_key = response['AccessKey']

    access_key_id = access_key['AccessKeyId']
    secret_access_key = access_key['SecretAccessKey']

    logger.info(f"✓ Created access key: {access_key_id}")

    return access_key_id, secret_access_key


def test_bedrock_credentials(
    access_key_id: str,
    secret_access_key: str,
    region: str,
    logger: logging.Logger
) -> bool:
    """Test AWS Bedrock credentials."""
    from .test_bedrock_credentials import test_bedrock_credentials as test_func

    logger.info("Testing Bedrock access with Claude Sonnet 4.5...")

    return test_func(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        region=region,
        logger=logger
    )


def save_aws_state(
    project_root: Path,
    access_key_id: str,
    owner_email: str,
    region: str,
    logger: logging.Logger
) -> None:
    """Save AWS state information for destroy command."""
    state_file = project_root / AWS_STATE_FILE

    state = {
        "iam_username": AWS_IAM_USERNAME,
        "policy_name": AWS_POLICY_NAME,
        "access_key_id": access_key_id,
        "owner_email": owner_email,
        "region": region,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    logger.debug(f"Saved state to {state_file}")


def save_aws_credentials_file(
    project_root: Path,
    access_key_id: str,
    secret_access_key: str,
    region: str,
    tags: Dict[str, str],
    logger: logging.Logger
) -> None:
    """Save AWS credentials to markdown file with usage instructions."""
    creds_file = project_root / AWS_CREDENTIALS_FILE

    # Format tags for display (exclude LocalPath as it's not useful for workshop participants)
    tags_display = "\n".join([f"**{key}:** `{value}`" for key, value in tags.items() if key != "LocalPath"])

    content = f"""# Workshop Credentials (AWS)

## AWS Bedrock Access Keys

Use these credentials when running `uv run deploy`:

```
AWS Access Key ID:     {access_key_id}
AWS Secret Access Key: {secret_access_key}
```

## Usage Instructions

### For Workshop Participants

1. Clone the repository:
   ```bash
   git clone https://github.com/confluentinc/quickstart-streaming-agents
   cd quickstart-streaming-agents
   ```

2. Run deployment:
   ```bash
   uv run deploy
   ```

3. When prompted, enter the credentials above:
   - AWS Bedrock Access Key: `{access_key_id}`
   - AWS Bedrock Secret Key: `{secret_access_key}`

## Security Notes

- **Do NOT commit these credentials to Git**
- These keys have minimal permissions (Bedrock model invocation only)
- Keys should be revoked immediately after the workshop
- Each participant will use the same shared credentials

## After Workshop (For Organizers)

To revoke these credentials, run:

```bash
uv run workshop-keys destroy
```

Or delete the IAM user directly with AWS CLI:

```bash
# Delete IAM user directly in AWS (must remove all dependencies first)
aws iam delete-access-key --user-name {AWS_IAM_USERNAME} --access-key-id {access_key_id}
aws iam delete-user-policy --user-name {AWS_IAM_USERNAME} --policy-name {AWS_POLICY_NAME}
aws iam delete-user --user-name {AWS_IAM_USERNAME}
```

The workshop-keys destroy command will:
1. Delete the access key `{access_key_id}`
2. Ask if you want to delete the IAM user (for reuse in future workshops)
3. Clean up state files

---

## Resource Details

**IAM User:** `{AWS_IAM_USERNAME}`
**Region:** `{region}`
**Policy:** `{AWS_POLICY_NAME}` (inline policy)
**Permissions:** `bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream`

**Tags:**
{tags_display}

**Created:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""

    with open(creds_file, 'w') as f:
        f.write(content)

    logger.info(f"✓ Saved credentials to {creds_file}")


def load_aws_state(project_root: Path) -> Optional[Dict]:
    """Load AWS state from previous create command."""
    state_file = project_root / AWS_STATE_FILE

    if not state_file.exists():
        return None

    with open(state_file, 'r') as f:
        return json.load(f)


def cleanup_user_dependencies(
    iam_client,
    username: str,
    logger: logging.Logger
) -> Tuple[bool, Optional[str]]:
    """Comprehensively clean up all IAM user dependencies before deletion."""
    errors = []

    # 1. Remove from all groups
    try:
        response = iam_client.list_groups_for_user(UserName=username)
        groups = response.get('Groups', [])
        if groups:
            for group in groups:
                group_name = group['GroupName']
                try:
                    iam_client.remove_user_from_group(
                        UserName=username,
                        GroupName=group_name
                    )
                    logger.debug(f"  Removed from group '{group_name}'")
                except ClientError as e:
                    if e.response['Error']['Code'] != 'NoSuchEntity':
                        error_msg = f"Failed to remove from group '{group_name}': {e.response['Error']['Code']}"
                        errors.append(error_msg)
                        logger.error(f"  ✗ {error_msg}")
            if not errors:
                logger.info(f"✓ Removed user from {len(groups)} group(s)")
        else:
            logger.info("✓ No groups to remove")
    except ClientError as e:
        error_msg = f"Failed to list groups: {e.response['Error']['Code']}"
        errors.append(error_msg)
        logger.error(f"✗ {error_msg}")

    # 2. Delete all access keys
    try:
        response = iam_client.list_access_keys(UserName=username)
        keys = response.get('AccessKeyMetadata', [])
        if keys:
            for key in keys:
                key_id = key['AccessKeyId']
                try:
                    iam_client.delete_access_key(
                        UserName=username,
                        AccessKeyId=key_id
                    )
                    logger.debug(f"  Deleted access key {key_id}")
                except ClientError as e:
                    if e.response['Error']['Code'] != 'NoSuchEntity':
                        error_msg = f"Failed to delete access key {key_id}: {e.response['Error']['Code']}"
                        errors.append(error_msg)
                        logger.error(f"  ✗ {error_msg}")
            if not errors or len(errors) < len(keys):
                logger.info(f"✓ Deleted {len(keys)} access key(s)")
        else:
            logger.info("✓ No access keys to delete")
    except ClientError as e:
        error_msg = f"Failed to list access keys: {e.response['Error']['Code']}"
        errors.append(error_msg)
        logger.error(f"✗ {error_msg}")

    # 3. Detach all managed policies
    try:
        response = iam_client.list_attached_user_policies(UserName=username)
        policies = response.get('AttachedPolicies', [])
        if policies:
            for policy in policies:
                policy_arn = policy['PolicyArn']
                try:
                    iam_client.detach_user_policy(
                        UserName=username,
                        PolicyArn=policy_arn
                    )
                    logger.debug(f"  Detached policy {policy_arn}")
                except ClientError as e:
                    if e.response['Error']['Code'] != 'NoSuchEntity':
                        error_msg = f"Failed to detach policy {policy_arn}: {e.response['Error']['Code']}"
                        errors.append(error_msg)
                        logger.error(f"  ✗ {error_msg}")
            if not errors or len(errors) < len(policies):
                logger.info(f"✓ Detached {len(policies)} managed policy/policies")
        else:
            logger.info("✓ No managed policies to detach")
    except ClientError as e:
        error_msg = f"Failed to list managed policies: {e.response['Error']['Code']}"
        errors.append(error_msg)
        logger.error(f"✗ {error_msg}")

    # 4. Delete all inline policies
    try:
        response = iam_client.list_user_policies(UserName=username)
        policy_names = response.get('PolicyNames', [])
        if policy_names:
            for policy_name in policy_names:
                try:
                    iam_client.delete_user_policy(
                        UserName=username,
                        PolicyName=policy_name
                    )
                    logger.debug(f"  Deleted inline policy '{policy_name}'")
                except ClientError as e:
                    if e.response['Error']['Code'] != 'NoSuchEntity':
                        error_msg = f"Failed to delete inline policy '{policy_name}': {e.response['Error']['Code']}"
                        errors.append(error_msg)
                        logger.error(f"  ✗ {error_msg}")
            if not errors or len(errors) < len(policy_names):
                logger.info(f"✓ Deleted {len(policy_names)} inline policy/policies")
        else:
            logger.info("✓ No inline policies to delete")
    except ClientError as e:
        error_msg = f"Failed to list inline policies: {e.response['Error']['Code']}"
        errors.append(error_msg)
        logger.error(f"✗ {error_msg}")

    # 5. Delete login profile
    try:
        iam_client.delete_login_profile(UserName=username)
        logger.info("✓ Deleted login profile")
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            logger.info("✓ No login profile to delete")
        else:
            error_msg = f"Failed to delete login profile: {e.response['Error']['Code']}"
            errors.append(error_msg)
            logger.error(f"✗ {error_msg}")

    # 6. Deactivate/delete MFA devices
    try:
        response = iam_client.list_mfa_devices(UserName=username)
        devices = response.get('MFADevices', [])
        if devices:
            for device in devices:
                serial = device['SerialNumber']
                try:
                    iam_client.deactivate_mfa_device(
                        UserName=username,
                        SerialNumber=serial
                    )
                    logger.debug(f"  Deactivated MFA device {serial}")

                    if ':mfa/' in serial:
                        try:
                            iam_client.delete_virtual_mfa_device(SerialNumber=serial)
                            logger.debug(f"  Deleted virtual MFA device {serial}")
                        except ClientError as e:
                            if e.response['Error']['Code'] != 'NoSuchEntity':
                                logger.warning(f"  Could not delete virtual MFA device: {e.response['Error']['Code']}")
                except ClientError as e:
                    if e.response['Error']['Code'] != 'NoSuchEntity':
                        error_msg = f"Failed to deactivate MFA device {serial}: {e.response['Error']['Code']}"
                        errors.append(error_msg)
                        logger.error(f"  ✗ {error_msg}")
            if not errors or len(errors) < len(devices):
                logger.info(f"✓ Deactivated {len(devices)} MFA device(s)")
        else:
            logger.info("✓ No MFA devices to deactivate")
    except ClientError as e:
        error_msg = f"Failed to list MFA devices: {e.response['Error']['Code']}"
        errors.append(error_msg)
        logger.error(f"✗ {error_msg}")

    # 7. Delete SSH public keys
    try:
        response = iam_client.list_ssh_public_keys(UserName=username)
        keys = response.get('SSHPublicKeys', [])
        if keys:
            for key in keys:
                key_id = key['SSHPublicKeyId']
                try:
                    iam_client.delete_ssh_public_key(
                        UserName=username,
                        SSHPublicKeyId=key_id
                    )
                    logger.debug(f"  Deleted SSH key {key_id}")
                except ClientError as e:
                    if e.response['Error']['Code'] != 'NoSuchEntity':
                        error_msg = f"Failed to delete SSH key {key_id}: {e.response['Error']['Code']}"
                        errors.append(error_msg)
                        logger.error(f"  ✗ {error_msg}")
            if not errors or len(errors) < len(keys):
                logger.info(f"✓ Deleted {len(keys)} SSH key(s)")
        else:
            logger.info("✓ No SSH keys to delete")
    except ClientError as e:
        error_msg = f"Failed to list SSH keys: {e.response['Error']['Code']}"
        errors.append(error_msg)
        logger.error(f"✗ {error_msg}")

    # 8. Delete signing certificates
    try:
        response = iam_client.list_signing_certificates(UserName=username)
        certs = response.get('Certificates', [])
        if certs:
            for cert in certs:
                cert_id = cert['CertificateId']
                try:
                    iam_client.delete_signing_certificate(
                        UserName=username,
                        CertificateId=cert_id
                    )
                    logger.debug(f"  Deleted signing certificate {cert_id}")
                except ClientError as e:
                    if e.response['Error']['Code'] != 'NoSuchEntity':
                        error_msg = f"Failed to delete certificate {cert_id}: {e.response['Error']['Code']}"
                        errors.append(error_msg)
                        logger.error(f"  ✗ {error_msg}")
            if not errors or len(errors) < len(certs):
                logger.info(f"✓ Deleted {len(certs)} signing certificate(s)")
        else:
            logger.info("✓ No signing certificates to delete")
    except ClientError as e:
        error_msg = f"Failed to list signing certificates: {e.response['Error']['Code']}"
        errors.append(error_msg)
        logger.error(f"✗ {error_msg}")

    # 9. Delete service-specific credentials
    try:
        response = iam_client.list_service_specific_credentials(UserName=username)
        creds = response.get('ServiceSpecificCredentials', [])
        if creds:
            for cred in creds:
                cred_id = cred['ServiceSpecificCredentialId']
                service_name = cred['ServiceName']
                try:
                    iam_client.delete_service_specific_credential(
                        UserName=username,
                        ServiceSpecificCredentialId=cred_id
                    )
                    logger.debug(f"  Deleted {service_name} credential {cred_id}")
                except ClientError as e:
                    if e.response['Error']['Code'] != 'NoSuchEntity':
                        error_msg = f"Failed to delete {service_name} credential: {e.response['Error']['Code']}"
                        errors.append(error_msg)
                        logger.error(f"  ✗ {error_msg}")
            if not errors or len(errors) < len(creds):
                logger.info(f"✓ Deleted {len(creds)} service-specific credential(s)")
        else:
            logger.info("✓ No service-specific credentials to delete")
    except ClientError as e:
        error_msg = f"Failed to list service-specific credentials: {e.response['Error']['Code']}"
        errors.append(error_msg)
        logger.error(f"✗ {error_msg}")

    # 10. Delete permission boundary
    try:
        iam_client.delete_user_permissions_boundary(UserName=username)
        logger.info("✓ Deleted permission boundary")
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            logger.info("✓ No permission boundary to delete")
        else:
            error_msg = f"Failed to delete permission boundary: {e.response['Error']['Code']}"
            errors.append(error_msg)
            logger.error(f"✗ {error_msg}")

    # Return results
    if errors:
        error_details = "Encountered the following errors during cleanup:\n\n"
        for i, error in enumerate(errors, 1):
            error_details += f"{i}. {error}\n"
        error_details += f"\nUser '{username}' could not be fully cleaned up."
        return False, error_details
    else:
        return True, None


# ============================================================================
# AZURE-SPECIFIC FUNCTIONS
# ============================================================================

def check_azure_cli_login() -> bool:
    """Check if user is authenticated to Azure CLI."""
    try:
        import subprocess
        result = subprocess.run(
            ["az", "account", "get-access-token"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, Exception):
        return False


def generate_random_id(length: int = 6) -> str:
    """Generate random alphanumeric ID for resource naming."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def get_azure_region(project_root: Path) -> str:
    """
    Get Azure region for workshop mode.

    IMPORTANT: Azure workshop mode MUST use eastus2 because the hardcoded
    MongoDB clusters for Lab2 and Lab3 are located in eastus2.
    """
    print("\n" + "=" * 70)
    print("IMPORTANT: Azure workshop mode requires eastus2 region")
    print("=" * 70)
    print("\nThe hardcoded MongoDB clusters for Lab2 and Lab3 are in eastus2.")
    print("Using any other region will cause connection failures.")
    print("Region will be set to: eastus2")
    print("=" * 70 + "\n")

    return "eastus2"


def get_subscription_id(credential) -> str:
    """Get Azure subscription ID from az CLI."""
    try:
        import subprocess
        result = subprocess.run(
            ["az", "account", "show", "--query", "id", "-o", "tsv"],
            capture_output=True,
            text=True,
            check=True
        )
        subscription_id = result.stdout.strip()
        if subscription_id:
            return subscription_id
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    raise Exception(
        "Could not determine Azure subscription ID. "
        "Please run 'az login' and 'az account set --subscription <id>'"
    )


def create_resource_group(
    resource_client: ResourceManagementClient,
    resource_group_name: str,
    region: str,
    tags: Dict[str, str],
    logger: logging.Logger
) -> None:
    """Create Azure resource group if it doesn't exist."""
    logger.info(f"Creating resource group '{resource_group_name}'...")

    resource_group = ResourceGroup(
        location=region,
        tags=tags
    )

    resource_client.resource_groups.create_or_update(
        resource_group_name,
        resource_group
    )

    logger.info(f"✓ Created resource group '{resource_group_name}'")


def create_cognitive_account(
    cognitive_client: CognitiveServicesManagementClient,
    resource_group_name: str,
    account_name: str,
    region: str,
    tags: Dict[str, str],
    logger: logging.Logger
) -> str:
    """Create Azure Cognitive Services account (OpenAI)."""
    logger.info(f"Creating Azure Cognitive Services account '{account_name}'...")

    account = Account(
        location=region,
        sku=CognitiveServicesSku(name="S0"),
        kind="OpenAI",
        properties=AccountProperties(
            public_network_access="Enabled",
            custom_sub_domain_name=account_name
        ),
        tags=tags
    )

    # This is a long-running operation
    poller = cognitive_client.accounts.begin_create(
        resource_group_name,
        account_name,
        account
    )

    result = poller.result()
    endpoint = result.properties.endpoint

    logger.info(f"✓ Created Cognitive Services account '{account_name}'")
    logger.info(f"  Endpoint: {endpoint}")

    return endpoint


def create_model_deployment(
    cognitive_client: CognitiveServicesManagementClient,
    resource_group_name: str,
    account_name: str,
    deployment_name: str,
    model_name: str,
    model_version: str,
    capacity: int,
    logger: logging.Logger
) -> None:
    """Create Azure OpenAI model deployment."""
    logger.info(f"Creating deployment '{deployment_name}' (model: {model_name}, version: {model_version})...")

    deployment = Deployment(
        properties=DeploymentProperties(
            model=DeploymentModel(
                format="OpenAI",
                name=model_name,
                version=model_version
            )
        ),
        sku=CognitiveServicesSku(
            name="GlobalStandard",
            capacity=capacity
        )
    )

    # This is a long-running operation
    poller = cognitive_client.deployments.begin_create_or_update(
        resource_group_name,
        account_name,
        deployment_name,
        deployment
    )

    poller.result()

    logger.info(f"✓ Created deployment '{deployment_name}' with capacity {capacity}")


def get_api_key(
    cognitive_client: CognitiveServicesManagementClient,
    resource_group_name: str,
    account_name: str,
    logger: logging.Logger
) -> str:
    """Retrieve API key for Cognitive Services account."""
    logger.info("Retrieving API key...")

    keys = cognitive_client.accounts.list_keys(
        resource_group_name,
        account_name
    )

    api_key = keys.key1

    logger.info("✓ Retrieved API key")

    return api_key


def test_azure_openai_credentials(
    endpoint: str,
    api_key: str,
    logger: logging.Logger
) -> bool:
    """Test Azure OpenAI credentials."""
    from .test_azure_openai_credentials import test_azure_openai_credentials as test_func

    logger.info("Testing Azure OpenAI credentials...")

    return test_func(endpoint, api_key, logger)


def save_azure_state(
    project_root: Path,
    resource_group: str,
    cognitive_account: str,
    deployments: list,
    endpoint: str,
    region: str,
    owner_email: str,
    logger: logging.Logger
) -> None:
    """Save Azure state information for destroy command."""
    state_file = project_root / AZURE_STATE_FILE

    state = {
        "resource_group": resource_group,
        "cognitive_account": cognitive_account,
        "deployments": deployments,
        "endpoint": endpoint,
        "region": region,
        "owner_email": owner_email,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    logger.debug(f"Saved state to {state_file}")


def save_azure_credentials_file(
    project_root: Path,
    endpoint: str,
    api_key: str,
    region: str,
    resource_group: str,
    cognitive_account: str,
    tags: Dict[str, str],
    logger: logging.Logger
) -> None:
    """Save Azure credentials to markdown file with usage instructions."""
    creds_file = project_root / AZURE_CREDENTIALS_FILE

    # Format tags for display (exclude LocalPath as it's not useful for workshop participants)
    tags_display = "\n".join([f"**{key}:** `{value}`" for key, value in tags.items() if key != "LocalPath"])

    content = f"""# Workshop Credentials (Azure)

## IMPORTANT: Region Requirement

**Azure deployment MUST use region: eastus2**

The hardcoded MongoDB clusters for Lab2 and Lab3 are located in eastus2.
Using any other region will cause MongoDB connection failures.

## Azure OpenAI Credentials

Use these credentials when running `uv run deploy`:

```
Azure OpenAI Endpoint: {endpoint}
Azure OpenAI API Key:  {api_key}
```

## Usage Instructions

### For Workshop Participants

1. Clone the repository:
   ```bash
   git clone https://github.com/confluentinc/quickstart-streaming-agents
   cd quickstart-streaming-agents
   ```

2. Run deployment:
   ```bash
   uv run deploy
   ```

3. When prompted, enter the credentials above:
   - Azure OpenAI Endpoint: `{endpoint}`
   - Azure OpenAI API Key: `{api_key}`

## Security Notes

- **Do NOT commit these credentials to Git**
- These credentials provide access only to the workshop Azure OpenAI account
- No broader Azure subscription access is granted
- Keys should be revoked immediately after the workshop
- Each participant will use the same shared credentials

## After Workshop (For Organizers)

To revoke these credentials and clean up resources, run:

```bash
uv run workshop-keys destroy
```

Or delete the resource group directly in Azure CLI:

```bash
# Delete resource group directly in Azure
az group delete --name {resource_group} --yes --no-wait
```

The workshop-keys destroy command will:
1. Delete model deployments (`gpt-5-mini`, `text-embedding-ada-002`)
2. Ask if you want to delete the entire resource group
3. Clean up state files

---

## Resource Details

**Resource Group:** `{resource_group}`
**Cognitive Account:** `{cognitive_account}`
**Region:** `{region}`

**Deployments:**
- `gpt-5-mini` - Chat completions model (version: 2025-08-07)
- `text-embedding-ada-002` - Embeddings model (version: 2)

**Tags:**
{tags_display}

**Created:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""

    with open(creds_file, 'w') as f:
        f.write(content)

    logger.info(f"✓ Saved credentials to {creds_file}")

    # Also update credentials.env if it exists
    env_file = project_root / "credentials.env"
    if env_file.exists():
        set_key(str(env_file), "TF_VAR_azure_openai_endpoint_raw", endpoint)
        set_key(str(env_file), "TF_VAR_azure_openai_api_key", api_key)
        logger.info(f"✓ Updated credentials.env with new Azure OpenAI credentials")


def load_azure_state(project_root: Path) -> Optional[Dict]:
    """Load Azure state from previous create command."""
    state_file = project_root / AZURE_STATE_FILE

    if not state_file.exists():
        return None

    with open(state_file, 'r') as f:
        return json.load(f)


# ============================================================================
# COMMAND HANDLERS
# ============================================================================

def create_aws_command(args: argparse.Namespace, logger: logging.Logger) -> int:
    """Create AWS IAM user and access keys for workshop."""
    if not BOTO3_AVAILABLE:
        print("\n" + "=" * 70)
        print("ERROR: boto3 is not installed")
        print("=" * 70)
        print("\nboto3 is required for AWS API calls.")
        print("Please install it with:")
        print("\n  pip install boto3")
        print("\nOr add it to your project dependencies.")
        print("=" * 70)
        return 1

    try:
        # Get project root
        project_root = get_project_root()
        logger.debug(f"Project root: {project_root}")

        # Get owner email and region
        owner_email = get_owner_email(project_root)
        region = get_aws_region(project_root)

        # Build tags
        tags = get_tags(project_root, owner_email)

        # Create IAM client (uses default AWS credentials from environment/config)
        iam_client = boto3.client('iam')

        print("\n" + "=" * 70)
        print("CREATING AWS WORKSHOP CREDENTIALS")
        print("=" * 70)

        # Create or get IAM user
        user_created = create_or_get_iam_user(iam_client, tags, logger)

        # Attach policy
        attach_bedrock_policy(iam_client, logger)

        # Create access key
        access_key_id, secret_access_key = create_access_key(iam_client, logger)

        # Test Bedrock access
        test_success = test_bedrock_credentials(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            region=region,
            logger=logger
        )

        if not test_success:
            print("\n" + "=" * 70)
            print("⚠ WARNING: Bedrock access test did not complete successfully")
            print("=" * 70)
            print("\nPossible issues:")
            print("  1. AWS credentials haven't propagated yet (wait 30-60 seconds)")
            print("  2. Claude Sonnet 4.5 model not enabled in your AWS account")
            print("  3. Insufficient Bedrock permissions")
            print("\nTo verify manually:")
            print(f"  uv run test-bedrock --access-key {access_key_id} \\")
            print(f"    --secret-key <SECRET_KEY>")
            print("\nTo enable Claude models:")
            print("  AWS Console → Bedrock → Model Access → Request access")
            print("=" * 70)
            logger.warning("Bedrock test did not pass, but continuing anyway")
        else:
            logger.info("✓ Bedrock access test passed - Claude Sonnet 4.5 is accessible")

        # Save state and credentials
        save_aws_state(project_root, access_key_id, owner_email, region, logger)
        save_aws_credentials_file(
            project_root, access_key_id, secret_access_key, region, tags, logger
        )

        print("=" * 70)
        print("✓ AWS WORKSHOP CREDENTIALS CREATED SUCCESSFULLY")
        print("=" * 70)
        print(f"\nCredentials saved to: {AWS_CREDENTIALS_FILE}")
        print(f"State saved to:       {AWS_STATE_FILE}")
        print("\nNext steps:")
        print(f"1. Review the credentials in {AWS_CREDENTIALS_FILE}")
        print("2. Share credentials with workshop participants")
        print("3. After workshop, run: uv run workshop-keys destroy aws")
        print("=" * 70 + "\n")

        return 0

    except ClientError as e:
        logger.error(f"AWS API error: {e}")
        print("\nPlease ensure you have:")
        print("1. Valid AWS credentials configured (aws configure)")
        print("2. IAM permissions to create users and policies")
        return 1
    except Exception as e:
        logger.error(f"Error creating workshop credentials: {e}")
        return 1


def destroy_aws_command(args: argparse.Namespace, logger: logging.Logger) -> int:
    """Destroy AWS workshop credentials and optionally delete IAM user."""
    if not BOTO3_AVAILABLE:
        print("\n" + "=" * 70)
        print("ERROR: boto3 is not installed")
        print("=" * 70)
        print("\nPlease install boto3 to use this command.")
        print("=" * 70)
        return 1

    try:
        # Get project root
        project_root = get_project_root()

        # Load state
        state = load_aws_state(project_root)

        if not state:
            print("\n" + "=" * 70)
            print("WARNING: No state file found")
            print("=" * 70)
            print(f"\nNo state file ({AWS_STATE_FILE}) found.")
            print("This usually means no credentials were created with this tool,")
            print("or they were already destroyed.")
            print("\nIf you want to manually delete workshop credentials:")
            print(f"1. AWS Console → IAM → Users → {AWS_IAM_USERNAME}")
            print("2. Delete access keys")
            print("3. Optionally delete the user")
            print("=" * 70 + "\n")
            return 1

        # Create IAM client
        iam_client = boto3.client('iam')

        print("\n" + "=" * 70)
        print("DESTROYING AWS WORKSHOP CREDENTIALS")
        print("=" * 70)

        # Delete access key
        access_key_id = state['access_key_id']
        logger.info(f"Deleting access key {access_key_id}...")

        try:
            iam_client.delete_access_key(
                UserName=state['iam_username'],
                AccessKeyId=access_key_id
            )
            logger.info(f"✓ Deleted access key {access_key_id}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                logger.warning(f"Access key {access_key_id} not found (may already be deleted)")
            else:
                raise

        # Ask about deleting user
        user_deleted = False
        if not args.keep_user:
            print("\nDelete IAM user entirely?")
            print(f"  User: {state['iam_username']}")
            print("  (Saying 'No' allows you to reuse this user for future workshops)")

            delete_user = prompt_choice(
                "Delete IAM user?",
                ["No (keep user for future workshops)", "Yes (delete user completely)"]
            )

            if "Yes" in delete_user:
                # Comprehensive cleanup of all user dependencies
                logger.info("Cleaning up all IAM user dependencies...")
                success, error_details = cleanup_user_dependencies(
                    iam_client, state['iam_username'], logger
                )
                if not success:
                    print("\n" + "=" * 70)
                    print("⚠ WARNING: Could not fully clean up IAM user")
                    print("=" * 70)
                    print(f"\n{error_details}")
                    print("\nTo manually delete the user:")
                    print(f"1. AWS Console → IAM → Users → {state['iam_username']}")
                    print("2. Review and remove remaining dependencies")
                    print("3. Delete the user")
                    print("=" * 70 + "\n")
                    logger.warning(f"User {state['iam_username']} could not be deleted automatically")
                else:
                    # All dependencies cleaned up, now delete user
                    logger.info(f"Deleting IAM user {state['iam_username']}...")
                    try:
                        iam_client.delete_user(UserName=state['iam_username'])
                        logger.info(f"✓ Deleted IAM user {state['iam_username']}")
                        user_deleted = True
                    except ClientError as e:
                        if e.response['Error']['Code'] == 'NoSuchEntity':
                            logger.warning(f"User {state['iam_username']} not found (may already be deleted)")
                            user_deleted = True
                        else:
                            print("\n" + "=" * 70)
                            print("⚠ WARNING: User cleanup succeeded but deletion failed")
                            print("=" * 70)
                            print(f"\nError: {e}")
                            print(f"User: {state['iam_username']}")
                            print("\nThe user dependencies were cleaned up, but deletion failed.")
                            print("Try running the command again, or delete manually via AWS Console.")
                            print("=" * 70 + "\n")
                            logger.error(f"Failed to delete user after cleanup: {e}")
        else:
            logger.info(f"Keeping IAM user {state['iam_username']} (--keep-user flag)")

        # Delete state files
        state_file = project_root / AWS_STATE_FILE
        creds_file = project_root / AWS_CREDENTIALS_FILE

        if state_file.exists():
            state_file.unlink()
            logger.info(f"✓ Deleted {AWS_STATE_FILE}")

        if creds_file.exists():
            creds_file.unlink()
            logger.info(f"✓ Deleted {AWS_CREDENTIALS_FILE}")

        print("=" * 70)
        print("✓ AWS WORKSHOP CREDENTIALS DESTROYED")
        print("=" * 70)
        print("\nDestroyed:")
        print(f"  - Access key: {access_key_id}")
        if user_deleted:
            print(f"  - IAM user: {state['iam_username']}")
        elif not args.keep_user:
            print(f"  - IAM user: {state['iam_username']} (cleanup attempted, may require manual deletion)")
        print(f"  - State files: {AWS_STATE_FILE}, {AWS_CREDENTIALS_FILE}")
        print("=" * 70 + "\n")

        return 0

    except ClientError as e:
        logger.error(f"AWS API error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error destroying credentials: {e}")
        return 1


def create_azure_command(args: argparse.Namespace, logger: logging.Logger) -> int:
    """Create Azure OpenAI resources for workshop."""
    if not AZURE_SDK_AVAILABLE:
        print("\n" + "=" * 70)
        print("ERROR: Azure SDK packages are not installed")
        print("=" * 70)
        print("\nRequired packages:")
        print("  - azure-identity")
        print("  - azure-mgmt-cognitiveservices")
        print("  - azure-mgmt-resource")
        print("  - azure-ai-inference")
        print("\nPlease install them with:")
        print("\n  pip install azure-identity azure-mgmt-cognitiveservices azure-mgmt-resource azure-ai-inference")
        print("\nOr add them to your project dependencies.")
        print("=" * 70)
        return 1

    # Check Azure CLI login
    if not check_azure_cli_login():
        print("\n" + "=" * 70)
        print("ERROR: Not logged into Azure CLI")
        print("=" * 70)
        print("\nYou must be logged into the Azure CLI to create workshop resources.")
        print("\nTo log in, run:")
        print("\n  az login")
        print("\nAfter logging in, set your subscription:")
        print("\n  az account set --subscription <subscription-id>")
        print("\nThen run this command again.")
        print("=" * 70 + "\n")
        return 1

    try:
        # Get project root
        project_root = get_project_root()
        logger.debug(f"Project root: {project_root}")

        # Get owner email and region
        owner_email = get_owner_email(project_root)
        region = get_azure_region(project_root)

        # Build tags
        tags = get_tags(project_root, owner_email)

        # Create Azure credential
        credential = DefaultAzureCredential()

        # Get subscription ID
        subscription_id = get_subscription_id(credential)
        logger.debug(f"Using subscription: {subscription_id}")

        # Create Azure clients
        resource_client = ResourceManagementClient(credential, subscription_id)
        cognitive_client = CognitiveServicesManagementClient(credential, subscription_id)

        print("\n" + "=" * 70)
        print("CREATING AZURE WORKSHOP CREDENTIALS")
        print("=" * 70)

        # Generate random ID for unique naming
        random_id = generate_random_id()
        resource_group_name = f"{AZURE_RESOURCE_GROUP_PREFIX}-{random_id}"
        account_name = f"{AZURE_COGNITIVE_ACCOUNT_PREFIX}-{random_id}"

        # Create resource group
        create_resource_group(
            resource_client,
            resource_group_name,
            region,
            tags,
            logger
        )

        # Create cognitive services account
        endpoint = create_cognitive_account(
            cognitive_client,
            resource_group_name,
            account_name,
            region,
            tags,
            logger
        )

        # Create model deployments
        deployment_names = []
        for deployment_name, config in AZURE_DEPLOYMENTS.items():
            create_model_deployment(
                cognitive_client,
                resource_group_name,
                account_name,
                deployment_name,
                config["model"],
                config["version"],
                config["capacity"],
                logger
            )
            deployment_names.append(deployment_name)

        # Get API key
        api_key = get_api_key(
            cognitive_client,
            resource_group_name,
            account_name,
            logger
        )

        # Test Azure OpenAI access
        test_success = test_azure_openai_credentials(endpoint, api_key, logger)

        if not test_success:
            print("\n" + "=" * 70)
            print("⚠ WARNING: Azure OpenAI access test did not complete successfully")
            print("=" * 70)
            print("\nPossible issues:")
            print("  1. Deployments haven't fully propagated yet (wait 1-2 minutes)")
            print("  2. Azure OpenAI service not fully initialized")
            print("  3. Network connectivity issues")
            print("\nResources were created successfully. You can test manually:")
            print(f"  Endpoint: {endpoint}")
            print(f"  Deployments: {', '.join(deployment_names)}")
            print("=" * 70)
            logger.warning("Azure OpenAI test did not pass, but continuing anyway")
        else:
            logger.info("✓ Azure OpenAI access test passed - models are accessible")

        # Save state and credentials
        save_azure_state(
            project_root,
            resource_group_name,
            account_name,
            deployment_names,
            endpoint,
            region,
            owner_email,
            logger
        )
        save_azure_credentials_file(
            project_root,
            endpoint,
            api_key,
            region,
            resource_group_name,
            account_name,
            tags,
            logger
        )

        print("=" * 70)
        print("✓ AZURE WORKSHOP CREDENTIALS CREATED SUCCESSFULLY")
        print("=" * 70)
        print(f"\nCredentials saved to: {AZURE_CREDENTIALS_FILE}")
        print(f"State saved to:       {AZURE_STATE_FILE}")
        print("\nNext steps:")
        print(f"1. Review the credentials in {AZURE_CREDENTIALS_FILE}")
        print("2. Share credentials with workshop participants")
        print("3. After workshop, run: uv run workshop-keys destroy azure")
        print("=" * 70 + "\n")

        return 0

    except HttpResponseError as e:
        logger.error(f"Azure API error: {e}")
        print("\nPlease ensure you have:")
        print("1. Valid Azure credentials configured (az login)")
        print("2. Permissions to create resource groups and Cognitive Services")
        print("3. Azure OpenAI service enabled in your subscription")
        return 1
    except Exception as e:
        logger.error(f"Error creating workshop credentials: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return 1


def destroy_azure_command(args: argparse.Namespace, logger: logging.Logger) -> int:
    """Destroy Azure workshop credentials and optionally delete resource group."""
    if not AZURE_SDK_AVAILABLE:
        print("\n" + "=" * 70)
        print("ERROR: Azure SDK packages are not installed")
        print("=" * 70)
        print("\nPlease install required Azure packages to use this command.")
        print("=" * 70)
        return 1

    # Check Azure CLI login
    if not check_azure_cli_login():
        print("\n" + "=" * 70)
        print("ERROR: Not logged into Azure CLI")
        print("=" * 70)
        print("\nYou must be logged into the Azure CLI to destroy workshop resources.")
        print("\nTo log in, run:")
        print("\n  az login")
        print("\nThen run this command again.")
        print("=" * 70 + "\n")
        return 1

    try:
        # Get project root
        project_root = get_project_root()

        # Load state
        state = load_azure_state(project_root)

        if not state:
            print("\n" + "=" * 70)
            print("WARNING: No state file found")
            print("=" * 70)
            print(f"\nNo state file ({AZURE_STATE_FILE}) found.")
            print("This usually means no credentials were created with this tool,")
            print("or they were already destroyed.")
            print("\nIf you want to manually delete workshop resources:")
            print("1. Azure Portal → Resource Groups")
            print(f"2. Find resource groups starting with '{AZURE_RESOURCE_GROUP_PREFIX}'")
            print("3. Delete the resource group and all its resources")
            print("=" * 70 + "\n")
            return 1

        # Create Azure credential
        credential = DefaultAzureCredential()

        # Get subscription ID
        subscription_id = get_subscription_id(credential)
        logger.debug(f"Using subscription: {subscription_id}")

        # Create Azure clients
        resource_client = ResourceManagementClient(credential, subscription_id)
        cognitive_client = CognitiveServicesManagementClient(credential, subscription_id)

        print("\n" + "=" * 70)
        print("DESTROYING AZURE WORKSHOP CREDENTIALS")
        print("=" * 70)

        resource_group = state['resource_group']
        cognitive_account = state['cognitive_account']
        deployments = state.get('deployments', [])

        # Delete model deployments
        for deployment_name in deployments:
            logger.info(f"Deleting deployment '{deployment_name}'...")
            try:
                poller = cognitive_client.deployments.begin_delete(
                    resource_group,
                    cognitive_account,
                    deployment_name
                )
                poller.result()
                logger.info(f"✓ Deleted deployment '{deployment_name}'")
            except ResourceNotFoundError:
                logger.warning(f"Deployment '{deployment_name}' not found (may already be deleted)")
            except Exception as e:
                logger.error(f"Failed to delete deployment '{deployment_name}': {e}")

        # Ask about deleting resource group
        resource_group_deleted = False
        if not args.keep_resource_group:
            print("\nDelete resource group entirely?")
            print(f"  Resource Group: {resource_group}")
            print("  (Saying 'No' keeps the resource group for future workshops)")

            delete_rg = prompt_choice(
                "Delete resource group?",
                ["No (keep for future workshops)", "Yes (delete all resources)"]
            )

            if "Yes" in delete_rg:
                logger.info(f"Deleting resource group '{resource_group}'...")
                try:
                    poller = resource_client.resource_groups.begin_delete(resource_group)
                    poller.result()
                    logger.info(f"✓ Deleted resource group '{resource_group}'")
                    resource_group_deleted = True
                except ResourceNotFoundError:
                    logger.warning(f"Resource group '{resource_group}' not found (may already be deleted)")
                    resource_group_deleted = True
                except Exception as e:
                    logger.error(f"Failed to delete resource group: {e}")
                    print("\n⚠ Resource group could not be deleted automatically")
                    print("Please delete it manually via Azure Portal")
            else:
                # Just delete the cognitive account
                logger.info(f"Deleting cognitive account '{cognitive_account}'...")
                try:
                    poller = cognitive_client.accounts.begin_delete(
                        resource_group,
                        cognitive_account
                    )
                    poller.result()
                    logger.info(f"✓ Deleted cognitive account '{cognitive_account}'")
                except ResourceNotFoundError:
                    logger.warning(f"Cognitive account '{cognitive_account}' not found (may already be deleted)")
                except Exception as e:
                    logger.error(f"Failed to delete cognitive account: {e}")
        else:
            logger.info(f"Keeping resource group '{resource_group}' (--keep-resource-group flag)")

        # Delete state files
        state_file = project_root / AZURE_STATE_FILE
        creds_file = project_root / AZURE_CREDENTIALS_FILE

        if state_file.exists():
            state_file.unlink()
            logger.info(f"✓ Deleted {AZURE_STATE_FILE}")

        if creds_file.exists():
            creds_file.unlink()
            logger.info(f"✓ Deleted {AZURE_CREDENTIALS_FILE}")

        print("=" * 70)
        print("✓ AZURE WORKSHOP CREDENTIALS DESTROYED")
        print("=" * 70)
        print("\nDestroyed:")
        print(f"  - Deployments: {', '.join(deployments)}")
        if resource_group_deleted:
            print(f"  - Resource group: {resource_group}")
        elif not args.keep_resource_group:
            print(f"  - Cognitive account: {cognitive_account}")
        print(f"  - State files: {AZURE_STATE_FILE}, {AZURE_CREDENTIALS_FILE}")
        print("=" * 70 + "\n")

        return 0

    except HttpResponseError as e:
        logger.error(f"Azure API error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error destroying credentials: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return 1


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for unified workshop key manager (AWS + Azure)."""
    parser = argparse.ArgumentParser(
        description="Create and manage workshop credentials for AWS Bedrock or Azure OpenAI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive cloud selection
  %(prog)s create
  %(prog)s destroy

  # Create AWS Bedrock credentials
  %(prog)s create aws

  # Create Azure OpenAI credentials
  %(prog)s create azure

  # Destroy AWS credentials
  %(prog)s destroy aws

  # Destroy Azure credentials
  %(prog)s destroy azure

  # Keep IAM user/resource group for reuse
  %(prog)s destroy aws --keep-user
  %(prog)s destroy azure --keep-resource-group
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Create command
    create_parser = subparsers.add_parser(
        'create',
        help='Create workshop credentials'
    )
    create_parser.add_argument(
        'cloud',
        nargs='?',
        choices=['aws', 'azure'],
        help='Cloud provider (aws or azure). If not specified, you will be prompted.'
    )
    create_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    # Destroy command
    destroy_parser = subparsers.add_parser(
        'destroy',
        help='Revoke workshop credentials'
    )
    destroy_parser.add_argument(
        'cloud',
        nargs='?',
        choices=['aws', 'azure'],
        help='Cloud provider (aws or azure). If not specified, you will be prompted.'
    )
    destroy_parser.add_argument(
        '--keep-user',
        action='store_true',
        help='Keep IAM user for reuse (AWS only)'
    )
    destroy_parser.add_argument(
        '--keep-resource-group',
        action='store_true',
        help='Keep resource group for reuse (Azure only)'
    )
    destroy_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Require subcommand
    if not args.command:
        parser.print_help()
        return 1

    # Set up logging
    logger = setup_logging(getattr(args, 'verbose', False))

    # Handle interactive cloud selection (for both create and destroy)
    if not args.cloud:
        args.cloud = prompt_cloud_provider()

    # Dispatch based on command and cloud provider
    if args.command == 'create':
        if args.cloud == 'aws':
            return create_aws_command(args, logger)
        elif args.cloud == 'azure':
            return create_azure_command(args, logger)
    elif args.command == 'destroy':
        if args.cloud == 'aws':
            return destroy_aws_command(args, logger)
        elif args.cloud == 'azure':
            return destroy_azure_command(args, logger)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
