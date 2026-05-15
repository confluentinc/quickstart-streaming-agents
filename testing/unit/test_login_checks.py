"""Unit tests for scripts/common/login_checks.py."""

import subprocess
from unittest.mock import MagicMock, call, patch

import pytest

from scripts.common.login_checks import (
    attempt_confluent_auto_login,
    check_confluent_login,
    ensure_confluent_login,
    _attempt_login_quiet,
)


# ---------------------------------------------------------------------------
# check_confluent_login
# ---------------------------------------------------------------------------


class TestCheckConfluentLogin:
    def _ok_result(self):
        r = MagicMock()
        r.returncode = 0
        r.stdout = "  ID          | Name\n  env-abc123  | my-env\n"
        return r

    def test_returns_true_when_command_succeeds(self):
        with patch(
            "scripts.common.login_checks.subprocess.run", return_value=self._ok_result()
        ):
            assert check_confluent_login() is True

    def test_returns_true_with_empty_environment_list(self):
        """Logged-in account with no environments yet should still return True."""
        r = MagicMock()
        r.returncode = 0
        r.stdout = ""
        with patch("scripts.common.login_checks.subprocess.run", return_value=r):
            assert check_confluent_login() is True

    def test_returns_false_on_called_process_error(self):
        with patch(
            "scripts.common.login_checks.subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "confluent"),
        ):
            assert check_confluent_login() is False

    def test_returns_false_when_confluent_not_installed(self):
        with patch(
            "scripts.common.login_checks.subprocess.run",
            side_effect=FileNotFoundError("confluent not found"),
        ):
            assert check_confluent_login() is False

    def test_calls_correct_command(self):
        with patch(
            "scripts.common.login_checks.subprocess.run", return_value=self._ok_result()
        ) as mock_run:
            check_confluent_login()
            mock_run.assert_called_once_with(
                ["confluent", "environment", "list"],
                capture_output=True,
                text=True,
                check=True,
            )


# ---------------------------------------------------------------------------
# attempt_confluent_auto_login
# ---------------------------------------------------------------------------


class TestAttemptConfluentAutoLogin:
    GOOD_CREDS = {"CONFLUENT_EMAIL": "user@example.com", "CONFLUENT_PASSWORD": "secret"}

    def _login_ok(self):
        r = MagicMock()
        r.returncode = 0
        r.stdout = "Logged in as user@example.com"
        r.stderr = ""
        return r

    def _login_fail(self, stderr="Invalid credentials", stdout=""):
        r = MagicMock()
        r.returncode = 1
        r.stderr = stderr
        r.stdout = stdout
        return r

    # --- missing credentials ---

    def test_returns_false_when_creds_empty(self):
        assert attempt_confluent_auto_login({}) is False

    def test_returns_false_when_email_missing(self):
        assert attempt_confluent_auto_login({"CONFLUENT_PASSWORD": "secret"}) is False

    def test_returns_false_when_password_missing(self):
        assert (
            attempt_confluent_auto_login({"CONFLUENT_EMAIL": "user@example.com"})
            is False
        )

    def test_returns_false_when_email_empty_string(self):
        assert (
            attempt_confluent_auto_login(
                {"CONFLUENT_EMAIL": "", "CONFLUENT_PASSWORD": "secret"}
            )
            is False
        )

    def test_returns_false_when_password_empty_string(self):
        assert (
            attempt_confluent_auto_login(
                {"CONFLUENT_EMAIL": "user@example.com", "CONFLUENT_PASSWORD": ""}
            )
            is False
        )

    # --- no TF_VAR_owner_email fallback ---

    def test_returns_false_when_only_tf_var_owner_email_provided(self):
        """TF_VAR_owner_email is no longer a fallback for CONFLUENT_EMAIL."""
        creds = {
            "TF_VAR_owner_email": "owner@example.com",
            "CONFLUENT_PASSWORD": "secret",
        }
        assert attempt_confluent_auto_login(creds) is False

    # --- login failure ---

    def test_returns_false_on_bad_password(self, capsys):
        with patch(
            "scripts.common.login_checks.subprocess.run",
            return_value=self._login_fail("Invalid credentials"),
        ):
            result = attempt_confluent_auto_login(self.GOOD_CREDS)
        assert result is False
        captured = capsys.readouterr()
        assert "Auto-login failed" in captured.out
        assert "Invalid credentials" in captured.out

    def test_returns_false_on_bad_email(self, capsys):
        with patch(
            "scripts.common.login_checks.subprocess.run",
            return_value=self._login_fail("User not found"),
        ):
            result = attempt_confluent_auto_login(self.GOOD_CREDS)
        assert result is False
        captured = capsys.readouterr()
        assert "Auto-login failed" in captured.out
        assert "User not found" in captured.out

    def test_prints_stdout_when_stderr_empty(self, capsys):
        fail = self._login_fail(stderr="", stdout="SSO required for this organization")
        with patch("scripts.common.login_checks.subprocess.run", return_value=fail):
            attempt_confluent_auto_login(self.GOOD_CREDS)
        captured = capsys.readouterr()
        assert "SSO required" in captured.out

    def test_prints_nothing_extra_on_success(self, capsys):
        with (
            patch(
                "scripts.common.login_checks.subprocess.run",
                return_value=self._login_ok(),
            ),
            patch(
                "scripts.common.login_checks.check_confluent_login", return_value=True
            ),
        ):
            attempt_confluent_auto_login(self.GOOD_CREDS)
        captured = capsys.readouterr()
        assert "Auto-login failed" not in captured.out

    # --- post-login check ---

    def test_returns_true_when_login_and_check_both_pass(self):
        with (
            patch(
                "scripts.common.login_checks.subprocess.run",
                return_value=self._login_ok(),
            ),
            patch(
                "scripts.common.login_checks.check_confluent_login", return_value=True
            ),
        ):
            assert attempt_confluent_auto_login(self.GOOD_CREDS) is True

    def test_returns_false_when_login_ok_but_check_fails(self):
        """Login command exits 0 but session is still not valid (edge case)."""
        with (
            patch(
                "scripts.common.login_checks.subprocess.run",
                return_value=self._login_ok(),
            ),
            patch(
                "scripts.common.login_checks.check_confluent_login", return_value=False
            ),
        ):
            assert attempt_confluent_auto_login(self.GOOD_CREDS) is False

    # --- stdin format ---

    def test_passes_credentials_via_stdin(self):
        with (
            patch(
                "scripts.common.login_checks.subprocess.run",
                return_value=self._login_ok(),
            ) as mock_run,
            patch(
                "scripts.common.login_checks.check_confluent_login", return_value=True
            ),
        ):
            attempt_confluent_auto_login(self.GOOD_CREDS)
        _, kwargs = mock_run.call_args
        assert kwargs["input"] == "user@example.com\nsecret\n"

    def test_uses_save_flag(self):
        with (
            patch(
                "scripts.common.login_checks.subprocess.run",
                return_value=self._login_ok(),
            ) as mock_run,
            patch(
                "scripts.common.login_checks.check_confluent_login", return_value=True
            ),
        ):
            attempt_confluent_auto_login(self.GOOD_CREDS)
        args, _ = mock_run.call_args
        assert args[0] == ["confluent", "login", "--save"]

    def test_password_with_special_characters(self):
        """Passwords containing $, &, *, etc. must pass through unchanged."""
        creds = {"CONFLUENT_EMAIL": "u@e.com", "CONFLUENT_PASSWORD": "wC&Wk5$$df*!"}
        with (
            patch(
                "scripts.common.login_checks.subprocess.run",
                return_value=self._login_ok(),
            ) as mock_run,
            patch(
                "scripts.common.login_checks.check_confluent_login", return_value=True
            ),
        ):
            attempt_confluent_auto_login(creds)
        _, kwargs = mock_run.call_args
        assert kwargs["input"] == "u@e.com\nwC&Wk5$$df*!\n"


# ---------------------------------------------------------------------------
# ensure_confluent_login
# ---------------------------------------------------------------------------


class TestEnsureConfluentLogin:
    GOOD_CREDS = {"CONFLUENT_EMAIL": "user@example.com", "CONFLUENT_PASSWORD": "secret"}

    def test_returns_when_already_logged_in(self):
        with patch(
            "scripts.common.login_checks.check_confluent_login", return_value=True
        ):
            ensure_confluent_login({})  # should not raise

    def test_auto_login_from_creds_on_not_logged_in(self):
        with (
            patch(
                "scripts.common.login_checks.check_confluent_login",
                side_effect=[False, True],
            ),
            patch(
                "scripts.common.login_checks.attempt_confluent_auto_login",
                return_value=True,
            ),
        ):
            ensure_confluent_login(self.GOOD_CREDS)  # should not raise

    def test_exits_when_not_logged_in_and_no_creds(self):
        with (
            patch(
                "scripts.common.login_checks.check_confluent_login", return_value=False
            ),
            patch(
                "scripts.common.login_checks.attempt_confluent_auto_login",
                return_value=False,
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            ensure_confluent_login({})
        assert exc_info.value.code == 1

    def test_exits_when_auto_login_fails(self):
        with (
            patch(
                "scripts.common.login_checks.check_confluent_login", return_value=False
            ),
            patch(
                "scripts.common.login_checks.attempt_confluent_auto_login",
                return_value=False,
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            ensure_confluent_login(self.GOOD_CREDS)
        assert exc_info.value.code == 1

    def test_no_creds_arg_loads_from_env_file(self, tmp_path, monkeypatch):
        """When creds=None, loads from credentials.env relative to this file."""
        env_file = tmp_path / "credentials.env"
        env_file.write_text(
            "CONFLUENT_EMAIL=loaded@example.com\nCONFLUENT_PASSWORD=pw\n"
        )
        import scripts.common.login_checks as lc

        monkeypatch.setattr(lc, "check_confluent_login", lambda: False)
        monkeypatch.setattr(lc, "attempt_confluent_auto_login", lambda c: True)
        # Patch the path resolution so it finds our tmp env file
        monkeypatch.setattr(
            lc,
            "dotenv_values",
            lambda _: {
                "CONFLUENT_EMAIL": "loaded@example.com",
                "CONFLUENT_PASSWORD": "pw",
            },
        )
        ensure_confluent_login()  # should not raise (auto_login returns True)

    def test_error_message_contains_manual_login_hint(self, capsys):
        with (
            patch(
                "scripts.common.login_checks.check_confluent_login", return_value=False
            ),
            patch(
                "scripts.common.login_checks.attempt_confluent_auto_login",
                return_value=False,
            ),
            pytest.raises(SystemExit),
        ):
            ensure_confluent_login({})
        out = capsys.readouterr().out
        assert "confluent login" in out

    def test_error_message_contains_redeploy_hint(self, capsys):
        with (
            patch(
                "scripts.common.login_checks.check_confluent_login", return_value=False
            ),
            patch(
                "scripts.common.login_checks.attempt_confluent_auto_login",
                return_value=False,
            ),
            pytest.raises(SystemExit),
        ):
            ensure_confluent_login({})
        out = capsys.readouterr().out
        assert "uv run deploy" in out

    def test_error_message_contains_sso_hint(self, capsys):
        with (
            patch(
                "scripts.common.login_checks.check_confluent_login", return_value=False
            ),
            patch(
                "scripts.common.login_checks.attempt_confluent_auto_login",
                return_value=False,
            ),
            pytest.raises(SystemExit),
        ):
            ensure_confluent_login({})
        out = capsys.readouterr().out
        assert "--sso" in out


# ---------------------------------------------------------------------------
# _attempt_login_quiet
# ---------------------------------------------------------------------------


class TestAttemptLoginQuiet:
    GOOD_CREDS = ("user@example.com", "secret")

    def _login_ok(self):
        r = MagicMock()
        r.returncode = 0
        r.stdout = ""
        r.stderr = ""
        return r

    def _login_fail(self):
        r = MagicMock()
        r.returncode = 1
        r.stderr = "Invalid credentials"
        r.stdout = ""
        return r

    def test_returns_true_on_successful_login(self):
        with (
            patch(
                "scripts.common.login_checks.subprocess.run",
                return_value=self._login_ok(),
            ),
            patch(
                "scripts.common.login_checks.check_confluent_login", return_value=True
            ),
        ):
            assert _attempt_login_quiet(*self.GOOD_CREDS) is True

    def test_returns_false_on_subprocess_failure(self):
        with patch(
            "scripts.common.login_checks.subprocess.run",
            return_value=self._login_fail(),
        ):
            assert _attempt_login_quiet(*self.GOOD_CREDS) is False

    def test_returns_false_when_check_fails_after_login(self):
        """Process exits 0 but subsequent check shows not logged in."""
        with (
            patch(
                "scripts.common.login_checks.subprocess.run",
                return_value=self._login_ok(),
            ),
            patch(
                "scripts.common.login_checks.check_confluent_login", return_value=False
            ),
        ):
            assert _attempt_login_quiet(*self.GOOD_CREDS) is False

    def test_produces_no_output_on_failure(self, capsys):
        with patch(
            "scripts.common.login_checks.subprocess.run",
            return_value=self._login_fail(),
        ):
            _attempt_login_quiet(*self.GOOD_CREDS)
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""

    def test_produces_no_output_on_success(self, capsys):
        with (
            patch(
                "scripts.common.login_checks.subprocess.run",
                return_value=self._login_ok(),
            ),
            patch(
                "scripts.common.login_checks.check_confluent_login", return_value=True
            ),
        ):
            _attempt_login_quiet(*self.GOOD_CREDS)
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""

    def test_passes_credentials_via_stdin(self):
        with (
            patch(
                "scripts.common.login_checks.subprocess.run",
                return_value=self._login_ok(),
            ) as mock_run,
            patch(
                "scripts.common.login_checks.check_confluent_login", return_value=True
            ),
        ):
            _attempt_login_quiet("u@example.com", "mypass")
        _, kwargs = mock_run.call_args
        assert kwargs["input"] == "u@example.com\nmypass\n"

    def test_uses_save_flag(self):
        with (
            patch(
                "scripts.common.login_checks.subprocess.run",
                return_value=self._login_ok(),
            ) as mock_run,
            patch(
                "scripts.common.login_checks.check_confluent_login", return_value=True
            ),
        ):
            _attempt_login_quiet(*self.GOOD_CREDS)
        args, _ = mock_run.call_args
        assert args[0] == ["confluent", "login", "--save"]

    def test_password_with_special_characters(self):
        with (
            patch(
                "scripts.common.login_checks.subprocess.run",
                return_value=self._login_ok(),
            ) as mock_run,
            patch(
                "scripts.common.login_checks.check_confluent_login", return_value=True
            ),
        ):
            _attempt_login_quiet("u@e.com", "p@$$w0rd!")
        _, kwargs = mock_run.call_args
        assert kwargs["input"] == "u@e.com\np@$$w0rd!\n"
