"""
Which provider backs the AWS LLM models (`llm_provider` in terraform/core).

"confluent" is CSP Hosted Flink Model Inference: Confluent runs the models, so
there is no Bedrock connection and no AWS key at all — the default.
`uv run deploy --bedrock` opts into the Bedrock flow (your own AWS keys).
Azure always uses its Azure OpenAI connections and ignores this setting.

The choice is saved in credentials.env as TF_VAR_llm_provider.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional

LLM_PROVIDER_KEY = "TF_VAR_llm_provider"
LLM_PROVIDERS = {
    "confluent": "CSP Hosted Flink Model Inference (Confluent-hosted, no AWS keys)",
    "bedrock": "AWS Bedrock (your own AWS access keys)",
}
DEFAULT_LLM_PROVIDER = "confluent"


def saved_llm_provider(creds: Dict[str, str]) -> str:
    """Exported TF_VAR_llm_provider, then credentials.env, then the default."""
    value = (
        os.environ.get(LLM_PROVIDER_KEY)
        or creds.get(LLM_PROVIDER_KEY)
        or DEFAULT_LLM_PROVIDER
    ).strip()
    if value not in LLM_PROVIDERS:
        print(
            f"Error: {LLM_PROVIDER_KEY}={value!r} — expected one of: {', '.join(LLM_PROVIDERS)}"
        )
        sys.exit(1)
    return value


def deployed_llm_provider(root: Path) -> Optional[str]:
    """What the live AWS `llm_textgen_model` is backed by, read from core's Terraform state.

    Core creates `bedrock_connection` only for Bedrock. None when core isn't
    deployed on AWS or the state can't be read.
    """
    state_path = root / "terraform" / "core" / "terraform.tfstate"
    try:
        resources = json.loads(state_path.read_text()).get("resources", [])
    except (OSError, ValueError):
        return None
    live = {r.get("name") for r in resources if r.get("instances")}
    if "llm_textgen_model_aws" not in live:
        return None
    return "bedrock" if "bedrock_connection" in live else "confluent"


def llm_provider_for(root: Path, creds: Dict[str, str]) -> str:
    """The provider to deploy: exported, else what core runs now, else credentials.env.

    Switching an applied core re-runs CREATE MODEL IF NOT EXISTS against an
    existing name — a silent no-op that would leave the old model pointing at a
    deleted connection. So the deployed state wins over credentials.env; an
    explicit export (or --bedrock) still wins over both.
    """
    deployed = deployed_llm_provider(root)
    saved = saved_llm_provider(creds)
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
