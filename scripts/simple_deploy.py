#!/usr/bin/env python3
"""
Simple deployment script for Confluent streaming agents quickstart.
Uses credentials.env for configuration and deploys via Terraform.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from dotenv import dotenv_values, set_key

# Valid cloud regions (MongoDB M0 free tier compatible)
AWS_REGIONS = [
    "us-east-1", "us-west-2", "sa-east-1",
    "ap-southeast-1", "ap-southeast-2", "ap-south-1",
    "ap-east-1", "ap-northeast-1", "ap-northeast-2"
]

AZURE_REGIONS = [
    "eastus2", "westus", "canadacentral",
    "northeurope", "westeurope", "eastasia", "centralindia"
]


def find_project_root():
    """Find the project root directory."""
    cwd = Path.cwd()
    if (cwd / "aws").exists() or (cwd / "azure").exists():
        return cwd
    if cwd.name == "scripts" and ((cwd.parent / "aws").exists() or (cwd.parent / "azure").exists()):
        return cwd.parent
    print("Error: Cannot find project root. Please run from project root or scripts/ directory.")
    sys.exit(1)


def check_confluent_login():
    """Check if user is logged into Confluent CLI."""
    try:
        result = subprocess.run(
            ["confluent", "environment", "list"],
            capture_output=True, text=True, check=True
        )
        return "ID" in result.stdout and "env-" in result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_cloud_cli_login(cloud):
    """Check if user is logged into AWS or Azure CLI."""
    try:
        if cloud == "aws":
            subprocess.run(["aws", "sts", "get-caller-identity"],
                         capture_output=True, check=True)
        else:  # azure
            subprocess.run(["az", "account", "show"],
                         capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def prompt_choice(prompt_text, options):
    """Prompt user to select from numbered options."""
    print(f"\n{prompt_text}")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    while True:
        choice = input(f"\nEnter choice (1-{len(options)}): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except ValueError:
            pass
        print(f"Invalid choice. Please enter a number between 1 and {len(options)}.")


def prompt_with_default(prompt_text, default=""):
    """Prompt user with optional default value."""
    if default:
        display_default = default if len(default) <= 50 else default[:47] + "..."
        value = input(f"{prompt_text} [current: \"{display_default}\"]: ").strip()
        return value if value else default
    else:
        value = input(f"{prompt_text}: ").strip()
        while not value:
            print("This field is required.")
            value = input(f"{prompt_text}: ").strip()
        return value


def get_credential_value(creds, key):
    """Get credential value, checking both TF_VAR_ prefixed and non-prefixed keys."""
    return creds.get(key) or creds.get(f"TF_VAR_{key}")


def write_tfvars_file(tfvars_path, content):
    """Write terraform.tfvars file with backup of existing file."""
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


def generate_core_tfvars_content(cloud, region, api_key, api_secret, azure_sub_id=None, owner_email=None):
    """Generate terraform.tfvars content for Core module."""
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


def generate_lab1_tfvars_content(zapier_endpoint):
    """Generate terraform.tfvars content for Lab1 module."""
    return f"""# Lab1 Configuration
ZAPIER_SSE_ENDPOINT = "{zapier_endpoint}"
"""


def generate_lab2_tfvars_content(mongo_conn, mongo_user, mongo_pass):
    """Generate terraform.tfvars content for Lab2 module."""
    return f"""# Lab2 Configuration
MONGODB_CONNECTION_STRING = "{mongo_conn}"
mongodb_username = "{mongo_user}"
mongodb_password = "{mongo_pass}"
"""


def write_tfvars_for_deployment(root, cloud, region, creds, envs_to_deploy):
    """Write terraform.tfvars files for all environments being deployed."""

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
        zapier_endpoint = get_credential_value(creds, "ZAPIER_SSE_ENDPOINT")
        if zapier_endpoint:
            lab1_tfvars_path = root / cloud / "lab1-tool-calling" / "terraform.tfvars"
            content = generate_lab1_tfvars_content(zapier_endpoint)
            if write_tfvars_file(lab1_tfvars_path, content):
                print(f"✓ Wrote {lab1_tfvars_path}")

    # Lab2 terraform.tfvars
    if "lab2-vector-search" in envs_to_deploy:
        mongo_conn = get_credential_value(creds, "MONGODB_CONNECTION_STRING")
        mongo_user = get_credential_value(creds, "mongodb_username")
        mongo_pass = get_credential_value(creds, "mongodb_password")

        if mongo_conn and mongo_user and mongo_pass:
            lab2_tfvars_path = root / cloud / "lab2-vector-search" / "terraform.tfvars"
            content = generate_lab2_tfvars_content(mongo_conn, mongo_user, mongo_pass)
            if write_tfvars_file(lab2_tfvars_path, content):
                print(f"✓ Wrote {lab2_tfvars_path}")


def load_or_create_credentials_file(root):
    """Load existing credentials.env or create from example."""
    creds_file = root / "credentials.env"
    example_file = root / "credentials.env.example"

    if creds_file.exists():
        return creds_file, dotenv_values(creds_file)

    if example_file.exists():
        shutil.copy(example_file, creds_file)
        example_file.unlink()
        print(f"\nCreated {creds_file} from example template.")
    else:
        creds_file.touch()
        print(f"\nCreated new {creds_file}.")

    return creds_file, {}


def load_credentials_json(root):
    """Load credentials from credentials.json for automated testing."""
    creds_file = root / "credentials.json"

    if not creds_file.exists():
        print(f"\nError: credentials.json not found at {creds_file}")
        print("Please create credentials.json from tests/credentials.template.json")
        sys.exit(1)

    try:
        with open(creds_file, 'r') as f:
            creds = json.load(f)
    except json.JSONDecodeError as e:
        print(f"\nError: Invalid JSON in credentials.json: {e}")
        sys.exit(1)

    # Validate required fields
    required_fields = ["cloud", "region", "confluent_cloud_api_key", "confluent_cloud_api_secret"]
    missing = [f for f in required_fields if f not in creds or not creds[f]]

    if missing:
        print(f"\nError: Missing required fields in credentials.json: {', '.join(missing)}")
        sys.exit(1)

    return creds


def generate_confluent_api_keys(prefix="ai"):
    """Generate Confluent API keys using CLI."""
    try:
        timestamp = str(int(time.time()))[-6:]
        sa_name = f"{prefix}-setup-sa-{timestamp}"

        print(f"Creating service account: {sa_name}...")
        sa_result = subprocess.run(
            ["confluent", "iam", "service-account", "create", sa_name,
             "--description", f"Service account for {prefix} streaming agents setup"],
            capture_output=True, text=True, check=True
        )

        sa_id = None
        for line in sa_result.stdout.split("\n"):
            if "| ID" in line and "sa-" in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 2 and "ID" in parts[0]:
                    sa_id = parts[1]
                    break

        if not sa_id:
            print("Error: Failed to extract service account ID.")
            return None, None

        print("Creating API key with Cloud Resource Management scope...")
        key_result = subprocess.run(
            ["confluent", "api-key", "create",
             "--service-account", sa_id,
             "--resource", "cloud",
             "--description", f"{prefix} setup key"],
            capture_output=True, text=True, check=True
        )

        api_key = api_secret = None
        for line in key_result.stdout.split("\n"):
            if "API Key" in line and "|" in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 2 and "API Key" in parts[0]:
                    api_key = parts[1]
            elif "API Secret" in line and "|" in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 2 and "API Secret" in parts[0]:
                    api_secret = parts[1]

        if api_key and api_secret:
            print("Assigning OrganizationAdmin role...")
            try:
                subprocess.run(
                    ["confluent", "iam", "rbac", "role-binding", "create",
                     "--principal", f"User:{sa_id}",
                     "--role", "OrganizationAdmin"],
                    capture_output=True, text=True, check=True
                )
                print("✓ API keys generated successfully!")
                return api_key, api_secret
            except subprocess.CalledProcessError:
                print("Warning: Role assignment failed, but API keys were created.")
                return api_key, api_secret

    except subprocess.CalledProcessError as e:
        print(f"Error generating API keys: {e}")

    return None, None


def run_terraform(env_path, auto_approve=True):
    """Run terraform init and apply in the specified environment."""
    print(f"\nInitializing Terraform in {env_path}...")

    try:
        subprocess.run(["terraform", "init"], cwd=env_path, check=True)

        apply_cmd = ["terraform", "apply"]
        if auto_approve:
            apply_cmd.append("-auto-approve")

        print(f"Running terraform apply in {env_path}...")
        subprocess.run(apply_cmd, cwd=env_path, check=True)

        print(f"✓ Deployment successful: {env_path.name}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ Terraform failed in {env_path.name}")
        return False
    except FileNotFoundError:
        print("Error: Terraform not found. Please install Terraform first.")
        sys.exit(1)


def run_terraform_destroy(env_path, auto_approve=True):
    """Run terraform destroy in the specified environment."""
    print(f"\nInitializing Terraform in {env_path}...")

    try:
        subprocess.run(["terraform", "init"], cwd=env_path, check=True)

        destroy_cmd = ["terraform", "destroy"]
        if auto_approve:
            destroy_cmd.append("-auto-approve")

        print(f"Running terraform destroy in {env_path}...")
        subprocess.run(destroy_cmd, cwd=env_path, check=True)

        print(f"✓ Destroy successful: {env_path.name}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ Terraform destroy failed in {env_path.name}")
        return False
    except FileNotFoundError:
        print("Error: Terraform not found. Please install Terraform first.")
        sys.exit(1)


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Simple deployment tool for Confluent streaming agents")
    parser.add_argument("--testing", action="store_true",
                       help="Non-interactive mode using credentials.json (for automated testing)")
    args = parser.parse_args()

    print("=== Simple Deployment Tool ===\n")
    if args.testing:
        print("Running in TESTING mode (non-interactive)\n")

    root = find_project_root()
    print(f"Project root: {root}")

    # TESTING MODE: Load credentials from JSON and skip all prompts
    if args.testing:
        creds = load_credentials_json(root)

        # Extract values from JSON
        cloud = creds["cloud"]
        region = creds["region"]
        envs_to_deploy = ["core", "lab1-tool-calling", "lab2-vector-search"]

        # Build environment variables for Terraform
        env_vars = {
            "TF_VAR_confluent_cloud_api_key": creds["confluent_cloud_api_key"],
            "TF_VAR_confluent_cloud_api_secret": creds["confluent_cloud_api_secret"],
            "TF_VAR_cloud_region": region,
        }

        # Optional fields
        if "zapier_sse_endpoint" in creds and creds["zapier_sse_endpoint"]:
            env_vars["TF_VAR_ZAPIER_SSE_ENDPOINT"] = creds["zapier_sse_endpoint"]
        if "mongodb_connection_string" in creds and creds["mongodb_connection_string"]:
            env_vars["TF_VAR_MONGODB_CONNECTION_STRING"] = creds["mongodb_connection_string"]
        if "mongodb_username" in creds and creds["mongodb_username"]:
            env_vars["TF_VAR_mongodb_username"] = creds["mongodb_username"]
        if "mongodb_password" in creds and creds["mongodb_password"]:
            env_vars["TF_VAR_mongodb_password"] = creds["mongodb_password"]
        if cloud == "azure" and "azure_subscription_id" in creds:
            env_vars["TF_VAR_azure_subscription_id"] = creds["azure_subscription_id"]

        print(f"✓ Credentials loaded from credentials.json")
        print(f"  Cloud: {cloud}")
        print(f"  Region: {region}")
        print(f"  Deploying: {', '.join(envs_to_deploy)}")
        print()

        # Write terraform.tfvars files
        write_tfvars_for_deployment(root, cloud, region, creds, envs_to_deploy)

        # Load into environment
        for key, value in env_vars.items():
            os.environ[key] = value

    # INTERACTIVE MODE: Original flow
    else:
        # Step 0: Check Confluent CLI login
        if not check_confluent_login():
            print("\nError: Not logged into Confluent Cloud.")
            print("Please run: confluent login")
            sys.exit(1)
        print("✓ Confluent CLI logged in")

        # Step 1: Select cloud provider
        cloud = prompt_choice("Select cloud provider:", ["aws", "azure"])

        if not check_cloud_cli_login(cloud):
            print(f"\nError: Not logged into {cloud.upper()} CLI.")
            print(f"Please login using: {'aws configure' if cloud == 'aws' else 'az login'}")
            sys.exit(1)
        print(f"✓ {cloud.upper()} CLI logged in")

        # Step 2: Select cloud region
        regions = AWS_REGIONS if cloud == "aws" else AZURE_REGIONS
        region = prompt_choice("Select cloud region:", regions)

        # Load credentials file
        creds_file, creds = load_or_create_credentials_file(root)

        # Step 3: Generate Confluent API keys (optional)
        generate = input("\nGenerate new Confluent Cloud API keys? (y/n): ").strip().lower()
        if generate == "y":
            api_key, api_secret = generate_confluent_api_keys()
            if api_key and api_secret:
                set_key(creds_file, "TF_VAR_confluent_cloud_api_key", api_key)
                set_key(creds_file, "TF_VAR_confluent_cloud_api_secret", api_secret)
                creds["TF_VAR_confluent_cloud_api_key"] = api_key
                creds["TF_VAR_confluent_cloud_api_secret"] = api_secret

        # Step 4: Select what to deploy
        envs_to_deploy = []
        env_choice = prompt_choice("What to deploy?", ["core", "lab1-tool-calling", "lab2-vector-search", "all"])

        if env_choice == "all":
            envs_to_deploy = ["core", "lab1-tool-calling", "lab2-vector-search"]
        else:
            envs_to_deploy = [env_choice]

        # Step 5: Prompt for required credentials
        print("\n--- Credential Configuration ---")

        # Confluent credentials (always required)
        api_key = prompt_with_default("Confluent Cloud API Key", creds.get("TF_VAR_confluent_cloud_api_key", ""))
        api_secret = prompt_with_default("Confluent Cloud API Secret", creds.get("TF_VAR_confluent_cloud_api_secret", ""))
        set_key(creds_file, "TF_VAR_confluent_cloud_api_key", api_key)
        set_key(creds_file, "TF_VAR_confluent_cloud_api_secret", api_secret)

        # Azure subscription ID (if Azure core)
        if cloud == "azure" and "core" in envs_to_deploy:
            azure_sub = prompt_with_default("Azure Subscription ID", creds.get("TF_VAR_azure_subscription_id", ""))
            set_key(creds_file, "TF_VAR_azure_subscription_id", azure_sub)

        # Lab-specific credentials
        if "lab1-tool-calling" in envs_to_deploy or env_choice == "all":
            zapier_endpoint = prompt_with_default("Zapier SSE Endpoint (Lab 1 only)", creds.get("TF_VAR_ZAPIER_SSE_ENDPOINT", ""))
            set_key(creds_file, "TF_VAR_ZAPIER_SSE_ENDPOINT", zapier_endpoint)

        if "lab2-vector-search" in envs_to_deploy or env_choice == "all":
            mongo_conn = prompt_with_default("MongoDB Connection String (Lab 2 only)", creds.get("TF_VAR_MONGODB_CONNECTION_STRING", ""))
            mongo_user = prompt_with_default("MongoDB Username (Lab 2 only)", creds.get("TF_VAR_mongodb_username", ""))
            mongo_pass = prompt_with_default("MongoDB Password (Lab 2 only)", creds.get("TF_VAR_mongodb_password", ""))
            set_key(creds_file, "TF_VAR_MONGODB_CONNECTION_STRING", mongo_conn)
            set_key(creds_file, "TF_VAR_mongodb_username", mongo_user)
            set_key(creds_file, "TF_VAR_mongodb_password", mongo_pass)

        # Set cloud region
        set_key(creds_file, "TF_VAR_cloud_region", region)

        # Step 6: Show all credentials and confirm
        print("\n--- Configuration Summary ---")
        final_creds = dotenv_values(creds_file)
        for key, value in sorted(final_creds.items()):
            if value:
                print(f"{key}: {value}")

        print(f"\nCloud: {cloud}")
        print(f"Region: {region}")
        print(f"Deploying: {', '.join(envs_to_deploy)}")

        confirm = input("\nReady to deploy? (y/n): ").strip().lower()
        if confirm != "y":
            print("Deployment cancelled.")
            sys.exit(0)

        # Step 6.5: Write terraform.tfvars files
        print()
        write_tfvars_for_deployment(root, cloud, region, final_creds, envs_to_deploy)

        # Step 7: Load credentials into environment and deploy
        for key, value in final_creds.items():
            if value:
                os.environ[key] = value

    print("\n=== Starting Deployment ===")
    for env in envs_to_deploy:
        env_path = root / cloud / env
        if not env_path.exists():
            print(f"Warning: {env_path} does not exist, skipping.")
            continue

        if not run_terraform(env_path):
            print(f"\nDeployment failed at {env}. Stopping.")
            sys.exit(1)

    print("\n✓ All deployments completed successfully!")


def destroy():
    """Destroy deployed resources using Terraform."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Destroy deployed Confluent streaming agents resources")
    parser.add_argument("--testing", action="store_true",
                       help="Non-interactive mode using credentials.json (for automated testing)")
    args = parser.parse_args(sys.argv[2:])  # Skip 'destroy' argument

    print("=== Simple Destroy Tool ===\n")
    if args.testing:
        print("Running in TESTING mode (non-interactive)\n")

    root = find_project_root()
    print(f"Project root: {root}")

    # TESTING MODE: Load from JSON and skip prompts
    if args.testing:
        creds = load_credentials_json(root)
        cloud = creds["cloud"]
        envs_to_destroy = ["lab2-vector-search", "lab1-tool-calling", "core"]  # Reverse order

        # Build environment variables
        env_vars = {
            "TF_VAR_confluent_cloud_api_key": creds["confluent_cloud_api_key"],
            "TF_VAR_confluent_cloud_api_secret": creds["confluent_cloud_api_secret"],
            "TF_VAR_cloud_region": creds["region"],
        }

        # Load optional fields
        if "zapier_sse_endpoint" in creds and creds["zapier_sse_endpoint"]:
            env_vars["TF_VAR_ZAPIER_SSE_ENDPOINT"] = creds["zapier_sse_endpoint"]
        if "mongodb_connection_string" in creds and creds["mongodb_connection_string"]:
            env_vars["TF_VAR_MONGODB_CONNECTION_STRING"] = creds["mongodb_connection_string"]
        if "mongodb_username" in creds and creds["mongodb_username"]:
            env_vars["TF_VAR_mongodb_username"] = creds["mongodb_username"]
        if "mongodb_password" in creds and creds["mongodb_password"]:
            env_vars["TF_VAR_mongodb_password"] = creds["mongodb_password"]
        if cloud == "azure" and "azure_subscription_id" in creds:
            env_vars["TF_VAR_azure_subscription_id"] = creds["azure_subscription_id"]

        # Load into environment
        for key, value in env_vars.items():
            os.environ[key] = value

        print(f"✓ Destroying all resources")
        print(f"  Cloud: {cloud}")
        print(f"  Environments: {', '.join(envs_to_destroy)}")
        print()

    # INTERACTIVE MODE: Original flow
    else:
        # Step 1: Select cloud provider
        cloud = prompt_choice("Select cloud provider to destroy:", ["aws", "azure"])

        # Step 2: Select what to destroy
        env_choice = prompt_choice("What to destroy?", ["core", "lab1-tool-calling", "lab2-vector-search", "all"])

        envs_to_destroy = []
        if env_choice == "all":
            envs_to_destroy = ["lab2-vector-search", "lab1-tool-calling", "core"]  # Reverse order
        else:
            envs_to_destroy = [env_choice]

        # Load credentials file
        creds_file, creds = load_or_create_credentials_file(root)

        # Step 3: Load credentials into environment
        for key, value in creds.items():
            if value:
                os.environ[key] = value

        # Step 4: Show summary and confirm
        print("\n--- Destroy Summary ---")
        print(f"Cloud: {cloud}")
        print(f"Destroying: {', '.join(envs_to_destroy)}")
        print("\n⚠️  WARNING: This will permanently destroy all resources in the selected environments!")

        confirm = input("\nAre you sure you want to proceed? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Destroy cancelled.")
            sys.exit(0)

    # Step 5: Destroy environments
    print("\n=== Starting Destroy ===")
    for env in envs_to_destroy:
        env_path = root / cloud / env
        if not env_path.exists():
            print(f"Warning: {env_path} does not exist, skipping.")
            continue

        if not run_terraform_destroy(env_path):
            print(f"\nDestroy failed at {env}. Continuing with remaining environments...")

    print("\n✓ Destroy process completed!")


if __name__ == "__main__":
    # Check if destroy mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == "destroy":
        destroy()
    else:
        main()
