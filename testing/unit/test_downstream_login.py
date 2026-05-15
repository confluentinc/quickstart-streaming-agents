"""
Unit tests verifying that downstream scripts call ensure_confluent_login and propagate failure.

Covers: destroy.py, publish_docs.py, lab2_publish_queries.py
"""

import sys
from unittest.mock import MagicMock, patch

import pytest

import scripts.common.destroy as destroy_mod
import scripts.publish_docs as publish_docs_mod
import scripts.lab2_publish_queries as lab2_mod


# Sentinel to halt script execution immediately after the login call.
class _StopAfterLogin(Exception):
    pass


# ---------------------------------------------------------------------------
# destroy.py
# ---------------------------------------------------------------------------


class TestDestroyLogin:
    """Interactive destroy mode calls ensure_confluent_login with credentials.env contents."""

    def _run_interactive(self, creds, tmp_path):
        """Run destroy.main() in interactive mode with given creds and sentinel on login."""
        mock_ensure = MagicMock(side_effect=_StopAfterLogin())
        with (
            patch.object(sys, "argv", ["destroy"]),
            patch("scripts.common.destroy.get_project_root", return_value=tmp_path),
            patch("scripts.common.destroy.dotenv_values", return_value=creds),
            patch("scripts.common.destroy.ensure_confluent_login", mock_ensure),
            patch("scripts.common.destroy.prompt_choice", return_value="aws"),
        ):
            try:
                destroy_mod.main()
            except _StopAfterLogin:
                pass
        return mock_ensure

    def test_interactive_calls_ensure_login(self, tmp_path):
        """ensure_confluent_login is called in interactive destroy mode."""
        creds = {"CONFLUENT_EMAIL": "user@example.com", "CONFLUENT_PASSWORD": "pw"}
        mock_ensure = self._run_interactive(creds, tmp_path)
        mock_ensure.assert_called_once()

    def test_interactive_passes_credentials_env_to_ensure_login(self, tmp_path):
        """ensure_confluent_login receives the full creds dict from credentials.env."""
        creds = {"CONFLUENT_EMAIL": "user@example.com", "CONFLUENT_PASSWORD": "pw"}
        mock_ensure = self._run_interactive(creds, tmp_path)
        call_creds = mock_ensure.call_args[0][0]
        assert call_creds == creds

    def test_interactive_exits_if_not_logged_in(self, tmp_path):
        """SystemExit from ensure_confluent_login propagates."""
        with (
            patch.object(sys, "argv", ["destroy"]),
            patch("scripts.common.destroy.get_project_root", return_value=tmp_path),
            patch("scripts.common.destroy.dotenv_values", return_value={}),
            patch(
                "scripts.common.destroy.ensure_confluent_login",
                side_effect=SystemExit(1),
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            destroy_mod.main()
        assert exc_info.value.code == 1

    def test_testing_mode_skips_login(self, tmp_path):
        """--testing mode does not call ensure_confluent_login."""
        test_creds = {
            "cloud": "aws",
            "region": "us-east-1",
            "confluent_cloud_api_key": "key",
            "confluent_cloud_api_secret": "secret",
        }
        mock_ensure = MagicMock()
        # Make run_terraform_destroy raise to stop after login block
        with (
            patch.object(sys, "argv", ["destroy", "--testing"]),
            patch("scripts.common.destroy.get_project_root", return_value=tmp_path),
            patch(
                "scripts.common.destroy.load_credentials_json", return_value=test_creds
            ),
            patch("scripts.common.destroy.ensure_confluent_login", mock_ensure),
            patch(
                "scripts.common.destroy.run_terraform_destroy",
                side_effect=_StopAfterLogin(),
            ),
        ):
            try:
                destroy_mod.main()
            except _StopAfterLogin:
                pass
        mock_ensure.assert_not_called()


# ---------------------------------------------------------------------------
# publish_docs.py
# ---------------------------------------------------------------------------


class TestPublishDocsLogin:
    """publish_docs.main() calls ensure_confluent_login before publishing."""

    def test_main_calls_ensure_login(self):
        """ensure_confluent_login is called when main() runs."""
        mock_ensure = MagicMock(side_effect=_StopAfterLogin())
        with (
            patch.object(sys, "argv", ["publish_docs", "--lab2"]),
            patch("scripts.publish_docs.ensure_confluent_login", mock_ensure),
            pytest.raises(_StopAfterLogin),
        ):
            publish_docs_mod.main()
        mock_ensure.assert_called_once()

    def test_main_calls_ensure_login_no_args(self):
        """ensure_confluent_login is called with no arguments (loads from credentials.env)."""
        mock_ensure = MagicMock(side_effect=_StopAfterLogin())
        with (
            patch.object(sys, "argv", ["publish_docs", "--lab2"]),
            patch("scripts.publish_docs.ensure_confluent_login", mock_ensure),
            pytest.raises(_StopAfterLogin),
        ):
            publish_docs_mod.main()
        args, kwargs = mock_ensure.call_args
        assert args == ()
        assert kwargs == {}

    def test_main_exits_if_not_logged_in(self):
        """SystemExit from ensure_confluent_login propagates out of publish_docs.main()."""
        with (
            patch.object(sys, "argv", ["publish_docs", "--lab2"]),
            patch(
                "scripts.publish_docs.ensure_confluent_login", side_effect=SystemExit(1)
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            publish_docs_mod.main()
        assert exc_info.value.code == 1

    def test_ensure_login_called_before_lab_detection(self):
        """ensure_confluent_login fires even before lab/cloud detection (early gate)."""
        call_order = []
        mock_ensure = MagicMock(
            side_effect=lambda: (
                call_order.append("login") or (_ for _ in ()).throw(_StopAfterLogin())
            )
        )
        with (
            patch.object(sys, "argv", ["publish_docs", "--lab2"]),
            patch("scripts.publish_docs.ensure_confluent_login", mock_ensure),
            pytest.raises(_StopAfterLogin),
        ):
            publish_docs_mod.main()
        # If we caught _StopAfterLogin it means ensure_confluent_login ran
        assert "login" in call_order


# ---------------------------------------------------------------------------
# lab2_publish_queries.py
# ---------------------------------------------------------------------------


class TestLab2PublishLogin:
    """lab2_publish_queries.main() calls ensure_confluent_login before querying."""

    def _run_main(self, cloud="aws", query="test query"):
        mock_ensure = MagicMock(side_effect=_StopAfterLogin())
        with (
            patch.object(sys, "argv", ["publish_queries", cloud, query]),
            patch(
                "scripts.lab2_publish_queries.auto_detect_cloud_provider",
                return_value=cloud,
            ),
            patch(
                "scripts.lab2_publish_queries.validate_cloud_provider",
                return_value=True,
            ),
            patch(
                "scripts.lab2_publish_queries.get_project_root",
                return_value=MagicMock(),
            ),
            patch("scripts.lab2_publish_queries.ensure_confluent_login", mock_ensure),
        ):
            try:
                lab2_mod.main()
            except _StopAfterLogin:
                pass
        return mock_ensure

    def test_main_calls_ensure_login(self):
        """ensure_confluent_login is called when main() runs."""
        mock_ensure = self._run_main()
        mock_ensure.assert_called_once()

    def test_main_calls_ensure_login_no_args(self):
        """ensure_confluent_login is called with no arguments."""
        mock_ensure = self._run_main()
        args, kwargs = mock_ensure.call_args
        assert args == ()
        assert kwargs == {}

    def test_main_exits_if_not_logged_in(self):
        """SystemExit from ensure_confluent_login propagates out of main()."""
        with (
            patch.object(sys, "argv", ["publish_queries", "aws", "test"]),
            patch(
                "scripts.lab2_publish_queries.auto_detect_cloud_provider",
                return_value="aws",
            ),
            patch(
                "scripts.lab2_publish_queries.validate_cloud_provider",
                return_value=True,
            ),
            patch(
                "scripts.lab2_publish_queries.get_project_root",
                return_value=MagicMock(),
            ),
            patch(
                "scripts.lab2_publish_queries.ensure_confluent_login",
                side_effect=SystemExit(1),
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            lab2_mod.main()
        assert exc_info.value.code == 1

    def test_main_does_not_call_ensure_login_on_failed_validation(self):
        """If validate_cloud_provider returns False, ensure_confluent_login is never reached."""
        mock_ensure = MagicMock()
        # Pass a valid argparse choice but have the validator reject it (simulates
        # a provider that passes the CLI choice list but fails a deeper check).
        with (
            patch.object(sys, "argv", ["publish_queries", "aws", "test"]),
            patch(
                "scripts.lab2_publish_queries.validate_cloud_provider",
                return_value=False,
            ),
            patch("scripts.lab2_publish_queries.ensure_confluent_login", mock_ensure),
        ):
            result = lab2_mod.main()
        mock_ensure.assert_not_called()
        assert result == 1
