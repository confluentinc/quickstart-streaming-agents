#!/usr/bin/env python3
"""
Simple deployment script for Confluent streaming agents quickstart.
Uses credentials from credentials.env or credentials.json and deploys via Terraform.
"""

import argparse
import os
import sys

from dotenv import dotenv_values, set_key

from scripts.common.credentials import (
    load_or_create_credentials_file,
    load_credentials_json,
    generate_confluent_api_keys
)
from scripts.common.login_checks import check_confluent_login, check_cloud_cli_login
from scripts.common.terraform import get_project_root
from scripts.common.terraform_runner import run_terraform
from scripts.common.tfvars import write_tfvars_for_deployment
from scripts.common.ui import prompt_choice, prompt_with_default

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


def main():
    """Main entry point for deploy."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Simple deployment tool for Confluent streaming agents")
    parser.add_argument("--testing", action="store_true",
                       help="Non-interactive mode using credentials.json (for automated testing)")
    args = parser.parse_args()

    print("=== Simple Deployment Tool ===\n")
    if args.testing:
        print("Running in TESTING mode (non-interactive)\n")

    root = get_project_root()
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
        if "owner_email" in creds and creds["owner_email"]:
            env_vars["TF_VAR_owner_email"] = creds["owner_email"]
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
        deploy_options = [
            "Lab 1: MCP Tool Calling",
            "Lab 2: Vector Search / RAG",
            "Both Labs",
            "Core Infrastructure Only (advanced)"
        ]
        env_choice = prompt_choice("What would you like to deploy?", deploy_options)

        # Map user-friendly choice to deployment targets (core auto-included for labs)
        if env_choice == "Lab 1: MCP Tool Calling":
            envs_to_deploy = ["core", "lab1-tool-calling"]
        elif env_choice == "Lab 2: Vector Search / RAG":
            envs_to_deploy = ["core", "lab2-vector-search"]
        elif env_choice == "Both Labs":
            envs_to_deploy = ["core", "lab1-tool-calling", "lab2-vector-search"]
        else:  # Core Infrastructure Only (advanced)
            envs_to_deploy = ["core"]

        # Step 5: Prompt for required credentials
        print("\n--- Credential Configuration ---")

        # Confluent credentials (always required)
        api_key = prompt_with_default("Confluent Cloud API Key", creds.get("TF_VAR_confluent_cloud_api_key", ""))
        api_secret = prompt_with_default("Confluent Cloud API Secret", creds.get("TF_VAR_confluent_cloud_api_secret", ""))
        set_key(creds_file, "TF_VAR_confluent_cloud_api_key", api_key)
        set_key(creds_file, "TF_VAR_confluent_cloud_api_secret", api_secret)

        # Owner email (optional, for resource tagging)
        owner_email = prompt_with_default("Owner Email (optional, for AWS/Azure resource tagging)", creds.get("TF_VAR_owner_email", ""))
        if owner_email:
            set_key(creds_file, "TF_VAR_owner_email", owner_email)

        # Azure subscription ID (if Azure core)
        if cloud == "azure" and "core" in envs_to_deploy:
            azure_sub = prompt_with_default("Azure Subscription ID", creds.get("TF_VAR_azure_subscription_id", ""))
            set_key(creds_file, "TF_VAR_azure_subscription_id", azure_sub)

        # Lab-specific credentials
        if "lab1-tool-calling" in envs_to_deploy or env_choice == "all":
            zapier_endpoint = prompt_with_default("Zapier SSE Endpoint (Lab 1 only)", creds.get("TF_VAR_zapier_sse_endpoint", ""))
            set_key(creds_file, "TF_VAR_zapier_sse_endpoint", zapier_endpoint)

        if "lab2-vector-search" in envs_to_deploy or env_choice == "all":
            mongo_conn = prompt_with_default("MongoDB Connection String (Lab 2 only)", creds.get("TF_VAR_mongodb_connection_string", ""))
            mongo_user = prompt_with_default("MongoDB Username (Lab 2 only)", creds.get("TF_VAR_mongodb_username", ""))
            mongo_pass = prompt_with_default("MongoDB Password (Lab 2 only)", creds.get("TF_VAR_mongodb_password", ""))
            set_key(creds_file, "TF_VAR_mongodb_connection_string", mongo_conn)
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


if __name__ == "__main__":
        main()
