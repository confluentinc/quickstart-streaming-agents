"""Unit tests for LLM provider resolution (CSP Hosted default, --bedrock / --azure-openai opt-in)."""

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


def _write_core_state(root, names, exist_ok=False):
    core = root / "terraform" / "core"
    core.mkdir(parents=True, exist_ok=exist_ok)
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


def test_saved_azure_defaults_to_confluent():
    assert saved_llm_provider({}, "azure") == "confluent"


def test_saved_azure_reads_azureopenai():
    assert (
        saved_llm_provider({LLM_PROVIDER_KEY: "azureopenai"}, "azure") == "azureopenai"
    )


def test_saved_export_for_wrong_cloud_exits(monkeypatch):
    monkeypatch.setenv(LLM_PROVIDER_KEY, "bedrock")
    with pytest.raises(SystemExit):
        saved_llm_provider({}, "azure")
    monkeypatch.setenv(LLM_PROVIDER_KEY, "azureopenai")
    with pytest.raises(SystemExit):
        saved_llm_provider({}, "aws")


def test_saved_credentials_env_for_other_cloud_falls_back_to_default():
    # Left over from an earlier AWS --bedrock deploy; harmless on Azure
    assert saved_llm_provider({LLM_PROVIDER_KEY: "bedrock"}, "azure") == "confluent"


# ---------------------------------------------------------------------------
# deployed_llm_provider
# ---------------------------------------------------------------------------


def test_deployed_none_without_state(tmp_path):
    assert deployed_llm_provider(tmp_path) is None


def test_deployed_none_when_core_runs_on_other_cloud(tmp_path):
    _write_core_state(tmp_path, ["llm_textgen_model_azure", "azureopenai_connection"])
    assert deployed_llm_provider(tmp_path, "aws") is None
    _write_core_state(tmp_path, ["llm_textgen_model_aws"], exist_ok=True)
    assert deployed_llm_provider(tmp_path, "azure") is None


def test_deployed_azureopenai_when_connection_live(tmp_path):
    _write_core_state(tmp_path, ["llm_textgen_model_azure", "azureopenai_connection"])
    assert deployed_llm_provider(tmp_path) == "azureopenai"
    assert deployed_llm_provider(tmp_path, "azure") == "azureopenai"


def test_deployed_azure_confluent_without_connection(tmp_path):
    _write_core_state(tmp_path, ["llm_textgen_model_azure"])
    assert deployed_llm_provider(tmp_path, "azure") == "confluent"


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


def test_for_existing_azure_openai_deploy_keeps_azureopenai(tmp_path, capsys):
    _write_core_state(tmp_path, ["llm_textgen_model_azure", "azureopenai_connection"])
    assert llm_provider_for(tmp_path, {}, "azure") == "azureopenai"
    assert "keeping 'azureopenai'" in capsys.readouterr().out


def test_for_azure_fresh_deploy_defaults_to_confluent(tmp_path):
    assert llm_provider_for(tmp_path, {}, "azure") == "confluent"


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


def _azure_core_tfvars(llm_provider):
    return generate_core_tfvars_content(
        cloud="azure",
        region="eastus2",
        api_key="k",
        api_secret="s",
        cloud_provider="azure",
        azure_openai_endpoint="https://example.openai.azure.com",
        azure_openai_api_key="azurekeyexample",
        llm_provider=llm_provider,
    )


def test_core_tfvars_azure_confluent_omits_azure_openai_creds():
    content = _azure_core_tfvars("confluent")
    assert 'llm_provider = "confluent"' in content
    assert "azurekeyexample" not in content
    assert "example.openai.azure.com" not in content


def test_core_tfvars_azure_openai_writes_creds():
    content = _azure_core_tfvars("azureopenai")
    assert 'llm_provider = "azureopenai"' in content
    assert 'azure_openai_api_key = "azurekeyexample"' in content


def test_core_tfvars_confluent_omits_bedrock_keys():
    content = _core_tfvars("confluent")
    assert 'llm_provider = "confluent"' in content
    assert "AKIAEXAMPLE" not in content


def test_core_tfvars_bedrock_writes_keys():
    content = _core_tfvars("bedrock")
    assert 'llm_provider = "bedrock"' in content
    assert "AKIAEXAMPLE" in content
