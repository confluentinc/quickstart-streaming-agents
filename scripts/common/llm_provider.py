"""
Which provider backs the LLM models (`llm_provider` in terraform/core).

"confluent" is CSP Hosted Flink Model Inference: Confluent runs the models, so
there is no connection and no LLM key at all — the default on both clouds.
`uv run deploy --bedrock` (AWS) or `uv run deploy --azure-openai` (Azure) opts
into the flow that uses your own keys instead.

The choice is saved in credentials.env as TF_VAR_llm_provider.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional

LLM_PROVIDER_KEY = "TF_VAR_llm_provider"
LLM_PROVIDERS = {
    "confluent": "CSP Hosted Flink Model Inference (Confluent-hosted, no LLM keys)",
    "bedrock": "AWS Bedrock (your own AWS access keys)",
    "azureopenai": "Azure OpenAI (your own endpoint and API key)",
}
# Providers each cloud supports (terraform/core rejects any other pairing).
CLOUD_LLM_PROVIDERS = {
    "aws": ("confluent", "bedrock"),
    "azure": ("confluent", "azureopenai"),
}
DEFAULT_LLM_PROVIDER = "confluent"


def saved_llm_provider(creds: Dict[str, str], cloud: str = "aws") -> str:
    """Exported TF_VAR_llm_provider, then credentials.env, then the default.

    An export for the wrong cloud (e.g. --bedrock on Azure) is an error. A
    credentials.env value for the other cloud is left over from an earlier
    deploy there, so it falls back to the default.
    """
    exported = (os.environ.get(LLM_PROVIDER_KEY) or "").strip()
    value = (
        exported or (creds.get(LLM_PROVIDER_KEY) or "").strip() or DEFAULT_LLM_PROVIDER
    )
    if value not in LLM_PROVIDERS:
        print(
            f"Error: {LLM_PROVIDER_KEY}={value!r} — expected one of: {', '.join(LLM_PROVIDERS)}"
        )
        sys.exit(1)
    allowed = CLOUD_LLM_PROVIDERS.get(cloud, tuple(LLM_PROVIDERS))
    if value not in allowed:
        if exported:
            print(
                f"Error: LLM provider {value!r} isn't available on {cloud} — use one of: {', '.join(allowed)}"
            )
            sys.exit(1)
        return DEFAULT_LLM_PROVIDER
    return value


def deployed_llm_provider(root: Path, cloud: Optional[str] = None) -> Optional[str]:
    """What the live `llm_textgen_model` is backed by, read from core's Terraform state.

    Core creates `bedrock_connection` (AWS) / `azureopenai_connection` (Azure)
    only when you bring your own keys. None when core isn't deployed (on
    `cloud`, if given) or the state can't be read.
    """
    state_path = root / "terraform" / "core" / "terraform.tfstate"
    try:
        resources = json.loads(state_path.read_text()).get("resources", [])
    except (OSError, ValueError):
        return None
    live = {r.get("name") for r in resources if r.get("instances")}
    if "llm_textgen_model_aws" in live and cloud in (None, "aws"):
        return "bedrock" if "bedrock_connection" in live else "confluent"
    if "llm_textgen_model_azure" in live and cloud in (None, "azure"):
        return "azureopenai" if "azureopenai_connection" in live else "confluent"
    return None


def llm_provider_for(root: Path, creds: Dict[str, str], cloud: str = "aws") -> str:
    """The provider to deploy: exported, else what core runs now, else credentials.env.

    Switching an applied core re-runs CREATE MODEL IF NOT EXISTS against an
    existing name — a silent no-op that would leave the old model pointing at a
    deleted connection. So the deployed state wins over credentials.env; an
    explicit export (or --bedrock / --azure-openai) still wins over both.
    """
    deployed = deployed_llm_provider(root, cloud)
    saved = saved_llm_provider(creds, cloud)
    if (os.environ.get(LLM_PROVIDER_KEY) or "").strip():
        if deployed and deployed != saved:
            print(
                f"  ⚠ LLM provider: switching the deployed core from {deployed!r} to {saved!r}."
            )
            print(
                "    The existing models keep their old definition — run `uv run destroy` first."
            )
        return saved
    if deployed and deployed != saved:
        print(f"  LLM provider: keeping {deployed!r}, which the deployed core runs now")
        print(
            f"    (credentials.env says {saved!r}; run `uv run destroy` first to switch)."
        )
    return deployed or saved
