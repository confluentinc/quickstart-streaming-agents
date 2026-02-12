"""Pytest configuration and shared fixtures for workshop tests."""

import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any
import pytest


# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
TESTING_DIR = Path(__file__).parent


def ensure_confluent_cli_installed():
    """Check that confluent CLI is installed.

    Raises:
        pytest.skip: If confluent CLI not found
    """
    if not shutil.which("confluent"):
        pytest.skip(
            "confluent CLI not found. Install from: "
            "https://docs.confluent.io/confluent-cli/current/install.html"
        )


def ensure_confluent_login(credentials: Dict[str, str]):
    """Ensure Confluent CLI is authenticated.

    Args:
        credentials: Credentials dict with confluent_cloud_email/password

    Raises:
        RuntimeError: If login fails or credentials missing
    """
    # Check if already logged in by trying to list environments
    result = subprocess.run(
        ["confluent", "environment", "list"],
        capture_output=True,
        text=True
    )

    # If command succeeds, we're already authenticated
    if result.returncode == 0:
        print("✅ Already logged into Confluent Cloud")
        return

    # Not logged in - attempt automatic login
    email = credentials.get("confluent_cloud_email") or credentials.get("owner_email")
    password = credentials.get("confluent_cloud_password")

    if not email or not password:
        raise RuntimeError(
            "Confluent Cloud login credentials missing.\n"
            "Add 'confluent_cloud_email' and 'confluent_cloud_password' to testing/credentials.json"
        )

    if password == "YOUR_PASSWORD_HERE":
        raise RuntimeError(
            "Please update 'confluent_cloud_password' in testing/credentials.json with your actual password"
        )

    print(f"🔐 Logging into Confluent Cloud as {email}...")

    # Attempt login using email + password
    result = subprocess.run(
        ["confluent", "login", "--save"],
        input=f"{email}\n{password}\n",
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Confluent Cloud login failed:\n{result.stderr}\n"
            "Please verify your email and password in testing/credentials.json"
        )

    # Verify login succeeded
    result = subprocess.run(
        ["confluent", "environment", "list"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError("Login appeared to succeed but cannot list environments")

    print("✅ Successfully logged into Confluent Cloud")


def load_test_credentials(cloud: str) -> Dict[str, Any]:
    """Load credentials from testing/credentials.json and set cloud/region.

    Args:
        cloud: Cloud provider ('aws' or 'azure')

    Returns:
        Credentials dictionary with cloud and region set

    Raises:
        FileNotFoundError: If testing/credentials.json not found
        json.JSONDecodeError: If credentials file is invalid JSON
    """
    creds_file = TESTING_DIR / "credentials.json"

    if not creds_file.exists():
        raise FileNotFoundError(
            f"Credentials file not found: {creds_file}\n"
            f"Copy credentials.template.json to testing/credentials.json "
            f"and fill in your API keys."
        )

    with open(creds_file, "r") as f:
        credentials = json.load(f)

    # Set cloud and region based on test parameter
    credentials["cloud"] = cloud
    if cloud == "aws":
        credentials["region"] = "us-east-1"
    elif cloud == "azure":
        credentials["region"] = "eastus2"
    else:
        raise ValueError(f"Unsupported cloud provider: {cloud}")

    # Validate required fields
    required_fields = [
        "confluent_cloud_api_key",
        "confluent_cloud_api_secret",
        "confluent_cloud_password",
    ]

    # Email can be either confluent_cloud_email or owner_email
    if not credentials.get("confluent_cloud_email") and not credentials.get("owner_email"):
        raise ValueError("Missing required field: confluent_cloud_email or owner_email")

    if cloud == "aws":
        required_fields.extend([
            "aws_bedrock_access_key",
            "aws_bedrock_secret_key",
        ])
    elif cloud == "azure":
        required_fields.extend([
            "azure_openai_endpoint",
            "azure_openai_api_key",
        ])

    missing = [f for f in required_fields if not credentials.get(f)]
    if missing:
        raise ValueError(
            f"Missing required credentials for {cloud}: {', '.join(missing)}"
        )

    return credentials


def write_credentials_to_project_root(credentials: Dict[str, Any]):
    """Write credentials.json to project root for deploy.py --testing.

    Args:
        credentials: Credentials dictionary
    """
    creds_file = PROJECT_ROOT / "credentials.json"
    with open(creds_file, "w") as f:
        json.dump(credentials, f, indent=2)


def remove_credentials_from_project_root():
    """Remove credentials.json from project root (cleanup)."""
    creds_file = PROJECT_ROOT / "credentials.json"
    if creds_file.exists():
        creds_file.unlink()


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get project root directory."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def testing_dir() -> Path:
    """Get testing directory."""
    return TESTING_DIR
