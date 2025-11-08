#!/usr/bin/env python3
"""
Simple destruction script for Confluent streaming agents quickstart.
Uses credentials from credentials.env or credentials.json for destruction via Terraform.
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

from .credentials import load_or_create_credentials_file, load_credentials_json
from .terraform import get_project_root
from .terraform_runner import run_terraform_destroy
from .ui import prompt_choice


def cleanup_terraform_artifacts(env_path: Path) -> None:
    """
    Remove all terraform artifacts from a directory after successful destroy.

    Removes:
    - *.tfstate* files
    - *.tfvars* files
    - .terraform/ directory
    - .terraform.lock.hcl file
    - FLINK_SQL_COMMANDS.md (auto-generated summary)
    - mcp_commands.txt (legacy file)

    Does NOT remove credentials.env (which is in project root, not env directories).

    Args:
        env_path: Path to terraform environment directory
    """
    try:
        # Remove all .tfstate files (including backups)
        for tfstate_file in env_path.glob("*.tfstate*"):
            tfstate_file.unlink()

        # Remove all .tfvars files (including backups)
        for tfvars_file in env_path.glob("*.tfvars*"):
            tfvars_file.unlink()

        # Remove .terraform directory
        terraform_dir = env_path / ".terraform"
        if terraform_dir.exists():
            shutil.rmtree(terraform_dir)

        # Remove .terraform.lock.hcl file
        lock_file = env_path / ".terraform.lock.hcl"
        if lock_file.exists():
            lock_file.unlink()

        # Remove auto-generated Flink SQL summary file
        flink_sql_summary = env_path / "FLINK_SQL_COMMANDS.md"
        if flink_sql_summary.exists():
            flink_sql_summary.unlink()

        # Remove legacy mcp_commands.txt file
        mcp_commands = env_path / "mcp_commands.txt"
        if mcp_commands.exists():
            mcp_commands.unlink()

    except Exception as e:
        # Silently continue if cleanup fails - destroy was successful
        pass


def main():
    """Main entry point for destroy."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Destroy deployed Confluent streaming agents resources")
    parser.add_argument("--testing", action="store_true",
                       help="Non-interactive mode using credentials.json (for automated testing)")
    args = parser.parse_args()

    print("=== Simple Destroy Tool ===\n")
    if args.testing:
        print("Running in TESTING mode (non-interactive)\n")

    root = get_project_root()
    print(f"Project root: {root}")

    # TESTING MODE: Load from JSON and skip prompts
    if args.testing:
        creds = load_credentials_json(root)
        cloud = creds["cloud"]
        envs_to_destroy = ["lab3-agentic-fleet-management", "lab2-vector-search", "lab1-tool-calling", "core"]  # Reverse order

        # Build environment variables
        workshop_mode = creds.get("workshop", False)
        env_vars = {
            "TF_VAR_confluent_cloud_api_key": creds["confluent_cloud_api_key"],
            "TF_VAR_confluent_cloud_api_secret": creds["confluent_cloud_api_secret"],
            "TF_VAR_cloud_region": creds["region"],
            "TF_VAR_workshop_mode": "true" if workshop_mode else "false",
        }

        # Load optional fields
        if "zapier_sse_endpoint" in creds and creds["zapier_sse_endpoint"]:
            env_vars["TF_VAR_zapier_sse_endpoint"] = creds["zapier_sse_endpoint"]
        if "mongodb_connection_string" in creds and creds["mongodb_connection_string"]:
            env_vars["TF_VAR_mongodb_connection_string"] = creds["mongodb_connection_string"]
        if "mongodb_username" in creds and creds["mongodb_username"]:
            env_vars["TF_VAR_mongodb_username"] = creds["mongodb_username"]
        if "mongodb_password" in creds and creds["mongodb_password"]:
            env_vars["TF_VAR_mongodb_password"] = creds["mongodb_password"]
        if cloud == "azure" and "azure_subscription_id" in creds:
            env_vars["TF_VAR_azure_subscription_id"] = creds["azure_subscription_id"]

        # Workshop mode credentials
        if workshop_mode and cloud == "aws":
            if "aws_bedrock_access_key" in creds and creds["aws_bedrock_access_key"]:
                env_vars["TF_VAR_aws_bedrock_access_key"] = creds["aws_bedrock_access_key"]
            if "aws_bedrock_secret_key" in creds and creds["aws_bedrock_secret_key"]:
                env_vars["TF_VAR_aws_bedrock_secret_key"] = creds["aws_bedrock_secret_key"]

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
        env_choice = prompt_choice("What to destroy?", ["core", "lab1-tool-calling", "lab2-vector-search", "lab3-agentic-fleet-management", "all"])

        envs_to_destroy = []
        if env_choice == "all":
            envs_to_destroy = ["lab3-agentic-fleet-management", "lab2-vector-search", "lab1-tool-calling", "core"]  # Reverse order
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

        if run_terraform_destroy(env_path):
            # Cleanup terraform artifacts after successful destroy
            cleanup_terraform_artifacts(env_path)
        else:
            print(f"\nDestroy failed at {env}. Continuing with remaining environments...")

    print("\n✓ Destroy process completed!")


if __name__ == "__main__":
    main()
