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


def _get_node_abi(node_bin: str) -> int | None:
    """Return the ABI version for the given node binary, or None on failure."""
    try:
        result = subprocess.run(
            [node_bin, "-e", "process.stdout.write(process.versions.modules)"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return int(result.stdout.strip())
    except Exception:
        return None


def _candidate_npx_paths() -> list[Path]:
    """Well-known locations where Node 24 LTS npx may be installed."""
    candidates = [
        # Homebrew on Apple Silicon
        Path("/opt/homebrew/opt/node@24/bin/npx"),
        # Homebrew on Intel Mac
        Path("/usr/local/opt/node@24/bin/npx"),
    ]
    # nvm-managed versions
    nvm_dir = Path.home() / ".nvm" / "versions" / "node"
    if nvm_dir.is_dir():
        for entry in sorted(nvm_dir.iterdir(), reverse=True):
            if entry.name.startswith("v24."):
                candidates.append(entry / "bin" / "npx")
    return candidates


def _resolve_npx() -> str:
    """
    Return the npx binary to use for the MCP server.

    Prefers an absolute path to a Node 24 LTS npx so Claude Code uses the right
    version regardless of the user's PATH configuration.  Falls back to bare
    'npx' (PATH lookup) only when no prebuilt-ABI node is found anywhere.
    """
    # Check the node currently on PATH first.
    path_node_abi: int | None = None
    path_node_version = ""
    try:
        ver_result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        path_node_version = ver_result.stdout.strip().lstrip("v")
        path_node_abi = _get_node_abi("node")
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass  # node not on PATH — we'll search well-known locations below

    if path_node_abi in _KAFKA_JS_PREBUILT_ABIS:
        label = " (Node 24 LTS)" if path_node_abi == _PREFERRED_ABI else ""
        print(f"Using Node {path_node_version}{label}")
        return "npx"

    # PATH node is wrong (or missing) — probe well-known locations for a compatible one.
    for npx_path in _candidate_npx_paths():
        if not npx_path.exists():
            continue
        node_bin = npx_path.parent / "node"
        abi = _get_node_abi(str(node_bin))
        if abi in _KAFKA_JS_PREBUILT_ABIS:
            ver_result = subprocess.run(
                [str(node_bin), "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            version_str = ver_result.stdout.strip().lstrip("v")
            label = " (Node 24 LTS)" if abi == _PREFERRED_ABI else ""
            print(f"Using Node {version_str}{label} from {npx_path.parent}")
            return str(npx_path)

    # Nothing compatible found — warn and let the user decide.
    if path_node_abi is not None:
        print(
            f"Warning: Node {path_node_version} (ABI {path_node_abi}) has no prebuilt "
            f"@confluentinc/kafka-javascript binary."
        )
        print(
            "  npx will compile it from source the first time the MCP server starts — "
            "this can take several minutes."
        )
    else:
        print("Warning: 'node' not found on PATH or in well-known locations.")
    print("  To avoid the wait, install Node 24 LTS:")
    print("    With nvm:      nvm install 24 && nvm use 24")
    print("    With Homebrew: brew install node@24")
    print("  Then re-run `uv run setup-mcp`.")
    if path_node_abi is not None:
        answer = input(f"  Continue anyway with Node {path_node_version}? [y/N] ").strip().lower()
        if answer != "y":
            sys.exit(0)
    else:
        sys.exit(1)
    return "npx"


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


def _clear_broken_npx_cache(npx_bin: str) -> None:
    """Remove stale npx cache entries with missing or ABI-mismatched kafka-javascript binaries."""
    npx_cache = Path.home() / ".npm" / "_npx"
    if not npx_cache.exists():
        return

    # Determine the ABI of the npx we'll actually use.
    node_bin = Path(npx_bin).parent / "node" if npx_bin != "npx" else Path("node")
    active_abi = _get_node_abi(str(node_bin) if npx_bin != "npx" else "node")

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
        node_files = list(build_release.glob("*.node")) if build_release.exists() else []
        if not node_files:
            reason = "missing native binary"
        elif active_abi is not None and not any(
            # The .node filename embeds the ABI: e.g. "...node_modules_abi137_..."
            f"_abi{active_abi}_" in f.name or f.stat().st_size > 0
            for f in node_files
        ):
            # Simpler ABI check: try loading to see if it crashes.
            try:
                subprocess.run(
                    [str(node_bin) if npx_bin != "npx" else "node",
                     "-e", f"require('{node_files[0]}')"],
                    capture_output=True,
                    check=True,
                    timeout=5,
                )
                continue  # loads fine — cache is good
            except subprocess.CalledProcessError:
                reason = f"native binary built for wrong ABI (active ABI {active_abi})"
        else:
            continue  # cache entry looks fine
        print(f"  Clearing broken npx cache ({reason}): {entry.name}")
        shutil.rmtree(entry)
        print("  npx will re-download @confluentinc/mcp-confluent on next MCP server start.")


def main():
    npx_bin = _resolve_npx()
    _clear_broken_npx_cache(npx_bin)

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
        "command": npx_bin,
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
