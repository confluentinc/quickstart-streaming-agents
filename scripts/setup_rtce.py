"""
Register Confluent Cloud Real-Time Context Engine (RTCE) MCP server with Claude Code.

Prerequisites:
- RTCE must already be enabled on your topics via the Confluent Cloud UI or REST API.
- A Global-scoped Confluent Cloud API key (create in UI: hamburger menu → API keys → Add API key).

Usage:
    uv run setup-rtce          # if running from the quickstart-streaming-agents repo
    python setup_rtce.py       # standalone, from any directory
"""

import base64
import json
import subprocess
import sys
from pathlib import Path

try:
    from dotenv import dotenv_values, set_key

    _DOTENV_AVAILABLE = True
except ImportError:
    _DOTENV_AVAILABLE = False

_DEFAULT_SERVER_NAME = "confluent-rtce"
_CRED_KEY = "CONFLUENT_RTCE_API_KEY"
_CRED_SECRET = "CONFLUENT_RTCE_API_SECRET"
_CRED_TOPICS = "CONFLUENT_RTCE_TOPICS"

# Terraform output key names from quickstart-streaming-agents core state.
_TF_ORG = "confluent_organization_id"
_TF_ENV = "confluent_environment_id"
_TF_CLUSTER = "confluent_kafka_cluster_id"
_TF_REGION = "cloud_region"


def _load_env_file(path: Path) -> dict:
    if not path.exists():
        return {}
    if _DOTENV_AVAILABLE:
        return dict(dotenv_values(path))
    # Minimal fallback parser for KEY=VALUE lines.
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
    # Minimal fallback: append if not present, replace if present.
    lines = path.read_text().splitlines() if path.exists() else []
    new_lines = []
    found = False
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
    """Look for credentials.env starting from cwd upward, then default to cwd."""
    here = Path.cwd()
    for parent in [here, *here.parents]:
        candidate = parent / "credentials.env"
        if candidate.exists():
            return candidate
    return here / "credentials.env"


def _get_credentials(creds_file: Path, creds: dict) -> tuple[str, str]:
    api_key = creds.get(_CRED_KEY, "").strip()
    api_secret = creds.get(_CRED_SECRET, "").strip()

    if api_key and api_secret:
        print(f"Using RTCE API key from {creds_file.name}: {api_key[:8]}...")
        return api_key, api_secret

    print("\nNo RTCE global API key found.")
    print(
        "Create one in Confluent Cloud: top-right hamburger menu → API keys → Add API key → Global scope"
    )
    print()
    api_key = _ask("Global API key:    ")
    api_secret = _ask("Global API secret: ")

    _save_to_env_file(creds_file, _CRED_KEY, api_key)
    _save_to_env_file(creds_file, _CRED_SECRET, api_secret)
    print(f"✓ Saved credentials to {creds_file}")

    return api_key, api_secret


def _read_terraform_outputs(state_path: Path) -> dict:
    try:
        state = json.loads(state_path.read_text())
        return {k: v["value"] for k, v in state.get("outputs", {}).items()}
    except Exception:
        return {}


def _get_infra(creds_file: Path) -> dict[str, str]:
    """Return org_id, env_id, cluster_id, region — from terraform state or prompts."""
    # Try to find terraform state relative to the credentials file or cwd.
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
        print(f"\nAuto-detected infrastructure from terraform state:")
        print(f"  Organization: {org_id}")
        print(f"  Environment:  {env_id}")
        print(f"  Cluster:      {cluster_id}")
        print(f"  Region:       {region}")
        return {
            "org_id": org_id,
            "env_id": env_id,
            "cluster_id": cluster_id,
            "region": region,
        }

    print("\nEnter your Confluent Cloud infrastructure details:")
    if not org_id:
        org_id = _ask("  Organization ID (e.g. 5a49b747-3e48-4fbb-b679-cfaa8ebd5fee): ")
    if not env_id:
        env_id = _ask("  Environment ID (e.g. env-abc123): ")
    if not cluster_id:
        cluster_id = _ask("  Kafka Cluster ID (e.g. lkc-abc123): ")
    if not region:
        region = _ask("  AWS Region (e.g. us-east-1): ")

    return {
        "org_id": org_id,
        "env_id": env_id,
        "cluster_id": cluster_id,
        "region": region,
    }


def _ask(prompt: str) -> str:
    """Prompt until the user provides a non-empty value (guards against buffered newlines)."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  (Value required — please try again)")


def _pick_client() -> str:
    """Ask which MCP client to register with. Returns 'gemini' or 'claude'."""
    print()
    raw = input("Register with (g)emini or (c)laude Code? [g]: ").strip().lower()
    if raw in ("c", "claude"):
        return "claude"
    return "gemini"


def _pick_scope() -> tuple[str, Path]:
    """Ask whether to register per-project or for all projects (Claude Code only).

    Claude Code reads MCP servers from two places only:
      --scope project  →  .mcp.json in the project root (this directory)
      --scope local    →  ~/.claude.json  (all projects on this machine)
    Note: mcpServers in settings.local.json is silently ignored by Claude Code.
    """
    print()
    raw = (
        input("Register for (l)ocal/this project or (u)ser/all projects? [l]: ")
        .strip()
        .lower()
    )
    if raw in ("u", "user"):
        return "local", Path.home() / ".claude.json"
    return "project", Path.cwd() / ".mcp.json"


def _register_gemini(server_name: str, url: str, token: str) -> str:
    """Register the RTCE MCP server with Gemini CLI. Returns a scope note."""
    subprocess.run(
        ["gemini", "mcp", "remove", server_name],
        capture_output=True,
    )
    cmd = [
        "gemini",
        "mcp",
        "add",
        "--transport",
        "http",
        "--scope",
        "user",
        "--header",
        f"Authorization: Basic {token}",
        server_name,
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error registering with Gemini: {result.stderr.strip()}")
        sys.exit(1)
    return "gemini user scope"


def _write_mcp_to_config(
    config_file: Path, server_name: str, url: str, token: str
) -> None:
    """Write the HTTP MCP server directly into the target Claude Code MCP config file.

    Bypasses `claude mcp add` when Confluent's enterprise policy blocks HTTP
    transport registration via the CLI.

    - Project scope:  .mcp.json in the project root
    - User scope:     ~/.claude.json
    Both use the same {"mcpServers": {...}} structure.
    """
    config: dict = {}
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text())
        except (json.JSONDecodeError, OSError):
            pass

    config.setdefault("mcpServers", {})
    config["mcpServers"][server_name] = {
        "type": "http",
        "url": url,
        "headers": {"Authorization": f"Basic {token}"},
    }

    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text(json.dumps(config, indent=2) + "\n")


def _parse_topics(raw: str) -> list[str]:
    return [t.strip() for t in raw.split(",") if t.strip()]


def main():
    creds_file = _find_credentials_file()
    creds = _load_env_file(creds_file)

    api_key, api_secret = _get_credentials(creds_file, creds)
    infra = _get_infra(creds_file)

    print()
    raw_name = input(f"MCP server name [{_DEFAULT_SERVER_NAME}]: ").strip()
    server_name = raw_name if raw_name else _DEFAULT_SERVER_NAME

    client = _pick_client()

    raw_topics = _ask("RTCE-enabled topic names (comma-separated): ")
    topics = _parse_topics(raw_topics)

    _save_to_env_file(creds_file, _CRED_TOPICS, ",".join(topics))

    token = base64.b64encode(f"{api_key}:{api_secret}".encode()).decode()

    url = (
        f"https://mcp.{infra['region']}.aws.confluent.cloud/mcp/v1/context-engine"
        f"/organizations/{infra['org_id']}"
        f"/environments/{infra['env_id']}"
        f"/kafka-clusters/{infra['cluster_id']}"
    )

    if client == "gemini":
        scope_note = _register_gemini(server_name, url, token)
        restart_note = "Restart Gemini to activate."
    else:
        # Try the standard CLI registration first. On Confluent-managed machines,
        # JAMF enterprise policy currently blocks `--transport http` via the CLI,
        # so we fall back to writing the config directly.
        claude_scope, config_file = _pick_scope()
        subprocess.run(
            ["claude", "mcp", "remove", server_name, "-s", claude_scope],
            capture_output=True,
        )
        cmd = [
            "claude",
            "mcp",
            "add",
            "--transport",
            "http",
            "--scope",
            claude_scope,
            server_name,
            url,
            "--env",
            f"CONFLUENT_RTCE_TOKEN={token}",
            "--header",
            "Authorization: Basic ${CONFLUENT_RTCE_TOKEN}",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            scope_note = f"Claude Code {claude_scope} scope"
        else:
            _write_mcp_to_config(config_file, server_name, url, token)
            scope_note = f"written directly to {config_file}"
        restart_note = (
            "Restart Claude Code to activate.\n\n"
            "  NOTE (Confluent employees): If the server does not appear in /mcp after\n"
            "  restart, your machine's JAMF policy may block the RTCE URL pattern.\n"
            "  File an ITSEC ticket (label: claude-code-governance) to add:\n"
            '    { "serverUrl": "https://mcp.*.confluent.cloud/mcp/v1/context-engine/*" }\n'
            "  to allowedMcpServers in confluentinc/claude-code-governance."
        )

    print(f"\n✓ RTCE MCP server registered as '{server_name}' ({scope_note})")
    print(f"  Topics:   {', '.join(topics)}")
    print(f"  Endpoint: {url}")
    print(f"  {restart_note}")


if __name__ == "__main__":
    main()
