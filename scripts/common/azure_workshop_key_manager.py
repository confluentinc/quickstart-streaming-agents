#!/usr/bin/env python3
"""
Azure Workshop Key Manager - Create and manage Azure OpenAI credentials for workshop mode.

This script helps workshop organizers create properly-scoped Azure OpenAI resources
for participants to use Azure OpenAI models without requiring Azure CLI or full Azure access.

Usage:
    uv run azure-workshop-keys create    # Create resource group, cognitive account, and deployments
    uv run azure-workshop-keys destroy   # Delete deployments and optionally resource group

    # With options:
    uv run azure-workshop-keys create --verbose
    uv run azure-workshop-keys destroy --keep-resource-group

Examples:
    # Day before workshop
    uv run azure-workshop-keys create
    # → Creates AZURE_WORKSHOP_CREDENTIALS.md with endpoint, key, and instructions

    # After workshop
    uv run azure-workshop-keys destroy
    # → Deletes deployments, asks if you want to delete the resource group
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

from dotenv import dotenv_values

from .terraform import get_project_root
from .ui import prompt_choice, prompt_with_default


# Constants
RESOURCE_GROUP_PREFIX = "rg-workshop-openai"
COGNITIVE_ACCOUNT_PREFIX = "workshop-openai"
STATE_FILE = ".azure-workshop-keys-state.json"
CREDENTIALS_FILE = "AZURE_WORKSHOP_CREDENTIALS.md"
PROJECT_URL = "https://github.com/confluentinc/quickstart-streaming-agents"

# Model deployment configurations
DEPLOYMENTS = {
    "gpt-4o": {
        "model": "gpt-4o",
        "version": "2024-08-06",
        "capacity": 50
    },
    "text-embedding-3-large": {
        "model": "text-embedding-3-large",
        "version": "1",
        "capacity": 120
    }
}


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)


def check_azure_cli_login() -> bool:
    """
    Check if user is authenticated to Azure CLI by attempting to get an access token.

    This is more reliable than 'az account show' which can return cached data
    even when not authenticated.

    Returns:
        True if authenticated and can get token, False otherwise
    """
    try:
        import subprocess
        # Try to get an access token - this requires active authentication
        result = subprocess.run(
            ["az", "account", "get-access-token"],
            capture_output=True,
            text=True,
            timeout=5
        )
        # If we can get a token, we're authenticated
        return result.returncode == 0
    except FileNotFoundError:
        # az command not found
        return False
    except Exception:
        # Any other error means not authenticated
        return False


def generate_random_id(length: int = 6) -> str:
    """
    Generate random alphanumeric ID for resource naming.

    Args:
        length: Length of random string

    Returns:
        Random lowercase alphanumeric string
    """
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def get_tags(project_root: Path, owner_email: str) -> Dict[str, str]:
    """
    Build Azure resource tags matching Terraform pattern.

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
        "ManagedBy": "azure-workshop-key-manager",
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
        "Enter owner email (for Azure resource tagging)",
        default=""
    )


def get_azure_region(project_root: Path) -> str:
    """
    Get Azure region for workshop mode.

    IMPORTANT: Azure workshop mode MUST use eastus2 because the hardcoded
    MongoDB clusters for Lab2 and Lab3 are located in eastus2. Using any
    other region will cause MongoDB connection failures.

    Args:
        project_root: Project root directory

    Returns:
        Azure region (always 'eastus2' for workshop mode)
    """
    # Workshop mode MUST use eastus2 for MongoDB connectivity
    print("\n" + "=" * 70)
    print("IMPORTANT: Azure workshop mode requires eastus2 region")
    print("=" * 70)
    print("\nThe hardcoded MongoDB clusters for Lab2 and Lab3 are in eastus2.")
    print("Using any other region will cause connection failures.")
    print("Region will be set to: eastus2")
    print("=" * 70 + "\n")

    return "eastus2"


def get_subscription_id(credential) -> str:
    """
    Get Azure subscription ID from az CLI or environment.

    Args:
        credential: Azure credential object

    Returns:
        Subscription ID

    Raises:
        Exception if no subscription found
    """
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
    """
    Create Azure resource group if it doesn't exist.

    Args:
        resource_client: Azure Resource Management client
        resource_group_name: Name of resource group to create
        region: Azure region
        tags: Tags to apply
        logger: Logger instance
    """
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
    """
    Create Azure Cognitive Services account (OpenAI).

    Args:
        cognitive_client: Azure Cognitive Services Management client
        resource_group_name: Resource group name
        account_name: Cognitive account name
        region: Azure region
        tags: Tags to apply
        logger: Logger instance

    Returns:
        Endpoint URL for the created account
    """
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
    """
    Create Azure OpenAI model deployment.

    Args:
        cognitive_client: Azure Cognitive Services Management client
        resource_group_name: Resource group name
        account_name: Cognitive account name
        deployment_name: Name for the deployment
        model_name: Model to deploy (e.g., 'gpt-4o')
        model_version: Model version
        capacity: Tokens-per-minute capacity
        logger: Logger instance
    """
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
            name="Standard",
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
    """
    Retrieve API key for Cognitive Services account.

    Args:
        cognitive_client: Azure Cognitive Services Management client
        resource_group_name: Resource group name
        account_name: Cognitive account name
        logger: Logger instance

    Returns:
        API key
    """
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
    """
    Test Azure OpenAI credentials by making API calls.

    Args:
        endpoint: Azure OpenAI endpoint URL
        api_key: Azure OpenAI API key
        logger: Logger instance

    Returns:
        True if test succeeded, False otherwise
    """
    from .test_azure_openai_credentials import test_azure_openai_credentials as test_func

    logger.info("Testing Azure OpenAI credentials...")

    return test_func(endpoint, api_key, logger)


def save_state(
    project_root: Path,
    resource_group: str,
    cognitive_account: str,
    deployments: list,
    endpoint: str,
    region: str,
    owner_email: str,
    logger: logging.Logger
) -> None:
    """
    Save state information for destroy command.

    Args:
        project_root: Project root directory
        resource_group: Resource group name
        cognitive_account: Cognitive account name
        deployments: List of deployment names
        endpoint: Azure OpenAI endpoint
        region: Azure region
        owner_email: Owner email
        logger: Logger instance
    """
    state_file = project_root / STATE_FILE

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


def save_credentials_file(
    project_root: Path,
    endpoint: str,
    api_key: str,
    region: str,
    resource_group: str,
    cognitive_account: str,
    logger: logging.Logger
) -> None:
    """
    Save credentials to markdown file with usage instructions.

    Args:
        project_root: Project root directory
        endpoint: Azure OpenAI endpoint
        api_key: Azure OpenAI API key
        region: Azure region
        resource_group: Resource group name
        cognitive_account: Cognitive account name
        logger: Logger instance
    """
    creds_file = project_root / CREDENTIALS_FILE

    content = f"""# Azure Workshop Credentials

**Created:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

## IMPORTANT: Region Requirement

**Azure workshop mode MUST use region: eastus2**

The hardcoded MongoDB clusters for Lab2 and Lab3 are located in eastus2.
Using any other region will cause MongoDB connection failures.

## Azure OpenAI Credentials

Use these credentials when running `uv run deploy --workshop --cloud azure`:

```
Azure OpenAI Endpoint: {endpoint}
Azure OpenAI API Key:  {api_key}
Azure Region:          eastus2
```

## Available Models

- **gpt-4o** (Chat completions, version: 2024-08-06, capacity: 50 TPM)
- **text-embedding-3-large** (Embeddings, version: 1, capacity: 120 TPM)

## Usage Instructions

### For Workshop Participants

1. Clone the repository:
   ```bash
   git clone https://github.com/confluentinc/quickstart-streaming-agents
   cd quickstart-streaming-agents
   ```

2. Run deployment in workshop mode for Azure:
   ```bash
   uv run deploy --workshop --cloud azure
   ```

3. When prompted, enter the credentials above:
   - Azure OpenAI Endpoint: `{endpoint}`
   - Azure OpenAI API Key: `{api_key}`
   - **IMPORTANT**: When asked for region, the deployment will auto-select eastus2

## Security Notes

- **Do NOT commit these credentials to Git**
- These credentials provide access only to the workshop Azure OpenAI account
- No broader Azure subscription access is granted
- Keys should be revoked immediately after the workshop
- Each participant will use the same shared credentials

## After Workshop (For Organizers)

To revoke these credentials and clean up resources, run:

```bash
uv run azure-workshop-keys destroy
```

This will:
1. Delete model deployments (gpt-4o, text-embedding-3-large)
2. Ask if you want to delete the entire resource group
3. Clean up state files

---

**Resource Group:** `{resource_group}`
**Cognitive Account:** `{cognitive_account}`
**Deployments:** gpt-4o, text-embedding-3-large
**Region:** {region}
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
    Create Azure OpenAI resources for workshop.

    Args:
        args: Command line arguments
        logger: Logger instance

    Returns:
        Exit code (0 for success, 1 for error)
    """
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
        resource_group_name = f"{RESOURCE_GROUP_PREFIX}-{random_id}"
        account_name = f"{COGNITIVE_ACCOUNT_PREFIX}-{random_id}"

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
        for deployment_name, config in DEPLOYMENTS.items():
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
        save_state(
            project_root,
            resource_group_name,
            account_name,
            deployment_names,
            endpoint,
            region,
            owner_email,
            logger
        )
        save_credentials_file(
            project_root,
            endpoint,
            api_key,
            region,
            resource_group_name,
            account_name,
            logger
        )

        print("=" * 70)
        print("✓ AZURE WORKSHOP CREDENTIALS CREATED SUCCESSFULLY")
        print("=" * 70)
        print(f"\nCredentials saved to: {CREDENTIALS_FILE}")
        print(f"State saved to:       {STATE_FILE}")
        print("\nNext steps:")
        print("1. Review the credentials in AZURE_WORKSHOP_CREDENTIALS.md")
        print("2. Share credentials with workshop participants")
        print("3. After workshop, run: uv run azure-workshop-keys destroy")
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


def destroy_command(args: argparse.Namespace, logger: logging.Logger) -> int:
    """
    Destroy workshop credentials and optionally delete resource group.

    Args:
        args: Command line arguments
        logger: Logger instance

    Returns:
        Exit code (0 for success, 1 for error)
    """
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
        state = load_state(project_root)

        if not state:
            print("\n" + "=" * 70)
            print("WARNING: No state file found")
            print("=" * 70)
            print(f"\nNo state file ({STATE_FILE}) found.")
            print("This usually means no credentials were created with this tool,")
            print("or they were already destroyed.")
            print("\nIf you want to manually delete workshop resources:")
            print("1. Azure Portal → Resource Groups")
            print(f"2. Find resource groups starting with '{RESOURCE_GROUP_PREFIX}'")
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
        state_file = project_root / STATE_FILE
        creds_file = project_root / CREDENTIALS_FILE

        if state_file.exists():
            state_file.unlink()
            logger.info(f"✓ Deleted {STATE_FILE}")

        if creds_file.exists():
            creds_file.unlink()
            logger.info(f"✓ Deleted {CREDENTIALS_FILE}")

        print("=" * 70)
        print("✓ AZURE WORKSHOP CREDENTIALS DESTROYED")
        print("=" * 70)
        print("\nDestroyed:")
        print(f"  - Deployments: {', '.join(deployments)}")
        if resource_group_deleted:
            print(f"  - Resource group: {resource_group}")
        elif not args.keep_resource_group:
            print(f"  - Cognitive account: {cognitive_account}")
        print(f"  - State files: {STATE_FILE}, {CREDENTIALS_FILE}")
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


def main():
    """Main entry point for Azure workshop key manager."""
    parser = argparse.ArgumentParser(
        description="Create and manage Azure OpenAI credentials for workshop mode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Day before workshop - create credentials
  %(prog)s create

  # After workshop - revoke credentials
  %(prog)s destroy

  # Keep resource group for reuse
  %(prog)s destroy --keep-resource-group
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Create command
    create_parser = subparsers.add_parser(
        'create',
        help='Create Azure OpenAI resources and credentials'
    )
    create_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    # Destroy command
    destroy_parser = subparsers.add_parser(
        'destroy',
        help='Delete deployments and optionally resource group'
    )
    destroy_parser.add_argument(
        '--keep-resource-group',
        action='store_true',
        help='Keep resource group (for reuse in future workshops)'
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
