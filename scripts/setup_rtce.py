"""
Register Confluent Cloud Real-Time Context Engine (RTCE) MCP server with Claude Code.

Prerequisites:
- RTCE is AWS-only. Azure deployments are not supported.
- A Global-scoped Confluent Cloud API key (--resource global). When deployed via
  `uv run deploy`, this key is created automatically via the Confluent CLI using the
  Terraform-provisioned RTCE service account (DeveloperRead on cluster + Schema Registry).
  For standalone use, create a key manually: Confluent Cloud UI → hamburger menu →
  API keys → Add API key → Global scope.
- Optionally, the script can enable RTCE on topics for you (requires topics to have a
  registered schema in Schema Registry).

Usage:
    uv run setup-rtce          # if running from the quickstart-streaming-agents repo
    python setup_rtce.py       # standalone, from any directory
"""

import base64
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

_SCRIPT_DIR = Path(__file__).parent  # scripts/
_PROJECT_ROOT = _SCRIPT_DIR.parent  # repo root

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
_TF_CLOUD = "cloud_provider"
_TF_RTCE_SA_ID = "confluent_rtce_service_account_id"

# AWS regions where RTCE is currently available.
# Source: https://docs.confluent.io/cloud/current/clusters/regions.html
# New regions are added regularly — warn but don't block if a region isn't listed.
_RTCE_SUPPORTED_AWS_REGIONS = {
    "us-east-1",
    "us-east-2",
    "us-west-2",
    "ap-northeast-2",
    "ap-south-1",
    "ap-southeast-1",
    "ap-southeast-2",
}


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


def _read_core_tf_outputs(creds_file: Path) -> dict:
    """Return terraform/core outputs dict, or empty dict if state is not found."""
    for root in [creds_file.parent, Path.cwd()]:
        state_path = root / "terraform" / "core" / "terraform.tfstate"
        if state_path.exists():
            return _read_terraform_outputs(state_path)
    return {}


def _create_rtce_global_key_via_cli(sa_id: str) -> tuple[str, str]:
    """Create a Global API key for the RTCE service account via Confluent CLI.

    Uses `confluent api-key create --resource global` which is the only way to create
    a Global-scoped key (the Terraform provider creates Cloud/CRM keys, not Global ones).
    Returns (api_key, api_secret) or ("", "") on failure.
    """
    result = subprocess.run(
        [
            "confluent",
            "api-key",
            "create",
            "--resource",
            "global",
            "--service-account",
            sa_id,
            "--description",
            "Global API Key for RTCE MCP server (auto-created by setup-rtce)",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        if result.stderr:
            print(f"  CLI error: {result.stderr.strip()[:300]}")
        return "", ""

    api_key = api_secret = ""
    for line in result.stdout.split("\n"):
        if "|" not in line:
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) < 2:
            continue
        if parts[0] == "API Key":
            api_key = parts[1]
        elif parts[0] == "API Secret":
            api_secret = parts[1]
    return api_key, api_secret


def _get_credentials(creds_file: Path, creds: dict) -> tuple[str, str]:
    api_key = creds.get(_CRED_KEY, "").strip()
    api_secret = creds.get(_CRED_SECRET, "").strip()

    if api_key and api_secret:
        print(f"Using RTCE API key from {creds_file.name}: {api_key[:8]}...")
        return api_key, api_secret

    print("\nNo RTCE Global API key found in credentials.env.")
    print(
        "For standalone use: create a key in the Confluent Cloud UI → hamburger → API keys → Global scope."
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
    cloud = outputs.get(_TF_CLOUD, "").strip().lower()

    if org_id and env_id and cluster_id and region:
        print(f"\nAuto-detected infrastructure from terraform state:")
        print(f"  Cloud:        {cloud or 'unknown'}")
        print(f"  Organization: {org_id}")
        print(f"  Environment:  {env_id}")
        print(f"  Cluster:      {cluster_id}")
        print(f"  Region:       {region}")
        return {
            "cloud": cloud,
            "org_id": org_id,
            "env_id": env_id,
            "cluster_id": cluster_id,
            "region": region,
        }

    print("\nEnter your Confluent Cloud infrastructure details:")
    if not cloud:
        raw_cloud = input("  Cloud provider (aws/azure) [aws]: ").strip().lower()
        cloud = raw_cloud if raw_cloud in ("aws", "azure") else "aws"
    if not org_id:
        org_id = _ask("  Organization ID (e.g. 5a49b747-3e48-4fbb-b679-cfaa8ebd5fee): ")
    if not env_id:
        env_id = _ask("  Environment ID (e.g. env-abc123): ")
    if not cluster_id:
        cluster_id = _ask("  Kafka Cluster ID (e.g. lkc-abc123): ")
    if not region:
        region = _ask("  AWS Region (e.g. us-east-1): ")

    return {
        "cloud": cloud,
        "org_id": org_id,
        "env_id": env_id,
        "cluster_id": cluster_id,
        "region": region,
    }


def _validate_rtce_support(infra: dict[str, str]) -> None:
    """Gate on cloud/region support. Hard-stops Azure; warns on unknown AWS regions."""
    cloud = infra.get("cloud", "aws").lower()
    region = infra.get("region", "")

    if cloud == "azure":
        print()
        print("=" * 70)
        print("ERROR: RTCE is not supported on Azure.")
        print()
        print("Real-Time Context Engine is currently an AWS-only feature.")
        print("Azure deployments use a different Confluent Cloud architecture and")
        print("the RTCE MCP endpoint does not exist for Azure clusters.")
        print()
        print("To use RTCE, redeploy the quickstart on AWS:")
        print("  uv run destroy && uv run deploy  (choose AWS when prompted)")
        print("=" * 70)
        sys.exit(1)

    if region not in _RTCE_SUPPORTED_AWS_REGIONS:
        print()
        print("!" * 70)
        print(
            f"WARNING: '{region}' is not in the known list of RTCE-supported AWS regions."
        )
        print()
        print("Known supported regions:")
        for r in sorted(_RTCE_SUPPORTED_AWS_REGIONS):
            print(f"  {r}")
        print()
        print("This probably will not work UNLESS Confluent has already rolled out")
        print("RTCE support for your region since this script was last updated.")
        print("Check https://docs.confluent.io/cloud/current/clusters/regions.html")
        print("for the current list.")
        print("!" * 70)
        raw = input("\nContinue anyway? [y/N]: ").strip().lower()
        if raw != "y":
            sys.exit(0)


def _list_rtce_topics(
    api_key: str, api_secret: str, infra: dict[str, str]
) -> list[str]:
    """Return RTCE-enabled topic names. Tries Confluent CLI first, then REST API.

    The CLI uses the logged-in user session (always has correct permissions).
    The REST API requires the Global API key to have CloudClusterAdmin on the
    cluster, which may not be the case — and it silently returns an empty list
    rather than a 403 when the key lacks that role.
    """
    env_id = infra["env_id"]
    cluster_id = infra["cluster_id"]

    # CLI path — reliable when user is logged in via `confluent login`.
    try:
        result = subprocess.run(
            [
                "confluent",
                "rtce",
                "rtce-topic",
                "list",
                "--cluster",
                cluster_id,
                "--environment",
                env_id,
                "-o",
                "json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            items = json.loads(result.stdout or "[]")
            return [i["topic_name"] for i in items if i.get("phase") != "DISABLED"]
    except Exception:
        pass

    # REST API fallback (requires CloudClusterAdmin on the Global API key).
    url = (
        f"https://api.confluent.cloud/rtce/v1/rtce-topics"
        f"?environment={env_id}&spec.kafka_cluster={cluster_id}"
    )
    token = base64.b64encode(f"{api_key}:{api_secret}".encode()).decode()
    req = urllib.request.Request(url, headers={"Authorization": f"Basic {token}"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        return [item["spec"]["topic_name"] for item in data.get("data", [])]
    except Exception as exc:
        print(f"  Warning: could not list RTCE-enabled topics ({exc})")
    return []


def _enable_rtce_topic(
    api_key: str,
    api_secret: str,
    infra: dict[str, str],
    topic_name: str,
    description: str,
) -> bool:
    """Enable RTCE on a topic. Tries Confluent CLI first, then REST API."""
    # CLI path — uses the logged-in session; avoids REST API permission issues.
    try:
        result = subprocess.run(
            [
                "confluent",
                "rtce",
                "rtce-topic",
                "create",
                "--cloud",
                infra["cloud"].lower(),
                "--region",
                infra["region"],
                "--topic-name",
                topic_name,
                "--description",
                description,
                "--cluster",
                infra["cluster_id"],
                "--environment",
                infra["env_id"],
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return True
        stderr = result.stderr.strip()
        if "already exists" in stderr.lower() or "conflict" in stderr.lower():
            return True
        if stderr:
            print(f"  CLI error: {stderr[:300]}")
        # Fall through to REST API on CLI failure.
    except Exception:
        pass

    # REST API fallback (requires CloudClusterAdmin on the Global API key).
    url = "https://api.confluent.cloud/rtce/v1/rtce-topics"
    token = base64.b64encode(f"{api_key}:{api_secret}".encode()).decode()
    body = json.dumps(
        {
            "spec": {
                "cloud": infra["cloud"].upper(),
                "region": infra["region"],
                "topic_name": topic_name,
                "description": description,
                "environment": {"id": infra["env_id"]},
                "kafka_cluster": {"id": infra["cluster_id"]},
            }
        }
    ).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Authorization": f"Basic {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status in (200, 201, 202)
    except urllib.error.HTTPError as exc:
        if exc.code == 409:  # already enabled
            return True
        err_body = exc.read().decode(errors="replace")
        print(f"  REST error {exc.code}: {err_body[:300]}")
        return False
    except Exception as exc:
        print(f"  Error: {exc}")
        return False


def _ask(prompt: str) -> str:
    """Prompt until the user provides a non-empty value (guards against buffered newlines)."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  (Value required — please try again)")


def _pick_client() -> str:
    """Ask which MCP client to register with. Returns 'claude', 'codex', or 'gemini'."""
    print()
    print("Which AI assistant should the MCP server be registered with?")
    print("  1. Claude Code (default)")
    print("  2. OpenAI Codex")
    print("  3. Gemini")
    raw = input("Enter 1, 2, or 3 [1]: ").strip()
    if raw == "2":
        return "codex"
    if raw == "3":
        return "gemini"
    return "claude"


def _register_with_claude_code(server_name: str, url: str, token: str) -> str:
    """Register RTCE as an HTTP MCP server in Claude Code.

    Writes the entry directly under projects[project_key].mcpServers in
    ~/.claude.json, mirroring mcp_setup.py. Direct-write keeps both setup scripts
    consistent and avoids depending on the `claude` binary being on PATH.
    """
    project_key = str(_PROJECT_ROOT)

    claude_json_path = Path.home() / ".claude.json"
    claude_data: dict = {}
    if claude_json_path.exists():
        try:
            claude_data = json.loads(claude_json_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass

    # Literal token: Claude Code does not auto-load credentials.env into its
    # environment, so an env-var placeholder ("Basic ${...}") would silently fail
    # to authenticate unless the user exports it in the launching shell. Writing
    # the resolved token here mirrors how mcp_setup.py stores secrets in this file.
    entry = {
        "type": "http",
        "url": url,
        "headers": {"Authorization": f"Basic {token}"},
    }

    (
        claude_data.setdefault("projects", {})
        .setdefault(project_key, {})
        .setdefault("mcpServers", {})
    )[server_name] = entry

    claude_json_path.write_text(json.dumps(claude_data, indent=2) + "\n")
    return "Claude Code local scope (http)"


def _codex_config_paths_rtce() -> list[Path]:
    """Return Codex config files that can affect this project (home + project-local)."""
    home_config_path = Path.home() / ".codex" / "config.toml"
    paths = [home_config_path]
    project_config_path = Path.cwd() / ".codex" / "config.toml"
    if project_config_path.exists() and (
        project_config_path.resolve() != home_config_path.resolve()
    ):
        paths.append(project_config_path)
    return paths


def _write_codex_config_rtce(
    config_path: Path, server_name: str, url: str, token: str
) -> None:
    """Write the HTTP MCP server entry into one Codex config.toml file."""
    import tomli_w

    try:
        import tomllib  # stdlib 3.11+
    except ImportError:
        import tomli as tomllib  # type: ignore[no-redef]

    config: dict = {}
    if config_path.exists():
        try:
            with config_path.open("rb") as f:
                config = tomllib.load(f)
        except Exception as exc:
            print(
                f"  Warning: could not parse existing config.toml ({exc}); preserving as .bak"
            )
            config_path.rename(config_path.with_suffix(".toml.bak"))

    config.setdefault("mcp_servers", {})[server_name] = {
        "url": url,
        "http_headers": {"Authorization": f"Basic {token}"},
    }

    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open("wb") as f:
        tomli_w.dump(config, f)


def _register_with_codex_rtce(server_name: str, url: str, token: str) -> str:
    """Write the RTCE HTTP MCP server into Codex config. Returns a scope note."""
    config_paths = _codex_config_paths_rtce()
    for codex_config_path in config_paths:
        _write_codex_config_rtce(codex_config_path, server_name, url, token)

    scope_note = f"Codex ({config_paths[0]})"
    for shadow_path in config_paths[1:]:
        print(f"✓ Updated project-local Codex config at {shadow_path}")
    return scope_note


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


def _test_mcp_connection(url: str, token: str) -> tuple[bool, int]:
    """Send an MCP initialize POST to verify the Global API key works with the endpoint."""
    body = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "setup-rtce", "version": "0.1"},
            },
        }
    ).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return True, resp.status
    except urllib.error.HTTPError as exc:
        return False, exc.code
    except Exception:
        return False, 0


def _parse_topics(raw: str) -> list[str]:
    return [t.strip() for t in raw.split(",") if t.strip()]


def main():
    creds_file = _find_credentials_file()
    creds = _load_env_file(creds_file)

    # Auto-create a Global API key when none is stored in credentials.env.
    # Terraform provisions the service account + role bindings; this script creates
    # the Global key (--resource global) via CLI, which the Terraform provider can't do.
    if not creds.get(_CRED_KEY):
        tf_outputs = _read_core_tf_outputs(creds_file)
        sa_id = tf_outputs.get(_TF_RTCE_SA_ID, "").strip()
        if sa_id:
            print(
                f"Creating Global API key for RTCE service account {sa_id} via CLI..."
            )
            key, secret = _create_rtce_global_key_via_cli(sa_id)
            if key and secret:
                print(f"  ✓ Created Global API key: {key[:8]}...")
                creds[_CRED_KEY] = key
                creds[_CRED_SECRET] = secret
                _save_to_env_file(creds_file, _CRED_KEY, key)
                _save_to_env_file(creds_file, _CRED_SECRET, secret)
            else:
                print(
                    "  ✗ CLI key creation failed — check that `confluent login` is active."
                )

    api_key, api_secret = _get_credentials(creds_file, creds)
    infra = _get_infra(creds_file)
    _validate_rtce_support(infra)

    print()
    raw_name = input(f"MCP server name [{_DEFAULT_SERVER_NAME}]: ").strip()
    server_name = raw_name if raw_name else _DEFAULT_SERVER_NAME

    client = _pick_client()

    print("\nFetching currently RTCE-enabled topics...")
    already_enabled = _list_rtce_topics(api_key, api_secret, infra)
    if already_enabled:
        print(f"  Already RTCE-enabled: {', '.join(already_enabled)}")
    else:
        print("  No topics are currently RTCE-enabled on this cluster.")

    print()
    raw_topics = _ask("Topics to connect to this MCP server (comma-separated): ")
    topics = _parse_topics(raw_topics)

    not_yet_enabled = [t for t in topics if t not in already_enabled]
    if not_yet_enabled:
        print(f"\nThe following topics are not yet RTCE-enabled:")
        for t in not_yet_enabled:
            print(f"  • {t}")
        print("  (Requires the topic to have a registered schema in Schema Registry.)")
        do_enable = input("Enable RTCE on them now? [Y/n]: ").strip().lower()
        if do_enable != "n":
            for topic in not_yet_enabled:
                desc = input(
                    f"  Description for '{topic}' (helps AI agents understand the data): "
                ).strip()
                if not desc:
                    desc = f"Data from the {topic} Kafka topic"
                print(f"  Enabling RTCE on '{topic}'...", end=" ", flush=True)
                ok = _enable_rtce_topic(api_key, api_secret, infra, topic, desc)
                print("✓" if ok else "✗  (see error above)")

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
    elif client == "codex":
        scope_note = _register_with_codex_rtce(server_name, url, token)
        restart_note = "Restart Codex CLI to activate."
    else:
        scope_note = _register_with_claude_code(server_name, url, token)
        restart_note = "Restart Claude Code to activate."

    print(f"\n✓ RTCE MCP server registered as '{server_name}' ({scope_note})")
    print(f"  Topics:   {', '.join(topics)}")
    print(f"  Endpoint: {url}")

    print("\nTesting MCP connection...", end=" ", flush=True)
    ok, status = _test_mcp_connection(url, token)
    if ok:
        print(f"✓ ({status}) MCP connection test passed — agent can query your topics")
    elif status in (401, 403):
        print(
            f"✗ ({status}) Global API key is invalid or lacks RTCE roles "
            f"(DeveloperRead + SchemaRegistryRead).\n"
            f"  Update CONFLUENT_RTCE_API_KEY / CONFLUENT_RTCE_API_SECRET in credentials.env\n"
            f"  and re-run: uv run setup-rtce"
        )
    elif status == 404:
        print(
            f"⚠ (404) RTCE MCP endpoint not yet provisioned for this cluster.\n"
            f"  Try connecting in Claude Code (/mcp) in a few minutes."
        )
    else:
        code_str = str(status) if status else "connection error"
        print(f"⚠ ({code_str}) Unexpected response — verify the endpoint manually.")

    print(f"\n  {restart_note}")


if __name__ == "__main__":
    main()
