"""
Generate confluent-mcp.env from Terraform core outputs and register with Claude Code.
"""

import os
import subprocess
import sys
from pathlib import Path

from scripts.common.terraform import get_project_root, run_terraform_output

MCP_ENV_PATH = Path("terraform") / "core" / "confluent-mcp.env"

# Node ABI versions that have prebuilt @confluentinc/kafka-javascript binaries.
# Verified against the GitHub release assets for the version pinned in package.json.
# Run: gh release view v<version> --repo confluentinc/confluent-kafka-javascript \
#        --json assets --jq '[.assets[].name | select(endswith(".tar.gz"))]'
# ABI → Node: 115=20, 120=21, 127=22, 131=23, 137=24  (141=25 has no prebuilt)
_KAFKA_JS_PREBUILT_ABIS = {115, 120, 127, 131, 137}
_PREFERRED_ABI = 137  # Node 24 LTS
_MIN_NODE_MAJOR = 20  # Node 18 (ABI 108) is EOL; don't encourage it

# Locations to search for version-managed Node installations (nvm, fnm, Homebrew).
_NVM_DIR = Path.home() / ".nvm" / "versions" / "node"
_FNM_DIR = Path.home() / ".local" / "share" / "fnm" / "node-versions"
_HOMEBREW_DIRS = [
    Path("/opt/homebrew/opt"),  # Apple Silicon
    Path("/usr/local/opt"),  # Intel
]


def _get_node_abi(node_bin: str) -> int | None:
    """Return the ABI version for a node binary, or None if it can't be run."""
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


def _find_preferred_node() -> str:
    """
    Return the path to a Node binary that has a prebuilt kafka-javascript binary,
    preferring ABI 137 (Node 24 LTS). Falls back to whatever 'node' is on PATH.

    Searches nvm, fnm, and Homebrew node@24 in addition to PATH. Picks the
    candidate with the highest score: ABI 137 scores 2, any other prebuilt ABI
    scores 1, anything else scores 0.
    """
    candidates: list[str] = []

    # nvm — versions sorted newest-first
    if _NVM_DIR.is_dir():
        for d in sorted(_NVM_DIR.iterdir(), reverse=True):
            p = d / "bin" / "node"
            if p.exists():
                candidates.append(str(p))

    # fnm
    if _FNM_DIR.is_dir():
        for d in sorted(_FNM_DIR.iterdir(), reverse=True):
            p = d / "installation" / "bin" / "node"
            if p.exists():
                candidates.append(str(p))

    # Homebrew node@24 (explicit formula, not the rolling `node`)
    for brew_opt in _HOMEBREW_DIRS:
        p = brew_opt / "node@24" / "bin" / "node"
        if p.exists():
            candidates.append(str(p))

    best_path = "node"
    best_score = -1

    for path in ["node", *candidates]:
        abi = _get_node_abi(path)
        if abi is None:
            continue
        if abi == _PREFERRED_ABI:
            score = 2
        elif abi in _KAFKA_JS_PREBUILT_ABIS:
            score = 1
        else:
            score = 0
        if score > best_score:
            best_score = score
            best_path = path

    return best_path


def _check_node_version(node_bin: str) -> None:
    """Abort if Node is missing or too old; warn if no prebuilt binary exists."""
    try:
        ver_result = subprocess.run([node_bin, "--version"], capture_output=True, text=True, check=True, timeout=5)
        abi_result = subprocess.run(
            [node_bin, "-e", "process.stdout.write(process.versions.modules)"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        print("Error: 'node' not found. Install Node.js v24 LTS.")
        print("  With nvm: nvm install 24 && nvm use 24")
        sys.exit(1)

    version_str = ver_result.stdout.strip().lstrip("v")
    major = int(version_str.split(".")[0])
    abi = int(abi_result.stdout.strip())

    if major < _MIN_NODE_MAJOR:
        print(f"Error: Node {version_str} is too old (minimum: v{_MIN_NODE_MAJOR}).")
        print("  With nvm: nvm install 24 && nvm use 24")
        sys.exit(1)

    if abi not in _KAFKA_JS_PREBUILT_ABIS:
        print(f"Warning: Node {version_str} (ABI {abi}) has no prebuilt @confluentinc/kafka-javascript binary.")
        print("  npm will attempt to compile from source — this requires build tools:")
        print("    macOS: xcode-select --install")
        print("    Linux: sudo apt install build-essential python3")
        print("  If the install fails, switch with:  nvm install 24 && nvm use 24")
    else:
        label = (
            " (Node 24 LTS — prebuilt binary available)" if abi == _PREFERRED_ABI else " (prebuilt binary available)"
        )
        print(f"Using Node {version_str}{label}")
        if node_bin != "node":
            print(f"  ({node_bin})")


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
    "confluent_environment_display_name": ["FLINK_ENV_NAME"],
    "confluent_kafka_cluster_display_name": ["FLINK_DATABASE_NAME"],
    "app_manager_schema_registry_api_key": ["SCHEMA_REGISTRY_API_KEY"],
    "app_manager_schema_registry_api_secret": ["SCHEMA_REGISTRY_API_SECRET"],
    "confluent_schema_registry_rest_endpoint": ["SCHEMA_REGISTRY_ENDPOINT"],
    "confluent_cloud_api_key": ["CONFLUENT_CLOUD_API_KEY"],
    "confluent_cloud_api_secret": ["CONFLUENT_CLOUD_API_SECRET"],
}


def write_mcp_env(core_outputs: dict, project_root: Path) -> Path:
    """Write confluent-mcp.env from Terraform core outputs. Returns the file path."""
    env_path = project_root / MCP_ENV_PATH
    env_path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for tf_key, mcp_vars in _TF_TO_MCP.items():
        value = core_outputs.get(tf_key, "")
        for var in mcp_vars:
            lines.append(f'{var}="{value}"')
    env_path.write_text("\n".join(lines) + "\n")
    return env_path


_MCP_PACKAGE = "@confluentinc/mcp-confluent"


def _ensure_local_mcp(project_root: Path, node_bin: str) -> Path:
    """
    Return the path to the mcp-confluent dist/index.js, installing it locally
    if not already present.

    Using npx risks pulling a cached version compiled for a different Node ABI.
    A local npm install compiles native bindings for the current Node version,
    which is the only reliable approach on newer Node releases (v25+).
    """
    dist_js = project_root / "node_modules" / _MCP_PACKAGE / "dist" / "index.js"
    if not dist_js.exists():
        print(f"Installing {_MCP_PACKAGE} locally (compiles native bindings for your Node version)...")

        # Ensure npm uses the same Node we selected by prepending its bin dir to PATH.
        env = os.environ.copy()
        if node_bin != "node":
            node_bin_dir = str(Path(node_bin).parent)
            env["PATH"] = node_bin_dir + os.pathsep + env.get("PATH", "")

        result = subprocess.run(
            ["npm", "install", _MCP_PACKAGE],
            cwd=project_root,
            capture_output=False,
            env=env,
        )
        if result.returncode != 0:
            print("Error: npm install failed. Make sure npm and build tools are available.")
            sys.exit(1)
        if not dist_js.exists():
            print(f"Error: {dist_js} not found after npm install.")
            sys.exit(1)
        print(f"Installed {_MCP_PACKAGE}")
    return dist_js


def main():
    node_bin = _find_preferred_node()
    _check_node_version(node_bin)

    project_root = get_project_root()
    state_path = project_root / "terraform" / "core" / "terraform.tfstate"

    if not state_path.exists():
        print("Error: terraform/core/terraform.tfstate not found. Run `uv run deploy` first.")
        sys.exit(1)

    core_outputs = run_terraform_output(state_path)
    env_path = write_mcp_env(core_outputs, project_root)

    dist_js = _ensure_local_mcp(project_root, node_bin)

    # Remove any existing registration before adding, to handle re-runs cleanly.
    subprocess.run(
        ["claude", "mcp", "remove", "confluent-cloud-mcp-server", "-s", "local"],
        capture_output=True,
    )

    result = subprocess.run(
        [
            "claude",
            "mcp",
            "add",
            "--scope",
            "local",
            "confluent-cloud-mcp-server",
            "--",
            node_bin,
            str(dist_js.resolve()),
            "-e",
            str(env_path.resolve()),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr)
        sys.exit(1)

    print("✓ Confluent MCP server registered as 'confluent-cloud-mcp-server' (local scope)")
    print("  Restart Claude Code to activate.")


if __name__ == "__main__":
    main()
