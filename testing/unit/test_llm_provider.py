"""Unit tests for LLM provider resolution (CSP Hosted default, --bedrock opt-in)."""

import json

import pytest

from scripts.common.llm_provider import (
    LLM_PROVIDER_KEY,
    deployed_llm_provider,
    llm_provider_for,
    saved_llm_provider,
)
from scripts.common.tfvars import generate_core_tfvars_content


@pytest.fixture(autouse=True)
def _no_exported_provider(monkeypatch):
    monkeypatch.delenv(LLM_PROVIDER_KEY, raising=False)


def _write_core_state(root, names):
    core = root / "terraform" / "core"
    core.mkdir(parents=True)
    resources = [{"name": n, "instances": [{}]} for n in names]
    (core / "terraform.tfstate").write_text(json.dumps({"resources": resources}))


# ---------------------------------------------------------------------------
# saved_llm_provider
# ---------------------------------------------------------------------------


def test_saved_defaults_to_confluent():
    assert saved_llm_provider({}) == "confluent"


def test_saved_reads_credentials_env():
    assert saved_llm_provider({LLM_PROVIDER_KEY: "bedrock"}) == "bedrock"


def test_saved_export_beats_credentials_env(monkeypatch):
    monkeypatch.setenv(LLM_PROVIDER_KEY, "confluent")
    assert saved_llm_provider({LLM_PROVIDER_KEY: "bedrock"}) == "confluent"


def test_saved_rejects_unknown_value():
    with pytest.raises(SystemExit):
        saved_llm_provider({LLM_PROVIDER_KEY: "openai"})


# ---------------------------------------------------------------------------
# deployed_llm_provider
# ---------------------------------------------------------------------------


def test_deployed_none_without_state(tmp_path):
    assert deployed_llm_provider(tmp_path) is None


def test_deployed_none_when_aws_model_not_live(tmp_path):
    _write_core_state(tmp_path, ["llm_textgen_model_azure", "azureopenai_connection"])
    assert deployed_llm_provider(tmp_path) is None


def test_deployed_bedrock_when_connection_live(tmp_path):
    _write_core_state(tmp_path, ["llm_textgen_model_aws", "bedrock_connection"])
    assert deployed_llm_provider(tmp_path) == "bedrock"


def test_deployed_confluent_without_connection(tmp_path):
    _write_core_state(tmp_path, ["llm_textgen_model_aws"])
    assert deployed_llm_provider(tmp_path) == "confluent"


# ---------------------------------------------------------------------------
# llm_provider_for
# ---------------------------------------------------------------------------


def test_for_fresh_deploy_uses_saved(tmp_path):
    assert llm_provider_for(tmp_path, {}) == "confluent"


def test_for_deployed_state_beats_credentials_env(tmp_path, capsys):
    _write_core_state(tmp_path, ["llm_textgen_model_aws", "bedrock_connection"])
    assert llm_provider_for(tmp_path, {LLM_PROVIDER_KEY: "confluent"}) == "bedrock"
    assert "keeping 'bedrock'" in capsys.readouterr().out


def test_for_export_beats_deployed_state_and_warns(tmp_path, monkeypatch, capsys):
    _write_core_state(tmp_path, ["llm_textgen_model_aws"])
    monkeypatch.setenv(LLM_PROVIDER_KEY, "bedrock")
    assert llm_provider_for(tmp_path, {}) == "bedrock"
    assert "uv run destroy" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# core tfvars
# ---------------------------------------------------------------------------


def _core_tfvars(llm_provider):
    return generate_core_tfvars_content(
        cloud="aws",
        region="us-east-1",
        api_key="k",
        api_secret="s",
        cloud_provider="aws",
        aws_bedrock_access_key="AKIAEXAMPLE",
        aws_bedrock_secret_key="secretexample",
        llm_provider=llm_provider,
    )


def test_core_tfvars_confluent_omits_bedrock_keys():
    content = _core_tfvars("confluent")
    assert 'llm_provider = "confluent"' in content
    assert "AKIAEXAMPLE" not in content


def test_core_tfvars_bedrock_writes_keys():
    content = _core_tfvars("bedrock")
    assert 'llm_provider = "bedrock"' in content
    assert "AKIAEXAMPLE" in content
