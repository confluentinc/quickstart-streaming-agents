"""Quick smoke test to verify fixture setup works."""

import pytest
from testing.conftest import (
    ensure_confluent_cli_installed,
    ensure_confluent_login,
    load_test_credentials,
)


def test_fixture_setup():
    """Test that fixture setup steps work without full deployment."""
    cloud = "aws"

    # Step 1: Ensure CLI installed
    ensure_confluent_cli_installed()
    print("✅ Confluent CLI is installed")

    # Step 2: Load test credentials
    try:
        credentials = load_test_credentials(cloud)
    except FileNotFoundError as e:
        pytest.skip(str(e))
    print(f"✅ Loaded credentials for {cloud}")

    # Step 3: Ensure Confluent CLI is logged in
    ensure_confluent_login(credentials)
    print("✅ Confluent CLI is authenticated")
