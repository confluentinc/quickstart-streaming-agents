#!/usr/bin/env python3
"""Destroy script v2 — reads credentials from credentials.env.

Visually and tonally distinct from deploy. Requires typing "destroy" to confirm.
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
    title = "  Confluent Labs  ·  Teardown Script"
    print("╔" + "═" * w + "╗")
    print(f"║{title:<{w}}║")
    print("╚" + "═" * w + "╝")
    print()
    print("  This will remove all provisioned lab resources.")
    print("  This action cannot be undone.")
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

    # Ensure cloud_provider and cloud_region are set
    os.environ["TF_VAR_cloud_provider"] = cloud
    os.environ["TF_VAR_cloud_region"] = region

    # Confirmation — must type the word "destroy"
    print()
    print("  " + "─" * 51)
    print(f"  ⚠  This will tear down all lab resources on {cloud.upper()}.")
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

    # Destroy all environments in reverse order
    envs = [
        "lab4-pubsec-fraud-agents",
        "lab3-agentic-fleet-management",
        "lab2-vector-search",
        "lab1-tool-calling",
        "core",
    ]

    print("\n=== Starting Destroy ===")
    for env in envs:
        env_path = root / "terraform" / env
        if not env_path.exists():
            print(f"  ⊘ Skipping {env}: directory does not exist")
            continue
        if not (env_path / "terraform.tfstate").exists():
            print(f"  ⊘ Skipping {env}: no terraform state found (never deployed)")
            continue
        print(f"\n  → Destroying {env}...")
        if run_terraform_destroy(env_path):
            _cleanup(env_path)
        else:
            print(f"  ✗ Destroy failed at {env}. Continuing with remaining environments...")

    print("\n  ✓ Destroy process completed!")


if __name__ == "__main__":
    main()
