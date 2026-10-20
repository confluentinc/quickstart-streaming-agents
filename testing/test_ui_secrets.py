from unittest.mock import patch

from scripts.common import ui


def test_is_secret_name_hides_secrets_not_key_ids():
    for name in ("TF_VAR_confluent_cloud_api_secret", "CONFLUENT_PASSWORD", "TF_VAR_mcp_token", "F1_RTCE_API_SECRET"):
        assert ui.is_secret_name(name)
    for name in ("TF_VAR_confluent_cloud_api_key", "TF_VAR_aws_bedrock_access_key", "CONFLUENT_EMAIL"):
        assert not ui.is_secret_name(name)


def test_mask_secret_keeps_edges_and_length():
    value = "A" * 4 + "x" * 32 + "Z" * 4
    masked = ui.mask_secret(value)
    assert masked == "AAAA" + "*" * 32 + "ZZZZ"
    assert len(masked) == len(value)


def test_mask_secret_fully_hides_short_values():
    assert ui.mask_secret("hunter2") == "*" * 7
    assert ui.mask_secret("") == ""


def test_prompt_with_default_secret_never_shows_default(capsys):
    seen = []
    with patch.object(ui, "prompt_secret", side_effect=lambda p: seen.append(p) or ""):
        out = ui.prompt_with_default("Secret", "s3cr3t-value-0123456789abcdef", secret=True)
    assert out == "s3cr3t-value-0123456789abcdef"
    assert "s3cr3t-value-0123456789abcdef" not in seen[0]
    assert seen[0].startswith("Secret [") and "s3cr" in seen[0] and "cdef" in seen[0]


def test_prompt_secret_falls_back_to_getpass_without_tty():
    with patch("sys.stdin.isatty", return_value=False), patch("getpass.getpass", return_value="pw") as gp:
        assert ui.prompt_secret("Password: ") == "pw"
    gp.assert_called_once_with("Password: ")
