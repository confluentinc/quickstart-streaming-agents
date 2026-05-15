"""Test workshop keys creation."""

import subprocess
from pathlib import Path
import pytest
from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).parent.parent.parent


def test_workshop_keys_create_and_destroy():
    """Test that workshop keys are available for use.

    Simple logic:
    - If credentials.env exists with AWS keys, use them
    - Else create new keys with workshop-keys command
    """
    cloud = "aws"
    creds_file = PROJECT_ROOT / "credentials.env"

    # Check if credentials exist with AWS keys
    if creds_file.exists():
        creds = dict(dotenv_values(str(creds_file)))
        if creds.get("TF_VAR_aws_bedrock_access_key") and creds.get("TF_VAR_aws_bedrock_secret_key"):
            print(f"\n✅ AWS Bedrock keys found in credentials.env")
            print(f"   Access Key: {creds['TF_VAR_aws_bedrock_access_key'][:10]}...")
            return
        else:
            print("⚠️  credentials.env missing AWS keys, will create new ones...")

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
                "  1. Add AWS keys to credentials.env, OR\n"
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
