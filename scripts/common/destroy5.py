#!/usr/bin/env python3
"""Destroy script for lab5 only — leaves core and other labs intact.

Tears down only the lab5-insurance-fraud-watson Terraform module.
Core infrastructure (environment, cluster, compute pool, API keys) is preserved,
so confluent-mcp-cdc and other lab MCP servers continue to work after teardown.
"""

import os
import shutil
import sys
from pathlib import Path

from .terraform import get_project_root
from .terraform_runner import run_terraform_destroy


def _load_credentials(root: Path) -> dict:
    """Load all values from credentials.env."""
    env_file = root / "credentials.env"
    if not env_file.exists():
        return {}
    from dotenv import dotenv_values
    return {k: v for k, v in dotenv_values(env_file).items() if v}


def _cleanup(env_path: Path) -> None:
    try:
        for f in env_path.glob("*.tfstate*"):
            f.unlink()
        for f in env_path.glob("*.tfvars*"):
            f.unlink()
        td = env_path / ".terraform"
        if td.exists():
            shutil.rmtree(td)
        for name in (".terraform.lock.hcl", "FLINK_SQL_COMMANDS.md", "mcp_commands.txt"):
            p = env_path / name
            if p.exists():
                p.unlink()
    except Exception:
        pass


def main() -> None:
    w = 54
    title = "  Confluent Labs  ·  Lab 5 Teardown"
    print("╔" + "═" * w + "╗")
    print(f"║{title:<{w}}║")
    print("╚" + "═" * w + "╝")
    print()
    print("  Destroys lab5-insurance-fraud-watson only.")
    print("  Core infrastructure and other labs are preserved.")
    print()

    root = get_project_root()
    creds = _load_credentials(root)
    saved = creds.get("TF_VAR_cloud_provider", "")

    # Cloud provider — numbered menu
    _CLOUD_OPTS = [("aws", "AWS"), ("azure", "Azure")]
    if saved:
        ordered = sorted(_CLOUD_OPTS, key=lambda x: x[0] != saved)
    else:
        ordered = _CLOUD_OPTS

    label = f"  Cloud Provider [previously: {saved.upper()}]:" if saved else "  Cloud Provider:"
    print(label)
    print()
    for i, (val, disp) in enumerate(ordered, 1):
        print(f"    {i}) {disp}")
    print()
    while True:
        print(f"  Choice [default: {ordered[0][1]}]: ", end="", flush=True)
        raw = input().strip()
        if not raw:
            cloud = ordered[0][0]
            break
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(ordered):
                cloud = ordered[idx][0]
                break
        except ValueError:
            pass
        print("  Invalid. Enter 1 or 2.")

    region = "us-east-1" if cloud == "aws" else "eastus2"

    # Load all TF_VAR_* from credentials.env into environment
    for k, v in creds.items():
        if k.startswith("TF_VAR_") and v:
            os.environ[k] = v

    os.environ["TF_VAR_cloud_provider"] = cloud
    os.environ["TF_VAR_cloud_region"] = region

    # Confirmation
    print()
    print("  " + "─" * 51)
    print(f"  ⚠  This will destroy lab5 resources on {cloud.upper()}.")
    print("  Core infrastructure will NOT be affected.")
    print()
    try:
        print('  Type "destroy" to confirm, or CTRL+C to cancel: ', end="", flush=True)
        confirm = input().strip()
    except KeyboardInterrupt:
        print("\n\n  Destroy cancelled.")
        sys.exit(0)

    if confirm != "destroy":
        print("\n  Destroy cancelled.")
        sys.exit(0)

    env = "lab5-insurance-fraud-watson"
    env_path = root / "terraform" / env

    if not env_path.exists():
        print(f"\n  ⊘ {env}: directory does not exist")
        sys.exit(1)
    if not (env_path / "terraform.tfstate").exists():
        print(f"\n  ⊘ {env}: no terraform state found (never deployed)")
        sys.exit(0)

    print(f"\n  → Destroying {env}...")
    if run_terraform_destroy(env_path):
        _cleanup(env_path)
        print("\n  ✓ Lab 5 destroyed. Core infrastructure intact.")
    else:
        print(f"\n  ✗ Destroy failed for {env}.")
        sys.exit(1)


if __name__ == "__main__":
    main()
