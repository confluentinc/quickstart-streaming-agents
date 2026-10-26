"""`run_terraform`: retry the cloud's bad day, never a permanent mistake.

A wrong Confluent API key, an unset `TF_VAR_`, a validation error or a name
collision fails identically on every retry, so retrying those is pure dead time
on exactly the failures an operator is most likely to hit. Network blips,
throttling and 5xx responses do clear, so those get the retries.

The classifier is only worth having if it keys on text Terraform actually emits,
so the samples marked VERIFIED below were reproduced locally (terraform 1.15.8,
hashicorp/aws 5.x, confluentinc/confluent 2.x) and pasted verbatim — including
the line wrapping, which is why the AWS network sample has "StatusCode: 0,"
and "no such host" on different lines. Samples marked SHAPE are the documented
form of an error we could not provoke without breaking something real; they are
the ones a live failure should confirm.

The other half of the contract: Terraform state survives every failure. Deleting
it after a partial apply strands whatever the apply already created.
"""

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts.common import terraform_runner as tr

# --- VERIFIED: confluentinc/confluent 2.x with a bad Cloud API key ------------
CONFLUENT_BAD_KEY = """
Error: error reading Environment "env-abc123": 401 Unauthorized: invalid API key: \
make sure you're using a Cloud or Global API Key, and not a Cluster API Key: \
https://docs.confluent.io/cloud/current/api.html#section/Authentication

  with data.confluent_environment.e,
  on main.tf line 10, in data "confluent_environment" "e":
  10: data "confluent_environment" "e" { id = "env-abc123" }
"""

# --- VERIFIED: hashicorp/aws 5.x with a bogus access key ----------------------
AWS_BAD_CREDENTIALS = """
Error: Retrieving AWS account details: validating provider credentials: retrieving \
caller identity from STS: operation error STS: GetCallerIdentity, https response error \
StatusCode: 403, RequestID: d32cc9b4-ed3b-43c9-b5c5-cbad504608e2, api error \
InvalidClientTokenId: The security token included in the request is invalid.

  with provider["registry.terraform.io/hashicorp/aws"],
  on main.tf line 6, in provider "aws":
   6: provider "aws" {
"""

# --- VERIFIED: terraform apply with an unset root variable --------------------
MISSING_VARIABLE = """
Error: No value for required variable

  on main.tf line 1:
   1: variable "needed" {

The root module input variable "needed" is not set, and has no default value.
Use a -var or -var-file command line argument to provide a value for this
variable.
"""

# --- VERIFIED: a failing `validation {}` block --------------------------------
FAILED_VALIDATION = """
Error: Invalid value for variable

  on main.tf line 1:
   1: variable "checked" {
    ├────────────────
    │ var.checked is 1

checked must exceed 5.

This was checked by the validation rule at main.tf:4,3-13.
"""

# --- VERIFIED: hashicorp/aws 5.x pointed at an unresolvable endpoint ----------
NETWORK_FAILURE = """
Error: reading STS Caller Identity

  with data.aws_caller_identity.me,
  on main.tf line 14, in data "aws_caller_identity" "me":
  14: data "aws_caller_identity" "me" {}

operation error STS: GetCallerIdentity, https response error StatusCode: 0,
RequestID: , request send failed, Post
"https://sts.this-host-does-not-exist.invalid/": dial tcp: lookup
sts.this-host-does-not-exist.invalid: no such host
"""

# --- SHAPE: aws-sdk-go-v2 wire format, throttle code from its retryable list --
AWS_THROTTLED = """
Error: creating Lambda Function (streaming-agents-mcp): operation error Lambda: \
CreateFunction, https response error StatusCode: 400, RequestID: 9f0e, api error \
ThrottlingException: Rate exceeded
"""

# --- SHAPE: aws-sdk-go-v2 wire format, 503 is on its retryable status list ----
AWS_SERVICE_UNAVAILABLE = """
Error: creating ECR Repository: operation error ECR: CreateRepository, https response \
error StatusCode: 503, RequestID: 1a2b, api error ServiceUnavailableException: \
Service is unavailable. Please try again later.
"""

# --- SHAPE: re-running LAB SQL against a live environment --------------------
FLINK_TABLE_EXISTS = """
Error: error creating Flink Statement: 400 Bad Request: Table 'enriched_orders' already exists
"""

# --- SHAPE: 409 is deliberately NOT treated as a collision -------------------
CC_CONFLICT = """
Error: error updating Kafka Cluster "lkc-abc123": 409 Conflict: another operation is \
already in progress for this cluster
"""

# --- SHAPE: provider double-POST of an auto-named Flink statement (409) -------
FLINK_STATEMENT_ORPHANED = """
Error: error creating Flink Statement "": 409 Conflict: Statement with name \
"tf-2026-10-15-151220-ec8bb612-81f5-423c-9915-76480c7dc986" already exists.
You can delete the existing statement, run a new statement with a different name.
"""

# A provider error nothing in either table matches.
UNKNOWN_FAILURE = """
Error: error creating Flink Connection: the moon is in the wrong phase
"""


class FakeProc:
    """Just enough of Popen for `_run_capturing_stderr`."""

    def __init__(self, returncode: int, diagnostics: str):
        self._returncode = returncode
        self.stderr = io.StringIO(diagnostics)

    def wait(self) -> int:
        return self._returncode


class ClassificationTests(unittest.TestCase):
    """Real error text in, the right verdict out."""

    def assertPermanent(self, diagnostics: str, expected_reason: str):
        retry, reason = tr.classify_apply_failure(diagnostics)
        self.assertFalse(retry, f"should not retry, got reason {reason!r}")
        self.assertEqual(reason, expected_reason)

    def assertTransient(self, diagnostics: str, expected_reason: str):
        retry, reason = tr.classify_apply_failure(diagnostics)
        self.assertTrue(retry, f"should retry, got reason {reason!r}")
        self.assertEqual(reason, expected_reason)

    def test_a_bad_confluent_api_key_is_permanent(self):
        self.assertPermanent(
            CONFLUENT_BAD_KEY, "authentication failed (401 Unauthorized)"
        )

    def test_bad_aws_credentials_are_permanent(self):
        self.assertPermanent(
            AWS_BAD_CREDENTIALS, "AWS API rejected the credentials (HTTP 401/403)"
        )

    def test_an_unset_terraform_variable_is_permanent(self):
        self.assertPermanent(
            MISSING_VARIABLE, "a required Terraform variable is not set"
        )

    def test_a_failed_variable_validation_is_permanent(self):
        self.assertPermanent(
            FAILED_VALIDATION, "a Terraform variable failed validation"
        )

    def test_an_existing_flink_table_is_permanent(self):
        self.assertPermanent(FLINK_TABLE_EXISTS, "the resource already exists")

    def test_an_orphaned_auto_named_flink_statement_is_retryable(self):
        self.assertTransient(
            FLINK_STATEMENT_ORPHANED,
            "an orphaned Flink statement (the re-apply is a no-op)",
        )

    def test_a_dns_failure_is_transient(self):
        self.assertTransient(NETWORK_FAILURE, "DNS lookup failed")

    def test_throttling_is_transient(self):
        self.assertTransient(AWS_THROTTLED, "the API is throttling us")

    def test_a_503_is_transient(self):
        self.assertTransient(AWS_SERVICE_UNAVAILABLE, "the API returned a 5xx")

    def test_a_409_conflict_is_left_retryable_on_purpose(self):
        # Confluent Cloud returns 409 for "another operation is already in
        # progress", which clears on its own — so 409 is not in the collision
        # table and this must NOT be classified as a permanent collision.
        retry, _reason = tr.classify_apply_failure(CC_CONFLICT)
        self.assertTrue(retry)

    def test_an_unrecognised_error_still_retries(self):
        # The documented default: unknown errors keep the old behaviour.
        self.assertTransient(UNKNOWN_FAILURE, tr.UNCLASSIFIED)

    def test_a_permanent_error_beats_a_transient_one_in_the_same_output(self):
        # A multi-resource apply can fail several ways at once. If any failure is
        # permanent the re-apply cannot succeed, so the sleeps are pure waste.
        both = AWS_THROTTLED + MISSING_VARIABLE
        self.assertPermanent(both, "a required Terraform variable is not set")
        self.assertPermanent(
            MISSING_VARIABLE + AWS_THROTTLED, "a required Terraform variable is not set"
        )

    def test_a_resource_id_containing_403_is_not_an_auth_failure(self):
        # Patterns are anchored on the wire format ("StatusCode: 403"), not on a
        # bare number that any cluster id or row count could contain.
        noise = 'Error: error creating Kafka Topic: cluster "lkc-403x" is not ready (503 orders)\n'
        retry, reason = tr.classify_apply_failure(noise)
        self.assertTrue(retry)
        self.assertNotIn("401/403", reason)

    def test_warnings_alone_are_not_a_permanent_failure(self):
        # stderr also carries warnings; none of them should look like a verdict.
        warning = (
            "\nWarning: Argument is deprecated\n\n"
            "  with confluent_kafka_topic.orders,\n"
            "  on main.tf line 20, in resource:\n"
            '  20: resource "confluent_kafka_topic" "orders" {\n'
        )
        retry, reason = tr.classify_apply_failure(warning)
        self.assertTrue(retry)
        self.assertEqual(reason, tr.UNCLASSIFIED)


class RealWireFormatTests(unittest.TestCase):
    """The bytes the runner really receives, not the tidy `-no-color` version.

    `run_terraform` does not pass `-no-color`, so terraform boxes each diagnostic
    in an ANSI-coloured `╷ │ ╵` gutter and splits the summary with resets:

        \\x1b[31m│\\x1b[0m \\x1b[0m\\x1b[1m\\x1b[31mError: \\x1b[0m\\x1b[0m\\x1b[1mUnsupported argument\\x1b[0m

    Both fixtures below are `repr()` captures of real terraform 1.15.8 stderr.
    Without normalisation not one `^Error:` pattern could ever fire against them,
    which is the exact failure mode of a classifier that looks like it works.
    """

    COLOURED_MISSING_VARIABLE = (
        "\x1b[31m╷\x1b[0m\x1b[0m\n"
        "\x1b[31m│\x1b[0m \x1b[0m\x1b[1m\x1b[31mError: \x1b[0m\x1b[0m\x1b[1mNo value for required variable\x1b[0m\n"
        "\x1b[31m│\x1b[0m \x1b[0m\n"
        "\x1b[31m│\x1b[0m \x1b[0m\x1b[0m  on main.tf line 1:\n"
        '\x1b[31m│\x1b[0m \x1b[0m   1: \x1b[4mvariable "needed"\x1b[0m {\x1b[0m\n'
        "\x1b[31m│\x1b[0m \x1b[0m\n"
        '\x1b[31m│\x1b[0m \x1b[0mThe root module input variable "needed" is not set, and has no default\n'
        "\x1b[31m│\x1b[0m \x1b[0mvalue. Use a -var or -var-file command line argument to provide a value for\n"
        "\x1b[31m│\x1b[0m \x1b[0mthis variable.\n"
        "\x1b[31m╵\x1b[0m\x1b[0m\n"
    )

    COLOURED_UNSUPPORTED_ARGUMENT = (
        "\x1b[31m╷\x1b[0m\x1b[0m\n"
        "\x1b[31m│\x1b[0m \x1b[0m\x1b[1m\x1b[31mError: \x1b[0m\x1b[0m\x1b[1mUnsupported argument\x1b[0m\n"
        "\x1b[31m│\x1b[0m \x1b[0m\n"
        '\x1b[31m│\x1b[0m \x1b[0m\x1b[0m  on main.tf line 4, in variable "v":\n'
        "\x1b[31m│\x1b[0m \x1b[0m   4:   \x1b[4mbogus_arg\x1b[0m = true\x1b[0m\n"
        "\x1b[31m│\x1b[0m \x1b[0m\n"
        '\x1b[31m│\x1b[0m \x1b[0mAn argument named "bogus_arg" is not expected here.\n'
        "\x1b[31m╵\x1b[0m\x1b[0m\n"
    )

    def test_the_gutter_and_colour_codes_are_stripped(self):
        lines, _flat = tr._normalise(self.COLOURED_UNSUPPORTED_ARGUMENT)
        self.assertIn("Error: Unsupported argument", lines)
        self.assertNotIn("\x1b", lines)
        self.assertNotIn("│", lines)

    def test_wrapped_prose_is_rejoined(self):
        # Terraform hard-wraps at ~78 columns: "...and has no default" / "value."
        _lines, flat = tr._normalise(self.COLOURED_MISSING_VARIABLE)
        self.assertIn("is not set, and has no default value.", flat)

    def test_a_coloured_missing_variable_is_permanent(self):
        retry, reason = tr.classify_apply_failure(self.COLOURED_MISSING_VARIABLE)
        self.assertFalse(retry)
        self.assertEqual(reason, "a required Terraform variable is not set")

    def test_a_coloured_config_error_is_permanent(self):
        # Nothing but the `^Error:` anchor can catch this one — no companion
        # pattern matches its prose — so it is the real test of normalisation.
        retry, reason = tr.classify_apply_failure(self.COLOURED_UNSUPPORTED_ARGUMENT)
        self.assertFalse(retry)
        self.assertEqual(reason, "invalid Terraform configuration")

    def test_the_no_color_form_classifies_identically(self):
        # Same errors as the fixtures above, as `-no-color` renders them.
        self.assertFalse(tr.classify_apply_failure(MISSING_VARIABLE)[0])
        self.assertFalse(tr.classify_apply_failure("Error: Unsupported argument\n")[0])


class ApplyLoopTests(unittest.TestCase):
    """What the classifier buys: attempt counts, sleeps, and surviving state."""

    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.env_path = Path(self._tmp.name) / "aws"
        self.env_path.mkdir()
        self.addCleanup(self._tmp.cleanup)

        # A partial apply's worth of state, which must survive every failure.
        self.state = self.env_path / "terraform.tfstate"
        self.state.write_text('{"resources": ["confluent_environment.main"]}')

        self.applies = 0
        self.sleeps: list[int] = []

    def run_apply(
        self, outcomes: list[tuple[int, str]], max_attempts: int = 3
    ) -> tuple[bool, str]:
        """Drive `run_terraform` with a scripted list of (returncode, stderr)."""

        def fake_popen(cmd, **_kwargs):
            self.applies += 1
            code, diagnostics = outcomes[min(self.applies - 1, len(outcomes) - 1)]
            return FakeProc(code, diagnostics)

        out, err = io.StringIO(), io.StringIO()
        with (
            # `terraform init` runs before the loop; stub it so no real
            # terraform is ever invoked from a temp dir.
            patch.object(tr.subprocess, "run", return_value=None),
            patch.object(tr.subprocess, "Popen", side_effect=fake_popen),
            patch.object(tr.time, "sleep", side_effect=self.sleeps.append),
            redirect_stdout(out),
            redirect_stderr(err),
        ):
            ok = tr.run_terraform(self.env_path, max_attempts=max_attempts)
        return ok, out.getvalue() + err.getvalue()

    def test_a_permanent_failure_costs_one_attempt_and_no_sleep(self):
        ok, output = self.run_apply([(1, CONFLUENT_BAD_KEY)])

        self.assertFalse(ok)
        self.assertEqual(self.applies, 1, "a permanent failure must not be retried")
        self.assertEqual(self.sleeps, [], "a permanent failure must not sleep")
        self.assertIn("Not retrying", output)
        self.assertIn("401 Unauthorized", output)

    def test_every_permanent_class_short_circuits(self):
        for name, diagnostics in (
            ("bad confluent key", CONFLUENT_BAD_KEY),
            ("bad aws credentials", AWS_BAD_CREDENTIALS),
            ("missing variable", MISSING_VARIABLE),
            ("failed validation", FAILED_VALIDATION),
            ("existing table", FLINK_TABLE_EXISTS),
        ):
            with self.subTest(name):
                self.applies, self.sleeps = 0, []
                ok, _ = self.run_apply([(1, diagnostics)])
                self.assertFalse(ok)
                self.assertEqual(self.applies, 1)
                self.assertEqual(self.sleeps, [])

    def test_a_transient_failure_uses_every_attempt(self):
        ok, output = self.run_apply([(1, NETWORK_FAILURE)])

        self.assertFalse(ok)
        self.assertEqual(self.applies, 3)
        self.assertEqual(self.sleeps, [tr.RETRY_DELAY_SECONDS, tr.RETRY_DELAY_SECONDS])
        self.assertIn("after 3 attempts", output)

    def test_a_transient_failure_that_clears_succeeds(self):
        ok, _ = self.run_apply([(1, AWS_THROTTLED), (0, "")])

        self.assertTrue(ok)
        self.assertEqual(self.applies, 2)
        self.assertEqual(self.sleeps, [tr.RETRY_DELAY_SECONDS])

    def test_an_unrecognised_failure_keeps_the_old_retry_behaviour(self):
        ok, _ = self.run_apply([(1, UNKNOWN_FAILURE)])

        self.assertFalse(ok)
        self.assertEqual(self.applies, 3)

    def test_a_clean_apply_neither_retries_nor_sleeps(self):
        ok, _ = self.run_apply([(0, "")])

        self.assertTrue(ok)
        self.assertEqual(self.applies, 1)
        self.assertEqual(self.sleeps, [])

    def test_state_survives_every_failure(self):
        for name, diagnostics in (
            ("permanent", MISSING_VARIABLE),
            ("transient", NETWORK_FAILURE),
            ("unclassified", UNKNOWN_FAILURE),
        ):
            with self.subTest(name):
                self.applies, self.sleeps = 0, []
                self.run_apply([(1, diagnostics)])
                self.assertTrue(
                    self.state.exists(), f"{name} failure deleted terraform.tfstate"
                )
                self.assertIn("confluent_environment.main", self.state.read_text())

    def test_the_operator_still_sees_terraform_diagnostics(self):
        # Capturing stderr to classify it must not swallow it.
        _ok, output = self.run_apply([(1, CONFLUENT_BAD_KEY)])
        self.assertIn("error reading Environment", output)
        self.assertIn("docs.confluent.io", output)

    def test_stdout_is_never_piped(self):
        # Terraform's progress output has to keep streaming live to the terminal,
        # so only stderr may be captured.
        seen: dict = {}

        def fake_popen(cmd, **kwargs):
            seen.update(kwargs)
            return FakeProc(0, "")

        with (
            patch.object(tr.subprocess, "run", return_value=None),
            patch.object(tr.subprocess, "Popen", side_effect=fake_popen),
            redirect_stdout(io.StringIO()),
        ):
            tr.run_terraform(self.env_path)

        self.assertNotIn("stdout", seen)
        self.assertIsNotNone(seen.get("stderr"))

    def test_only_a_successful_core_apply_writes_the_deployment_summary(self):
        core = Path(self._tmp.name) / "core"
        core.mkdir()
        for code, expected_calls in ((1, 0), (0, 1)):
            with self.subTest(returncode=code):
                with (
                    patch.object(tr.subprocess, "run", return_value=None),
                    patch.object(
                        tr.subprocess,
                        "Popen",
                        return_value=FakeProc(code, MISSING_VARIABLE),
                    ),
                    patch.object(tr, "_generate_deployment_summary") as summary,
                    redirect_stdout(io.StringIO()),
                    redirect_stderr(io.StringIO()),
                ):
                    tr.run_terraform(core)
                self.assertEqual(summary.call_count, expected_calls)


if __name__ == "__main__":
    unittest.main()
