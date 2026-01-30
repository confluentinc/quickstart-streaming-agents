#!/usr/bin/env python3
"""
Workshop Key Manager - Create and manage AWS credentials for workshop mode.

This script helps workshop organizers create properly-scoped AWS IAM credentials
for participants to use Bedrock models without full infrastructure permissions.

Usage:
    uv run workshop-keys create    # Create IAM user and access keys
    uv run workshop-keys destroy   # Revoke keys and optionally delete user

    # With options:
    uv run workshop-keys create --verbose
    uv run workshop-keys destroy --keep-user

Examples:
    # Day before workshop
    uv run workshop-keys create
    # → Creates WORKSHOP_CREDENTIALS.md with keys and instructions

    # After workshop
    uv run workshop-keys destroy
    # → Revokes keys, asks if you want to delete the IAM user
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

from dotenv import dotenv_values

from .terraform import get_project_root
from .ui import prompt_choice, prompt_with_default


# Constants
IAM_USERNAME = "workshop-bedrock-user"
POLICY_NAME = "BedrockInvokeOnly"
STATE_FILE = ".workshop-keys-state.json"
CREDENTIALS_FILE = "WORKSHOP_CREDENTIALS.md"
PROJECT_URL = "https://github.com/confluentinc/quickstart-streaming-agents"


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)


def get_bedrock_policy() -> Dict:
    """
    Get the IAM policy document for Bedrock model invocation.

    Returns:
        Policy document as a dictionary
    """
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


def get_tags(project_root: Path, owner_email: str) -> Dict[str, str]:
    """
    Build AWS resource tags matching Terraform pattern.

    Args:
        project_root: Project root directory
        owner_email: Owner email address

    Returns:
        Dictionary of tags
    """
    return {
        "Owner": owner_email,
        "Project": PROJECT_URL,
        "Environment": "workshop",
        "ManagedBy": "workshop-key-manager",
        "LocalPath": str(project_root)
    }


def get_owner_email(project_root: Path) -> str:
    """
    Get owner email from credentials.env or prompt user.

    Args:
        project_root: Project root directory

    Returns:
        Owner email address
    """
    creds_file = project_root / "credentials.env"

    # Try to load from credentials.env
    if creds_file.exists():
        creds = dotenv_values(creds_file)
        if "TF_VAR_owner_email" in creds and creds["TF_VAR_owner_email"]:
            return creds["TF_VAR_owner_email"].strip("'\"")

    # Prompt user
    return prompt_with_default(
        "Enter owner email (for AWS resource tagging)",
        default=""
    )


def get_aws_region(project_root: Path) -> str:
    """
    Get AWS region from credentials.env or prompt user.

    Args:
        project_root: Project root directory

    Returns:
        AWS region (e.g., 'us-east-1')
    """
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
    """
    Create IAM user if it doesn't exist, or get existing user.

    Args:
        iam_client: boto3 IAM client
        tags: Tags to apply to user
        logger: Logger instance

    Returns:
        True if user was created, False if it already existed
    """
    try:
        # Check if user exists
        iam_client.get_user(UserName=IAM_USERNAME)
        logger.info(f"IAM user '{IAM_USERNAME}' already exists")
        return False
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            # User doesn't exist, create it
            logger.info(f"Creating IAM user '{IAM_USERNAME}'...")
            tag_list = [{"Key": k, "Value": v} for k, v in tags.items()]
            iam_client.create_user(
                UserName=IAM_USERNAME,
                Tags=tag_list
            )
            logger.info(f"✓ Created IAM user '{IAM_USERNAME}'")
            return True
        else:
            raise


def attach_bedrock_policy(iam_client, logger: logging.Logger) -> None:
    """
    Attach inline Bedrock policy to IAM user.

    Args:
        iam_client: boto3 IAM client
        logger: Logger instance
    """
    logger.info(f"Attaching Bedrock policy '{POLICY_NAME}'...")

    policy_doc = get_bedrock_policy()

    iam_client.put_user_policy(
        UserName=IAM_USERNAME,
        PolicyName=POLICY_NAME,
        PolicyDocument=json.dumps(policy_doc)
    )

    logger.info(f"✓ Attached inline policy '{POLICY_NAME}'")


def create_access_key(iam_client, logger: logging.Logger) -> Tuple[str, str]:
    """
    Create new access key for IAM user.

    Args:
        iam_client: boto3 IAM client
        logger: Logger instance

    Returns:
        Tuple of (access_key_id, secret_access_key)

    Raises:
        Exception if user already has 2 keys (AWS limit)
    """
    # Check existing keys
    response = iam_client.list_access_keys(UserName=IAM_USERNAME)
    existing_keys = response.get('AccessKeyMetadata', [])

    if len(existing_keys) >= 2:
        raise Exception(
            f"User '{IAM_USERNAME}' already has 2 access keys (AWS limit). "
            f"Please delete an old key before creating a new one."
        )

    logger.info("Generating new access key...")

    response = iam_client.create_access_key(UserName=IAM_USERNAME)
    access_key = response['AccessKey']

    access_key_id = access_key['AccessKeyId']
    secret_access_key = access_key['SecretAccessKey']

    logger.info(f"✓ Created access key: {access_key_id}")

    return access_key_id, secret_access_key


def test_bedrock_access(
    access_key_id: str,
    secret_access_key: str,
    region: str,
    logger: logging.Logger
) -> bool:
    """
    Test that the access keys can invoke Bedrock models.

    Args:
        access_key_id: AWS access key ID
        secret_access_key: AWS secret access key
        region: AWS region
        logger: Logger instance

    Returns:
        True if test succeeded, False otherwise
    """
    try:
        logger.info("Testing Bedrock access...")

        # Create Bedrock Runtime client with new credentials
        bedrock_client = boto3.client(
            'bedrock-runtime',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region
        )

        # Try a simple invocation with minimal tokens
        model_id = "amazon.titan-embed-text-v1"  # Use embeddings model (cheaper)

        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps({"inputText": "test"})
        )

        logger.info("✓ Bedrock access test succeeded")
        return True

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            logger.warning(
                f"⚠ Bedrock model access may not be enabled in region {region}. "
                f"Credentials were created but may need model access approval."
            )
            return True  # Credentials are valid, just need model access
        else:
            logger.error(f"✗ Bedrock access test failed: {e}")
            return False
    except Exception as e:
        logger.error(f"✗ Bedrock access test failed: {e}")
        return False


def save_state(
    project_root: Path,
    access_key_id: str,
    owner_email: str,
    region: str,
    logger: logging.Logger
) -> None:
    """
    Save state information for destroy command.

    Args:
        project_root: Project root directory
        access_key_id: AWS access key ID
        owner_email: Owner email
        region: AWS region
        logger: Logger instance
    """
    state_file = project_root / STATE_FILE

    state = {
        "iam_username": IAM_USERNAME,
        "policy_name": POLICY_NAME,
        "access_key_id": access_key_id,
        "owner_email": owner_email,
        "region": region,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    logger.debug(f"Saved state to {state_file}")


def save_credentials_file(
    project_root: Path,
    access_key_id: str,
    secret_access_key: str,
    region: str,
    logger: logging.Logger
) -> None:
    """
    Save credentials to markdown file with usage instructions.

    Args:
        project_root: Project root directory
        access_key_id: AWS access key ID
        secret_access_key: AWS secret access key
        region: AWS region
        logger: Logger instance
    """
    creds_file = project_root / CREDENTIALS_FILE

    content = f"""# Workshop Credentials

**Created:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

## AWS Bedrock Access Keys

Use these credentials when running `uv run deploy --workshop`:

```
AWS Access Key ID:     {access_key_id}
AWS Secret Access Key: {secret_access_key}
AWS Region:            {region}
```

## Usage Instructions

### For Workshop Participants

1. Clone the repository:
   ```bash
   git clone https://github.com/confluentinc/quickstart-streaming-agents
   cd quickstart-streaming-agents
   ```

2. Run deployment in workshop mode:
   ```bash
   uv run deploy --workshop
   ```

3. When prompted, enter the credentials above:
   - AWS Bedrock Access Key: `{access_key_id}`
   - AWS Bedrock Secret Key: `{secret_access_key}`
   - AWS Region: `{region}`

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

This will:
1. Delete the access key `{access_key_id}`
2. Ask if you want to delete the IAM user (for reuse in future workshops)
3. Clean up state files

---

**IAM User:** `{IAM_USERNAME}`
**Policy:** `{POLICY_NAME}` (inline policy)
**Permissions:** `bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream`
"""

    with open(creds_file, 'w') as f:
        f.write(content)

    logger.info(f"✓ Saved credentials to {creds_file}")


def load_state(project_root: Path) -> Optional[Dict]:
    """
    Load state from previous create command.

    Args:
        project_root: Project root directory

    Returns:
        State dictionary or None if file doesn't exist
    """
    state_file = project_root / STATE_FILE

    if not state_file.exists():
        return None

    with open(state_file, 'r') as f:
        return json.load(f)


def create_command(args: argparse.Namespace, logger: logging.Logger) -> int:
    """
    Create IAM user and access keys for workshop.

    Args:
        args: Command line arguments
        logger: Logger instance

    Returns:
        Exit code (0 for success, 1 for error)
    """
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
        print("CREATING WORKSHOP CREDENTIALS")
        print("=" * 70)

        # Create or get IAM user
        user_created = create_or_get_iam_user(iam_client, tags, logger)

        # Attach policy
        attach_bedrock_policy(iam_client, logger)

        # Create access key
        access_key_id, secret_access_key = create_access_key(iam_client, logger)

        # Test Bedrock access with the actual Claude model
        from .test_bedrock_credentials import test_bedrock_credentials

        logger.info("Testing Bedrock access with Claude Sonnet 4.5...")
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
        save_state(project_root, access_key_id, owner_email, region, logger)
        save_credentials_file(
            project_root, access_key_id, secret_access_key, region, logger
        )

        print("=" * 70)
        print("✓ WORKSHOP CREDENTIALS CREATED SUCCESSFULLY")
        print("=" * 70)
        print(f"\nCredentials saved to: {CREDENTIALS_FILE}")
        print(f"State saved to:       {STATE_FILE}")
        print("\nNext steps:")
        print("1. Review the credentials in WORKSHOP_CREDENTIALS.md")
        print("2. Share credentials with workshop participants")
        print("3. After workshop, run: uv run workshop-keys destroy")
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


def cleanup_user_dependencies(
    iam_client,
    username: str,
    logger: logging.Logger
) -> Tuple[bool, Optional[str]]:
    """
    Comprehensively clean up all IAM user dependencies before deletion.

    AWS requires ALL of the following to be removed before DeleteUser succeeds:
    - Group memberships
    - Access keys
    - Inline policies
    - Attached managed policies
    - Login profile/password
    - MFA devices
    - SSH public keys
    - Signing certificates
    - Git credentials
    - Permission boundary

    Args:
        iam_client: boto3 IAM client
        username: IAM username to clean up
        logger: Logger instance

    Returns:
        Tuple of (success, error_details):
        - success: True if all cleanups succeeded, False if any failed
        - error_details: None if success, otherwise a string with error information
    """
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
                    # Deactivate first
                    iam_client.deactivate_mfa_device(
                        UserName=username,
                        SerialNumber=serial
                    )
                    logger.debug(f"  Deactivated MFA device {serial}")

                    # If it's a virtual device, delete it
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

    # 9. Delete Git credentials (service-specific credentials)
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


def destroy_command(args: argparse.Namespace, logger: logging.Logger) -> int:
    """
    Destroy workshop credentials and optionally delete IAM user.

    Args:
        args: Command line arguments
        logger: Logger instance

    Returns:
        Exit code (0 for success, 1 for error)
    """
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
        state = load_state(project_root)

        if not state:
            print("\n" + "=" * 70)
            print("WARNING: No state file found")
            print("=" * 70)
            print(f"\nNo state file ({STATE_FILE}) found.")
            print("This usually means no credentials were created with this tool,")
            print("or they were already destroyed.")
            print("\nIf you want to manually delete workshop credentials:")
            print(f"1. AWS Console → IAM → Users → {IAM_USERNAME}")
            print("2. Delete access keys")
            print("3. Optionally delete the user")
            print("=" * 70 + "\n")
            return 1

        # Create IAM client
        iam_client = boto3.client('iam')

        print("\n" + "=" * 70)
        print("DESTROYING WORKSHOP CREDENTIALS")
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
                            # Unexpected error after cleanup
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
        state_file = project_root / STATE_FILE
        creds_file = project_root / CREDENTIALS_FILE

        if state_file.exists():
            state_file.unlink()
            logger.info(f"✓ Deleted {STATE_FILE}")

        if creds_file.exists():
            creds_file.unlink()
            logger.info(f"✓ Deleted {CREDENTIALS_FILE}")

        print("=" * 70)
        print("✓ WORKSHOP CREDENTIALS DESTROYED")
        print("=" * 70)
        print("\nDestroyed:")
        print(f"  - Access key: {access_key_id}")
        if user_deleted:
            print(f"  - IAM user: {state['iam_username']}")
        elif not args.keep_user:
            print(f"  - IAM user: {state['iam_username']} (cleanup attempted, may require manual deletion)")
        print(f"  - State files: {STATE_FILE}, {CREDENTIALS_FILE}")
        print("=" * 70 + "\n")

        return 0

    except ClientError as e:
        logger.error(f"AWS API error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error destroying credentials: {e}")
        return 1


def main():
    """Main entry point for workshop key manager."""
    parser = argparse.ArgumentParser(
        description="Create and manage AWS credentials for workshop mode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Day before workshop - create credentials
  %(prog)s create

  # After workshop - revoke credentials
  %(prog)s destroy

  # Keep IAM user for reuse
  %(prog)s destroy --keep-user
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Create command
    create_parser = subparsers.add_parser(
        'create',
        help='Create IAM user and access keys'
    )
    create_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    # Destroy command
    destroy_parser = subparsers.add_parser(
        'destroy',
        help='Revoke access keys and optionally delete IAM user'
    )
    destroy_parser.add_argument(
        '--keep-user',
        action='store_true',
        help='Keep IAM user (for reuse in future workshops)'
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
    logger = setup_logging(args.verbose)

    # Execute command
    if args.command == 'create':
        return create_command(args, logger)
    elif args.command == 'destroy':
        return destroy_command(args, logger)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
