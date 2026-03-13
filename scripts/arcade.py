#!/usr/bin/env python3
"""
Arcade Mode: Multi-user workshop deployment system.

Deploys up to 25 isolated participant environments in a shared Confluent Cloud
organization. Each participant gets their own environment, cluster, compute pool,
connections, and models for Labs 2, 3, and 4.

Usage:
    uv run arcade deploy                  # Deploy arcade (interactive)
    uv run arcade destroy                 # Tear down ALL arcade resources
    uv run arcade destroy --user 05       # Tear down specific user only
    uv run arcade deploy --add-users 5    # Add 5 more users to existing
    uv run arcade status                  # Show deployment status
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import dotenv_values

from .common.credentials import (
    gather_credentials_interactive,
    load_or_create_credentials_file,
)
from .common.login_checks import check_confluent_login
from .common.terraform import extract_kafka_credentials, get_project_root
from .common.terraform_runner import run_terraform, run_terraform_destroy
from .common.tfvars import (
    generate_core_tfvars_content,
    generate_lab2_tfvars_content,
    generate_lab3_tfvars_content,
    get_credential_value,
    write_tfvars_file,
)
from .common.ui import prompt_choice, prompt_with_default

logger = logging.getLogger(__name__)

PROJECT_ROOT = get_project_root()
ARCADE_DIR = PROJECT_ROOT / "arcade"
STATE_FILE = ARCADE_DIR / "arcade-state.json"

LAB_MODULES = [
    "lab2-vector-search",
    "lab3-agentic-fleet-management",
    "lab4-pubsec-fraud-agents",
]

DEPLOY_ORDER = ["core"] + LAB_MODULES
DESTROY_ORDER = list(reversed(LAB_MODULES)) + ["core"]


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def load_state() -> Dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state: Dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# ---------------------------------------------------------------------------
# Symlink directory creation
# ---------------------------------------------------------------------------

def _tf_files_for_module(module_name: str) -> List[str]:
    """Return the list of .tf files in a shared terraform module directory."""
    module_dir = PROJECT_ROOT / "terraform" / module_name
    return [f.name for f in module_dir.glob("*.tf")]


def create_user_symlink_dir(user_id: str, module_name: str) -> Path:
    """Create a per-user terraform directory with symlinks to shared .tf files."""
    user_tf_dir = ARCADE_DIR / user_id / "terraform" / module_name
    user_tf_dir.mkdir(parents=True, exist_ok=True)

    shared_module_dir = PROJECT_ROOT / "terraform" / module_name

    # Remove all existing .tf symlinks (including dangling ones from deleted files)
    for existing in user_tf_dir.glob("*.tf"):
        if existing.is_symlink():
            existing.unlink()

    for tf_file in shared_module_dir.glob("*.tf"):
        link_path = user_tf_dir / tf_file.name
        link_path.symlink_to(tf_file.resolve())

    return user_tf_dir


def create_org_symlink_dir() -> Path:
    """Create the org-level terraform directory with symlinks."""
    org_dir = ARCADE_DIR / "org"
    org_dir.mkdir(parents=True, exist_ok=True)

    shared_org_dir = PROJECT_ROOT / "terraform" / "arcade-org"

    for existing in org_dir.glob("*.tf"):
        if existing.is_symlink():
            existing.unlink()

    for tf_file in shared_org_dir.glob("*.tf"):
        link_path = org_dir / tf_file.name
        link_path.symlink_to(tf_file.resolve())

    return org_dir


# ---------------------------------------------------------------------------
# Per-user tfvars generation
# ---------------------------------------------------------------------------

def write_user_core_tfvars(
    user_dir: Path,
    cloud: str,
    region: str,
    creds: Dict[str, str],
) -> None:
    """Write core terraform.tfvars for a specific arcade user."""
    api_key = get_credential_value(creds, "confluent_cloud_api_key")
    api_secret = get_credential_value(creds, "confluent_cloud_api_secret")

    content = generate_core_tfvars_content(
        cloud=cloud,
        region=region,
        api_key=api_key,
        api_secret=api_secret,
        cloud_provider=cloud,
        aws_bedrock_access_key=get_credential_value(creds, "aws_bedrock_access_key") if cloud == "aws" else None,
        aws_bedrock_secret_key=get_credential_value(creds, "aws_bedrock_secret_key") if cloud == "aws" else None,
        azure_openai_endpoint=get_credential_value(creds, "azure_openai_endpoint") if cloud == "azure" else None,
        azure_openai_api_key=get_credential_value(creds, "azure_openai_api_key") if cloud == "azure" else None,
    )

    tfvars_path = user_dir / "terraform" / "core" / "terraform.tfvars"
    write_tfvars_file(tfvars_path, content)


def write_user_lab_tfvars(
    user_dir: Path,
    module: str,
    creds: Dict[str, str],
) -> None:
    """Write lab terraform.tfvars for a specific arcade user."""
    if module == "lab2-vector-search":
        mongo_conn = get_credential_value(creds, "mongodb_connection_string") or ""
        mongo_user = get_credential_value(creds, "mongodb_username") or ""
        mongo_pass = get_credential_value(creds, "mongodb_password") or ""
        content = generate_lab2_tfvars_content(mongo_conn, mongo_user, mongo_pass)
    elif module == "lab3-agentic-fleet-management":
        zapier_token = get_credential_value(creds, "zapier_token") or ""
        mongo_conn = get_credential_value(creds, "mongodb_connection_string")
        mongo_user = get_credential_value(creds, "mongodb_username")
        mongo_pass = get_credential_value(creds, "mongodb_password")
        content = generate_lab3_tfvars_content(
            zapier_token, mongo_conn, mongo_user, mongo_pass
        )
    elif module == "lab4-pubsec-fraud-agents":
        content = "# Lab4 Configuration\n"
    else:
        return

    content += 'arcade_mode = true\n'

    tfvars_path = user_dir / "terraform" / module / "terraform.tfvars"
    write_tfvars_file(tfvars_path, content)


# ---------------------------------------------------------------------------
# Terraform operations
# ---------------------------------------------------------------------------

def terraform_init_apply(tf_dir: Path) -> bool:
    """Run terraform init && apply in the given directory."""
    return run_terraform(tf_dir, auto_approve=True)


def terraform_destroy(tf_dir: Path) -> bool:
    """Run terraform init && destroy in the given directory."""
    return run_terraform_destroy(tf_dir, auto_approve=True)


# ---------------------------------------------------------------------------
# Per-user deploy / destroy
# ---------------------------------------------------------------------------

def deploy_user(
    user_id: str,
    creds: Dict[str, str],
    cloud: str,
    region: str,
    arcade_user_id: str,
    state: Dict,
) -> bool:
    """Deploy full infrastructure for one arcade user."""
    user_state = state["users"].setdefault(user_id, {
        "email": "",
        "user_id": arcade_user_id,
        "status": "deploying",
        "phases_completed": [],
    })
    user_state["status"] = "deploying"
    user_state["user_id"] = arcade_user_id

    user_dir = ARCADE_DIR / user_id

    # Deploy core
    if "core" not in user_state["phases_completed"]:
        print(f"\n  [{user_id}] Deploying core...")
        core_dir = create_user_symlink_dir(user_id, "core")
        write_user_core_tfvars(user_dir, cloud, region, creds)
        if not terraform_init_apply(core_dir):
            print(f"  [{user_id}] Core deployment failed!")
            save_state(state)
            return False
        user_state["phases_completed"].append("core")
        # Capture environment info from terraform state
        try:
            core_state_path = core_dir / "terraform.tfstate"
            from .common.terraform import run_terraform_output
            outputs = run_terraform_output(core_state_path)
            user_state["environment_id"] = outputs.get("confluent_environment_id", "")
            user_state["environment_name"] = outputs.get("confluent_environment_display_name", "")
        except Exception as e:
            logger.warning(f"  [{user_id}] Could not read core outputs: {e}")
        # Grant EnvironmentAdmin to the arcade participant.
        # This is required — without it the user sees "no access to any resources".
        if not arcade_user_id:
            print(f"  [{user_id}] Error: no arcade_user_id — cannot grant EnvironmentAdmin")
            save_state(state)
            return False
        if not user_state.get("environment_id"):
            print(f"  [{user_id}] Error: missing environment_id — cannot grant EnvironmentAdmin")
            save_state(state)
            return False
        print(f"  [{user_id}] Granting EnvironmentAdmin role...")
        result = subprocess.run(
            [
                "confluent", "iam", "rbac", "role-binding", "create",
                "--principal", f"User:{arcade_user_id}",
                "--role", "EnvironmentAdmin",
                "--environment", user_state["environment_id"],
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"  [{user_id}] Error: role binding failed: {result.stderr.strip()}")
            save_state(state)
            return False
        print(f"  [{user_id}] EnvironmentAdmin granted ✓")
        save_state(state)
        print(f"  [{user_id}] core ✓")

    # Deploy labs
    for lab in LAB_MODULES:
        if lab not in user_state["phases_completed"]:
            print(f"  [{user_id}] Deploying {lab}...")
            lab_dir = create_user_symlink_dir(user_id, lab)
            write_user_lab_tfvars(user_dir, lab, creds)
            if not terraform_init_apply(lab_dir):
                print(f"  [{user_id}] {lab} deployment failed!")
                save_state(state)
                return False
            user_state["phases_completed"].append(lab)
            save_state(state)
            print(f"  [{user_id}] {lab} ✓")

    user_state["status"] = "deployed"
    save_state(state)
    return True


def run_datagen_for_user(
    user_id: str,
    cloud: str,
    state: Dict,
) -> None:
    """Run datagen for labs 3 and 4 using the user's terraform state."""
    user_state = state["users"].get(user_id, {})
    user_dir = ARCADE_DIR / user_id
    phases = user_state.get("phases_completed", [])

    # Lab 3 datagen
    if "lab3-agentic-fleet-management" in phases and "datagen-lab3" not in phases:
        print(f"  [{user_id}] Running Lab 3 datagen...")
        try:
            creds = extract_kafka_credentials(cloud, project_root=user_dir)
            from .publish_lab3_data import Lab3DataPublisher

            data_file = PROJECT_ROOT / "assets" / "lab3" / "data" / "ride_requests.jsonl"
            if data_file.exists():
                publisher = Lab3DataPublisher(
                    bootstrap_servers=creds["bootstrap_servers"],
                    kafka_api_key=creds["kafka_api_key"],
                    kafka_api_secret=creds["kafka_api_secret"],
                )
                results = publisher.publish_jsonl_file(data_file, "ride_requests")
                publisher.close()
                print(f"  [{user_id}] Lab 3 datagen: {results['success']}/{results['total']} published")
                user_state["phases_completed"].append("datagen-lab3")
            else:
                print(f"  [{user_id}] Lab 3 data file not found: {data_file}")
        except Exception as e:
            print(f"  [{user_id}] Lab 3 datagen failed: {e}")
        save_state(state)

    # Lab 4 datagen
    if "lab4-pubsec-fraud-agents" in phases and "datagen-lab4" not in phases:
        print(f"  [{user_id}] Running Lab 4 datagen...")
        try:
            creds = extract_kafka_credentials(cloud, project_root=user_dir)
            from .lab4_datagen import Lab4DataPublisher

            data_file = PROJECT_ROOT / "assets" / "lab4" / "data" / "fema_claims_synthetic.csv"
            if data_file.exists():
                publisher = Lab4DataPublisher(
                    bootstrap_servers=creds["bootstrap_servers"],
                    kafka_api_key=creds["kafka_api_key"],
                    kafka_api_secret=creds["kafka_api_secret"],
                    schema_registry_url=creds["schema_registry_url"],
                    schema_registry_api_key=creds["schema_registry_api_key"],
                    schema_registry_api_secret=creds["schema_registry_api_secret"],
                )
                results = publisher.publish_csv_file(data_file, "claims")
                publisher.close()
                print(f"  [{user_id}] Lab 4 datagen: {results['success']}/{results['total']} published")
                user_state["phases_completed"].append("datagen-lab4")
            else:
                print(f"  [{user_id}] Lab 4 data file not found: {data_file}")
        except Exception as e:
            print(f"  [{user_id}] Lab 4 datagen failed: {e}")
        save_state(state)

    if "datagen-lab3" in user_state.get("phases_completed", []) and \
       "datagen-lab4" in user_state.get("phases_completed", []):
        user_state["status"] = "ready"
        save_state(state)


def destroy_user(user_id: str, state: Dict) -> bool:
    """Destroy all infrastructure for one arcade user (labs reverse, then core)."""
    user_dir = ARCADE_DIR / user_id / "terraform"

    for module in DESTROY_ORDER:
        tf_dir = user_dir / module
        state_file = tf_dir / "terraform.tfstate"
        if not tf_dir.exists() or not state_file.exists():
            continue
        print(f"  [{user_id}] Destroying {module}...")
        if not terraform_destroy(tf_dir):
            print(f"  [{user_id}] Destroy failed for {module}")
            return False
        print(f"  [{user_id}] {module} destroyed ✓")

    # Remove user directory
    user_full_dir = ARCADE_DIR / user_id
    if user_full_dir.exists():
        shutil.rmtree(user_full_dir)

    # Update state
    if user_id in state.get("users", {}):
        del state["users"][user_id]
    save_state(state)
    return True


# ---------------------------------------------------------------------------
# Credential sheet generation
# ---------------------------------------------------------------------------

def generate_credentials_sheet(state: Dict) -> None:
    """Generate the credentials-sheet.md with login info for all users."""
    arcade_name = state.get("arcade_name", "arcade")
    sheet_path = ARCADE_DIR / "credentials-sheet.md"

    lines = [
        f"# Arcade Credentials — {arcade_name}",
        "",
        "## Login: https://confluent.cloud/login",
        "",
        "| # | Email | Password | Environment |",
        "|---|-------|----------|-------------|",
    ]

    for user_id in sorted(state.get("users", {}).keys()):
        user = state["users"][user_id]
        num = user_id.replace("user-", "")
        email = user.get("email", "")
        env_name = user.get("environment_name", "")
        password = f"Arcade-{num}!"
        lines.append(f"| {num} | {email} | {password} | {env_name} |")

    lines.extend([
        "",
        "## Available Labs",
        "- Lab 2: Vector Search / RAG Pipeline",
        "- Lab 3: Agentic Fleet Management",
        "- Lab 4: Insurance Claims Fraud Detection",
        "",
        "## Notes",
        "- Data has been pre-generated for Labs 3 and 4",
        "- Follow the LAB[2-4]-Walkthrough.md documents",
        "",
    ])

    with open(sheet_path, "w") as f:
        f.write("\n".join(lines))
    print(f"\n✓ Credentials sheet written to {sheet_path}")


# ---------------------------------------------------------------------------
# Email generation
# ---------------------------------------------------------------------------

def generate_emails(email_prefix: str, arcade_name: str, start: int, count: int) -> List[str]:
    """Generate plus-addressed emails for participants."""
    local_part, domain = email_prefix.split("@", 1)
    return [
        f"{local_part}+{arcade_name}-{i:02d}@{domain}"
        for i in range(start, start + count)
    ]


# ---------------------------------------------------------------------------
# Deploy command
# ---------------------------------------------------------------------------

def cmd_deploy(args: argparse.Namespace) -> int:
    # Preflight
    if not _preflight_checks():
        return 1

    state = load_state()

    # Handle --add-users to an existing deployment
    if args.add_users and state.get("users"):
        return _add_users(state, args.add_users)

    # If resuming an existing deployment
    if state.get("users"):
        print(f"\nExisting arcade deployment found: {state.get('arcade_name', '?')}")
        print(f"  Users: {len(state['users'])}")
        incomplete = [
            uid for uid, u in state["users"].items()
            if u.get("status") != "ready"
        ]
        if incomplete:
            print(f"  Incomplete: {', '.join(incomplete)}")
            resume = input("\nResume deployment? (y/n): ").strip().lower()
            if resume == "y":
                return _resume_deploy(state)
            else:
                print("Use 'uv run arcade destroy' first to start fresh, or --add-users N to expand.")
                return 0
        else:
            print("  All users are ready. Use --add-users N to add more.")
            return 0

    # Fresh deployment — gather arcade-specific inputs
    print("\n--- Arcade Configuration ---")
    event_name = prompt_with_default(
        "Event name (used in attendee email addresses, e.g. summit-2025)"
    )
    num_users_str = prompt_with_default("Number of participants (1-25)", "5")
    try:
        num_users = max(1, min(25, int(num_users_str)))
    except ValueError:
        print(f"Invalid number: {num_users_str}, using default of 5")
        num_users = 5
    email_prefix = prompt_with_default(
        "Host email address (attendees log in as <you>+<event>-NN@domain)"
    )

    # Cloud provider selection (same as deploy)
    cloud = prompt_choice("Cloud provider:", ["aws", "azure"])
    region = "us-east-1" if cloud == "aws" else "eastus2"

    # Promo code
    promo_code = prompt_with_default("Confluent Cloud promo code")
    print(f"\nApplying promo code: {promo_code}")
    try:
        subprocess.run(
            ["confluent", "billing", "promo", "add", promo_code],
            check=True,
        )
        print("✓ Promo code applied")
    except subprocess.CalledProcessError as e:
        print(f"Warning: Promo code application returned an error: {e}")
        cont = input("Continue anyway? (y/n): ").strip().lower()
        if cont != "y":
            return 1

    # Gather all credentials via the shared interactive flow
    # (API key generation offer, LLM keys, Zapier, validation — same as uv run deploy)
    arcade_envs = ["core"] + list(LAB_MODULES)
    creds_file, creds = gather_credentials_interactive(PROJECT_ROOT, cloud, arcade_envs)

    api_key = get_credential_value(creds, "confluent_cloud_api_key")
    api_secret = get_credential_value(creds, "confluent_cloud_api_secret")

    # Initialize state
    emails = generate_emails(email_prefix, event_name, 1, num_users)
    state = {
        "arcade_name": event_name,
        "cloud": cloud,
        "region": region,
        "email_prefix": email_prefix,
        "promo_code": promo_code,
        "labs": [m for m in LAB_MODULES],
        "users": {},
    }
    for i, email in enumerate(emails, 1):
        uid = f"user-{i:02d}"
        state["users"][uid] = {
            "email": email,
            "user_id": "",
            "status": "pending",
            "phases_completed": [],
        }
    save_state(state)

    # Step 2: Create invitations
    print("\n=== Step 1: Creating Invitations ===")
    org_dir = create_org_symlink_dir()
    org_tfvars = f"""confluent_cloud_api_key    = "{api_key}"
confluent_cloud_api_secret = "{api_secret}"
user_emails = {json.dumps(emails)}
"""
    write_tfvars_file(org_dir / "terraform.tfvars", org_tfvars)

    if not terraform_init_apply(org_dir):
        print("Error: Failed to create invitations")
        return 1

    # Read invitation outputs
    try:
        from .common.terraform import run_terraform_output
        org_state_path = org_dir / "terraform.tfstate"
        outputs = run_terraform_output(org_state_path)
        user_ids_map = outputs.get("user_ids", {})
        for uid, user_data in state["users"].items():
            email = user_data["email"]
            if email in user_ids_map:
                raw = user_ids_map[email]
                user_data["user_id"] = raw[0]["id"] if isinstance(raw, list) else raw
                user_data["phases_completed"].append("invitation")
        save_state(state)
    except Exception as e:
        print(f"Warning: Could not read invitation outputs: {e}")

    # Pause for invitation acceptance
    print("\n" + "=" * 60)
    print("INVITATIONS SENT")
    print("=" * 60)
    for uid in sorted(state["users"]):
        user = state["users"][uid]
        print(f"  {user['email']}")
    print()
    print("Accept each invitation from your inbox:")
    print("  1. Open invitation link (use incognito window)")
    print("  2. Create account with suggested password: Arcade-01!, Arcade-02!, etc.")
    print("  3. Repeat for each user")
    print()
    input("Press Enter when all invitations accepted...")

    # Step 3: Deploy per-user infrastructure
    return _deploy_all_users(state, creds)


def _resume_deploy(state: Dict) -> int:
    """Resume a partially completed deployment."""
    _, creds = load_or_create_credentials_file(PROJECT_ROOT)
    cloud = state["cloud"]
    region = state["region"]

    incomplete = [
        uid for uid in sorted(state["users"])
        if state["users"][uid].get("status") != "ready"
    ]

    if not incomplete:
        print("All users are fully deployed!")
        return 0

    print(f"\nResuming deployment for {len(incomplete)} users...")

    total = len(state["users"])
    for idx, uid in enumerate(incomplete, 1):
        user = state["users"][uid]
        arcade_user_id = user.get("user_id", "")
        if not arcade_user_id:
            print(f"  [{uid}] Skipping — no user_id (invitation not accepted?)")
            continue

        print(f"\n[{idx}/{len(incomplete)}] Deploying {uid}...")
        if not deploy_user(uid, creds, cloud, region, arcade_user_id, state):
            print(f"\nDeployment stopped. Fix the issue above, then resume with:")
            print(f"  uv run arcade deploy")
            return 1
        run_datagen_for_user(uid, cloud, state)

        completed = sum(1 for u in state["users"].values() if u.get("status") == "ready")
        print(f"  Progress: {completed}/{total} users ready")

    generate_credentials_sheet(state)
    _print_final_summary(state)
    return 0


def _deploy_all_users(state: Dict, creds: Dict[str, str]) -> int:
    """Deploy infrastructure for all users in state."""
    cloud = state["cloud"]
    region = state["region"]
    users = sorted(state["users"].keys())
    total = len(users)

    print(f"\n=== Step 2: Deploying Per-User Infrastructure ({total} users) ===")

    for idx, uid in enumerate(users, 1):
        user = state["users"][uid]
        arcade_user_id = user.get("user_id", "")
        if not arcade_user_id:
            print(f"\n[{idx:02d}/{total}] {uid}: Skipping — no user_id")
            continue
        if user.get("status") == "ready":
            print(f"\n[{idx:02d}/{total}] {uid}: Already ready, skipping")
            continue

        print(f"\n[{idx:02d}/{total}] Deploying {uid}...")
        if not deploy_user(uid, creds, cloud, region, arcade_user_id, state):
            print(f"\nDeployment stopped. Fix the issue above, then resume with:")
            print(f"  uv run arcade deploy")
            return 1

    # Step 4: Datagen
    print(f"\n=== Step 3: Data Generation ({total} users) ===")
    for idx, uid in enumerate(users, 1):
        user = state["users"][uid]
        if user.get("status") in ("ready",):
            continue
        print(f"\n[{idx:02d}/{total}] Datagen for {uid}...")
        run_datagen_for_user(uid, cloud, state)

    # Step 5: Credentials sheet
    generate_credentials_sheet(state)
    _print_final_summary(state)
    return 0


def _add_users(state: Dict, count: int) -> int:
    """Add more users to an existing arcade deployment."""
    _, creds = load_or_create_credentials_file(PROJECT_ROOT)
    cloud = state["cloud"]
    region = state["region"]
    arcade_name = state["arcade_name"]
    email_prefix = state["email_prefix"]

    # Find highest existing user number
    existing_nums = []
    for uid in state["users"]:
        try:
            existing_nums.append(int(uid.replace("user-", "")))
        except ValueError:
            pass
    start = max(existing_nums) + 1 if existing_nums else 1

    total_after = start + count - 1
    if total_after > 25:
        print(f"Error: Adding {count} users would exceed 25 total ({total_after})")
        return 1

    # Generate new emails
    new_emails = generate_emails(email_prefix, arcade_name, start, count)
    for i, email in enumerate(new_emails):
        uid = f"user-{start + i:02d}"
        state["users"][uid] = {
            "email": email,
            "user_id": "",
            "status": "pending",
            "phases_completed": [],
        }
    save_state(state)

    # Update org module — include ALL emails
    all_emails = [u["email"] for u in state["users"].values()]
    api_key = get_credential_value(creds, "confluent_cloud_api_key")
    api_secret = get_credential_value(creds, "confluent_cloud_api_secret")

    org_dir = create_org_symlink_dir()
    org_tfvars = f"""confluent_cloud_api_key    = "{api_key}"
confluent_cloud_api_secret = "{api_secret}"
user_emails = {json.dumps(all_emails)}
"""
    write_tfvars_file(org_dir / "terraform.tfvars", org_tfvars)

    print(f"\nAdding {count} new users (user-{start:02d} to user-{start + count - 1:02d})...")
    if not terraform_init_apply(org_dir):
        print("Error: Failed to update invitations")
        return 1

    # Read updated invitation outputs
    try:
        from .common.terraform import run_terraform_output
        outputs = run_terraform_output(org_dir / "terraform.tfstate")
        user_ids_map = outputs.get("user_ids", {})
        for uid, user_data in state["users"].items():
            email = user_data["email"]
            if email in user_ids_map and not user_data.get("user_id"):
                raw = user_ids_map[email]
                user_data["user_id"] = raw[0]["id"] if isinstance(raw, list) else raw
                if "invitation" not in user_data["phases_completed"]:
                    user_data["phases_completed"].append("invitation")
        save_state(state)
    except Exception as e:
        print(f"Warning: Could not read invitation outputs: {e}")

    # Pause for new invitations
    print("\n" + "=" * 60)
    print("NEW INVITATIONS SENT")
    print("=" * 60)
    for email in new_emails:
        print(f"  {email}")
    print()
    input("Press Enter when new invitations accepted...")

    # Deploy new users only
    new_uids = [f"user-{start + i:02d}" for i in range(count)]
    for idx, uid in enumerate(new_uids, 1):
        user = state["users"][uid]
        arcade_user_id = user.get("user_id", "")
        if not arcade_user_id:
            print(f"\n[{idx}/{count}] {uid}: Skipping — no user_id")
            continue
        print(f"\n[{idx}/{count}] Deploying {uid}...")
        if deploy_user(uid, creds, cloud, region, arcade_user_id, state):
            run_datagen_for_user(uid, cloud, state)

    generate_credentials_sheet(state)
    _print_final_summary(state)
    return 0


# ---------------------------------------------------------------------------
# Destroy command
# ---------------------------------------------------------------------------

def cmd_destroy(args: argparse.Namespace) -> int:
    state = load_state()
    if not state.get("users"):
        print("No arcade deployment found.")
        return 0

    # Selective destroy
    if args.user:
        user_id = f"user-{int(args.user):02d}"
        if user_id not in state["users"]:
            print(f"User {user_id} not found in arcade state.")
            return 1

        print(f"\nDestroying {user_id}...")
        confirm = input(f"Are you sure you want to destroy {user_id}? (y/n): ").strip().lower()
        if confirm != "y":
            print("Cancelled.")
            return 0

        if not destroy_user(user_id, state):
            return 1

        # Update org module to remove this user's email
        remaining_emails = [u["email"] for u in state["users"].values()]
        if remaining_emails:
            _, creds = load_or_create_credentials_file(PROJECT_ROOT)
            api_key = get_credential_value(creds, "confluent_cloud_api_key")
            api_secret = get_credential_value(creds, "confluent_cloud_api_secret")
            org_dir = ARCADE_DIR / "org"
            if org_dir.exists():
                org_tfvars = f"""confluent_cloud_api_key    = "{api_key}"
confluent_cloud_api_secret = "{api_secret}"
user_emails = {json.dumps(remaining_emails)}
"""
                write_tfvars_file(org_dir / "terraform.tfvars", org_tfvars)
                terraform_init_apply(org_dir)

        print(f"\n✓ {user_id} destroyed successfully")
        generate_credentials_sheet(state)
        return 0

    # Full destroy
    print(f"\nArcade: {state.get('arcade_name', '?')}")
    print(f"Users: {len(state['users'])}")
    print("\n⚠️  WARNING: This will permanently destroy ALL arcade resources!")
    confirm = input("\nAre you sure? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return 0

    # Destroy all users
    for uid in sorted(state["users"].keys()):
        print(f"\nDestroying {uid}...")
        destroy_user(uid, state)

    # Destroy org module
    org_dir = ARCADE_DIR / "org"
    org_state = org_dir / "terraform.tfstate"
    if org_dir.exists() and org_state.exists():
        print("\nDestroying org invitations...")
        terraform_destroy(org_dir)

    # Prompt to delete arcade directory
    delete_dir = input(f"\nDelete {ARCADE_DIR}/ directory? (y/n): ").strip().lower()
    if delete_dir == "y" and ARCADE_DIR.exists():
        shutil.rmtree(ARCADE_DIR)
        print(f"✓ Removed {ARCADE_DIR}")

    print("\n✓ Arcade destroy completed!")
    return 0


# ---------------------------------------------------------------------------
# Status command
# ---------------------------------------------------------------------------

def cmd_status(args: argparse.Namespace) -> int:
    state = load_state()
    if not state.get("users"):
        print("No arcade deployment found.")
        return 0

    _print_final_summary(state)
    return 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _preflight_checks() -> bool:
    """Verify prerequisites are met."""
    # Confluent CLI
    if not check_confluent_login():
        print("Error: Not logged into Confluent CLI. Run: confluent login")
        return False
    print("✓ Confluent CLI logged in")

    # Terraform
    try:
        subprocess.run(["terraform", "version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Terraform not installed. Visit: https://developer.hashicorp.com/terraform/install")
        return False
    print("✓ Terraform installed")

    return True


def _print_final_summary(state: Dict) -> None:
    """Print deployment status summary."""
    arcade_name = state.get("arcade_name", "?")
    cloud = state.get("cloud", "?")
    region = state.get("region", "?")
    users = state.get("users", {})

    ready = sum(1 for u in users.values() if u.get("status") == "ready")
    deploying = sum(1 for u in users.values() if u.get("status") == "deploying")
    deployed = sum(1 for u in users.values() if u.get("status") == "deployed")
    pending = sum(1 for u in users.values() if u.get("status") == "pending")

    print(f"\n{'=' * 60}")
    print(f"ARCADE STATUS — {arcade_name}")
    print(f"{'=' * 60}")
    print(f"  Cloud:     {cloud} ({region})")
    print(f"  Total:     {len(users)} users")
    print(f"  Ready:     {ready}")
    if deployed:
        print(f"  Deployed:  {deployed} (awaiting datagen)")
    if deploying:
        print(f"  Deploying: {deploying}")
    if pending:
        print(f"  Pending:   {pending}")
    print()

    for uid in sorted(users.keys()):
        u = users[uid]
        status = u.get("status", "?")
        phases = u.get("phases_completed", [])
        env = u.get("environment_name", "")
        phase_str = " ".join(f"{p}✓" for p in phases)
        print(f"  {uid}: [{status}] {env}  {phase_str}")

    print(f"{'=' * 60}")

    sheet = ARCADE_DIR / "credentials-sheet.md"
    if sheet.exists():
        print(f"\nCredentials sheet: {sheet}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Arcade Mode: Multi-user workshop deployment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # deploy
    deploy_parser = subparsers.add_parser("deploy", help="Deploy arcade environments")
    deploy_parser.add_argument("--add-users", type=int, metavar="N",
                               help="Add N more users to existing deployment")

    # destroy
    destroy_parser = subparsers.add_parser("destroy", help="Destroy arcade environments")
    destroy_parser.add_argument("--user", type=str, metavar="NN",
                                help="Destroy only user NN (e.g., 05)")

    # status
    subparsers.add_parser("status", help="Show deployment status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "deploy":
        return cmd_deploy(args)
    elif args.command == "destroy":
        return cmd_destroy(args)
    elif args.command == "status":
        return cmd_status(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
