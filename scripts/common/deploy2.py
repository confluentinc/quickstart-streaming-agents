#!/usr/bin/env python3
"""Deploy script v2 — single source of truth in credentials.env.

Usage:
    uv run deploy2                   # Auto-detect: full flow or quick-deploy
    uv run deploy2 --full            # Force full setup flow
    uv run deploy2 --plain           # Plain text mode (no rich/questionary UI)
    uv run deploy2 --edit            # Edit a saved variable (menu)
    uv run deploy2 --edit <key>      # Edit directly: cloud, labs, confluent-keys,
                                     #                cloud-creds, zapier, email
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Optional enhanced libraries (degrade gracefully if missing) ───────────────
try:
    from rich.console import Console
    from rich.panel import Panel
    _console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

try:
    import questionary
    HAS_QUESTIONARY = True
    try:
        import questionary.prompts.common as _qpc
        _qpc.INDICATOR_SELECTED   = "[x]"
        _qpc.INDICATOR_UNSELECTED = "[ ]"
    except (ImportError, AttributeError):
        pass
    QSTYLE = questionary.Style([
        ("qmark",       "fg:#5f87ff bold"),
        ("question",    "bold"),
        ("answer",      "fg:#5f87ff bold"),
        ("pointer",     "fg:#5f87ff bold"),
        ("highlighted", "fg:#ffffff bg:#005faf bold"),
        ("selected",    "fg:#5f87ff bold"),
        ("instruction", "fg:#858585"),
        ("text",        "bold"),
        ("disabled",    "fg:#858585 italic"),
    ])
except ImportError:
    HAS_QUESTIONARY = False
    QSTYLE = None

# ── Constants ─────────────────────────────────────────────────────────────────
VERSION = "2.1.0"

# (config_key, display_name, terraform_dir)
LABS = [
    ("lab1", "Lab 1 — MCP Tool Calling",         "lab1-tool-calling"),
    ("lab2", "Lab 2 — Vector Search / RAG",       "lab2-vector-search"),
    ("lab3", "Lab 3 — Streaming Agents",          "lab3-agentic-fleet-management"),
    ("lab4", "Lab 4 — Fraud Detection",           "lab4-pubsec-fraud-agents"),
]

EDIT_KEYS = {
    "cloud":          "Cloud Provider",
    "labs":           "Labs",
    "confluent-keys": "Confluent API Keys",
    "cloud-creds":    "Cloud Credentials",
    "zapier":         "Zapier Token",
    "email":          "Email (for tagging)",
}

# Keys that must be present in credentials.env for quick-deploy
_REQUIRED_KEYS = [
    "TF_VAR_confluent_cloud_api_key",
    "TF_VAR_confluent_cloud_api_secret",
    "TF_VAR_cloud_provider",
    "TF_VAR_zapier_token",
]

# Cloud-specific credential keys
_AWS_KEYS   = ["TF_VAR_aws_bedrock_access_key", "TF_VAR_aws_bedrock_secret_key"]
_AZURE_KEYS = ["TF_VAR_azure_openai_endpoint_raw", "TF_VAR_azure_openai_api_key"]


# ── Project root ──────────────────────────────────────────────────────────────
def _project_root() -> Path:
    here = Path(__file__).resolve().parent
    for p in [here, *here.parents]:
        if (p / "pyproject.toml").exists():
            return p
    return here


# ── credentials.env helpers ──────────────────────────────────────────────────
def _env_path() -> Path:
    return _project_root() / "credentials.env"


def _load_env() -> dict:
    """Load all values from credentials.env."""
    p = _env_path()
    if not p.exists():
        return {}
    from dotenv import dotenv_values
    return {k: v for k, v in dotenv_values(p).items() if v}


def _save_env(key: str, value: str) -> None:
    """Write a single key to credentials.env."""
    p = _env_path()
    if not p.exists():
        p.touch()
    from dotenv import set_key
    set_key(str(p), key, value)


def _save_env_many(pairs: dict) -> None:
    """Write multiple keys to credentials.env."""
    p = _env_path()
    if not p.exists():
        p.touch()
    from dotenv import set_key
    for k, v in pairs.items():
        if v is not None:
            set_key(str(p), k, v)


def _is_ready(env: dict) -> bool:
    """Check if all required keys exist for quick-deploy."""
    for k in _REQUIRED_KEYS:
        if not env.get(k):
            return False
    # Must have labs selected
    if not env.get("DEPLOY_LABS"):
        return False
    # Must have cloud-specific credentials
    cloud = env.get("TF_VAR_cloud_provider", "aws")
    cloud_keys = _AWS_KEYS if cloud == "aws" else _AZURE_KEYS
    for k in cloud_keys:
        if not env.get(k):
            return False
    return True


# ── Terminal hyperlinks ───────────────────────────────────────────────────────
def _smart_link(url: str, text: str) -> str:
    if sys.stdout.isatty() and not os.environ.get("NO_COLOR") and os.environ.get("TERM") != "dumb":
        return f"\033]8;;{url}\033\\{text}\033]8;;\033\\"
    return f"{text}: {url}"


# ── Credential display helpers ────────────────────────────────────────────────
def _trunc(value: str, n: int = 12) -> str:
    if not value:
        return "not set"
    return value[:n] + "..." if len(value) > n else value


def _mask(value: str) -> str:
    if not value:
        return "not set"
    if len(value) <= 4:
        return "••••" + value
    return "••••••••" + value[-4:]


def _get_cloud_cred_info(env: dict) -> tuple[str, str]:
    """Get the cloud credential label and masked value based on provider."""
    cloud = env.get("TF_VAR_cloud_provider", "aws")
    if cloud == "aws":
        label = "AWS Bedrock"
        value = env.get("TF_VAR_aws_bedrock_access_key")
    else:
        label = "Azure OpenAI"
        value = env.get("TF_VAR_azure_openai_api_key")
    return label, _mask(value)


# ── Migration from .deploy-config.json ────────────────────────────────────────
def _migrate_json_config() -> None:
    """One-time migration: copy values from .deploy-config.json to credentials.env."""
    json_path = _project_root() / ".deploy-config.json"
    if not json_path.exists():
        return

    try:
        with open(json_path) as f:
            config = json.load(f)
    except (json.JSONDecodeError, OSError):
        return

    env = _load_env()
    pairs = {}

    # Map JSON config keys → credentials.env TF_VAR keys
    mapping = {
        "confluent_api_key":      "TF_VAR_confluent_cloud_api_key",
        "confluent_api_secret":   "TF_VAR_confluent_cloud_api_secret",
        "cloud_provider":         "TF_VAR_cloud_provider",
        "email":                  "TF_VAR_owner_email",
        "zapier_token":           "TF_VAR_zapier_token",
        "aws_access_key_id":      "TF_VAR_aws_bedrock_access_key",
        "aws_secret_access_key":  "TF_VAR_aws_bedrock_secret_key",
        "azure_openai_endpoint":  "TF_VAR_azure_openai_endpoint_raw",
        "azure_openai_api_key":   "TF_VAR_azure_openai_api_key",
    }

    for json_key, env_key in mapping.items():
        val = config.get(json_key)
        if val and not env.get(env_key):
            pairs[env_key] = val

    # Migrate labs
    labs = config.get("labs")
    if labs and not env.get("DEPLOY_LABS"):
        pairs["DEPLOY_LABS"] = ",".join(labs)

    if pairs:
        _save_env_many(pairs)
        print(f"  Migrated {len(pairs)} value(s) from .deploy-config.json → credentials.env")


# ── Display ───────────────────────────────────────────────────────────────────
def _banner() -> None:
    if HAS_RICH:
        _console.print(Panel.fit(
            f"  Streaming Agents Quickstart  ·  Deploy Script  ·  v{VERSION}  ",
            border_style="bright_blue",
        ))
    else:
        content = f"  Streaming Agents Quickstart  ·  Deploy Script  ·  v{VERSION}  "
        w = len(content)
        print("╔" + "═" * w + "╗")
        print(f"║{content}║")
        print("╚" + "═" * w + "╝")
    print()


def _section(title: str) -> None:
    width = 54
    inner = f" {title} "
    remaining = max(0, width - len(inner))
    left = remaining // 2
    right = remaining - left
    print(f"\n  {'═' * left}{inner}{'═' * right}")


def _fmt_labs(env: dict) -> str:
    ids = (env.get("DEPLOY_LABS") or "").split(",")
    ids = [i.strip() for i in ids if i.strip()]
    names = [name.split(" — ")[0] for lid, name, _ in LABS if lid in ids]
    return ", ".join(names) if names else "none selected"


def _show_summary(env: dict) -> None:
    cloud = (env.get("TF_VAR_cloud_provider") or "not set").upper()
    labs = _fmt_labs(env)
    ck = _mask(env.get("TF_VAR_confluent_cloud_api_key"))
    cl_label, cl_value = _get_cloud_cred_info(env)
    zap = _mask(env.get("TF_VAR_zapier_token"))
    email = env.get("TF_VAR_owner_email") or "not set"

    print(f"  Cloud:          {cloud}")
    print(f"  Labs:           {labs}")
    print(f"  Confluent Key:  {ck}")
    print(f"  {cl_label}:    {cl_value}")
    print(f"  Zapier Token:   {zap}")
    print(f"  Email:          {email}")

    lr = env.get("DEPLOY_LAST_RUN", "")
    if lr:
        try:
            dt = datetime.fromisoformat(lr)
            h = str(int(dt.strftime("%I")))
            print(f"\n  Last run: {dt.strftime('%b %d, %Y at ')}{h}{dt.strftime(':%M %p')}")
        except (ValueError, AttributeError):
            pass


# ── Phase 0: Pre-flight ───────────────────────────────────────────────────────
def _preflight(env: dict) -> bool:
    from scripts.common.login_checks import check_confluent_login

    print("  Checking prerequisites...")
    results, failures = {}, []

    for cmd, label, fix in [
        (["confluent", "version"], "confluent CLI installed",
         "confluent CLI not found — install from https://docs.confluent.io/confluent-cli/"),
        (["terraform", "version"],  "terraform installed",
         "terraform not found — install from https://developer.hashicorp.com/terraform/install"),
    ]:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            ok = r.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            ok = False
        results[label] = ok
        if not ok:
            failures.append(fix)

    logged_in = check_confluent_login()
    results["Logged into Confluent Cloud"] = logged_in
    if not logged_in:
        failures.append("Not logged in — run: confluent login")

    for label, ok in results.items():
        print(f"  {'✓' if ok else '✗'} {label}")

    if failures:
        print()
        for msg in failures:
            print(f"  ✗  {msg}")
        return False

    # ── Advisory credential checks (all soft — user can override) ─────────────
    cloud = env.get("TF_VAR_cloud_provider", "aws")
    selected_labs = [s.strip() for s in (env.get("DEPLOY_LABS") or "").split(",") if s.strip()]

    # LLM access (cloud-specific)
    if cloud == "aws":
        access_key = env.get("TF_VAR_aws_bedrock_access_key")
        secret_key = env.get("TF_VAR_aws_bedrock_secret_key")
        if access_key and secret_key:
            if not _check_bedrock_creds(env, access_key, secret_key):
                return False
    elif cloud == "azure":
        endpoint = env.get("TF_VAR_azure_openai_endpoint_raw")
        api_key  = env.get("TF_VAR_azure_openai_api_key")
        if endpoint and api_key:
            if not _check_azure_openai_creds(endpoint, api_key):
                return False

    # MongoDB (lab2, lab3 — user-provided or workshop defaults)
    if any(lab in selected_labs for lab in ("lab2", "lab3")):
        if not _check_mongodb_for_labs(env, selected_labs, cloud):
            return False

    # Lab4 data source (hardcoded workshop data — CosmosDB for Azure, MongoDB for AWS)
    if "lab4" in selected_labs:
        if not _check_lab4_data(cloud):
            return False

    return True


def _check_bedrock_creds(env: dict, access_key: str, secret_key: str) -> bool:
    """
    Advisory check for AWS Bedrock credentials.
    Returns True to continue, False to abort (user cancelled).
    """
    import logging
    from scripts.common.test_bedrock_credentials import test_bedrock_credentials, test_titan_embeddings

    region = env.get("TF_VAR_cloud_region", "us-east-1")
    _logger = logging.getLogger("preflight.bedrock")
    _logger.setLevel(logging.CRITICAL)  # suppress library noise

    print()
    print("  Checking AWS Bedrock model access...")

    sonnet_ok, sonnet_err = test_bedrock_credentials(
        access_key, secret_key, region, logger=_logger, max_retries=1
    )
    titan_ok, titan_err = test_titan_embeddings(
        access_key, secret_key, region, logger=_logger, max_retries=1
    )

    sonnet_label = f"Claude Sonnet 4.5 accessible ({region})"
    titan_label  = f"Titan Embeddings accessible ({region})"
    print(f"  {'✓' if sonnet_ok else '✗'} {sonnet_label}")
    print(f"  {'✓' if titan_ok  else '✗'} {titan_label}")

    if sonnet_ok and titan_ok:
        return True

    # Collect warnings per failure type
    warnings = []
    model_enable_needed = False

    for ok, err, model_name in [
        (sonnet_ok, sonnet_err, "Claude Sonnet 4.5"),
        (titan_ok,  titan_err,  "Titan Embed Text v1"),
    ]:
        if ok:
            continue
        if err == "invalid_keys":
            warnings.append(
                "The AWS credentials were not recognized. They may be expired or incorrect.\n"
                "Generate fresh credentials with:  uv run api-keys create aws"
            )
            break  # both will fail with same root cause — only show once
        elif err == "model_not_enabled":
            model_enable_needed = True
            warnings.append(f"{model_name} is not enabled in your AWS account for region {region}.")
        elif err == "no_boto3":
            warnings.append("boto3 is not installed — skipping live Bedrock check.")
            return True  # not a blocker, skip advisory

    if model_enable_needed:
        warnings.append(
            "To enable Claude models, visit the AWS Bedrock Model Catalog:\n"
            "  https://console.aws.amazon.com/bedrock/home#/model-catalog\n"
            "Select Claude Sonnet 4.5 → open in Playground → send a message.\n"
            "The access request form will appear automatically."
        )

    print()
    print("  ┌─────────────────────────────────────────────────────┐")
    print("  │  ⚠  WARNING: AWS Bedrock model access issue         │")
    print("  └─────────────────────────────────────────────────────┘")
    for w in warnings:
        for line in w.splitlines():
            print(f"  {line}")
    print()
    print("  If you deploy without resolving this, the demo may fail")
    print("  when Flink attempts to call the LLM models.")
    print()

    OPT_CONTINUE = "I understand — deploy anyway"
    OPT_ABORT    = "Abort — I'll fix my credentials first"
    choice = _select("How would you like to proceed?", [OPT_CONTINUE, OPT_ABORT])

    if choice == OPT_ABORT:
        print("\n  Deployment aborted.")
        return False
    return True


# ── Advisory check: Azure OpenAI ─────────────────────────────────────────────
def _check_azure_openai_creds(endpoint: str, api_key: str) -> bool:
    """
    Advisory check for Azure OpenAI credentials.
    Returns True to continue, False if user chose to abort.
    """
    import logging
    from scripts.common.test_azure_openai_credentials import (
        test_azure_openai_chat,
        test_azure_openai_embeddings,
    )

    _logger = logging.getLogger("preflight.azure_openai")
    _logger.setLevel(logging.CRITICAL)

    print()
    print("  Checking Azure OpenAI model access...")

    chat_ok, chat_err = test_azure_openai_chat(endpoint, api_key, logger=_logger, max_retries=1)
    emb_ok,  emb_err  = test_azure_openai_embeddings(endpoint, api_key, logger=_logger, max_retries=1)

    print(f"  {'✓' if chat_ok else '✗'} gpt-5-mini accessible")
    print(f"  {'✓' if emb_ok  else '✗'} text-embedding-ada-002 accessible")

    if chat_ok and emb_ok:
        return True

    warnings = []
    for ok, err, model in [
        (chat_ok, chat_err, "gpt-5-mini"),
        (emb_ok,  emb_err,  "text-embedding-ada-002"),
    ]:
        if ok:
            continue
        if err == "invalid_credentials":
            warnings.append(
                "Azure OpenAI credentials were rejected (401 Unauthorized).\n"
                "Generate fresh credentials with:  uv run api-keys create azure"
            )
            break
        elif err == "deployment_not_found":
            warnings.append(
                f"The '{model}' deployment was not found in your Azure OpenAI resource.\n"
                "Ensure both 'gpt-5-mini' and 'text-embedding-ada-002' deployments exist."
            )
        elif err == "no_requests":
            return True  # can't check; skip silently

    return _advisory_prompt(
        "Azure OpenAI model access issue",
        warnings,
        "If you deploy without resolving this, the demo may fail\n"
        "  when Flink attempts to call the LLM models.",
    )


# ── Advisory check: MongoDB (lab2, lab3) ─────────────────────────────────────
def _check_mongodb_for_labs(env: dict, selected_labs: list, cloud: str) -> bool:
    """
    Advisory check for MongoDB connectivity.
    Tests user-provided credentials if present, otherwise tests the workshop defaults.
    Returns True to continue, False if user chose to abort.
    """
    import logging
    from scripts.common.test_mongodb_credentials import test_mongodb_connection, test_workshop_mongodb

    _logger = logging.getLogger("preflight.mongodb")
    _logger.setLevel(logging.CRITICAL)

    user_conn = env.get("TF_VAR_mongodb_connection_string")
    user_name = env.get("TF_VAR_mongodb_username")
    user_pass = env.get("TF_VAR_mongodb_password")

    print()
    print("  Checking MongoDB connectivity...")

    if user_conn and user_name and user_pass:
        # User has provided their own MongoDB — test those credentials
        ok, err = test_mongodb_connection(user_conn, user_name, user_pass, logger=_logger)
        print(f"  {'✓' if ok else '✗'} User-provided MongoDB reachable")
        if ok:
            return True
        warnings = _mongodb_warnings(err, user_provided=True)
    else:
        # No user credentials — test the pre-populated workshop defaults
        results = {}
        for lab in ("lab2", "lab3"):
            if lab not in selected_labs:
                continue
            ok, err = test_workshop_mongodb(lab, cloud, logger=_logger)
            label = f"Workshop MongoDB ({lab}/{cloud})"
            print(f"  {'✓' if ok else '✗'} {label}")
            results[lab] = (ok, err)

        if all(v[0] for v in results.values()):
            return True

        # At least one failed
        first_err = next((err for _, (ok, err) in results.items() if not ok), "error")
        warnings = _mongodb_warnings(first_err, user_provided=False)

    return _advisory_prompt(
        "MongoDB connectivity issue",
        warnings,
        "If you deploy without resolving this, Lab2/Lab3 vector search\n"
        "  may fail at runtime.",
    )


def _mongodb_warnings(err: str, user_provided: bool) -> list:
    if err == "no_pymongo":
        return []  # can't check; caller should return True silently
    if user_provided:
        if err == "invalid_credentials":
            return ["Your MongoDB credentials were rejected.\n"
                    "Check your username and password, then update with:\n"
                    "  uv run deploy2 --edit cloud-creds"]
        return ["Could not connect to your MongoDB instance.\n"
                "Check that the connection string is correct and that\n"
                "0.0.0.0/0 is allowed in your MongoDB Atlas Network Access settings."]
    else:
        return ["The workshop MongoDB demo data could not be reached.\n"
                "This is a Confluent-managed resource. Contact the workshop team\n"
                "or check your network connection."]


# ── Advisory check: Lab4 data source ─────────────────────────────────────────
def _check_lab4_data(cloud: str) -> bool:
    """
    Advisory check for Lab4's hardcoded data source:
      - Azure: CosmosDB workshop demo endpoint
      - AWS:   Workshop MongoDB lab4 instance
    Returns True to continue, False if user chose to abort.
    """
    import logging

    _logger = logging.getLogger("preflight.lab4")
    _logger.setLevel(logging.CRITICAL)

    print()

    if cloud == "azure":
        from scripts.common.test_cosmosdb_credentials import test_cosmosdb_access
        print("  Checking Lab4 CosmosDB demo data...")
        ok, err = test_cosmosdb_access(logger=_logger)
        print(f"  {'✓' if ok else '✗'} CosmosDB workshop demo data reachable")
        if ok:
            return True
        if err == "no_requests":
            return True
        warnings = [
            "The Lab4 CosmosDB demo database could not be reached.\n"
            "This is a Confluent-managed resource used for the FEMA fraud detection demo.\n"
            "Contact the workshop team or check your network connection."
        ]
        blurb = "Lab4 may fail to load FEMA claims data at runtime."

    else:  # aws
        from scripts.common.test_mongodb_credentials import test_workshop_mongodb
        print("  Checking Lab4 MongoDB demo data...")
        ok, err = test_workshop_mongodb("lab4", "aws", logger=_logger)
        print(f"  {'✓' if ok else '✗'} MongoDB workshop demo data (lab4/aws) reachable")
        if ok:
            return True
        if err in ("no_pymongo", "no_config"):
            return True
        warnings = [
            "The Lab4 workshop MongoDB demo database could not be reached.\n"
            "This is a Confluent-managed resource used for the FEMA fraud detection demo.\n"
            "Contact the workshop team or check your network connection."
        ]
        blurb = "Lab4 may fail to load FEMA claims data at runtime."

    return _advisory_prompt("Lab4 demo data connectivity issue", warnings, blurb)


# ── Shared advisory prompt helper ─────────────────────────────────────────────
def _advisory_prompt(title: str, warnings: list, blurb: str) -> bool:
    """
    Display a warning box with the given messages and ask the user to
    continue or abort.  Returns True to continue, False to abort.
    If warnings is empty, returns True silently.
    """
    if not warnings:
        return True

    box_width = 53
    padded = f"  ⚠  WARNING: {title}"
    print()
    print(f"  ┌{'─' * box_width}┐")
    print(f"  │{padded:<{box_width}}│")
    print(f"  └{'─' * box_width}┘")
    for w in warnings:
        for line in w.splitlines():
            print(f"  {line}")
    print()
    for line in blurb.splitlines():
        print(f"  {line}")
    print()

    OPT_CONTINUE = "I understand — deploy anyway"
    OPT_ABORT    = "Abort — I'll fix this first"
    choice = _select("How would you like to proceed?", [OPT_CONTINUE, OPT_ABORT])

    if choice == OPT_ABORT:
        print("\n  Deployment aborted.")
        return False
    return True


# ── Interactive prompt helpers ────────────────────────────────────────────────
def _select(question: str, choices: list, default: str = None) -> str:
    if HAS_QUESTIONARY and sys.stdout.isatty():
        result = questionary.select(question, choices=choices, default=default, style=QSTYLE).ask()
        if result is None:
            print("\n  Aborted.")
            sys.exit(0)
        return result
    effective_default = default if default is not None else choices[0]
    print(f"\n  {question}\n")
    for i, c in enumerate(choices, 1):
        marker = "> " if c == effective_default else "  "
        print(f"    {marker}{i}) {c}")
    print(f"\n  [default: {effective_default}]  ", end="")
    while True:
        raw = input("Choice: ").strip()
        if not raw:
            return effective_default
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except ValueError:
            pass
        print(f"  Invalid. Enter 1–{len(choices)}.")


def _checkbox(question: str, choices: list, defaults: list = None) -> list:
    defaults = defaults or []
    if HAS_QUESTIONARY and sys.stdout.isatty():
        q = [
            questionary.Choice(title=label, value=val, checked=(val in defaults))
            for val, label in choices
        ]
        result = questionary.checkbox(
            question, choices=q,
            instruction="(↑↓ navigate · SPACE select · ENTER confirm)",
            style=QSTYLE,
        ).ask()
        if result is None:
            print("\n  Aborted.")
            sys.exit(0)
        return result
    print(f"\n  {question}")
    print("  (Enter numbers separated by commas, e.g. 1,3)\n")
    for i, (val, label) in enumerate(choices, 1):
        mark = "[x]" if val in defaults else "[ ]"
        print(f"    {mark} {i}) {label}")
    if defaults:
        names = [lbl for v, lbl in choices if v in defaults]
        print(f"\n  [previously: {', '.join(names)}]  ", end="")
    while True:
        raw = input("Selection (ENTER to keep defaults): ").strip()
        if not raw and defaults:
            return list(defaults)
        if not raw:
            print("  Please select at least one option.")
            continue
        try:
            indices = [int(x.strip()) - 1 for x in raw.split(",")]
            selected = [choices[i][0] for i in indices if 0 <= i < len(choices)]
            if selected:
                return selected
        except (ValueError, IndexError):
            pass
        print("  Invalid selection. Try again.")


def _text(prompt: str, default: str = None, secret: bool = False) -> str:
    if default is not None:
        preview = _mask(default) if secret else _trunc(default)
        disp = f"  {prompt} [previously: {preview}]: "
        value = input(disp).strip()
        return value if value else default
    disp = f"  {prompt}: "
    while True:
        value = input(disp).strip()
        if value:
            return value
        print("  This field is required.")


# ── Phase 2: Cloud Provider ───────────────────────────────────────────────────
def prompt_cloud_provider(env: dict) -> str:
    _section("Cloud Provider")
    prev = env.get("TF_VAR_cloud_provider", "aws")
    choices = ["AWS", "Azure"] if prev == "aws" else ["Azure", "AWS"]
    choice = _select("Which cloud provider are you deploying to?", choices=choices)
    result = choice.lower()
    _save_env("TF_VAR_cloud_provider", result)
    return result


# ── Phase 3: Lab Selection ────────────────────────────────────────────────────
def prompt_lab_selection(env: dict) -> list:
    _section("Lab Selection")
    saved = [s.strip() for s in (env.get("DEPLOY_LABS") or "").split(",") if s.strip()]
    choices = [(lid, name) for lid, name, _ in LABS] + [("all", "All Labs")]
    selected = _checkbox("Which labs do you want to deploy?", choices=choices, defaults=saved)
    if "all" in selected:
        selected = [lid for lid, _, _ in LABS]
    else:
        selected = [s for s in selected if s != "all"]
    _save_env("DEPLOY_LABS", ",".join(selected))
    return selected


# ── Phase 4: Confluent API Keys ───────────────────────────────────────────────
def prompt_confluent_keys(env: dict) -> None:
    _section("Confluent Cloud API Keys")
    print()
    print("  We strongly recommend letting us generate these")
    print("  automatically to avoid configuration errors.")
    print()

    saved_key    = env.get("TF_VAR_confluent_cloud_api_key")
    saved_secret = env.get("TF_VAR_confluent_cloud_api_secret")

    OPT_REUSE  = "Reuse my saved keys"
    OPT_AUTO   = "Generate automatically"
    OPT_MANUAL = "Enter manually"

    if saved_key and saved_secret:
        choices = [OPT_REUSE, OPT_AUTO, OPT_MANUAL]
    else:
        choices = [OPT_AUTO, OPT_MANUAL]

    choice = _select("Confluent Cloud API Keys:", choices=choices)

    if choice == OPT_REUSE:
        return

    if choice == OPT_AUTO:
        from scripts.common.credentials import generate_confluent_api_keys
        print("\n  Generating Confluent Cloud API keys...")
        api_key, api_secret = generate_confluent_api_keys()
        if not api_key or not api_secret:
            print("  ✗ Failed to generate Confluent API keys. Aborting.")
            sys.exit(1)
        _save_env_many({
            "TF_VAR_confluent_cloud_api_key":    api_key,
            "TF_VAR_confluent_cloud_api_secret": api_secret,
        })
        print(f"  ✓ Generated key: {_trunc(api_key)}")
        return

    # Manual entry
    key    = _text("API Key",    default=saved_key)
    secret = _text("API Secret", default=saved_secret, secret=True)
    _save_env_many({
        "TF_VAR_confluent_cloud_api_key":    key,
        "TF_VAR_confluent_cloud_api_secret": secret,
    })


# ── Phase 5: Cloud Credentials ────────────────────────────────────────────────
def prompt_cloud_creds(env: dict, cloud: str) -> None:
    label = "AWS Bedrock" if cloud == "aws" else "Azure OpenAI"
    _section(f"{label} Credentials")
    print()
    print("  These are required to deploy. You can let us")
    print("  generate them, or provide your own.")
    print()

    if cloud == "aws":
        has_saved = bool(env.get("TF_VAR_aws_bedrock_access_key") and env.get("TF_VAR_aws_bedrock_secret_key"))
    else:
        has_saved = bool(env.get("TF_VAR_azure_openai_endpoint_raw") and env.get("TF_VAR_azure_openai_api_key"))

    OPT_REUSE  = "Reuse my saved keys"
    OPT_AUTO   = "Generate automatically"
    OPT_MANUAL = "Enter manually"

    if has_saved:
        choices = [OPT_REUSE, OPT_AUTO, OPT_MANUAL]
    else:
        choices = [OPT_AUTO, OPT_MANUAL]

    choice = _select(f"{label} Credentials:", choices=choices)

    if choice == OPT_REUSE:
        return

    if choice == OPT_AUTO:
        email = _prompt_email(env)
        _save_env("TF_VAR_owner_email", email)

        print(f"\n  Generating {label} credentials...")
        root = _project_root()
        subprocess.run(["uv", "run", "api-keys", "create", cloud], cwd=root)
        return

    # Manual entry
    if cloud == "aws":
        key    = _text("AWS Access Key ID",     default=env.get("TF_VAR_aws_bedrock_access_key"))
        secret = _text("AWS Secret Access Key", default=env.get("TF_VAR_aws_bedrock_secret_key"), secret=True)
        _save_env_many({
            "TF_VAR_aws_bedrock_access_key": key,
            "TF_VAR_aws_bedrock_secret_key": secret,
        })
    elif cloud == "azure":
        endpoint = _text("Azure OpenAI Endpoint", default=env.get("TF_VAR_azure_openai_endpoint_raw"))
        api_key  = _text("Azure OpenAI API Key",  default=env.get("TF_VAR_azure_openai_api_key"), secret=True)
        _save_env_many({
            "TF_VAR_azure_openai_endpoint_raw": endpoint,
            "TF_VAR_azure_openai_api_key":      api_key,
        })


def _prompt_email(env: dict) -> str:
    print()
    print("  To tag your cloud resources correctly, we need")
    print("  your email address.")
    print()
    return _text("Email", default=env.get("TF_VAR_owner_email"))


# ── Phase 6: Zapier Token ─────────────────────────────────────────────────────
def prompt_zapier_token(env: dict) -> None:
    _section("Zapier Integration")
    print()
    print("  A Zapier API token is required. You must provide")
    print("  this — we can't generate it on your behalf.")
    print()
    zapier_guide_url = "https://github.com/confluentinc/quickstart-streaming-agents/blob/master/assets/pre-setup/Zapier-Setup.md"
    link = _smart_link(zapier_guide_url, "Setup Guide → Zapier Token")
    print(f"  Don't have one? See: {link}")
    print()

    saved = env.get("TF_VAR_zapier_token")

    if saved:
        OPT_REUSE = "Reuse my saved token"
        OPT_ENTER = "Enter new token"
        choice = _select("Zapier Token:", choices=[OPT_REUSE, OPT_ENTER])
        if choice == OPT_REUSE:
            return

    token = _text("Zapier Token", secret=True)
    _save_env("TF_VAR_zapier_token", token)


# ── Phase 7: Review & Confirm ─────────────────────────────────────────────────
def show_review_and_confirm(env: dict) -> bool:
    _section("Deployment Summary")
    print()
    cloud = (env.get("TF_VAR_cloud_provider") or "not set").upper()
    labs = _fmt_labs(env)
    ck = _mask(env.get("TF_VAR_confluent_cloud_api_key"))
    cl_label, cl_value = _get_cloud_cred_info(env)
    zap = _mask(env.get("TF_VAR_zapier_token"))

    print(f"  Cloud Provider:        {cloud}")
    print(f"  Labs to Deploy:        {labs}")
    print(f"  Confluent API Key:     {ck}")
    print(f"  {cl_label + ' Keys:':23}{cl_value}")
    print(f"  Zapier Token:          {zap}")
    print()
    choice = _select("Proceed with deployment?", ["Yes, deploy", "No, cancel"])
    if choice == "Yes, deploy":
        return True
    print("\n  Deployment aborted.")
    return False


# ── Mode 1: Full Flow ─────────────────────────────────────────────────────────
def run_full_flow(env: dict) -> dict:
    if any(env.get(k) for k in _REQUIRED_KEYS):
        print()
        print("  " + "─" * 51)
        print("  Saved credentials found in credentials.env.")
        print("  Your previous answers are shown as defaults.")
        print("  Press ENTER to accept any default, or type to change.")
        print("  " + "─" * 51)

    prompt_cloud_provider(env)
    env = _load_env()

    prompt_lab_selection(env)
    env = _load_env()

    prompt_confluent_keys(env)
    env = _load_env()

    prompt_cloud_creds(env, env.get("TF_VAR_cloud_provider", "aws"))
    env = _load_env()

    prompt_zapier_token(env)
    env = _load_env()

    if not show_review_and_confirm(env):
        sys.exit(0)
    return env


# ── Mode 2: Quick-Deploy ──────────────────────────────────────────────────────
def run_quick_deploy(env: dict) -> dict:
    _section("Saved Configuration Found")
    print()
    _show_summary(env)
    print()

    OPT_DEPLOY = "Deploy with saved settings"
    OPT_EDIT   = "Edit a setting"
    OPT_FULL   = "Run full setup"
    OPT_QUIT   = "Quit"

    choice = _select(
        "What would you like to do?",
        choices=[OPT_DEPLOY, OPT_EDIT, OPT_FULL, OPT_QUIT],
    )

    if choice == OPT_DEPLOY:
        if not show_review_and_confirm(env):
            sys.exit(0)
        return env
    elif choice == OPT_EDIT:
        run_edit_menu(env)
        return run_quick_deploy(_load_env())
    elif choice == OPT_FULL:
        return run_full_flow(env)
    else:
        print("\n  Goodbye.")
        sys.exit(0)


# ── Mode 3: Edit ──────────────────────────────────────────────────────────────
def _edit_key(key: str, env: dict) -> None:
    cloud = env.get("TF_VAR_cloud_provider", "aws")
    if key == "cloud":
        prompt_cloud_provider(env)
    elif key == "labs":
        prompt_lab_selection(env)
    elif key == "confluent-keys":
        prompt_confluent_keys(env)
    elif key == "cloud-creds":
        prompt_cloud_creds(env, cloud)
    elif key == "zapier":
        prompt_zapier_token(env)
    elif key == "email":
        email = _prompt_email(env)
        _save_env("TF_VAR_owner_email", email)


def run_edit_menu(env: dict) -> None:
    while True:
        env = _load_env()
        _section("Edit Configuration")
        print()

        cloud = (env.get("TF_VAR_cloud_provider") or "not set").upper()
        labs = _fmt_labs(env)
        ck = _mask(env.get("TF_VAR_confluent_cloud_api_key"))
        cl_label, cl_value = _get_cloud_cred_info(env)
        zap = _mask(env.get("TF_VAR_zapier_token"))
        email = env.get("TF_VAR_owner_email") or "not set"

        FIELD_ITEMS = [
            ("cloud",          f"Cloud Provider       {cloud}"),
            ("labs",           f"Labs                 {labs}"),
            ("confluent-keys", f"Confluent API Keys   {ck}"),
            ("cloud-creds",    f"{cl_label} Keys       {cl_value}"),
            ("zapier",         f"Zapier Token         {zap}"),
            ("email",          f"Email (for tagging)  {email}"),
            ("__back__",       "← Done editing"),
        ]

        if HAS_QUESTIONARY and sys.stdout.isatty():
            q_choices = [
                questionary.Choice(title=label, value=key)
                for key, label in FIELD_ITEMS
            ]
            key = questionary.select(
                "Select a field to change:",
                choices=q_choices,
                style=QSTYLE,
            ).ask()
            if key is None:
                break
        else:
            print("  Select a field to change:\n")
            for i, (k, label) in enumerate(FIELD_ITEMS[:-1], 1):
                print(f"    {i}) {label}")
            print(f"    Q) ← Done editing\n")
            raw = input("  Choice: ").strip().upper()
            if raw == "Q":
                break
            try:
                idx = int(raw) - 1
                if 0 <= idx < len(FIELD_ITEMS) - 1:
                    key = FIELD_ITEMS[idx][0]
                else:
                    print("  Invalid choice.")
                    continue
            except ValueError:
                print("  Invalid choice.")
                continue

        if key == "__back__":
            break

        _edit_key(key, env)
        print()
        print(f"  ✓ {EDIT_KEYS[key]} updated.")
        print()

        next_action = _select(
            "What next?",
            choices=["Edit another setting", "Deploy now", "Quit"],
        )
        if next_action == "Deploy now":
            env = _load_env()
            if not show_review_and_confirm(env):
                sys.exit(0)
            return
        elif next_action == "Quit":
            sys.exit(0)


# ── Deployment execution ──────────────────────────────────────────────────────
def run_deployment(env: dict) -> None:
    from scripts.common.terraform_runner import run_terraform
    from scripts.common.tfvars import write_tfvars_for_deployment

    root   = _project_root()
    cloud  = env.get("TF_VAR_cloud_provider", "aws")
    region = env.get("TF_VAR_cloud_region", "us-east-1" if cloud == "aws" else "eastus2")

    # Load all TF_VAR_* into os.environ for Terraform
    for k, v in env.items():
        if k.startswith("TF_VAR_") and v:
            os.environ[k] = v

    # Also set cloud_region if not already present
    if "TF_VAR_cloud_region" not in os.environ:
        os.environ["TF_VAR_cloud_region"] = region

    # Build creds dict (strip TF_VAR_ prefix for write_tfvars_for_deployment)
    creds = {k: v for k, v in env.items() if k.startswith("TF_VAR_") and v}

    # Determine terraform environments
    lab_to_tf = {lid: tf for lid, _, tf in LABS}
    selected  = [s.strip() for s in (env.get("DEPLOY_LABS") or "").split(",") if s.strip()]
    envs      = ["core"] + [lab_to_tf[lab] for lab in selected if lab in lab_to_tf]

    # Write terraform.tfvars files
    write_tfvars_for_deployment(root, cloud, region, creds, envs)

    # Record last run
    _save_env("DEPLOY_LAST_RUN", datetime.now(timezone.utc).isoformat())

    print("\n=== Starting Deployment ===")
    for e in envs:
        env_path = root / "terraform" / e
        if not env_path.exists():
            print(f"  Warning: {env_path} does not exist, skipping.")
            continue
        if not run_terraform(env_path):
            print(f"\n  ✗ Deployment failed at {e}. Stopping.")
            sys.exit(1)

    print("\n  ✓ All deployments completed successfully!")


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description="Confluent Labs deploy script (v2)")
    parser.add_argument(
        "--edit", nargs="?", const="__menu__", metavar="KEY",
        help="Edit a saved variable. Keys: " + ", ".join(EDIT_KEYS),
    )
    parser.add_argument(
        "--full", action="store_true",
        help="Force full setup flow even if saved credentials exist",
    )
    parser.add_argument(
        "--plain", action="store_true",
        help="Plain text mode: disable rich/questionary UI (useful on EC2 or dumb terminals)",
    )
    args = parser.parse_args()

    if args.plain:
        global HAS_RICH, HAS_QUESTIONARY
        HAS_RICH = False
        HAS_QUESTIONARY = False

    _banner()

    # One-time migration from old JSON config
    _migrate_json_config()

    env = _load_env()

    # Edit mode (skips pre-flight)
    if args.edit is not None:
        if not env:
            print("  No saved configuration found. Run the full setup first.")
            sys.exit(1)
        if args.edit == "__menu__":
            run_edit_menu(env)
        elif args.edit in EDIT_KEYS:
            _edit_key(args.edit, env)
            print(f"\n  ✓ {EDIT_KEYS[args.edit]} updated.")
        else:
            print(f"  Unknown key: {args.edit!r}")
            print(f"  Valid keys: {', '.join(EDIT_KEYS)}")
            sys.exit(1)
        sys.exit(0)

    # Pre-flight
    if not _preflight(env):
        print()
        sys.exit(1)

    # Mode selection
    if not args.full and _is_ready(env):
        env = run_quick_deploy(env)
    else:
        env = run_full_flow(env)

    run_deployment(env)


if __name__ == "__main__":
    main()