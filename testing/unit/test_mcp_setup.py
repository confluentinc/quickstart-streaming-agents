"""Unit tests for scripts/mcp_setup.py."""

try:
    import tomllib  # stdlib 3.11+
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]

from scripts import mcp_setup


def _load_toml(path):
    with path.open("rb") as f:
        return tomllib.load(f)


def test_build_env_vars_normalizes_bootstrap_and_uses_flink_catalog():
    env_vars = mcp_setup._build_env_vars(
        {
            "confluent_kafka_cluster_bootstrap_endpoint": "SASL_SSL://broker:9092",
            "confluent_environment_display_name": "catalog",
        }
    )

    assert env_vars["BOOTSTRAP_SERVERS"] == "broker:9092"
    assert env_vars["FLINK_CATALOG_NAME"] == "catalog"
    assert "FLINK_ENV_NAME" not in env_vars


def test_register_with_codex_updates_existing_project_local_config(
    tmp_path, monkeypatch
):
    home = tmp_path / "home"
    project_root = tmp_path / "repo"
    project_config = project_root / ".codex" / "config.toml"
    project_config.parent.mkdir(parents=True)
    project_config.write_text(
        """
model = "gpt-5"

[mcp_servers.confluent-cloud-mcp-server]
command = "old"
args = ["old-package"]

[mcp_servers.confluent-cloud-mcp-server.env]
BOOTSTRAP_SERVERS = "SASL_SSL://old-broker:9092"
FLINK_ENV_NAME = "old-catalog"
""".lstrip()
    )

    monkeypatch.setattr(mcp_setup.Path, "home", staticmethod(lambda: home))

    env_vars = {
        "BOOTSTRAP_SERVERS": "new-broker:9092",
        "FLINK_CATALOG_NAME": "new-catalog",
        "KAFKA_API_KEY": "key",
    }
    mcp_setup._register_with_codex(env_vars, "npx", project_root)

    home_config = _load_toml(home / ".codex" / "config.toml")
    local_config = _load_toml(project_config)

    for config in (home_config, local_config):
        server = config["mcp_servers"]["confluent-cloud-mcp-server"]
        assert server["command"] == "npx"
        assert server["args"] == ["-y", "@confluentinc/mcp-confluent"]
        assert server["env"]["BOOTSTRAP_SERVERS"] == "new-broker:9092"
        assert server["env"]["FLINK_CATALOG_NAME"] == "new-catalog"
        assert "FLINK_ENV_NAME" not in server["env"]

    assert local_config["model"] == "gpt-5"


def test_register_with_codex_does_not_create_project_local_config(
    tmp_path, monkeypatch
):
    home = tmp_path / "home"
    project_root = tmp_path / "repo"
    project_root.mkdir()
    monkeypatch.setattr(mcp_setup.Path, "home", staticmethod(lambda: home))

    mcp_setup._register_with_codex(
        {"BOOTSTRAP_SERVERS": "broker:9092"}, "npx", project_root
    )

    assert (home / ".codex" / "config.toml").exists()
    assert not (project_root / ".codex" / "config.toml").exists()
