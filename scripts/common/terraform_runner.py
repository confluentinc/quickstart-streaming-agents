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


def _run_streaming(cmd: list[str], cwd: Path) -> tuple[int, str]:
    """Run a command, echoing output live and returning (returncode, output)."""
    proc = subprocess.Popen(
        cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
    )
    lines: list[str] = []
    assert proc.stdout is not None
    for line in proc.stdout:
        print(line, end="")
        lines.append(line)
    return proc.wait(), "".join(lines)


def _is_dead_flink_key(output: str) -> bool:
    return "401 Unauthorized" in output and "flink" in output.lower()


def _forget_flink_objects(env_path: Path) -> list[str]:
    """`terraform state rm` every Flink statement/connection; return what was removed."""
    listed = subprocess.run(
        ["terraform", "state", "list"], cwd=env_path, capture_output=True, text=True, check=False
    )
    targets = [
        addr
        for addr in listed.stdout.splitlines()
        if "confluent_flink_statement." in addr or "confluent_flink_connection." in addr
    ]
    if targets:
        subprocess.run(["terraform", "state", "rm", *targets], cwd=env_path, check=True)
    return targets


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
        returncode, output = _run_streaming(destroy_cmd, env_path)

        if returncode != 0 and _is_dead_flink_key(output):
            # The Flink API key in state is already gone (e.g. an earlier partial
            # destroy deleted it), so refreshing/deleting Flink statements and
            # connections 401s forever. Those objects live inside the compute pool
            # and are removed with the environment, so forgetting them is safe.
            dropped = _forget_flink_objects(env_path)
            if dropped:
                print(
                    f"\nFlink API key is no longer valid (401). Removed {len(dropped)} Flink "
                    "statement/connection resource(s) from state — they are deleted with the "
                    "environment. Retrying destroy..."
                )
                returncode, output = _run_streaming(destroy_cmd, env_path)

        if returncode != 0:
            raise subprocess.CalledProcessError(returncode, destroy_cmd)

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
        env_path: Path to the terraform core directory (e.g., terraform/core)
    """
    try:
        # Get terraform outputs as JSON
        print("\nGenerating deployment summary...")
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=env_path,
            capture_output=True,
            text=True,
            check=True,
        )

        # Parse terraform outputs
        tf_outputs = json.loads(result.stdout)

        # Extract cloud_provider from terraform output, default to "aws"
        cloud_provider = "aws"
        if "cloud_provider" in tf_outputs:
            cloud_provider = (
                tf_outputs["cloud_provider"].get("value", "aws")
                if isinstance(tf_outputs["cloud_provider"], dict)
                else tf_outputs["cloud_provider"]
            )

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
        env_path: Path to the terraform core directory (e.g., terraform/core)
    """
    try:
        output_file = env_path / "DEPLOYED_RESOURCES.md"
        if output_file.exists():
            output_file.unlink()
            print(f"Removed {output_file}")
    except Exception as e:
        print(f"Warning: Failed to remove deployment summary: {e}")
