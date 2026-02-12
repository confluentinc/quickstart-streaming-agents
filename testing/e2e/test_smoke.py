"""Quick smoke test to verify fixture setup works."""

import pytest
from testing.conftest import (
    ensure_confluent_cli_installed,
    ensure_confluent_login,
    load_test_credentials,
    write_credentials_to_project_root,
    remove_credentials_from_project_root,
)


def test_fixture_setup():
    """Test that fixture setup steps work without full deployment."""
    cloud = "aws"

    # Step 1: Ensure CLI installed
    ensure_confluent_cli_installed()
    print("✅ Confluent CLI is installed")

    # Step 2: Load test credentials
    credentials = load_test_credentials(cloud)
    print(f"✅ Loaded credentials for {cloud}")

    # Step 3: Ensure Confluent CLI is logged in
    ensure_confluent_login(credentials)
    print("✅ Confluent CLI is authenticated")

    # Step 4: Write credentials to project root
    write_credentials_to_project_root(credentials)
    print("✅ Wrote credentials to project root")

    try:
        # Verify credentials.json exists
        import os
        from pathlib import Path
        creds_file = Path.cwd() / "credentials.json"
        assert creds_file.exists(), "credentials.json not created"
        print("✅ credentials.json exists in project root")

    finally:
        # Cleanup
        remove_credentials_from_project_root()
        print("✅ Cleaned up credentials.json")
