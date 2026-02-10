#!/usr/bin/env python3
"""
Simple deployment script for Confluent streaming agents quickstart.
Uses credentials from credentials.env or credentials.json and deploys via Terraform.

IMPORTANT: Interactive mode always uses hardcoded regions:
- AWS: us-east-1 (required for workshop mode MongoDB compatibility)
- Azure: eastus2 (required for workshop mode MongoDB compatibility)

Testing mode (--testing flag) respects the region in credentials.json,
allowing developers to override the default regions if needed.
"""

import argparse
import os
import subprocess
import sys

from dotenv import dotenv_values, set_key

from scripts.common.credentials import (
    load_or_create_credentials_file,
    load_credentials_json,
    generate_confluent_api_keys
)
from scripts.common.login_checks import check_confluent_login
from scripts.common.terraform import get_project_root
from scripts.common.terraform_runner import run_terraform
from scripts.common.tfvars import write_tfvars_for_deployment
from scripts.common.ui import prompt_choice, prompt_with_default

# Valid cloud regions (MongoDB M0 free tier compatible)
# NOTE: These are kept for reference and testing mode, but interactive mode
# always uses us-east-1 (AWS) or eastus2 (Azure) for workshop compatibility
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

        # Extract values from JSON (ensure cloud provider is lowercase)
        cloud = creds["cloud"].lower()
        region = creds["region"]
        envs_to_deploy = ["core", "lab1-tool-calling", "lab2-vector-search", "lab3-agentic-fleet-management"]

        # Build environment variables for Terraform
        env_vars = {
            "TF_VAR_confluent_cloud_api_key": creds["confluent_cloud_api_key"],
            "TF_VAR_confluent_cloud_api_secret": creds["confluent_cloud_api_secret"],
            "TF_VAR_cloud_region": region,
            "TF_VAR_cloud_provider": cloud,
        }

        # Optional fields
        if "owner_email" in creds and creds["owner_email"]:
            env_vars["TF_VAR_owner_email"] = creds["owner_email"]
        if "zapier_token" in creds and creds["zapier_token"]:
            env_vars["TF_VAR_zapier_token"] = creds["zapier_token"]
        if "mongodb_connection_string" in creds and creds["mongodb_connection_string"]:
            env_vars["TF_VAR_mongodb_connection_string"] = creds["mongodb_connection_string"]
        if "mongodb_username" in creds and creds["mongodb_username"]:
            env_vars["TF_VAR_mongodb_username"] = creds["mongodb_username"]
        if "mongodb_password" in creds and creds["mongodb_password"]:
            env_vars["TF_VAR_mongodb_password"] = creds["mongodb_password"]

        # Cloud-specific LLM credentials
        if cloud == "aws":
            if "aws_bedrock_access_key" in creds and creds["aws_bedrock_access_key"]:
                env_vars["TF_VAR_aws_bedrock_access_key"] = creds["aws_bedrock_access_key"]
            if "aws_bedrock_secret_key" in creds and creds["aws_bedrock_secret_key"]:
                env_vars["TF_VAR_aws_bedrock_secret_key"] = creds["aws_bedrock_secret_key"]
        if cloud == "azure":
            if "azure_openai_endpoint" in creds and creds["azure_openai_endpoint"]:
                env_vars["TF_VAR_azure_openai_endpoint_raw"] = creds["azure_openai_endpoint"]
            if "azure_openai_api_key" in creds and creds["azure_openai_api_key"]:
                env_vars["TF_VAR_azure_openai_api_key"] = creds["azure_openai_api_key"]

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

        # Step 2: Set cloud region (hardcoded for simplicity)
        # Note: AWS MUST use us-east-1, Azure MUST use eastus2 for workshop mode compatibility
        region = "us-east-1" if cloud == "aws" else "eastus2"
        print(f"Using region: {region} (required for workshop mode compatibility)")

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
            "Lab 3: Agentic Fleet Management",
            "All Labs (Labs 1, 2, and 3)"
        ]
        env_choice = prompt_choice("What would you like to deploy?", deploy_options)

        # Map user-friendly choice to deployment targets (core auto-included for labs)
        if env_choice == "Lab 1: MCP Tool Calling":
            envs_to_deploy = ["core", "lab1-tool-calling"]
        elif env_choice == "Lab 2: Vector Search / RAG":
            envs_to_deploy = ["core", "lab2-vector-search"]
        elif env_choice == "Lab 3: Agentic Fleet Management":
            envs_to_deploy = ["core", "lab3-agentic-fleet-management"]
        elif env_choice == "All Labs (Labs 1, 2, and 3)":
            envs_to_deploy = ["core", "lab1-tool-calling", "lab2-vector-search", "lab3-agentic-fleet-management"]

        # Step 5: Prompt for required credentials
        print("\n--- Credential Configuration ---")

        # Confluent credentials (always required)
        api_key = prompt_with_default("Confluent Cloud API Key", creds.get("TF_VAR_confluent_cloud_api_key", ""))
        api_secret = prompt_with_default("Confluent Cloud API Secret", creds.get("TF_VAR_confluent_cloud_api_secret", ""))
        set_key(creds_file, "TF_VAR_confluent_cloud_api_key", api_key)
        set_key(creds_file, "TF_VAR_confluent_cloud_api_secret", api_secret)

        # Owner email (optional, for resource tagging)
        owner_email = prompt_with_default("Owner Email (for AWS/Azure resource tagging)", creds.get("TF_VAR_owner_email", ""))
        if owner_email:
            set_key(creds_file, "TF_VAR_owner_email", owner_email)

        # AWS Bedrock credentials
        if cloud == "aws":
            aws_bedrock_key = prompt_with_default("AWS Bedrock Access Key", creds.get("TF_VAR_aws_bedrock_access_key", ""))
            aws_bedrock_secret = prompt_with_default("AWS Bedrock Secret Key", creds.get("TF_VAR_aws_bedrock_secret_key", ""))
            set_key(creds_file, "TF_VAR_aws_bedrock_access_key", aws_bedrock_key)
            set_key(creds_file, "TF_VAR_aws_bedrock_secret_key", aws_bedrock_secret)

        # Azure OpenAI credentials
        if cloud == "azure":
            azure_openai_endpoint = prompt_with_default("Azure OpenAI Endpoint", creds.get("TF_VAR_azure_openai_endpoint_raw", ""))
            azure_openai_key = prompt_with_default("Azure OpenAI API Key", creds.get("TF_VAR_azure_openai_api_key", ""))
            set_key(creds_file, "TF_VAR_azure_openai_endpoint_raw", azure_openai_endpoint)
            set_key(creds_file, "TF_VAR_azure_openai_api_key", azure_openai_key)

        # Lab-specific credentials
        if "lab1-tool-calling" in envs_to_deploy or "lab3-agentic-fleet-management" in envs_to_deploy:
            zapier_token = prompt_with_default("Zapier Token (Lab 1 and Lab 3)", creds.get("TF_VAR_zapier_token", ""))
            set_key(creds_file, "TF_VAR_zapier_token", zapier_token)

        # Set cloud region and cloud provider
        set_key(creds_file, "TF_VAR_cloud_region", region)
        set_key(creds_file, "TF_VAR_cloud_provider", cloud)

        # Step 5.5: Validate configurations (advisory only, never blocks deployment)
        needs_zapier = "lab1-tool-calling" in envs_to_deploy or "lab3-agentic-fleet-management" in envs_to_deploy
        needs_mongodb = False  # MongoDB uses terraform defaults

        if needs_zapier:
            print("\n--- Configuration Validation (Advisory Only) ---")

            # Load credentials into environment for validation
            temp_creds = dotenv_values(creds_file)
            for key, value in temp_creds.items():
                if value:
                    os.environ[key] = value

            # Validate Zapier
            if needs_zapier:
                try:
                    result = subprocess.run(
                        ["uv", "run", "validate", "zapier"],
                        cwd=root,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if "ALL VALIDATION CHECKS PASSED" in result.stdout:
                        print("✓ Zapier configuration validated")
                    else:
                        print(result.stdout)
                        response = input("\nZapier validation warnings detected. Continue anyway? (y/n): ")
                        if response.lower() != 'y':
                            sys.exit(1)
                except Exception as e:
                    print(f"⚠ Could not validate Zapier configuration: {e}")
                    print("  (This is advisory only - deployment will continue)")

            # Validate MongoDB
            if needs_mongodb:
                try:
                    result = subprocess.run(
                        ["uv", "run", "validate", "mongodb"],
                        cwd=root,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if "ALL VALIDATION CHECKS PASSED" in result.stdout:
                        print("✓ MongoDB configuration validated")
                    else:
                        print(result.stdout)
                        response = input("\nMongoDB validation warnings detected. Continue anyway? (y/n): ")
                        if response.lower() != 'y':
                            sys.exit(1)
                except Exception as e:
                    print(f"⚠ Could not validate MongoDB configuration: {e}")
                    print("  (This is advisory only - deployment will continue)")

            print()

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
        env_path = root / "terraform" / env
        if not env_path.exists():
            print(f"Warning: {env_path} does not exist, skipping.")
            continue

        if not run_terraform(env_path):
            print(f"\nDeployment failed at {env}. Stopping.")
            sys.exit(1)

    print("\n✓ All deployments completed successfully!")


if __name__ == "__main__":
        main()
