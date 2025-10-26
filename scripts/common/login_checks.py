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


def check_cloud_cli_login(cloud: str) -> bool:
    """
    Check if user is logged into AWS or Azure CLI.

    Args:
        cloud: Cloud provider ('aws' or 'azure')

    Returns:
        True if logged in, False otherwise
    """
    try:
        if cloud == "aws":
            subprocess.run(["aws", "sts", "get-caller-identity"],
                         capture_output=True, check=True)
        else:  # azure
            subprocess.run(["az", "account", "show"],
                         capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
