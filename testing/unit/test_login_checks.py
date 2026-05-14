"""Unit tests for scripts/common/login_checks.py."""

import subprocess
from unittest.mock import MagicMock, call, patch

import pytest

from scripts.common.login_checks import attempt_confluent_auto_login, check_confluent_login


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
        with patch("scripts.common.login_checks.subprocess.run", return_value=self._ok_result()):
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
        assert attempt_confluent_auto_login({"CONFLUENT_EMAIL": "user@example.com"}) is False

    def test_returns_false_when_email_empty_string(self):
        assert attempt_confluent_auto_login({"CONFLUENT_EMAIL": "", "CONFLUENT_PASSWORD": "secret"}) is False

    def test_returns_false_when_password_empty_string(self):
        assert attempt_confluent_auto_login({"CONFLUENT_EMAIL": "user@example.com", "CONFLUENT_PASSWORD": ""}) is False

    # --- email fallback ---

    def test_falls_back_to_tf_var_owner_email(self):
        creds = {"TF_VAR_owner_email": "owner@example.com", "CONFLUENT_PASSWORD": "secret"}
        with patch("scripts.common.login_checks.subprocess.run", return_value=self._login_ok()) as mock_run, \
             patch("scripts.common.login_checks.check_confluent_login", return_value=True):
            result = attempt_confluent_auto_login(creds)
        assert result is True
        mock_run.assert_called_once()
        _, kwargs = mock_run.call_args
        assert kwargs["input"] == "owner@example.com\nsecret\n"

    def test_confluent_email_takes_precedence_over_tf_var(self):
        creds = {
            "CONFLUENT_EMAIL": "primary@example.com",
            "TF_VAR_owner_email": "fallback@example.com",
            "CONFLUENT_PASSWORD": "secret",
        }
        with patch("scripts.common.login_checks.subprocess.run", return_value=self._login_ok()) as mock_run, \
             patch("scripts.common.login_checks.check_confluent_login", return_value=True):
            attempt_confluent_auto_login(creds)
        _, kwargs = mock_run.call_args
        assert kwargs["input"] == "primary@example.com\nsecret\n"

    # --- login failure ---

    def test_returns_false_on_bad_password(self, capsys):
        with patch("scripts.common.login_checks.subprocess.run", return_value=self._login_fail("Invalid credentials")):
            result = attempt_confluent_auto_login(self.GOOD_CREDS)
        assert result is False
        captured = capsys.readouterr()
        assert "Auto-login failed" in captured.out
        assert "Invalid credentials" in captured.out

    def test_returns_false_on_bad_email(self, capsys):
        with patch("scripts.common.login_checks.subprocess.run", return_value=self._login_fail("User not found")):
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
        with patch("scripts.common.login_checks.subprocess.run", return_value=self._login_ok()), \
             patch("scripts.common.login_checks.check_confluent_login", return_value=True):
            attempt_confluent_auto_login(self.GOOD_CREDS)
        captured = capsys.readouterr()
        assert "Auto-login failed" not in captured.out

    # --- post-login check ---

    def test_returns_true_when_login_and_check_both_pass(self):
        with patch("scripts.common.login_checks.subprocess.run", return_value=self._login_ok()), \
             patch("scripts.common.login_checks.check_confluent_login", return_value=True):
            assert attempt_confluent_auto_login(self.GOOD_CREDS) is True

    def test_returns_false_when_login_ok_but_check_fails(self):
        """Login command exits 0 but session is still not valid (edge case)."""
        with patch("scripts.common.login_checks.subprocess.run", return_value=self._login_ok()), \
             patch("scripts.common.login_checks.check_confluent_login", return_value=False):
            assert attempt_confluent_auto_login(self.GOOD_CREDS) is False

    # --- stdin format ---

    def test_passes_credentials_via_stdin(self):
        with patch("scripts.common.login_checks.subprocess.run", return_value=self._login_ok()) as mock_run, \
             patch("scripts.common.login_checks.check_confluent_login", return_value=True):
            attempt_confluent_auto_login(self.GOOD_CREDS)
        _, kwargs = mock_run.call_args
        assert kwargs["input"] == "user@example.com\nsecret\n"

    def test_uses_save_flag(self):
        with patch("scripts.common.login_checks.subprocess.run", return_value=self._login_ok()) as mock_run, \
             patch("scripts.common.login_checks.check_confluent_login", return_value=True):
            attempt_confluent_auto_login(self.GOOD_CREDS)
        args, _ = mock_run.call_args
        assert args[0] == ["confluent", "login", "--save"]

    def test_password_with_special_characters(self):
        """Passwords containing $, &, *, etc. must pass through unchanged."""
        creds = {"CONFLUENT_EMAIL": "u@e.com", "CONFLUENT_PASSWORD": "wC&Wk5$$df*!"}
        with patch("scripts.common.login_checks.subprocess.run", return_value=self._login_ok()) as mock_run, \
             patch("scripts.common.login_checks.check_confluent_login", return_value=True):
            attempt_confluent_auto_login(creds)
        _, kwargs = mock_run.call_args
        assert kwargs["input"] == "u@e.com\nwC&Wk5$$df*!\n"
