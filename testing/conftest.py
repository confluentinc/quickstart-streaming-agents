"""Pytest configuration and shared fixtures for workshop tests."""

import json
import os
import subprocess
import shutil
import sys
from pathlib import Path
from typing import Dict, Any, List
import pytest


# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
TESTING_DIR = Path(__file__).parent

# Test session environment flags
RESUME_MODE = os.environ.get("PYTEST_RESUME", "false").lower() == "true"
KEEP_STATEMENTS = os.environ.get("PYTEST_KEEP_STATEMENTS", "false").lower() == "true"
FAIL_FAST = os.environ.get("PYTEST_FAIL_FAST", "false").lower() == "true"

_failures: List = []


# --- Session hooks ---

def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.failed:
        _failures.append(report)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    if _failures:
        _write_failure_summary(_failures)
        if _is_interactive() and _claude_available():
            try:
                answer = input("\nTests failed. Launch Claude to investigate? [y/N] ")
                if answer.strip().lower() == "y":
                    summary_path = PROJECT_ROOT / "testing" / "reports" / "failure_summary.md"
                    subprocess.Popen(["claude", "--add-file", str(summary_path)])
            except (EOFError, KeyboardInterrupt):
                pass
    elif exitstatus == 0 and RESUME_MODE and _is_interactive():
        try:
            answer = input(
                "\nTests passed in resume mode. "
                "Run clean validation (delete + recreate all statements)? [y/N] "
            )
            if answer.strip().lower() == "y":
                print("Re-run without PYTEST_RESUME=true to perform a full clean validation.")
        except (EOFError, KeyboardInterrupt):
            pass


def _write_failure_summary(failures: List) -> None:
    path = PROJECT_ROOT / "testing" / "reports" / "failure_summary.md"
    path.parent.mkdir(exist_ok=True)
    lines = ["# Test Failure Summary\n"]
    for report in failures:
        lines.append(f"## `{report.nodeid}`\n")
        if hasattr(report, "longreprtext"):
            lines.append(f"```\n{report.longreprtext}\n```\n")
        elif report.longrepr:
            lines.append(f"```\n{report.longrepr}\n```\n")
    path.write_text("\n".join(lines))
    print(f"\nFailure summary written to: {path}")
    print(
        "To investigate: claude 'investigate the test failures' "
        f"--add-file {path}"
    )


def _is_interactive() -> bool:
    return sys.stdout.isatty() and os.environ.get("CI", "").lower() != "true"


def _claude_available() -> bool:
    return shutil.which("claude") is not None


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
        pytest.skip(
            "Confluent CLI not logged in and no password in credentials.json — "
            "run `confluent login --save` to authenticate"
        )

    if password == "YOUR_PASSWORD_HERE":
        pytest.skip(
            "Confluent CLI not logged in and password not set in testing/credentials.json"
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

    # Validate required fields (password is optional when CLI is already logged in)
    required_fields = [
        "confluent_cloud_api_key",
        "confluent_cloud_api_secret",
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
