"""Unit tests for scripts/mcp_setup.py — no live infra required."""

from pathlib import Path

import pytest

from scripts.mcp_setup import MCP_ENV_PATH, _TF_TO_MCP, write_mcp_env


SAMPLE_OUTPUTS = {
    "confluent_kafka_cluster_bootstrap_endpoint": "pkc-abc123.us-east-1.aws.confluent.cloud:9092",
    "app_manager_kafka_api_key": "KAFKAKEY123",
    "app_manager_kafka_api_secret": "kafkasecret456",
    "confluent_kafka_cluster_rest_endpoint": "https://pkc-abc123.us-east-1.aws.confluent.cloud",
    "confluent_kafka_cluster_id": "lkc-abc123",
    "confluent_environment_id": "env-abc123",
    "app_manager_flink_api_key": "FLINKKEY123",
    "app_manager_flink_api_secret": "flinksecret456",
    "confluent_flink_rest_endpoint": "https://flink.us-east-1.aws.confluent.cloud",
    "confluent_flink_compute_pool_id": "lfcp-abc123",
    "confluent_organization_id": "org-abc123",
    "confluent_environment_display_name": "streaming-agents-env",
    "confluent_kafka_cluster_display_name": "streaming-agents-cluster",
    "app_manager_schema_registry_api_key": "SRKEY123",
    "app_manager_schema_registry_api_secret": "srsecret456",
    "confluent_schema_registry_rest_endpoint": "https://psrc-abc123.us-east-1.aws.confluent.cloud",
    "confluent_cloud_api_key": "CLOUDKEY123",
    "confluent_cloud_api_secret": "cloudsecret456",
}


def test_write_mcp_env_creates_file(tmp_path):
    env_path = write_mcp_env(SAMPLE_OUTPUTS, tmp_path)
    assert env_path.exists()
    assert env_path == tmp_path / MCP_ENV_PATH


def test_write_mcp_env_all_vars_present(tmp_path):
    env_path = write_mcp_env(SAMPLE_OUTPUTS, tmp_path)
    content = env_path.read_text()
    expected_vars = [var for vars in _TF_TO_MCP.values() for var in vars]
    for var in expected_vars:
        assert f"{var}=" in content, f"Missing {var} in confluent-mcp.env"


def test_write_mcp_env_environment_id_maps_to_both_kafka_and_flink(tmp_path):
    env_path = write_mcp_env(SAMPLE_OUTPUTS, tmp_path)
    content = env_path.read_text()
    assert 'KAFKA_ENV_ID="env-abc123"' in content
    assert 'FLINK_ENV_ID="env-abc123"' in content


def test_write_mcp_env_values_quoted(tmp_path):
    env_path = write_mcp_env(SAMPLE_OUTPUTS, tmp_path)
    for line in env_path.read_text().splitlines():
        key, _, rest = line.partition("=")
        assert rest.startswith('"') and rest.endswith('"'), (
            f"Value not quoted on line: {line}"
        )


def test_write_mcp_env_missing_outputs_produce_empty_string(tmp_path):
    env_path = write_mcp_env({}, tmp_path)
    content = env_path.read_text()
    assert 'BOOTSTRAP_SERVERS=""' in content


def test_write_mcp_env_overwrites_existing(tmp_path):
    write_mcp_env(SAMPLE_OUTPUTS, tmp_path)
    updated = {**SAMPLE_OUTPUTS, "app_manager_kafka_api_key": "NEWKEY999"}
    env_path = write_mcp_env(updated, tmp_path)
    assert 'KAFKA_API_KEY="NEWKEY999"' in env_path.read_text()
