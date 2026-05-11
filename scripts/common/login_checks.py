"""
Login verification utilities for Confluent and cloud providers.

Provides functions for:
- Checking Confluent CLI login status
- Checking AWS CLI login status
- Checking Azure CLI login status
"""

import subprocess


def check_confluent_login() -> bool:
    """
    Check if user is logged into Confluent CLI.

    Returns:
        True if logged in, False otherwise
    """
    try:
        result = subprocess.run(
            ["confluent", "environment", "list"],
            capture_output=True, text=True, check=True
        )
        return "ID" in result.stdout and "env-" in result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def attempt_confluent_auto_login(creds: dict) -> bool:
    """Try to log into Confluent Cloud using a credentials dict.

    Reads CONFLUENT_EMAIL (falling back to TF_VAR_owner_email) and
    CONFLUENT_PASSWORD from the provided dict. Returns True on success,
    False if credentials are missing or login fails.
    """
    email = creds.get("CONFLUENT_EMAIL") or creds.get("TF_VAR_owner_email")
    password = creds.get("CONFLUENT_PASSWORD")
    if not email or not password:
        return False
    result = subprocess.run(
        ["confluent", "login", "--save"],
        input=f"{email}\n{password}\n",
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return False
    return check_confluent_login()
