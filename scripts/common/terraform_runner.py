"""
Terraform execution wrapper utilities.

Provides functions for:
- Running terraform init and apply
- Running terraform destroy
- Handling terraform errors and output
"""

import json
import subprocess
import sys
from pathlib import Path

from .generate_deployment_summary import generate_credentials_markdown


def run_terraform(env_path: Path, auto_approve: bool = True) -> bool:
    """
    Run terraform init and apply in the specified environment.

    Args:
        env_path: Path to terraform directory
        auto_approve: Whether to auto-approve terraform apply (default: True)

    Returns:
        True if successful, False otherwise

    Raises:
        SystemExit: If terraform binary is not found
    """
    print(f"\nInitializing Terraform in {env_path}...")

    try:
        subprocess.run(["terraform", "init"], cwd=env_path, check=True)

        apply_cmd = ["terraform", "apply"]
        if auto_approve:
            apply_cmd.append("-auto-approve")

        print(f"Running terraform apply in {env_path}...")
        subprocess.run(apply_cmd, cwd=env_path, check=True)

        print(f"✓ Deployment successful: {env_path.name}")

        # Generate credentials markdown for Core deployments
        if env_path.name == "core":
            _generate_deployment_summary(env_path)

        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ Terraform failed in {env_path.name}")
        return False
    except FileNotFoundError:
        print("Error: Terraform not found. Please install Terraform first.")
        sys.exit(1)


def run_terraform_destroy(env_path: Path, auto_approve: bool = True) -> bool:
    """
    Run terraform destroy in the specified environment.

    Args:
        env_path: Path to terraform directory
        auto_approve: Whether to auto-approve terraform destroy (default: True)

    Returns:
        True if successful, False otherwise

    Raises:
        SystemExit: If terraform binary is not found
    """
    print(f"\nInitializing Terraform in {env_path}...")

    try:
        subprocess.run(["terraform", "init"], cwd=env_path, check=True)

        destroy_cmd = ["terraform", "destroy"]
        if auto_approve:
            destroy_cmd.append("-auto-approve")

        print(f"Running terraform destroy in {env_path}...")
        subprocess.run(destroy_cmd, cwd=env_path, check=True)

        print(f"✓ Destroy successful: {env_path.name}")

        # Clean up deployment summary for Core deployments
        if env_path.name == "core":
            _cleanup_deployment_summary(env_path)

        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ Terraform destroy failed in {env_path.name}")
        return False
    except FileNotFoundError:
        print("Error: Terraform not found. Please install Terraform first.")
        sys.exit(1)


def _generate_deployment_summary(env_path: Path) -> None:
    """
    Generate DEPLOYED_RESOURCES.md file after successful Core deployment.

    Args:
        env_path: Path to the terraform core directory (e.g., aws/core or azure/core)
    """
    try:
        # Detect cloud provider from parent directory
        cloud_provider = env_path.parent.name  # "aws" or "azure"

        # Get terraform outputs as JSON
        print("\nGenerating deployment summary...")
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=env_path,
            capture_output=True,
            text=True,
            check=True
        )

        # Parse terraform outputs
        tf_outputs = json.loads(result.stdout)

        # Generate markdown file
        output_file = env_path / "DEPLOYED_RESOURCES.md"
        generate_credentials_markdown(cloud_provider, tf_outputs, output_file)

    except Exception as e:
        print(f"Warning: Failed to generate deployment summary: {e}")
        # Don't fail the deployment if summary generation fails


def _cleanup_deployment_summary(env_path: Path) -> None:
    """
    Delete DEPLOYED_RESOURCES.md file after successful Core destroy.

    Args:
        env_path: Path to the terraform core directory (e.g., aws/core or azure/core)
    """
    try:
        output_file = env_path / "DEPLOYED_RESOURCES.md"
        if output_file.exists():
            output_file.unlink()
            print(f"Removed {output_file}")
    except Exception as e:
        print(f"Warning: Failed to remove deployment summary: {e}")
