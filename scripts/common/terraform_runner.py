"""
Terraform execution wrapper utilities.

Provides functions for:
- Running terraform init and apply
- Running terraform destroy
- Handling terraform errors and output
"""

import subprocess
import sys
from pathlib import Path


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
        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ Terraform destroy failed in {env_path.name}")
        return False
    except FileNotFoundError:
        print("Error: Terraform not found. Please install Terraform first.")
        sys.exit(1)
