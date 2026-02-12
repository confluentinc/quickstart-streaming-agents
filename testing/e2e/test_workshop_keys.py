"""Test workshop keys creation."""

import subprocess
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent


def test_workshop_keys_create_and_destroy():
    """Test that workshop keys are available for use.

    Simple logic:
    - If credentials.json exists in repo root with AWS keys, use it
    - Else if testing/credentials.json has AWS keys, use that
    - Else create new keys with workshop-keys command
    """
    import json

    cloud = "aws"
    root_creds_file = PROJECT_ROOT / "credentials.json"
    testing_creds_file = PROJECT_ROOT / "testing" / "credentials.json"

    # Check if credentials exist in root
    if root_creds_file.exists():
        print(f"\n✅ Found credentials.json in repo root")
        with open(root_creds_file) as f:
            creds = json.load(f)

        # Validate AWS keys exist
        if "aws_bedrock_access_key" in creds and "aws_bedrock_secret_key" in creds:
            print("✅ AWS Bedrock keys found in root credentials.json")
            print(f"   Access Key: {creds['aws_bedrock_access_key'][:10]}...")
            return
        else:
            print("⚠️  Root credentials.json missing AWS keys, checking testing/...")

    # Check if credentials exist in testing/
    if testing_creds_file.exists():
        print(f"\n✅ Found credentials.json in testing/")
        with open(testing_creds_file) as f:
            creds = json.load(f)

        # Validate AWS keys exist
        if "aws_bedrock_access_key" in creds and "aws_bedrock_secret_key" in creds:
            print("✅ AWS Bedrock keys found in testing/credentials.json")
            print(f"   Access Key: {creds['aws_bedrock_access_key'][:10]}...")
            print("ℹ️  Tests will use keys from testing/credentials.json")
            return
        else:
            print("⚠️  testing/credentials.json missing AWS keys, will create new ones...")

    # No valid credentials found - create new keys
    print(f"\n=== No existing AWS keys found, creating new ones ===")
    api_keys_file = PROJECT_ROOT / f"API-KEYS-{cloud.upper()}.md"

    result = subprocess.run(
        ["uv", "run", "workshop-keys", "create", cloud],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=300
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    # Check if failed due to AWS key limits
    if result.returncode != 0:
        if "already has 2 access keys" in result.stderr:
            pytest.fail(
                "AWS IAM user already has 2 access keys (AWS limit).\n"
                "Either:\n"
                "  1. Add AWS keys to testing/credentials.json, OR\n"
                "  2. Delete existing keys: uv run workshop-keys destroy aws"
            )
        else:
            pytest.fail(f"Workshop keys creation failed: {result.stderr}")

    # Verify file created
    assert api_keys_file.exists(), f"{api_keys_file.name} not created"
    print(f"✅ {api_keys_file.name} created successfully")

    # Clean up the newly created keys
    print(f"\n=== Cleaning up newly created keys ===")
    result = subprocess.run(
        ["uv", "run", "workshop-keys", "destroy", cloud, "--keep-user"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=300
    )

    if result.returncode != 0:
        print(f"⚠️ Destroy returned {result.returncode}, continuing anyway")

    if api_keys_file.exists():
        api_keys_file.unlink()
        print(f"✅ Removed {api_keys_file.name}")
