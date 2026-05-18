"""
Configure WatsonX Orchestrate SaaS to query Confluent Real-Time Context Engine.

Sets up:
  - orchestrate env (saas-us-south → your WXO SaaS instance)
  - basic_auth connection (rtce_claims_reviewed → RTCE key/secret)
  - MCP toolkit  (confluent_rtce → RTCE HTTP endpoint)
  - demo agent   (rtce_claims_demo_agent)

Prerequisites:
  - ibmcloud CLI installed and logged in  (ibmcloud login)
  - orchestrate CLI installed             (pip install ibm-watsonx-orchestrate)
  - Lab 5 deployed                        (terraform/core/terraform.tfstate exists)
  - RTCE enabled on claims_reviewed in the Confluent Cloud UI
  - A Global-scoped Confluent Cloud API key (create in UI: hamburger → API keys → Global scope)

Usage:
    uv run setup-wxo-rtce
"""

import json
import subprocess
import sys
from pathlib import Path

try:
    from dotenv import dotenv_values, set_key

    _DOTENV_AVAILABLE = True
except ImportError:
    _DOTENV_AVAILABLE = False

# ── Credential keys stored in credentials.env ──────────────────────────────
_CRED_RTCE_KEY = "CONFLUENT_RTCE_API_KEY"
_CRED_RTCE_SECRET = "CONFLUENT_RTCE_API_SECRET"
_CRED_IBM_KEY = "IBM_CLOUD_API_KEY"

# ── WXO configuration ───────────────────────────────────────────────────────
_WXO_ENV_NAME = "saas-us-south"
_WXO_CONNECTION_APP_ID = "rtce_claims_reviewed"
_WXO_TOOLKIT_NAME = "confluent_rtce"
_WXO_AGENT_FILE = "orchestrate/agent/rtce_claims_demo_agent.yaml"

# Name used when creating a new IBM Cloud API key on the user's behalf.
_IBM_KEY_NAME = "wxo-rtce-setup"

# Terraform output keys from core state.
_TF_ORG = "confluent_organization_id"
_TF_ENV = "confluent_environment_id"
_TF_CLUSTER = "confluent_kafka_cluster_id"
_TF_REGION = "cloud_region"


# ── Credential file helpers (same pattern as setup_rtce.py) ─────────────────

def _load_env_file(path: Path) -> dict:
    if not path.exists():
        return {}
    if _DOTENV_AVAILABLE:
        return dict(dotenv_values(path))
    result = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        result[k.strip()] = v.strip().strip('"').strip("'")
    return result


def _save_to_env_file(path: Path, key: str, value: str) -> None:
    if _DOTENV_AVAILABLE:
        set_key(str(path), key, value)
        return
    lines = path.read_text().splitlines() if path.exists() else []
    new_lines, found = [], False
    for line in lines:
        if line.startswith(f"{key}=") or line.startswith(f"{key} ="):
            new_lines.append(f'{key}="{value}"')
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(f'{key}="{value}"')
    path.write_text("\n".join(new_lines) + "\n")


def _find_credentials_file() -> Path:
    here = Path.cwd()
    for parent in [here, *here.parents]:
        candidate = parent / "credentials.env"
        if candidate.exists():
            return candidate
    return here / "credentials.env"


def _ask(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  (Value required — please try again)")


# ── Terraform state ──────────────────────────────────────────────────────────

def _read_terraform_outputs(state_path: Path) -> dict:
    try:
        state = json.loads(state_path.read_text())
        return {k: v["value"] for k, v in state.get("outputs", {}).items()}
    except Exception:
        return {}


def _get_infra(creds_file: Path) -> dict:
    search_roots = [creds_file.parent, Path.cwd()]
    outputs: dict = {}
    for root in search_roots:
        state_path = root / "terraform" / "core" / "terraform.tfstate"
        if state_path.exists():
            outputs = _read_terraform_outputs(state_path)
            break

    org_id = outputs.get(_TF_ORG, "").strip()
    env_id = outputs.get(_TF_ENV, "").strip()
    cluster_id = outputs.get(_TF_CLUSTER, "").strip()
    region = outputs.get(_TF_REGION, "").strip()

    if org_id and env_id and cluster_id and region:
        print(f"  Organization: {org_id}")
        print(f"  Environment:  {env_id}")
        print(f"  Cluster:      {cluster_id}")
        print(f"  Region:       {region}")
        return {"org_id": org_id, "env_id": env_id, "cluster_id": cluster_id, "region": region}

    print("Terraform state not found. Enter your Confluent Cloud infrastructure details:")
    return {
        "org_id":     org_id     or _ask("  Organization ID (e.g. eaae541a-...): "),
        "env_id":     env_id     or _ask("  Environment ID  (e.g. env-abc123):  "),
        "cluster_id": cluster_id or _ask("  Kafka Cluster ID (e.g. lkc-abc123): "),
        "region":     region     or _ask("  AWS Region (e.g. us-east-1):         "),
    }


# ── RTCE credentials ─────────────────────────────────────────────────────────

def _get_rtce_credentials(creds_file: Path, creds: dict) -> tuple[str, str]:
    key = creds.get(_CRED_RTCE_KEY, "").strip()
    secret = creds.get(_CRED_RTCE_SECRET, "").strip()
    if key and secret:
        print(f"  Using RTCE API key from {creds_file.name}: {key[:8]}…")
        return key, secret

    print(
        "\nNo Confluent Cloud Global API key found.\n"
        "Create one: Confluent Cloud → hamburger menu → API keys → Add API key → Global scope\n"
    )
    key = _ask("Global API key:    ")
    secret = _ask("Global API secret: ")
    _save_to_env_file(creds_file, _CRED_RTCE_KEY, key)
    _save_to_env_file(creds_file, _CRED_RTCE_SECRET, secret)
    print(f"  ✓ Saved to {creds_file.name}")
    return key, secret


# ── IBM Cloud API key ────────────────────────────────────────────────────────

def _check_ibmcloud() -> None:
    """Abort with a helpful message if ibmcloud is not logged in."""
    result = subprocess.run(
        ["ibmcloud", "target", "--output", "json"],
        capture_output=True, text=True,
    )
    if result.returncode != 0 or '"user"' not in result.stdout:
        print(
            "\nError: ibmcloud CLI is not logged in.\n"
            "Run:  ibmcloud login -a https://cloud.ibm.com\n"
            "Then re-run this script."
        )
        sys.exit(1)


def _find_existing_ibm_api_key() -> str | None:
    """Return the apikey value if a key named _IBM_KEY_NAME already exists, else None."""
    result = subprocess.run(
        ["ibmcloud", "iam", "api-keys", "--output", "json"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return None
    try:
        keys = json.loads(result.stdout)
        for k in keys:
            if k.get("name") == _IBM_KEY_NAME and not k.get("locked") and not k.get("disabled"):
                # The list endpoint does not return the actual key value — only metadata.
                # We can only confirm it exists; the caller must re-use the saved value.
                return "__EXISTS__"
    except (json.JSONDecodeError, TypeError):
        pass
    return None


def _create_ibm_api_key() -> str:
    """Create a new IBM Cloud API key and return its value."""
    result = subprocess.run(
        ["ibmcloud", "iam", "api-key-create", _IBM_KEY_NAME,
         "-d", "WXO RTCE setup key", "--output", "json"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"\nError: Failed to create IBM Cloud API key:\n{result.stderr.strip()}")
        sys.exit(1)
    try:
        return json.loads(result.stdout)["apikey"]
    except (json.JSONDecodeError, KeyError):
        print(f"\nError: Unexpected output from ibmcloud api-key-create:\n{result.stdout}")
        sys.exit(1)


def _get_ibm_api_key(creds_file: Path, creds: dict) -> str:
    """
    Return an IBM Cloud API key for orchestrate env activation, in this order:
      1. IBM_CLOUD_API_KEY already in credentials.env
      2. An existing key named _IBM_KEY_NAME in the account (re-use saved value from a prior run)
      3. Create a new key and save it
    """
    saved = creds.get(_CRED_IBM_KEY, "").strip()
    if saved:
        print(f"  Using IBM Cloud API key from {creds_file.name}: {saved[:8]}…")
        return saved

    existing = _find_existing_ibm_api_key()
    if existing == "__EXISTS__":
        # Key exists but value is not recoverable from the list API.
        # User must have it saved somewhere; prompt rather than create a duplicate.
        print(
            f"\nAn IBM Cloud API key named '{_IBM_KEY_NAME}' already exists in your account,\n"
            f"but its value is not stored in {creds_file.name}.\n"
            "Paste the key value (or press Enter to create a new one): "
        )
        pasted = input().strip()
        if pasted:
            _save_to_env_file(creds_file, _CRED_IBM_KEY, pasted)
            return pasted
        # Fall through to create a fresh key.

    print(f"  Creating IBM Cloud API key '{_IBM_KEY_NAME}'…")
    new_key = _create_ibm_api_key()
    _save_to_env_file(creds_file, _CRED_IBM_KEY, new_key)
    print(f"  ✓ Created and saved to {creds_file.name}")
    return new_key


# ── WXO instance discovery ───────────────────────────────────────────────────

def _get_wxo_instance_url() -> str:
    """Discover the WXO service instance URL from ibmcloud."""
    result = subprocess.run(
        ["ibmcloud", "resource", "service-instances",
         "--service-name", "watsonx-orchestrate", "--output", "json"],
        capture_output=True, text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        print(
            "\nError: Could not list WXO service instances.\n"
            "Make sure you are logged into the correct IBM Cloud account."
        )
        sys.exit(1)
    try:
        instances = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"\nError: Unexpected output from ibmcloud:\n{result.stdout[:200]}")
        sys.exit(1)

    if not instances:
        print(
            "\nError: No 'watsonx-orchestrate' service instances found in this account.\n"
            "Check you are logged into the correct IBM Cloud account."
        )
        sys.exit(1)

    if len(instances) == 1:
        instance = instances[0]
    else:
        print("\nMultiple WXO instances found:")
        for i, inst in enumerate(instances):
            print(f"  [{i}] {inst['name']} ({inst['region_id']})")
        idx = int(_ask("Select instance number: "))
        instance = instances[idx]

    guid = instance["guid"]
    region = instance["region_id"]  # e.g. "us-south"
    url = f"https://api.{region}.watson-orchestrate.cloud.ibm.com/instances/{guid}"
    print(f"  WXO instance: {instance['name']} ({region})")
    print(f"  Instance URL: {url}")
    return url


# ── orchestrate CLI helpers ──────────────────────────────────────────────────

def _orchestrate(*args, input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess:
    cmd = ["orchestrate", *args]
    result = subprocess.run(
        cmd,
        input=input_text.encode() if input_text else None,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        # Surface stderr so the user can see what failed.
        print(f"\nError running: {' '.join(cmd)}\n{result.stderr.strip()}")
        sys.exit(1)
    return result


def _orchestrate_visible(*args, input_bytes: bytes | None = None) -> subprocess.CompletedProcess:
    """Run an orchestrate command with output shown to the user (for activation prompts)."""
    result = subprocess.run(
        ["orchestrate", *args],
        input=input_bytes,
    )
    return result


def _ensure_wxo_env(instance_url: str, ibm_api_key: str) -> None:
    """Add the SaaS env if it doesn't exist, then activate it."""
    # Check current active env.
    result = _orchestrate("env", "list", check=False)
    env_list = result.stdout + result.stderr

    if f"{_WXO_ENV_NAME}" in env_list and "(active)" in env_list:
        # Check if our env is already the active one.
        for line in env_list.splitlines():
            if _WXO_ENV_NAME in line and "(active)" in line:
                print(f"  WXO env '{_WXO_ENV_NAME}' already active.")
                return

    # Add the env if not present.
    if _WXO_ENV_NAME not in env_list:
        _orchestrate("env", "add", "-n", _WXO_ENV_NAME, "-u", instance_url, "--type", "ibm_iam")
        print(f"  ✓ Registered WXO env '{_WXO_ENV_NAME}'")

    # Activate — orchestrate uses getpass which falls back to stdin when not a tty.
    print(f"  Activating '{_WXO_ENV_NAME}' (piping API key)…")
    result = _orchestrate_visible(
        "env", "activate", _WXO_ENV_NAME,
        input_bytes=f"{ibm_api_key}\n".encode(),
    )
    if result.returncode != 0:
        print(
            "\nError: 'orchestrate env activate' failed.\n"
            "Try running manually: orchestrate env activate saas-us-south\n"
            "(You will be prompted to paste the IBM Cloud API key.)"
        )
        sys.exit(1)
    print(f"  ✓ '{_WXO_ENV_NAME}' is now active")


def _setup_connection(rtce_key: str, rtce_secret: str) -> None:
    """Create and configure the rtce_claims_reviewed basic_auth connection."""
    # connections add — ignore "already exists" errors.
    result = _orchestrate("connections", "add", "--app-id", _WXO_CONNECTION_APP_ID, check=False)
    if result.returncode == 0:
        print(f"  ✓ Connection '{_WXO_CONNECTION_APP_ID}' created")
    else:
        print(f"  Connection '{_WXO_CONNECTION_APP_ID}' already exists (re-configuring)")

    # Configure for both draft and live so deploy doesn't show "Configuration Pending".
    for env in ("draft", "live"):
        _orchestrate(
            "connections", "configure",
            "--app-id", _WXO_CONNECTION_APP_ID,
            "--env", env,
            "--type", "team",
            "--kind", "basic",
        )
        _orchestrate(
            "connections", "set-credentials",
            "--app-id", _WXO_CONNECTION_APP_ID,
            "--env", env,
            "-u", rtce_key,
            "-p", rtce_secret,
        )
    print(f"  ✓ Credentials set for draft + live")


def _setup_toolkit(rtce_url: str) -> None:
    """Add the RTCE MCP toolkit, replacing any previous version."""
    # Remove first to allow clean re-registration (ignore failures if not present).
    _orchestrate("toolkits", "remove", "--name", _WXO_TOOLKIT_NAME, check=False)

    _orchestrate(
        "toolkits", "add",
        "--kind", "mcp",
        "--name", _WXO_TOOLKIT_NAME,
        "--description", "Confluent Real-Time Context Engine — claims_reviewed topic",
        "--url", rtce_url,
        "--transport", "streamable_http",
        "--tools", "*",
        "--app-id", _WXO_CONNECTION_APP_ID,
    )
    print(f"  ✓ Toolkit '{_WXO_TOOLKIT_NAME}' registered")


def _import_agent(agent_file: Path) -> None:
    """Import the demo agent YAML into WXO."""
    if not agent_file.exists():
        print(f"\nError: Agent file not found: {agent_file}")
        print("Expected at orchestrate/agent/rtce_claims_demo_agent.yaml")
        sys.exit(1)
    _orchestrate("agents", "import", "--file", str(agent_file))
    print(f"  ✓ Agent 'rtce_claims_demo_agent' imported")


# ── Entry point ──────────────────────────────────────────────────────────────

def main():
    creds_file = _find_credentials_file()
    creds = _load_env_file(creds_file)

    print("\n── Step 1: Confluent infrastructure ───────────────────────────────────")
    infra = _get_infra(creds_file)

    rtce_url = (
        f"https://mcp.{infra['region']}.aws.confluent.cloud/mcp/v1/context-engine"
        f"/organizations/{infra['org_id']}"
        f"/environments/{infra['env_id']}"
        f"/kafka-clusters/{infra['cluster_id']}"
    )
    print(f"  RTCE URL: {rtce_url}")

    print("\n── Step 2: Confluent RTCE API key ─────────────────────────────────────")
    rtce_key, rtce_secret = _get_rtce_credentials(creds_file, creds)

    print("\n── Step 3: IBM Cloud API key ───────────────────────────────────────────")
    _check_ibmcloud()
    ibm_api_key = _get_ibm_api_key(creds_file, creds)

    print("\n── Step 4: WXO instance ────────────────────────────────────────────────")
    instance_url = _get_wxo_instance_url()

    print("\n── Step 5: Activate WXO env ────────────────────────────────────────────")
    _ensure_wxo_env(instance_url, ibm_api_key)

    print("\n── Step 6: RTCE connection ─────────────────────────────────────────────")
    _setup_connection(rtce_key, rtce_secret)

    print("\n── Step 7: RTCE MCP toolkit ────────────────────────────────────────────")
    _setup_toolkit(rtce_url)

    print("\n── Step 8: Demo agent ──────────────────────────────────────────────────")
    # Resolve agent file relative to the project root (where credentials.env lives).
    agent_file = creds_file.parent / _WXO_AGENT_FILE
    _import_agent(agent_file)

    print(
        f"\n✓ WXO → RTCE setup complete.\n"
        f"  Open your WXO tenant and chat with 'rtce_claims_demo_agent'.\n"
        f"  Ask: \"What are the most recent claims in claims_reviewed?\""
    )


if __name__ == "__main__":
    main()
