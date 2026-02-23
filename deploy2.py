#!/usr/bin/env python3
"""Deploy script v2 — implements the UX design from deploy-cli-ux-design_1.md.

Usage:
    uv run deploy2                   # Auto-detect: full flow or quick-deploy
    uv run deploy2 --full            # Force full setup flow
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
    # Patch checkbox indicators to [ ]/[x] instead of ○/●
    try:
        import questionary.prompts.common as _qpc
        _qpc.INDICATOR_SELECTED   = "[x]"
        _qpc.INDICATOR_UNSELECTED = "[ ]"
    except (ImportError, AttributeError):
        pass
    # Highlighted row = bold white text on blue background; pointer = blue arrow
    QSTYLE = questionary.Style([
        ("qmark",       "fg:#5f87ff bold"),
        ("question",    "bold"),
        ("answer",      "fg:#5f87ff bold"),
        ("pointer",     "fg:#5f87ff bold"),
        ("highlighted", "fg:#ffffff bg:#005faf bold"),
        ("selected",    "fg:#5f87ff bold"),
        ("instruction", "fg:#858585"),
        ("text",        "bold"),           # choices stand out from surrounding text
        ("disabled",    "fg:#858585 italic"),
    ])
except ImportError:
    HAS_QUESTIONARY = False
    QSTYLE = None

# ── Constants ─────────────────────────────────────────────────────────────────
VERSION = "2.0.0"
CONFIG_FILENAME = ".deploy-config.json"

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

_REQUIRED_FIELDS = [
    "cloud_provider", "labs", "confluent_api_key_mode", "cloud_creds_mode", "zapier_token",
]

# ── Project root ──────────────────────────────────────────────────────────────
def _project_root() -> Path:
    here = Path(__file__).resolve().parent
    for p in [here, *here.parents]:
        if (p / "pyproject.toml").exists():
            return p
    return here


# ── Terminal hyperlinks ───────────────────────────────────────────────────────
def _smart_link(url: str, text: str) -> str:
    if sys.stdout.isatty() and not os.environ.get("NO_COLOR") and os.environ.get("TERM") != "dumb":
        return f"\033]8;;{url}\033\\{text}\033]8;;\033\\"
    return f"{text}: {url}"


# ── Credential display helpers ────────────────────────────────────────────────
def _trunc(value: str, n: int = 12) -> str:
    """Show first n chars of a value, with ellipsis if truncated."""
    if not value:
        return "not set"
    if len(value) <= n:
        return value
    return value[:n] + "..."


def _mask(value: str) -> str:
    """Show last 4 chars with bullet prefix, or 'not set'."""
    if not value:
        return "not set"
    if len(value) <= 4:
        return "••••" + value
    return "••••••••" + value[-4:]


# ── credentials.env helpers ───────────────────────────────────────────────────
def _load_env_confluent_keys() -> tuple:
    """Return (api_key, api_secret) from credentials.env, or (None, None)."""
    env_file = _project_root() / "credentials.env"
    if not env_file.exists():
        return None, None
    from dotenv import dotenv_values
    creds = dotenv_values(env_file)
    key    = creds.get("TF_VAR_confluent_cloud_api_key")
    secret = creds.get("TF_VAR_confluent_cloud_api_secret")
    return (key, secret) if key and secret else (None, None)


def _load_env_zapier_token() -> str | None:
    """Return Zapier token from credentials.env, or None."""
    env_file = _project_root() / "credentials.env"
    if not env_file.exists():
        return None
    from dotenv import dotenv_values
    return dotenv_values(env_file).get("TF_VAR_zapier_token") or None


def _write_env_key(tf_var: str, value: str) -> None:
    """Write a single TF_VAR key to credentials.env, creating the file if needed."""
    env_file = _project_root() / "credentials.env"
    if not env_file.exists():
        env_file.touch()
    from dotenv import set_key
    set_key(str(env_file), tf_var, value)


def _load_env_cloud_creds(cloud: str) -> dict:
    """Return existing cloud credentials from credentials.env, or empty dict."""
    env_file = _project_root() / "credentials.env"
    if not env_file.exists():
        return {}
    from dotenv import dotenv_values
    creds = dotenv_values(env_file)
    if cloud == "aws":
        key    = creds.get("TF_VAR_aws_bedrock_access_key")
        secret = creds.get("TF_VAR_aws_bedrock_secret_key")
        if key and secret:
            return {"aws_access_key_id": key, "aws_secret_access_key": secret}
    elif cloud == "azure":
        endpoint = creds.get("TF_VAR_azure_openai_endpoint_raw")
        api_key  = creds.get("TF_VAR_azure_openai_api_key")
        if endpoint and api_key:
            return {"azure_openai_endpoint": endpoint, "azure_openai_api_key": api_key}
    return {}


# ── Config persistence ────────────────────────────────────────────────────────
def _config_path() -> Path:
    return _project_root() / CONFIG_FILENAME


def load_config() -> dict:
    p = _config_path()
    if p.exists():
        try:
            with open(p) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_config(config: dict) -> None:
    config = dict(config)
    config["last_run"] = datetime.now(timezone.utc).isoformat()
    with open(_config_path(), "w") as f:
        json.dump(config, f, indent=2)


def _config_complete(config: dict) -> bool:
    """Return True only when quick-deploy can succeed without further input."""
    for f in _REQUIRED_FIELDS:
        # zapier_token may live in credentials.env rather than the saved config
        if f == "zapier_token" and not config.get(f):
            if not _load_env_zapier_token():
                return False
            continue
        if not config.get(f):
            return False

    # Confluent Cloud API keys — must exist unless auto-generate will create them
    if config.get("confluent_api_key_mode") == "auto":
        pass  # will be generated during deployment
    else:
        env_key, env_secret = _load_env_confluent_keys()
        if not ((config.get("confluent_api_key") and config.get("confluent_api_secret"))
                or (env_key and env_secret)):
            return False

    # Cloud (LLM) credentials — must exist in config or credentials.env
    cloud = config.get("cloud_provider", "aws")
    cloud_mode = config.get("cloud_creds_mode", "")
    saved_cloud = _load_env_cloud_creds(cloud)
    if cloud_mode == "auto":
        # Auto generates during prompt flow and writes to credentials.env;
        # if values aren't there yet, config is incomplete
        if not saved_cloud:
            return False
    else:
        if cloud == "aws":
            has = (config.get("aws_access_key_id") and config.get("aws_secret_access_key")) or bool(saved_cloud)
        elif cloud == "azure":
            has = (config.get("azure_openai_endpoint") and config.get("azure_openai_api_key")) or bool(saved_cloud)
        else:
            has = False
        if not has:
            return False

    return True


# ── Display ───────────────────────────────────────────────────────────────────
def _banner() -> None:
    if HAS_RICH:
        _console.print(Panel.fit(
            f"  Confluent Labs  ·  Deploy Script  ·  v{VERSION}  ",
            border_style="bright_blue",
        ))
    else:
        w = 54
        print("╔" + "═" * w + "╗")
        print(f"║  Confluent Labs  ·  Deploy Script  ·  v{VERSION:<10}║")
        print("╚" + "═" * w + "╝")
    print()


def _section(title: str) -> None:
    print(f"\n  ─── {title} " + "─" * max(0, 47 - len(title)))


def _fmt_labs(config: dict) -> str:
    ids = config.get("labs") or []
    names = [name.split(" — ")[0] for lid, name, _ in LABS if lid in ids]
    return ", ".join(names) if names else "none selected"


def _fmt_cloud_creds(config: dict) -> str:
    mode = config.get("cloud_creds_mode", "")
    if mode == "auto":
        email = config.get("email", "")
        return f"Auto-generate  ({email})" if email else "Auto-generate"
    if mode == "manual":
        return "Manual"
    if mode == "reuse":
        return "Reuse saved"
    return "not set"


def _show_summary(config: dict) -> None:
    cloud  = (config.get("cloud_provider") or "not set").upper()
    labs   = _fmt_labs(config)
    cm     = config.get("confluent_api_key_mode", "")
    c_disp = "Auto-generate" if cm == "auto" else "Manual" if cm == "manual" else "Reuse saved" if cm == "reuse" else "not set"
    cl     = "AWS Bedrock" if config.get("cloud_provider") == "aws" else "Azure OpenAI"
    cc     = _fmt_cloud_creds(config)
    zap    = _mask(config.get("zapier_token", ""))
    print(f"  Cloud:          {cloud}")
    print(f"  Labs:           {labs}")
    print(f"  Confluent Keys: {c_disp}")
    print(f"  {cl}:    {cc}")
    print(f"  Zapier Token:   {zap}")
    lr = config.get("last_run", "")
    if lr:
        try:
            dt = datetime.fromisoformat(lr)
            h = str(int(dt.strftime("%I")))
            print(f"\n  Last run: {dt.strftime('%b %d, %Y at ')}{h}{dt.strftime(':%M %p')}")
        except (ValueError, AttributeError):
            pass


# ── Phase 0: Pre-flight ───────────────────────────────────────────────────────
def _preflight() -> bool:
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
            print(f"  Please run:  {msg}")
        return False
    return True


# ── Phase 1: Saved state notice ───────────────────────────────────────────────
def _saved_notice(config: dict) -> None:
    lr = config.get("last_run", "")
    date_str = ""
    if lr:
        try:
            dt = datetime.fromisoformat(lr)
            date_str = f" from {dt.strftime('%b %d, %Y')}"
        except (ValueError, AttributeError):
            pass
    print()
    print("  " + "─" * 51)
    print(f"  Saved session found{date_str}.")
    print("  Your previous answers are shown as defaults.")
    print("  Press ENTER to accept any default, or type to change.")
    print("  " + "─" * 51)


# ── Interactive prompt helpers ────────────────────────────────────────────────
def _select(question: str, choices: list, default: str = None) -> str:
    """Arrow-key selector; falls back to numbered list for non-TTY.

    If default is None, the cursor lands on the first choice (no extra highlight).
    If default is set, the cursor lands on that choice.
    """
    if HAS_QUESTIONARY and sys.stdout.isatty():
        result = questionary.select(question, choices=choices, default=default, style=QSTYLE).ask()
        if result is None:
            print("\n  Aborted.")
            sys.exit(0)
        return result
    # Non-TTY fallback
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
    """Multi-select with [x]/[ ] indicators.

    In TTY mode: ↑↓ to navigate, SPACE to toggle, ENTER to confirm.
    choices: list of (value, label). defaults: list of pre-selected values.
    """
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

    # ── Non-TTY fallback ──────────────────────────────────────────────────────
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
    """Text input. If default provided, ENTER accepts it. Required if no default."""
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
def prompt_cloud_provider(config: dict) -> str:
    _section("Cloud Provider")
    prev = config.get("cloud_provider", "aws")
    # Previous choice is placed first so the cursor lands on it naturally
    choices = ["AWS", "Azure"] if prev == "aws" else ["Azure", "AWS"]
    choice = _select("Which cloud provider are you deploying to?", choices=choices)
    return choice.lower()


# ── Phase 3: Lab Selection ────────────────────────────────────────────────────
def prompt_lab_selection(config: dict) -> list:
    _section("Lab Selection")
    saved = config.get("labs") or []
    choices = [(lid, name) for lid, name, _ in LABS] + [("all", "All Labs")]
    selected = _checkbox("Which labs do you want to deploy?", choices=choices, defaults=saved)
    if "all" in selected:
        return [lid for lid, _, _ in LABS]
    return [s for s in selected if s != "all"]


# ── Phase 4: Confluent API Keys ───────────────────────────────────────────────
def prompt_confluent_keys(config: dict) -> dict:
    _section("Confluent Cloud API Keys")
    print()
    print("  We strongly recommend letting us generate these")
    print("  automatically to avoid configuration errors.")
    print()

    env_key, env_secret = _load_env_confluent_keys()
    prev_mode = config.get("confluent_api_key_mode", "auto")

    # Build ordered choices — previous/best option goes first
    OPT_REUSE  = "Reuse my saved keys"
    OPT_AUTO   = "Generate automatically"
    OPT_MANUAL = "Enter manually"

    choices = []
    if prev_mode == "reuse" and env_key:
        choices = [OPT_REUSE, OPT_AUTO, OPT_MANUAL]
    elif prev_mode == "auto":
        choices = [OPT_AUTO, OPT_MANUAL]
        if env_key:
            choices.insert(0, OPT_REUSE)  # surfaced but not default
    else:  # manual
        choices = [OPT_MANUAL, OPT_AUTO]
        if env_key:
            choices.insert(0, OPT_REUSE)
    # If no saved keys, remove the reuse option
    if not env_key and OPT_REUSE in choices:
        choices.remove(OPT_REUSE)

    choice = _select("Confluent Cloud API Keys:", choices=choices)

    if choice == OPT_REUSE:
        return {
            "confluent_api_key_mode": "reuse",
            "confluent_api_key":    env_key,
            "confluent_api_secret": env_secret,
        }
    if choice == OPT_AUTO:
        return {"confluent_api_key_mode": "auto", "confluent_api_key": None, "confluent_api_secret": None}

    result = {"confluent_api_key_mode": "manual"}
    result["confluent_api_key"]    = _text("API Key",    default=config.get("confluent_api_key"))
    result["confluent_api_secret"] = _text("API Secret", default=config.get("confluent_api_secret"), secret=True)
    return result


# ── Phase 5: Cloud Credentials ────────────────────────────────────────────────
def prompt_cloud_creds(config: dict, cloud: str) -> dict:
    label = "AWS Bedrock" if cloud == "aws" else "Azure OpenAI"
    _section(f"{label} Credentials")
    print()
    print("  These are required to deploy. You can let us")
    print("  generate them, or provide your own.")
    print()

    prev_mode  = config.get("cloud_creds_mode", "auto")
    saved_creds = _load_env_cloud_creds(cloud)

    OPT_REUSE  = "Reuse my saved keys"
    OPT_AUTO   = "Generate automatically"
    OPT_MANUAL = "Enter manually"

    if prev_mode == "reuse" and saved_creds:
        choices = [OPT_REUSE, OPT_AUTO, OPT_MANUAL]
    elif prev_mode == "auto":
        choices = [OPT_AUTO, OPT_MANUAL]
        if saved_creds:
            choices.insert(0, OPT_REUSE)
    else:  # manual
        choices = [OPT_MANUAL, OPT_AUTO]
        if saved_creds:
            choices.insert(0, OPT_REUSE)

    choice = _select(f"{label} Credentials:", choices=choices)

    if choice == OPT_REUSE:
        return {"cloud_creds_mode": "reuse", **saved_creds}

    result = {"cloud_creds_mode": "auto" if choice == OPT_AUTO else "manual"}

    if choice == OPT_AUTO:
        result["email"] = _prompt_email(config)

        # Write email to credentials.env so the key manager can read it
        root     = _project_root()
        env_file = root / "credentials.env"
        if env_file.exists():
            from dotenv import set_key as _set_key
            _set_key(str(env_file), "TF_VAR_owner_email", result["email"])

        # Generate credentials immediately — user gets feedback right now
        print(f"\n  Generating {label} credentials...")
        subprocess.run(["uv", "run", "api-keys", "create", cloud], cwd=root)

        # Read the generated values back from credentials.env
        if env_file.exists():
            from dotenv import dotenv_values as _dv
            env_creds = _dv(env_file)
            if cloud == "aws":
                result["aws_access_key_id"]     = env_creds.get("TF_VAR_aws_bedrock_access_key")
                result["aws_secret_access_key"] = env_creds.get("TF_VAR_aws_bedrock_secret_key")
            elif cloud == "azure":
                result["azure_openai_endpoint"] = env_creds.get("TF_VAR_azure_openai_endpoint_raw")
                result["azure_openai_api_key"]  = env_creds.get("TF_VAR_azure_openai_api_key")
        return result

    if cloud == "aws":
        result["aws_access_key_id"]     = _text("AWS Access Key ID",     default=config.get("aws_access_key_id"))
        result["aws_secret_access_key"] = _text("AWS Secret Access Key", default=config.get("aws_secret_access_key"), secret=True)
    elif cloud == "azure":
        result["azure_openai_endpoint"] = _text("Azure OpenAI Endpoint", default=config.get("azure_openai_endpoint"))
        result["azure_openai_api_key"]  = _text("Azure OpenAI API Key",  default=config.get("azure_openai_api_key"), secret=True)
    return result


def _prompt_email(config: dict) -> str:
    print()
    print("  To tag your cloud resources correctly, we need")
    print("  your email address.")
    print()
    return _text("Email", default=config.get("email"))


# ── Phase 6: Zapier Token ─────────────────────────────────────────────────────
def prompt_zapier_token(config: dict) -> str:
    _section("Zapier Integration")
    print()
    print("  A Zapier API token is required. You must provide")
    print("  this — we can't generate it on your behalf.")
    print()
    zapier_guide_url = "https://github.com/confluentinc/quickstart-streaming-agents/blob/master/assets/pre-setup/Zapier-Setup.md"
    link = _smart_link(zapier_guide_url, "Setup Guide → Zapier Token")
    print(f"  Don't have one? See: {link}")
    print()

    # Check credentials.env first, fall back to saved config
    env_token  = _load_env_zapier_token()
    saved_token = env_token or config.get("zapier_token")

    OPT_REUSE = "Reuse my saved token"
    OPT_ENTER = "Enter token"

    if saved_token:
        prev_mode = config.get("zapier_mode", "reuse")
        choices   = [OPT_REUSE, OPT_ENTER] if prev_mode != "enter" else [OPT_ENTER, OPT_REUSE]
        choice    = _select("Zapier Token:", choices=choices)
        if choice == OPT_REUSE:
            config["zapier_mode"] = "reuse"
            return saved_token
        config["zapier_mode"] = "enter"

    token = _text("Zapier Token", secret=True)
    _write_env_key("TF_VAR_zapier_token", token)
    return token


# ── Phase 7: Review & Confirm ─────────────────────────────────────────────────
def show_review_and_confirm(config: dict) -> bool:
    _section("Deployment Summary")
    print()
    cloud  = (config.get("cloud_provider") or "not set").upper()
    labs   = _fmt_labs(config)
    cm     = config.get("confluent_api_key_mode", "")
    c_disp = "Auto-generate" if cm == "auto" else "Manual"
    cl     = "AWS Bedrock Keys" if config.get("cloud_provider") == "aws" else "Azure OpenAI Keys"
    cc     = _fmt_cloud_creds(config)
    zap    = _mask(config.get("zapier_token", ""))
    print(f"  Cloud Provider:        {cloud}")
    print(f"  Labs to Deploy:        {labs}")
    print(f"  Confluent API Keys:    {c_disp}")
    print(f"  {cl}:      {cc}")
    print(f"  Zapier Token:          {zap}")
    print()
    print("  ⚠  This will provision real cloud resources")
    print("     and may incur costs.")
    print()
    choice = _select("Proceed with deployment?", ["Yes, deploy", "No, cancel"])
    if choice == "Yes, deploy":
        return True
    print("\n  Deployment aborted.")
    return False


# ── Mode 1: Full Flow ─────────────────────────────────────────────────────────
def run_full_flow(config: dict) -> dict:
    if config:
        _saved_notice(config)

    config["cloud_provider"] = prompt_cloud_provider(config)
    save_config(config)

    config["labs"] = prompt_lab_selection(config)
    save_config(config)

    config.update(prompt_confluent_keys(config))
    save_config(config)

    config.update(prompt_cloud_creds(config, config["cloud_provider"]))
    save_config(config)

    config["zapier_token"] = prompt_zapier_token(config)
    save_config(config)

    if not show_review_and_confirm(config):
        sys.exit(0)
    return config


# ── Mode 2: Quick-Deploy ──────────────────────────────────────────────────────
def run_quick_deploy(config: dict) -> dict:
    _section("Saved Configuration Found")
    print()
    _show_summary(config)
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
        if not show_review_and_confirm(config):
            sys.exit(0)
        return config
    elif choice == OPT_EDIT:
        config = run_edit_menu(config)
        return run_quick_deploy(config)
    elif choice == OPT_FULL:
        return run_full_flow(config)
    else:  # Quit
        print("\n  Goodbye.")
        sys.exit(0)


# ── Mode 3: Edit ──────────────────────────────────────────────────────────────
def _edit_key(key: str, config: dict) -> dict:
    cloud = config.get("cloud_provider", "aws")
    if key == "cloud":
        config["cloud_provider"] = prompt_cloud_provider(config)
    elif key == "labs":
        config["labs"] = prompt_lab_selection(config)
    elif key == "confluent-keys":
        config.update(prompt_confluent_keys(config))
    elif key == "cloud-creds":
        config.update(prompt_cloud_creds(config, cloud))
    elif key == "zapier":
        config["zapier_token"] = prompt_zapier_token(config)
    elif key == "email":
        config["email"] = _prompt_email(config)
    save_config(config)
    return config


def run_edit_menu(config: dict) -> dict:
    while True:
        _section("Edit Configuration")
        print()

        # Build display values for each editable field
        cloud  = (config.get("cloud_provider") or "not set").upper()
        labs   = _fmt_labs(config)
        cm     = config.get("confluent_api_key_mode", "not set")
        c_disp = "auto-generate" if cm == "auto" else "reuse saved" if cm == "reuse" else "manual" if cm == "manual" else "not set"
        cl     = "AWS Bedrock" if config.get("cloud_provider") == "aws" else "Azure OpenAI"
        cc     = _fmt_cloud_creds(config)
        zap    = _mask(config.get("zapier_token", ""))
        email  = config.get("email") or "not set"

        FIELD_ITEMS = [
            ("cloud",          f"Cloud Provider       {cloud}"),
            ("labs",           f"Labs                 {labs}"),
            ("confluent-keys", f"Confluent API Keys   {c_disp}"),
            ("cloud-creds",    f"{cl} Keys       {cc}"),
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
            # Non-TTY fallback
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

        config = _edit_key(key, config)
        print()
        print(f"  ✓ {EDIT_KEYS[key]} updated.")
        print()

        next_action = _select(
            "What next?",
            choices=["Edit another setting", "Deploy now", "Quit"],
        )
        if next_action == "Deploy now":
            if not show_review_and_confirm(config):
                sys.exit(0)
            return config
        elif next_action == "Quit":
            sys.exit(0)
        # else: Edit another setting → loop

    return config


# ── Deployment execution ──────────────────────────────────────────────────────
def _build_creds(config: dict) -> dict:
    """Build a flat {key: value} dict for write_tfvars_for_deployment."""
    c = {}
    cloud = config.get("cloud_provider", "aws")

    if config.get("confluent_api_key"):
        c["confluent_cloud_api_key"] = config["confluent_api_key"]
    if config.get("confluent_api_secret"):
        c["confluent_cloud_api_secret"] = config["confluent_api_secret"]
    if config.get("email"):
        c["owner_email"] = config["email"]

    if cloud == "aws":
        if config.get("aws_access_key_id"):
            c["aws_bedrock_access_key"] = config["aws_access_key_id"]
        if config.get("aws_secret_access_key"):
            c["aws_bedrock_secret_key"] = config["aws_secret_access_key"]
    elif cloud == "azure":
        if config.get("azure_openai_endpoint"):
            c["azure_openai_endpoint"] = config["azure_openai_endpoint"]
        if config.get("azure_openai_api_key"):
            c["azure_openai_api_key"] = config["azure_openai_api_key"]

    if config.get("zapier_token"):
        c["zapier_token"] = config["zapier_token"]
    return c


def run_deployment(config: dict) -> None:
    from scripts.common.credentials import generate_confluent_api_keys
    from scripts.common.terraform_runner import run_terraform
    from scripts.common.tfvars import write_tfvars_for_deployment

    root   = _project_root()
    cloud  = config.get("cloud_provider", "aws")
    region = "us-east-1" if cloud == "aws" else "eastus2"

    # Auto-generate Confluent keys
    if config.get("confluent_api_key_mode") == "auto":
        print("\n  Generating Confluent Cloud API keys...")
        api_key, api_secret = generate_confluent_api_keys()
        if not api_key or not api_secret:
            print("  ✗ Failed to generate Confluent API keys. Aborting.")
            sys.exit(1)
        config["confluent_api_key"]    = api_key
        config["confluent_api_secret"] = api_secret
        save_config(config)

    # Build creds dict and load TF_VAR_* into environment
    creds = _build_creds(config)
    for k, v in creds.items():
        if v:
            os.environ[f"TF_VAR_{k}"] = v

    # Determine terraform environments
    lab_to_tf = {lid: tf for lid, _, tf in LABS}
    selected  = config.get("labs") or []
    envs      = ["core"] + [lab_to_tf[lab] for lab in selected if lab in lab_to_tf]

    # Write terraform.tfvars files
    write_tfvars_for_deployment(root, cloud, region, creds, envs)

    print("\n=== Starting Deployment ===")
    for env in envs:
        env_path = root / "terraform" / env
        if not env_path.exists():
            print(f"  Warning: {env_path} does not exist, skipping.")
            continue
        if not run_terraform(env_path):
            print(f"\n  ✗ Deployment failed at {env}. Stopping.")
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
        help="Force full setup flow even if a saved config exists",
    )
    args = parser.parse_args()

    _banner()
    config = load_config()

    # Edit mode (skips pre-flight)
    if args.edit is not None:
        if not config:
            print("  No saved configuration found. Run the full setup first.")
            sys.exit(1)
        if args.edit == "__menu__":
            run_edit_menu(config)
        elif args.edit in EDIT_KEYS:
            _edit_key(args.edit, config)
            print(f"\n  ✓ {EDIT_KEYS[args.edit]} updated.")
        else:
            print(f"  Unknown key: {args.edit!r}")
            print(f"  Valid keys: {', '.join(EDIT_KEYS)}")
            sys.exit(1)
        sys.exit(0)

    # Pre-flight
    if not _preflight():
        print()
        sys.exit(1)

    # Mode selection
    if not args.full and _config_complete(config):
        config = run_quick_deploy(config)
    else:
        config = run_full_flow(config)

    run_deployment(config)


if __name__ == "__main__":
    main()
