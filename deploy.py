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
import time

from dotenv import dotenv_values, set_key

from scripts.common.credentials import (
    load_or_create_credentials_file,
    load_credentials_json,
    generate_confluent_api_keys
)
from scripts.common.login_checks import check_confluent_login
from scripts.common.terraform import get_project_root, run_terraform_output
from scripts.common.terraform_runner import run_terraform
from scripts.common.tfvars import write_tfvars_for_deployment
from scripts.common.ui import prompt_choice, prompt_with_default
from scripts.common.validate import validate_aws_bedrock_credentials, validate_azure_openai_credentials

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

# Module-level buffer for Plan B fallback when set_key() fails on Windows
_pending_writes: dict = {}
_write_failed: bool = False


def _save_env_safe(creds_file, key: str, value: str) -> None:
    """Write a key to credentials.env with retry + in-memory fallback.

    Plan A: call set_key() up to 3 times with back-off (handles transient locks
    from Defender scans, OneDrive, etc. on Windows).
    Plan B: if all retries fail, buffer in memory and flush at end of flow via
    _flush_pending_writes(). This preserves auto-generated keys that only exist
    in memory.
    """
    global _write_failed

    if _write_failed:
        # Already in Plan B — buffer for bulk write at the end
        _pending_writes[key] = value
        return

    for attempt in range(3):
        result = set_key(str(creds_file), key, value)
        # set_key returns (key, value, encoding) on success, (None, ...) on failure
        if result[0] is not None:
            check = dotenv_values(str(creds_file))
            if check.get(key) == value:
                return  # verified success
        if attempt < 2:
            time.sleep(0.3 * (attempt + 1))  # 0.3s then 0.6s back-off

    # Plan A exhausted — switch to Plan B
    _write_failed = True
    _pending_writes[key] = value


def _flush_pending_writes(creds_file) -> None:
    """Bulk-write any buffered credentials at the end of the flow (Plan B).

    Called unconditionally at the end of main(); exits with an actionable error
    message if the write cannot be completed.
    """
    if not _pending_writes:
        return

    try:
        existing = dotenv_values(str(creds_file)) if creds_file.exists() else {}
        existing.update(_pending_writes)
        with open(creds_file, "w", encoding="utf-8", newline="\n") as f:
            for k, v in existing.items():
                f.write(f"{k}='{v}'\n")
        # Verify
        check = dotenv_values(str(creds_file))
        for k, v in _pending_writes.items():
            if check.get(k) != v:
                raise ValueError(f"Read-back verification failed for {k}")
    except Exception as e:
        _print_write_error(e)
        sys.exit(1)


def _print_write_error(exc) -> None:
    print(
        f"\n✗ Could not write credentials.env: {exc}\n\n"
        "Common causes on Windows:\n"
        "  • OneDrive/Dropbox is syncing the project folder — pause sync and retry\n"
        "  • Windows Defender or antivirus is scanning the file — add an exclusion\n"
        "  • VS Code or another editor has the file open — close and retry\n"
        "  • Project is in a protected folder (e.g. C:\\Program Files\\) — move it\n"
        "  • Running from a network drive — run from a local drive instead\n",
        file=sys.stderr,
    )


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
        envs_to_deploy = ["core", "lab1-tool-calling", "lab2-vector-search", "lab3-agentic-fleet-management", "lab4-pubsec-fraud-agents", "lab5-insurance-fraud-watson"]

        # Build environment variables for Terraform
        env_vars = {
            "TF_VAR_confluent_cloud_api_key": creds["confluent_cloud_api_key"],
            "TF_VAR_confluent_cloud_api_secret": creds["confluent_cloud_api_secret"],
            "TF_VAR_cloud_region": region,
            "TF_VAR_cloud_provider": cloud,
            "TF_VAR_enable_testing_sql": "true",
        }

        # Optional fields
        if "owner_email" in creds and creds["owner_email"]:
            env_vars["TF_VAR_owner_email"] = creds["owner_email"]
        if "zapier_token" in creds and creds["zapier_token"]:
            env_vars["TF_VAR_zapier_token"] = creds["zapier_token"]
        if "ibmmq_password" in creds and creds["ibmmq_password"]:
            env_vars["TF_VAR_ibmmq_password"] = creds["ibmmq_password"]
        if "activemq_password" in creds and creds["activemq_password"]:
            env_vars["TF_VAR_activemq_password"] = creds["activemq_password"]
        if "schema_registry_auth" in creds and creds["schema_registry_auth"]:
            env_vars["TF_VAR_schema_registry_auth"] = creds["schema_registry_auth"]
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
            if "aws_session_token" in creds and creds["aws_session_token"]:
                env_vars["TF_VAR_aws_session_token"] = creds["aws_session_token"]
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
                _save_env_safe(creds_file, "TF_VAR_confluent_cloud_api_key", api_key)
                _save_env_safe(creds_file, "TF_VAR_confluent_cloud_api_secret", api_secret)
                creds["TF_VAR_confluent_cloud_api_key"] = api_key
                creds["TF_VAR_confluent_cloud_api_secret"] = api_secret

        # Step 4: Select what to deploy
        envs_to_deploy = []
        deploy_options = [
            "Lab 1: MCP Tool Calling",
            "Lab 2: Vector Search / RAG",
            "Lab 3: Agentic Fleet Management",
            "Lab 4: FEMA Fraud Detection",
            "Lab 5: Insurance Fraud Detection with IBM Watson X",
            "All Labs (Labs 1, 2, 3, 4, and 5)"
        ]
        env_choice = prompt_choice("What would you like to deploy?", deploy_options)

        # Map user-friendly choice to deployment targets (core auto-included for labs)
        if env_choice == "Lab 1: MCP Tool Calling":
            envs_to_deploy = ["core", "lab1-tool-calling"]
        elif env_choice == "Lab 2: Vector Search / RAG":
            envs_to_deploy = ["core", "lab2-vector-search"]
        elif env_choice == "Lab 3: Agentic Fleet Management":
            envs_to_deploy = ["core", "lab3-agentic-fleet-management"]
        elif env_choice == "Lab 4: FEMA Fraud Detection":
            envs_to_deploy = ["core", "lab4-pubsec-fraud-agents"]
        elif env_choice == "Lab 5: Insurance Fraud Detection with IBM Watson X":
            envs_to_deploy = ["core", "lab5-insurance-fraud-watson"]
        elif env_choice == "All Labs (Labs 1, 2, 3, 4, and 5)":
            envs_to_deploy = ["core", "lab1-tool-calling", "lab2-vector-search", "lab3-agentic-fleet-management", "lab4-pubsec-fraud-agents", "lab5-insurance-fraud-watson"]

        # Step 5: Prompt for required credentials
        print("\n--- Credential Configuration ---")

        # Confluent credentials (always required)
        api_key = prompt_with_default("Confluent Cloud API Key", creds.get("TF_VAR_confluent_cloud_api_key", ""))
        api_secret = prompt_with_default("Confluent Cloud API Secret", creds.get("TF_VAR_confluent_cloud_api_secret", ""))
        _save_env_safe(creds_file, "TF_VAR_confluent_cloud_api_key", api_key)
        _save_env_safe(creds_file, "TF_VAR_confluent_cloud_api_secret", api_secret)

        # Owner email (optional, for resource tagging)
        owner_email = prompt_with_default("Owner Email (for AWS/Azure resource tagging)", creds.get("TF_VAR_owner_email", ""))
        if owner_email:
            _save_env_safe(creds_file, "TF_VAR_owner_email", owner_email)

        # AWS Bedrock credentials
        if cloud == "aws":
            aws_bedrock_key = prompt_with_default("AWS Bedrock Access Key", creds.get("TF_VAR_aws_bedrock_access_key", ""))
            aws_bedrock_secret = prompt_with_default("AWS Bedrock Secret Key", creds.get("TF_VAR_aws_bedrock_secret_key", ""))
            _save_env_safe(creds_file, "TF_VAR_aws_bedrock_access_key", aws_bedrock_key)
            _save_env_safe(creds_file, "TF_VAR_aws_bedrock_secret_key", aws_bedrock_secret)

            # Prompt for session token if using temporary credentials (ASIA*)
            aws_session_token = ""
            if aws_bedrock_key.startswith("ASIA"):
                aws_session_token = prompt_with_default("AWS Session Token (required for temporary credentials)", creds.get("TF_VAR_aws_session_token", ""))
                if aws_session_token:
                    _save_env_safe(creds_file, "TF_VAR_aws_session_token", aws_session_token)

            # Validate AWS credentials format (advisory only)
            print("\nValidating AWS Bedrock credentials format...")
            passed, messages = validate_aws_bedrock_credentials(aws_bedrock_key, aws_bedrock_secret, aws_session_token)
            for msg in messages:
                print(msg)

            if not passed:
                print("\n⚠️  Credential format validation failed.")
                proceed = input("Do you want to proceed anyway? (y/n): ").strip().lower()
                if proceed != 'y':
                    print("Deployment cancelled. Please correct your credentials and try again.")
                    sys.exit(1)
                print("Proceeding with deployment despite validation warnings...\n")

            # Live Bedrock model access check (advisory)
            if aws_bedrock_key and aws_bedrock_secret:
                import logging
                from scripts.common.test_bedrock_credentials import test_bedrock_credentials, test_titan_embeddings
                _log = logging.getLogger("deploy.bedrock")
                _log.setLevel(logging.CRITICAL)
                print("\nChecking AWS Bedrock model access...")
                _region = "us-east-1"
                sonnet_ok, sonnet_err = test_bedrock_credentials(aws_bedrock_key, aws_bedrock_secret, _region, logger=_log, max_retries=1, session_token=aws_session_token or None)
                titan_ok,  titan_err  = test_titan_embeddings(aws_bedrock_key, aws_bedrock_secret, _region, logger=_log, max_retries=1, session_token=aws_session_token or None)
                print(f"  {'✓' if sonnet_ok else '✗'} Claude Sonnet 4.5 accessible ({_region}){'' if sonnet_ok else f' [{sonnet_err}]'}")
                print(f"  {'✓' if titan_ok  else '✗'} Titan Embeddings accessible ({_region}){'' if titan_ok else f' [{titan_err}]'}")
                if not sonnet_ok or not titan_ok:
                    print()
                    if (sonnet_err == "invalid_keys" or titan_err == "invalid_keys"):
                        print("⚠️  WARNING: AWS credentials were not recognized by Bedrock.")
                        print("   Generate fresh credentials with:  uv run api-keys create aws")
                    else:
                        print("⚠️  WARNING: One or more Bedrock models could not be accessed.")
                        print("   To enable Claude models, visit the AWS Bedrock Model Catalog:")
                        print("     https://console.aws.amazon.com/bedrock/home#/model-catalog")
                        print("   Select Claude Sonnet 4.5 → open in Playground → send a message.")
                        print("   The access request form will appear automatically.")
                    proceed = input("\nContinue anyway? (y/n): ").strip().lower()
                    if proceed != 'y':
                        print("Deployment cancelled.")
                        sys.exit(1)

        # Azure OpenAI credentials
        if cloud == "azure":
            azure_openai_endpoint = prompt_with_default("Azure OpenAI Endpoint", creds.get("TF_VAR_azure_openai_endpoint_raw", ""))
            azure_openai_key = prompt_with_default("Azure OpenAI API Key", creds.get("TF_VAR_azure_openai_api_key", ""))
            _save_env_safe(creds_file, "TF_VAR_azure_openai_endpoint_raw", azure_openai_endpoint)
            _save_env_safe(creds_file, "TF_VAR_azure_openai_api_key", azure_openai_key)

            # Validate Azure credentials format (advisory only)
            print("\nValidating Azure OpenAI credentials format...")
            passed, messages = validate_azure_openai_credentials(azure_openai_endpoint, azure_openai_key)
            for msg in messages:
                print(msg)

            if not passed:
                print("\n⚠️  Credential format validation failed.")
                proceed = input("Do you want to proceed anyway? (y/n): ").strip().lower()
                if proceed != 'y':
                    print("Deployment cancelled. Please correct your credentials and try again.")
                    sys.exit(1)
                print("Proceeding with deployment despite validation warnings...\n")

            # Live Azure OpenAI model access check (advisory)
            if azure_openai_endpoint and azure_openai_key:
                import logging
                from scripts.common.test_azure_openai_credentials import test_azure_openai_chat, test_azure_openai_embeddings
                _log = logging.getLogger("deploy.azure_openai")
                _log.setLevel(logging.CRITICAL)
                print("\nChecking Azure OpenAI model access...")
                chat_ok, chat_err = test_azure_openai_chat(azure_openai_endpoint, azure_openai_key, logger=_log, max_retries=1)
                emb_ok,  emb_err  = test_azure_openai_embeddings(azure_openai_endpoint, azure_openai_key, logger=_log, max_retries=1)
                print(f"  {'✓' if chat_ok else '✗'} gpt-5-mini accessible")
                print(f"  {'✓' if emb_ok  else '✗'} text-embedding-ada-002 accessible")
                if not chat_ok or not emb_ok:
                    print()
                    if chat_err == "invalid_credentials" or emb_err == "invalid_credentials":
                        print("⚠️  WARNING: Azure OpenAI credentials were rejected (401 Unauthorized).")
                        print("   Generate fresh credentials with:  uv run api-keys create azure")
                    else:
                        print("⚠️  WARNING: One or more Azure OpenAI deployments could not be accessed.")
                        print("   Ensure 'gpt-5-mini' and 'text-embedding-ada-002' deployments exist")
                        print("   in your Azure OpenAI resource.")
                    proceed = input("\nContinue anyway? (y/n): ").strip().lower()
                    if proceed != 'y':
                        print("Deployment cancelled.")
                        sys.exit(1)

        # Lab-specific credentials
        if "lab1-tool-calling" in envs_to_deploy or "lab3-agentic-fleet-management" in envs_to_deploy or "lab5-insurance-fraud-watson" in envs_to_deploy:
            zapier_token = prompt_with_default("Zapier Token (Lab 1, Lab 3, and Lab 5)", creds.get("TF_VAR_zapier_token", ""))
            _save_env_safe(creds_file, "TF_VAR_zapier_token", zapier_token)

        if "lab5-insurance-fraud-watson" in envs_to_deploy:
            ibmmq_password = prompt_with_default("IBM MQ Password (Lab 5 — IBM Cloud US South, CLAIMSQM)", creds.get("TF_VAR_ibmmq_password", ""))
            set_key(creds_file, "TF_VAR_ibmmq_password", ibmmq_password)
            activemq_password = prompt_with_default("ActiveMQ Password (Lab 5 — optional, leave blank if unused)", creds.get("TF_VAR_activemq_password", ""))
            if activemq_password:
                set_key(creds_file, "TF_VAR_activemq_password", activemq_password)
            schema_registry_auth = prompt_with_default("Schema Registry Auth (Lab 5 — KEY:SECRET format)", creds.get("TF_VAR_schema_registry_auth", ""))
            if schema_registry_auth:
                set_key(creds_file, "TF_VAR_schema_registry_auth", schema_registry_auth)

        # Set cloud region and cloud provider
        _save_env_safe(creds_file, "TF_VAR_cloud_region", region)
        _save_env_safe(creds_file, "TF_VAR_cloud_provider", cloud)

        # Step 5.5: Validate configurations (advisory only, never blocks deployment)
        needs_zapier  = "lab1-tool-calling" in envs_to_deploy or "lab3-agentic-fleet-management" in envs_to_deploy or "lab5-insurance-fraud-watson" in envs_to_deploy
        needs_mongodb = "lab2-vector-search" in envs_to_deploy or "lab3-agentic-fleet-management" in envs_to_deploy
        needs_lab4    = "lab4-pubsec-fraud-agents" in envs_to_deploy

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

        # Validate workshop MongoDB (lab2 / lab3 use pre-populated workshop data by default)
        if needs_mongodb:
            import logging
            from scripts.common.test_mongodb_credentials import test_workshop_mongodb
            _log = logging.getLogger("deploy.mongodb")
            _log.setLevel(logging.CRITICAL)
            print("\nChecking workshop MongoDB demo data...")
            lab_map = {"lab2-vector-search": "lab2", "lab3-agentic-fleet-management": "lab3"}
            mongo_all_ok = True
            for env_name, lab_key in lab_map.items():
                if env_name not in envs_to_deploy:
                    continue
                ok, err = test_workshop_mongodb(lab_key, cloud, logger=_log)
                print(f"  {'✓' if ok else '✗'} Workshop MongoDB ({lab_key}/{cloud})")
                if not ok:
                    mongo_all_ok = False
            if not mongo_all_ok:
                print()
                print("⚠️  WARNING: The workshop MongoDB demo data could not be reached.")
                print("   This is a Confluent-managed resource. Contact the workshop team")
                print("   or check your network connection.")
                response = input("\nContinue anyway? (y/n): ").strip().lower()
                if response != 'y':
                    sys.exit(1)

        # Validate Lab4 data source
        if needs_lab4:
            import logging
            _log = logging.getLogger("deploy.lab4")
            _log.setLevel(logging.CRITICAL)
            if cloud == "azure":
                from scripts.common.test_cosmosdb_credentials import test_cosmosdb_access
                print("\nChecking Lab4 CosmosDB demo data...")
                ok, err = test_cosmosdb_access(logger=_log)
                print(f"  {'✓' if ok else '✗'} CosmosDB workshop demo data reachable")
                if not ok and err != "no_requests":
                    print()
                    print("⚠️  WARNING: The Lab4 CosmosDB demo database could not be reached.")
                    print("   Contact the workshop team or check your network connection.")
                    response = input("\nContinue anyway? (y/n): ").strip().lower()
                    if response != 'y':
                        sys.exit(1)
            else:
                from scripts.common.test_mongodb_credentials import test_workshop_mongodb
                print("\nChecking Lab4 MongoDB demo data...")
                ok, err = test_workshop_mongodb("lab4", "aws", logger=_log)
                print(f"  {'✓' if ok else '✗'} Workshop MongoDB demo data (lab4/aws) reachable")
                if not ok and err not in ("no_pymongo", "no_config"):
                    print()
                    print("⚠️  WARNING: The Lab4 workshop MongoDB demo database could not be reached.")
                    print("   Contact the workshop team or check your network connection.")
                    response = input("\nContinue anyway? (y/n): ").strip().lower()
                    if response != 'y':
                        sys.exit(1)

        print()

        # Flush any buffered credentials (Plan B fallback for Windows write failures)
        _flush_pending_writes(creds_file)

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

    # Display the environment name
    try:
        core_state_path = root / "terraform" / "core" / "terraform.tfstate"
        if core_state_path.exists():
            core_outputs = run_terraform_output(core_state_path)
            if "confluent_environment_display_name" in core_outputs:
                env_name = core_outputs["confluent_environment_display_name"]
                print(f"\nEnvironment name: {env_name}")
    except Exception as e:
        # Don't fail deployment if we can't read the environment name
        print(f"\n⚠ Could not read environment name: {e}")


if __name__ == "__main__":
        main()
