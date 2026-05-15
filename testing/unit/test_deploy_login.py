"""Unit tests for deploy.py login behavior — Step 0 interactive flow and mode-specific paths."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

import deploy


# Sentinel exception used to halt deploy.main() right after the login block,
# preventing Terraform and other I/O from running in tests.
class _StopAfterLogin(Exception):
    pass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VALID_ENV_CREDS = {
    "TF_VAR_confluent_cloud_api_key": "key123",
    "TF_VAR_confluent_cloud_api_secret": "secret123",
    "TF_VAR_cloud_provider": "aws",
    "TF_VAR_cloud_region": "us-east-1",
    "TF_VAR_aws_bedrock_access_key": "awskey",
    "TF_VAR_aws_bedrock_secret_key": "awssecret",
    "TF_VAR_mcp_token": "tok123",
    "CONFLUENT_EMAIL": "user@example.com",
    "CONFLUENT_PASSWORD": "password123",
}

_VALID_JSON_CREDS = {
    "cloud": "aws",
    "region": "us-east-1",
    "confluent_cloud_api_key": "key123",
    "confluent_cloud_api_secret": "secret123",
    "aws_bedrock_access_key": "awskey",
    "aws_bedrock_secret_key": "awssecret",
    "mcp_token": "tok123",
    "confluent_cloud_email": "user@example.com",
    "confluent_cloud_password": "password123",
}


def _run_main(argv):
    """Run deploy.main() with the given sys.argv (excluding the program name)."""
    with patch.object(sys, "argv", ["deploy"] + argv):
        deploy.main()


# ---------------------------------------------------------------------------
# Interactive mode — Step 0 login flow
# ---------------------------------------------------------------------------


class TestDeployInteractiveStep0:
    """Tests for the interactive credential prompt in deploy.py Step 0."""

    def _base_patches(self, env_creds, tmp_path):
        """Return a dict of attr-name → mock for patch.multiple("deploy", ...)."""
        creds_file = tmp_path / "credentials.env"
        return {
            "get_project_root": MagicMock(return_value=tmp_path),
            "load_or_create_credentials_file": MagicMock(
                return_value=(creds_file, dict(env_creds))
            ),
            "_save_env_safe": MagicMock(),
            # Raise sentinel after login block completes to stop the rest of deploy
            "ensure_confluent_login": MagicMock(side_effect=_StopAfterLogin()),
        }

    def test_skips_prompt_when_creds_already_saved(self, tmp_path):
        """When CONFLUENT_EMAIL + PASSWORD are already in credentials.env, no prompt appears."""
        saved_creds = {
            "CONFLUENT_EMAIL": "saved@example.com",
            "CONFLUENT_PASSWORD": "saved_pass",
        }
        patches = self._base_patches(saved_creds, tmp_path)

        with (
            patch.multiple("deploy", **patches),
            patch("builtins.input", MagicMock()) as mock_input,
            pytest.raises(_StopAfterLogin),
        ):
            _run_main([])

        mock_input.assert_not_called()

    def test_ensure_confluent_login_called_with_saved_creds(self, tmp_path):
        """ensure_confluent_login receives the full env_creds dict."""
        saved_creds = {
            "CONFLUENT_EMAIL": "saved@example.com",
            "CONFLUENT_PASSWORD": "saved_pass",
        }
        patches = self._base_patches(saved_creds, tmp_path)
        mock_ensure = patches["ensure_confluent_login"]

        with (
            patch.multiple("deploy", **patches),
            patch("builtins.input", MagicMock()),
            pytest.raises(_StopAfterLogin),
        ):
            _run_main([])

        mock_ensure.assert_called_once()
        call_creds = mock_ensure.call_args[0][0]
        assert call_creds.get("CONFLUENT_EMAIL") == "saved@example.com"

    def test_prompts_when_no_saved_creds(self, tmp_path):
        """When credentials are absent, an email prompt appears."""
        patches = self._base_patches({}, tmp_path)

        with (
            patch.multiple("deploy", **patches),
            patch("builtins.input", return_value="") as mock_input,
            pytest.raises(_StopAfterLogin),
        ):
            _run_main([])

        mock_input.assert_called()
        first_call_arg = mock_input.call_args_list[0][0][0]
        assert "Email" in first_call_arg

    def test_valid_email_password_saves_and_stops_retry(self, tmp_path):
        """On first successful login attempt, credentials are saved and loop exits."""
        patches = self._base_patches({}, tmp_path)
        mock_save = patches["_save_env_safe"]

        with (
            patch.multiple("deploy", **patches),
            patch("builtins.input", return_value="user@example.com"),
            patch("deploy.getpass") as mock_gp,
            patch("deploy._attempt_login_quiet", return_value=True),
            pytest.raises(_StopAfterLogin),
        ):
            mock_gp.getpass.return_value = "secret"
            _run_main([])

        assert any(
            c
            == call(tmp_path / "credentials.env", "CONFLUENT_EMAIL", "user@example.com")
            for c in mock_save.call_args_list
        )
        assert any(
            c == call(tmp_path / "credentials.env", "CONFLUENT_PASSWORD", "secret")
            for c in mock_save.call_args_list
        )

    def test_skip_on_empty_email_does_not_save(self, tmp_path):
        """Pressing Enter at the email prompt skips saving and calls ensure_confluent_login."""
        patches = self._base_patches({}, tmp_path)
        mock_save = patches["_save_env_safe"]

        with (
            patch.multiple("deploy", **patches),
            patch("builtins.input", return_value=""),
            pytest.raises(_StopAfterLogin),
        ):
            _run_main([])

        mock_save.assert_not_called()
        patches["ensure_confluent_login"].assert_called_once()

    def test_retries_on_bad_password(self, tmp_path):
        """Failed login increments attempt count; success on 3rd attempt saves creds."""
        patches = self._base_patches({}, tmp_path)
        mock_save = patches["_save_env_safe"]
        attempt_results = [False, False, True]

        with (
            patch.multiple("deploy", **patches),
            patch("builtins.input", return_value="user@example.com"),
            patch("deploy.getpass") as mock_gp,
            patch("deploy._attempt_login_quiet", side_effect=attempt_results),
            pytest.raises(_StopAfterLogin),
        ):
            mock_gp.getpass.return_value = "secret"
            _run_main([])

        # Saved only on the successful 3rd attempt
        assert mock_save.call_count == 2  # CONFLUENT_EMAIL + CONFLUENT_PASSWORD

    def test_exhausts_retries_without_saving(self, tmp_path):
        """Three failed login attempts skip saving and still call ensure_confluent_login."""
        patches = self._base_patches({}, tmp_path)
        mock_save = patches["_save_env_safe"]

        with (
            patch.multiple("deploy", **patches),
            patch("builtins.input", return_value="user@example.com"),
            patch("deploy.getpass") as mock_gp,
            patch("deploy._attempt_login_quiet", return_value=False),
            pytest.raises(_StopAfterLogin),
        ):
            mock_gp.getpass.return_value = "secret"
            _run_main([])

        mock_save.assert_not_called()
        patches["ensure_confluent_login"].assert_called_once()

    def test_exhausts_retries_prints_sso_hint(self, tmp_path, capsys):
        """After all retries fail, the SSO hint is printed."""
        patches = self._base_patches({}, tmp_path)

        with (
            patch.multiple("deploy", **patches),
            patch("builtins.input", return_value="user@example.com"),
            patch("deploy.getpass") as mock_gp,
            patch("deploy._attempt_login_quiet", return_value=False),
            pytest.raises(_StopAfterLogin),
        ):
            mock_gp.getpass.return_value = "secret"
            _run_main([])

        out = capsys.readouterr().out
        assert "--sso" in out

    def test_ensure_login_propagates_system_exit(self, tmp_path):
        """If ensure_confluent_login exits (not logged in), SystemExit propagates."""
        saved_creds = {
            "CONFLUENT_EMAIL": "user@example.com",
            "CONFLUENT_PASSWORD": "secret",
        }
        patches = self._base_patches(saved_creds, tmp_path)
        # Override sentinel with a real SystemExit
        patches["ensure_confluent_login"] = MagicMock(side_effect=SystemExit(1))

        with (
            patch.multiple("deploy", **patches),
            patch("builtins.input", MagicMock()),
            pytest.raises(SystemExit) as exc_info,
        ):
            _run_main([])

        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# --automated mode
# ---------------------------------------------------------------------------


class TestDeployAutomatedLogin:
    """Tests for ensure_confluent_login behavior in --automated mode."""

    def _make_creds_file(self, tmp_path, extra=None):
        creds = dict(_VALID_ENV_CREDS)
        if extra:
            creds.update(extra)
        content = "\n".join(f"{k}={v}" for k, v in creds.items())
        f = tmp_path / "credentials.env"
        f.write_text(content)
        return f

    def test_calls_ensure_login_with_loaded_creds(self, tmp_path):
        """ensure_confluent_login is called with the creds dict from credentials.env."""
        self._make_creds_file(tmp_path)

        mock_ensure = MagicMock(side_effect=_StopAfterLogin())
        with (
            patch("deploy.get_project_root", return_value=tmp_path),
            patch("deploy.ensure_confluent_login", mock_ensure),
            patch("deploy.write_tfvars_for_deployment"),
            pytest.raises(_StopAfterLogin),
        ):
            _run_main(["--automated"])

        mock_ensure.assert_called_once()
        call_creds = mock_ensure.call_args[0][0]
        assert call_creds.get("CONFLUENT_EMAIL") == "user@example.com"
        assert call_creds.get("TF_VAR_cloud_provider") == "aws"

    def test_exits_if_credentials_env_missing(self, tmp_path):
        """--automated mode exits with code 1 if credentials.env does not exist."""
        with (
            patch("deploy.get_project_root", return_value=tmp_path),
            pytest.raises(SystemExit) as exc_info,
        ):
            _run_main(["--automated"])

        assert exc_info.value.code == 1

    def test_exits_if_ensure_login_fails(self, tmp_path):
        """SystemExit from ensure_confluent_login propagates out of automated mode."""
        self._make_creds_file(tmp_path)

        with (
            patch("deploy.get_project_root", return_value=tmp_path),
            patch("deploy.ensure_confluent_login", side_effect=SystemExit(1)),
            pytest.raises(SystemExit) as exc_info,
        ):
            _run_main(["--automated"])

        assert exc_info.value.code == 1

    def test_does_not_prompt_user(self, tmp_path):
        """--automated mode never calls input() — it's non-interactive."""
        self._make_creds_file(tmp_path)

        with (
            patch("deploy.get_project_root", return_value=tmp_path),
            patch("deploy.ensure_confluent_login", side_effect=_StopAfterLogin()),
            patch("builtins.input") as mock_input,
            pytest.raises(_StopAfterLogin),
        ):
            _run_main(["--automated"])

        mock_input.assert_not_called()


# ---------------------------------------------------------------------------
# --testing mode
# ---------------------------------------------------------------------------


class TestDeployTestingLogin:
    """Tests for ensure_confluent_login behavior in --testing mode."""

    def test_calls_ensure_login_with_json_email_password(self, tmp_path):
        """When credentials.json has email + password, ensure_confluent_login receives them."""
        mock_ensure = MagicMock(side_effect=_StopAfterLogin())

        with (
            patch("deploy.get_project_root", return_value=tmp_path),
            patch("deploy.load_credentials_json", return_value=dict(_VALID_JSON_CREDS)),
            patch("deploy.ensure_confluent_login", mock_ensure),
            patch("deploy.write_tfvars_for_deployment"),
            pytest.raises(_StopAfterLogin),
        ):
            _run_main(["--testing"])

        mock_ensure.assert_called_once()
        call_arg = mock_ensure.call_args[0][0]
        assert call_arg is not None
        assert call_arg.get("CONFLUENT_EMAIL") == "user@example.com"
        assert call_arg.get("CONFLUENT_PASSWORD") == "password123"

    def test_calls_ensure_login_with_none_when_no_email_in_json(self, tmp_path):
        """When credentials.json lacks email/password, ensure_confluent_login(None) is called."""
        creds_no_email = {
            k: v
            for k, v in _VALID_JSON_CREDS.items()
            if k not in ("confluent_cloud_email", "confluent_cloud_password")
        }
        mock_ensure = MagicMock(side_effect=_StopAfterLogin())

        with (
            patch("deploy.get_project_root", return_value=tmp_path),
            patch("deploy.load_credentials_json", return_value=creds_no_email),
            patch("deploy.ensure_confluent_login", mock_ensure),
            patch("deploy.write_tfvars_for_deployment"),
            pytest.raises(_StopAfterLogin),
        ):
            _run_main(["--testing"])

        mock_ensure.assert_called_once_with(None)

    def test_calls_ensure_login_with_none_when_email_empty(self, tmp_path):
        """Empty email string in json is treated the same as missing."""
        creds_empty = dict(_VALID_JSON_CREDS)
        creds_empty["confluent_cloud_email"] = ""
        creds_empty["confluent_cloud_password"] = ""
        mock_ensure = MagicMock(side_effect=_StopAfterLogin())

        with (
            patch("deploy.get_project_root", return_value=tmp_path),
            patch("deploy.load_credentials_json", return_value=creds_empty),
            patch("deploy.ensure_confluent_login", mock_ensure),
            patch("deploy.write_tfvars_for_deployment"),
            pytest.raises(_StopAfterLogin),
        ):
            _run_main(["--testing"])

        mock_ensure.assert_called_once_with(None)

    def test_exits_if_ensure_login_fails(self, tmp_path):
        """SystemExit from ensure_confluent_login propagates in --testing mode."""
        with (
            patch("deploy.get_project_root", return_value=tmp_path),
            patch("deploy.load_credentials_json", return_value=dict(_VALID_JSON_CREDS)),
            patch("deploy.ensure_confluent_login", side_effect=SystemExit(1)),
            patch("deploy.write_tfvars_for_deployment"),
            pytest.raises(SystemExit) as exc_info,
        ):
            _run_main(["--testing"])

        assert exc_info.value.code == 1

    def test_does_not_prompt_user(self, tmp_path):
        """--testing mode never calls input()."""
        with (
            patch("deploy.get_project_root", return_value=tmp_path),
            patch("deploy.load_credentials_json", return_value=dict(_VALID_JSON_CREDS)),
            patch("deploy.ensure_confluent_login", side_effect=_StopAfterLogin()),
            patch("deploy.write_tfvars_for_deployment"),
            patch("builtins.input") as mock_input,
            pytest.raises(_StopAfterLogin),
        ):
            _run_main(["--testing"])

        mock_input.assert_not_called()
