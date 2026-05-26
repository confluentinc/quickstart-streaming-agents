"""
Generate Claude Code MCP registration for Confluent Cloud from Terraform core outputs.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

from scripts.common.terraform import get_project_root, run_terraform_output

# Node ABI versions that have prebuilt @confluentinc/kafka-javascript binaries.
_KAFKA_JS_PREBUILT_ABIS = {115, 120, 127, 131, 137}
_PREFERRED_ABI = 137  # Node 24 LTS


def _check_node_version() -> None:
    """Warn if the active Node has no prebuilt kafka-javascript binary."""
    try:
        abi_result = subprocess.run(
            ["node", "-e", "process.stdout.write(process.versions.modules)"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        ver_result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        print("Warning: 'node' not found on PATH.")
        print("  Install Node 24 LTS before running this command:")
        print("    With nvm:      nvm install 24 && nvm use 24")
        print("    With Homebrew: brew install node@24")
        print('                   export PATH="/opt/homebrew/opt/node@24/bin:$PATH"')
        return

    version_str = ver_result.stdout.strip().lstrip("v")
    abi = int(abi_result.stdout.strip())

    if abi not in _KAFKA_JS_PREBUILT_ABIS:
        print(
            f"Warning: Node {version_str} (ABI {abi}) has no prebuilt @confluentinc/kafka-javascript binary."
        )
        print(
            "  npx will compile it from source the first time the MCP server starts — this can take several minutes."
        )
        print("  To avoid the wait, switch to Node 24 LTS first:")
        print("    With nvm:      nvm install 24 && nvm use 24")
        print("    With Homebrew: brew install node@24")
        print('                   export PATH="/opt/homebrew/opt/node@24/bin:$PATH"')
        answer = (
            input(f"  Continue anyway with Node {version_str}? [y/N] ").strip().lower()
        )
        if answer != "y":
            sys.exit(0)
    else:
        label = " (Node 24 LTS)" if abi == _PREFERRED_ABI else ""
        print(f"Using Node {version_str}{label}")


# Maps terraform output names to MCP env var names.
# Values are lists to handle one-to-many mappings.
_TF_TO_MCP = {
    "confluent_kafka_cluster_bootstrap_endpoint": ["BOOTSTRAP_SERVERS"],
    "app_manager_kafka_api_key": ["KAFKA_API_KEY"],
    "app_manager_kafka_api_secret": ["KAFKA_API_SECRET"],
    "confluent_kafka_cluster_rest_endpoint": ["KAFKA_REST_ENDPOINT"],
    "confluent_kafka_cluster_id": ["KAFKA_CLUSTER_ID"],
    "confluent_environment_id": ["KAFKA_ENV_ID", "FLINK_ENV_ID"],
    "app_manager_flink_api_key": ["FLINK_API_KEY"],
    "app_manager_flink_api_secret": ["FLINK_API_SECRET"],
    "confluent_flink_rest_endpoint": ["FLINK_REST_ENDPOINT"],
    "confluent_flink_compute_pool_id": ["FLINK_COMPUTE_POOL_ID"],
    "confluent_organization_id": ["FLINK_ORG_ID"],
    "confluent_environment_display_name": ["FLINK_CATALOG_NAME"],
    "confluent_kafka_cluster_display_name": ["FLINK_DATABASE_NAME"],
    "app_manager_schema_registry_api_key": ["SCHEMA_REGISTRY_API_KEY"],
    "app_manager_schema_registry_api_secret": ["SCHEMA_REGISTRY_API_SECRET"],
    "confluent_schema_registry_rest_endpoint": ["SCHEMA_REGISTRY_ENDPOINT"],
    "confluent_cloud_api_key": ["CONFLUENT_CLOUD_API_KEY"],
    "confluent_cloud_api_secret": ["CONFLUENT_CLOUD_API_SECRET"],
}


def _clear_broken_npx_cache() -> None:
    """Remove stale npx cache entries where the kafka-javascript native binary is missing."""
    npx_cache = Path.home() / ".npm" / "_npx"
    if not npx_cache.exists():
        return
    for entry in npx_cache.iterdir():
        if not entry.is_dir():
            continue
        if not (entry / "node_modules" / "@confluentinc" / "mcp-confluent").exists():
            continue
        build_release = (
            entry
            / "node_modules"
            / "@confluentinc"
            / "kafka-javascript"
            / "build"
            / "Release"
        )
        if not any(build_release.glob("*.node")) if build_release.exists() else True:
            print(f"  Clearing broken npx cache (missing native binary): {entry.name}")
            shutil.rmtree(entry)
            print(
                "  npx will re-download @confluentinc/mcp-confluent on next MCP server start."
            )


def main():
    _check_node_version()
    _clear_broken_npx_cache()

    project_root = get_project_root()
    state_path = project_root / "terraform" / "core" / "terraform.tfstate"

    if not state_path.exists():
        print(
            "Error: terraform/core/terraform.tfstate not found. Run `uv run deploy` first."
        )
        sys.exit(1)

    core_outputs = run_terraform_output(state_path)

    env_vars = {}
    for tf_key, mcp_vars in _TF_TO_MCP.items():
        value = core_outputs.get(tf_key, "")
        for var in mcp_vars:
            # Terraform emits BOOTSTRAP_SERVERS as "SASL_SSL://host:port" but the
            # MCP server requires bare "host:port".
            if var == "BOOTSTRAP_SERVERS" and "://" in value:
                value = value.split("://", 1)[1]
            env_vars[var] = value

    # Write MCP config directly to ~/.claude.json, mirroring what `claude mcp add
    # --scope local` does. `claude mcp add` is blocked by the enterprise JAMF
    # allowlist; settings.json/settings.local.json don't support mcpServers.
    claude_json_path = Path.home() / ".claude.json"
    if claude_json_path.exists():
        with claude_json_path.open() as f:
            claude_data = json.load(f)
    else:
        claude_data = {}

    project_key = str(project_root)
    (
        claude_data
        .setdefault("projects", {})
        .setdefault(project_key, {})
        .setdefault("mcpServers", {})
    )["confluent-cloud-mcp-server"] = {
        "command": "npx",
        "args": ["-y", "@confluentinc/mcp-confluent"],
        "env": env_vars,
    }

    with claude_json_path.open("w") as f:
        json.dump(claude_data, f, indent=2)
        f.write("\n")

    print(
        "✓ Confluent MCP server registered as 'confluent-cloud-mcp-server' (local scope)"
    )
    print("  Restart Claude Code to activate.")


if __name__ == "__main__":
    main()
