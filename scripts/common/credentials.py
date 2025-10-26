"""
Credential loading and management utilities.

Provides functions for:
- Loading credentials from credentials.env files
- Loading credentials from credentials.json (for automated testing)
- Generating Confluent Cloud API keys via CLI
"""

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

from dotenv import dotenv_values


def load_or_create_credentials_file(root: Path) -> Tuple[Path, Dict[str, str]]:
    """
    Load existing credentials.env or create from example.

    Args:
        root: Project root directory

    Returns:
        Tuple of (credentials file path, credentials dictionary)
    """
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


def load_credentials_json(root: Path) -> Dict[str, str]:
    """
    Load credentials from credentials.json for automated testing.

    Args:
        root: Project root directory

    Returns:
        Credentials dictionary

    Raises:
        SystemExit: If file not found, invalid JSON, or missing required fields
    """
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


def generate_confluent_api_keys(prefix: str = "ai") -> Tuple[Optional[str], Optional[str]]:
    """
    Generate Confluent API keys using CLI.

    Creates a service account and generates API keys with OrganizationAdmin role.

    Args:
        prefix: Prefix for service account name (default: "ai")

    Returns:
        Tuple of (api_key, api_secret) or (None, None) if generation fails
    """
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
