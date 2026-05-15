#!/usr/bin/env python3
"""
Simple destruction script for Confluent streaming agents quickstart.
Uses credentials from credentials.env or credentials.json for destruction via Terraform.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values

from .credentials import load_or_create_credentials_file, load_credentials_json
from .login_checks import ensure_confluent_login
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


def strip_stale_lab_state(env_path: Path, root: Path) -> int:
    """
    Remove Flink/SR resources from a lab's tfstate when core credentials are gone.

    When a previous destroy attempted core before labs, it deletes API keys and the
    compute pool while the Kafka cluster survives (blocked by active connectors).
    Those Flink statements and subject configs no longer exist in Confluent Cloud, but
    terraform still tries to DELETE them using the now-invalid credentials → 401 error.

    Detection: core state has the Kafka cluster but no confluent_api_key resources.
    Action: drop confluent_flink_statement and confluent_subject_config from lab state.

    Returns the number of resources removed.
    """
    core_state_path = root / "terraform" / "core" / "terraform.tfstate"
    state_path = env_path / "terraform.tfstate"
    if not core_state_path.exists() or not state_path.exists():
        return 0

    with open(core_state_path) as f:
        core_state = json.load(f)

    core_types = {r["type"] for r in core_state.get("resources", []) if r.get("mode") == "managed"}
    # Only strip when cluster survived but API keys are gone (partial destroy signature)
    if "confluent_kafka_cluster" not in core_types or "confluent_api_key" in core_types:
        return 0

    stale_types = {"confluent_flink_statement", "confluent_subject_config"}
    with open(state_path) as f:
        lab_state = json.load(f)

    stale = [r for r in lab_state.get("resources", []) if r.get("type") in stale_types]
    if not stale:
        return 0

    lab_state["resources"] = [r for r in lab_state["resources"] if r.get("type") not in stale_types]
    lab_state["serial"] = lab_state.get("serial", 0) + 1
    with open(state_path, "w") as f:
        json.dump(lab_state, f, indent=2)
    return len(stale)


def restore_core_outputs(root: Path) -> bool:
    """
    Restore missing outputs in core's tfstate by reading values from resource instances
    and from lab state files.

    A previous partial destroy can clear core's outputs ({}) while leaving the Kafka
    cluster and environment intact (due to active connectors blocking cluster deletion).
    When outputs are empty, lab environment terraform destroys fail immediately because
    lab configs read provider credentials from data.terraform_remote_state.core.outputs.

    Returns True if outputs are present (restored or already populated), False on error.
    """
    core_state_path = root / "terraform" / "core" / "terraform.tfstate"
    lab5_state_path = root / "terraform" / "lab5-insurance-fraud-watson" / "terraform.tfstate"

    if not core_state_path.exists():
        return False

    with open(core_state_path) as f:
        core_state = json.load(f)

    if core_state.get("outputs"):
        return True  # Already populated

    outputs: dict = {}

    # From core resource instances
    for r in core_state.get("resources", []):
        if not r.get("instances"):
            continue
        attrs = r["instances"][0].get("attributes", {})
        if r["type"] == "confluent_environment":
            outputs["confluent_environment_id"] = {"value": attrs.get("id"), "type": "string", "sensitive": False}
            outputs["confluent_environment_display_name"] = {"value": attrs.get("display_name"), "type": "string", "sensitive": False}
        elif r["type"] == "confluent_kafka_cluster":
            outputs["confluent_kafka_cluster_id"] = {"value": attrs.get("id"), "type": "string", "sensitive": False}
            outputs["confluent_kafka_cluster_display_name"] = {"value": attrs.get("display_name"), "type": "string", "sensitive": False}
            outputs["confluent_kafka_cluster_bootstrap_endpoint"] = {"value": attrs.get("bootstrap_endpoint"), "type": "string", "sensitive": False}
            outputs["confluent_kafka_cluster_rest_endpoint"] = {"value": attrs.get("rest_endpoint"), "type": "string", "sensitive": False}
        elif r["type"] == "random_id":
            outputs["random_id"] = {"value": attrs.get("hex"), "type": "string", "sensitive": False}

    # From environment variables (already loaded by destroy.py before this call)
    for env_key, out_key, sensitive in [
        ("TF_VAR_confluent_cloud_api_key", "confluent_cloud_api_key", True),
        ("TF_VAR_confluent_cloud_api_secret", "confluent_cloud_api_secret", True),
        ("TF_VAR_cloud_provider", "cloud_provider", False),
        ("TF_VAR_cloud_region", "cloud_region", False),
    ]:
        val = os.environ.get(env_key, "")
        if val:
            outputs[out_key] = {"value": val, "type": "string", "sensitive": sensitive}

    # From lab5 state (Flink statements and subject configs carry the remaining IDs/keys)
    if lab5_state_path.exists():
        with open(lab5_state_path) as f:
            lab5_state = json.load(f)

        for r in lab5_state.get("resources", []):
            if not r.get("instances"):
                continue
            attrs = r["instances"][0].get("attributes", {})

            if r["type"] == "confluent_flink_statement" and "confluent_flink_compute_pool_id" not in outputs:
                for pool in attrs.get("compute_pool", []):
                    outputs["confluent_flink_compute_pool_id"] = {"value": pool["id"], "type": "string", "sensitive": False}
                for principal in attrs.get("principal", []):
                    outputs["app_manager_service_account_id"] = {"value": principal["id"], "type": "string", "sensitive": False}
                for creds in attrs.get("credentials", []):
                    outputs["app_manager_flink_api_key"] = {"value": creds["key"], "type": "string", "sensitive": True}
                    outputs["app_manager_flink_api_secret"] = {"value": creds["secret"], "type": "string", "sensitive": True}
                rest_ep = attrs.get("rest_endpoint")
                if rest_ep:
                    outputs["confluent_flink_rest_endpoint"] = {"value": rest_ep, "type": "string", "sensitive": False}

            elif r["type"] == "confluent_subject_config" and "confluent_schema_registry_id" not in outputs:
                for creds in attrs.get("credentials", []):
                    outputs["app_manager_schema_registry_api_key"] = {"value": creds["key"], "type": "string", "sensitive": True}
                    outputs["app_manager_schema_registry_api_secret"] = {"value": creds["secret"], "type": "string", "sensitive": True}
                sr_ep = attrs.get("rest_endpoint")
                if sr_ep:
                    outputs["confluent_schema_registry_rest_endpoint"] = {"value": sr_ep, "type": "string", "sensitive": False}
                for sr in attrs.get("schema_registry_cluster", []):
                    outputs["confluent_schema_registry_id"] = {"value": sr["id"], "type": "string", "sensitive": False}

    if not outputs:
        return False

    core_state["outputs"] = outputs
    core_state["serial"] = core_state.get("serial", 0) + 1
    with open(core_state_path, "w") as f:
        json.dump(core_state, f, indent=2)
    return True


def _cleanup_mcp(root: Path) -> None:
    """Remove MCP server config and registration if MCP was installed."""
    mcp_env = root / "terraform" / "core" / "confluent-mcp.env"
    node_modules = root / "node_modules" / "@confluentinc" / "mcp-confluent"

    if not mcp_env.exists() and not node_modules.exists():
        return

    try:
        if mcp_env.exists():
            mcp_env.unlink()

        subprocess.run(
            ["claude", "mcp", "remove", "confluent-cloud-mcp-server", "-s", "local"],
            capture_output=True,
        )

        # Removes the entire node_modules/ tree — assumes @confluentinc/mcp-confluent
        # is the only npm package installed in this project root.
        node_modules_root = root / "node_modules"
        if node_modules_root.exists():
            shutil.rmtree(node_modules_root)

        package_lock = root / "package-lock.json"
        if package_lock.exists():
            package_lock.unlink()

        print("✓ Removed MCP server config and registration")
    except Exception as e:
        print(f"⚠ MCP cleanup failed: {e}")


def main():
    """Main entry point for destroy."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Destroy deployed Confluent streaming agents resources"
    )
    parser.add_argument(
        "--testing",
        action="store_true",
        help="Non-interactive mode using credentials.json (for automated testing)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force-clean local state files even if terraform destroy fails (use when resources are already gone)",
    )
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
        envs_to_destroy = [
            "lab5-insurance-fraud-watson",
            "lab4-pubsec-fraud-agents",
            "lab3-agentic-fleet-management",
            "lab2-vector-search",
            "lab1-tool-calling",
            "core",
        ]  # Reverse order

        # Build environment variables
        env_vars = {
            "TF_VAR_confluent_cloud_api_key": creds["confluent_cloud_api_key"],
            "TF_VAR_confluent_cloud_api_secret": creds["confluent_cloud_api_secret"],
            "TF_VAR_cloud_region": creds["region"],
            "TF_VAR_cloud_provider": cloud,
        }

        # Load optional fields
        if "mcp_token" in creds and creds["mcp_token"]:
            env_vars["TF_VAR_mcp_token"] = creds["mcp_token"]
        if "mongodb_connection_string" in creds and creds["mongodb_connection_string"]:
            env_vars["TF_VAR_mongodb_connection_string"] = creds[
                "mongodb_connection_string"
            ]
        if "mongodb_username" in creds and creds["mongodb_username"]:
            env_vars["TF_VAR_mongodb_username"] = creds["mongodb_username"]
        if "mongodb_password" in creds and creds["mongodb_password"]:
            env_vars["TF_VAR_mongodb_password"] = creds["mongodb_password"]

        # Cloud-specific LLM credentials
        if cloud == "aws":
            if "aws_bedrock_access_key" in creds and creds["aws_bedrock_access_key"]:
                env_vars["TF_VAR_aws_bedrock_access_key"] = creds[
                    "aws_bedrock_access_key"
                ]
            if "aws_bedrock_secret_key" in creds and creds["aws_bedrock_secret_key"]:
                env_vars["TF_VAR_aws_bedrock_secret_key"] = creds[
                    "aws_bedrock_secret_key"
                ]
        if cloud == "azure":
            if "azure_openai_endpoint" in creds and creds["azure_openai_endpoint"]:
                env_vars["TF_VAR_azure_openai_endpoint_raw"] = creds[
                    "azure_openai_endpoint"
                ]
            if "azure_openai_api_key" in creds and creds["azure_openai_api_key"]:
                env_vars["TF_VAR_azure_openai_api_key"] = creds["azure_openai_api_key"]

        # Load into environment
        for key, value in env_vars.items():
            os.environ[key] = value

        print(f"✓ Destroying all resources")
        print(f"  Cloud: {cloud}")
        print(f"  Environments: {', '.join(envs_to_destroy)}")
        print()

    # INTERACTIVE MODE: Original flow
    else:
        # Step 0: Ensure Confluent CLI login
        env_creds = dotenv_values(str(root / "credentials.env"))
        ensure_confluent_login(env_creds)
        print("✓ Confluent CLI logged in")

        # Step 1: Select cloud provider
        cloud = prompt_choice("Select cloud provider to destroy:", ["aws", "azure"])

        # Step 2: Always destroy all environments
        envs_to_destroy = [
            "lab5-insurance-fraud-watson",
            "lab4-pubsec-fraud-agents",
            "lab3-agentic-fleet-management",
            "lab2-vector-search",
            "lab1-tool-calling",
            "core",
        ]
        print(f"✓ Will destroy all environments: {', '.join(envs_to_destroy)}")

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
        print(
            "\n⚠️  WARNING: This will permanently destroy all resources in the selected environments!"
        )

        confirm = input("\nAre you sure you want to proceed? (y/n): ").strip().lower()
        if confirm != "y":
            print("Destroy cancelled.")
            sys.exit(0)

    # Step 5: Restore core outputs if a previous partial destroy cleared them
    print("\n→ Checking core state outputs...")
    core_state_path = root / "terraform" / "core" / "terraform.tfstate"
    if core_state_path.exists():
        if restore_core_outputs(root):
            print("  ✓ Core outputs verified")
        else:
            print("  ⚠ Could not restore core outputs — lab destroys may fail")

    # Step 6: Destroy environments
    print("\n=== Starting Destroy ===")
    any_lab_failed = False
    for env in envs_to_destroy:
        env_path = root / "terraform" / env
        if not env_path.exists():
            print(f"⊘ Skipping {env}: directory does not exist")
            continue

        # Check if terraform state exists (indicates it was deployed)
        state_file = env_path / "terraform.tfstate"
        if not state_file.exists():
            print(f"⊘ Skipping {env}: no terraform state found (never deployed)")
            continue

        # Don't attempt core if a lab environment failed — connectors would still be active
        if env == "core" and any_lab_failed and not args.force:
            print(f"\n✗ Skipping core destroy: lab environment(s) failed above. Fix those errors first, or use --force.")
            continue

        if env != "core":
            stripped = strip_stale_lab_state(env_path, root)
            if stripped:
                print(f"  → Removed {stripped} Flink/SR resources from state (core credentials already deleted)")

        print(f"\n→ Destroying {env}...")
        if run_terraform_destroy(env_path):
            cleanup_terraform_artifacts(env_path)
        elif args.force:
            print(f"  ⚠ Destroy failed but --force set: cleaning local state for {env}")
            cleanup_terraform_artifacts(env_path)
        else:
            if env != "core":
                any_lab_failed = True
            print(
                f"\n✗ Destroy failed at {env}. Use --force to clean local state anyway. Continuing..."
            )

    _cleanup_mcp(root)

    print("\n✓ Destroy process completed!")


if __name__ == "__main__":
    main()
