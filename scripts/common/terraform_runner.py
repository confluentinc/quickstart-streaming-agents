"""
Terraform execution wrapper utilities.

Provides functions for:
- Running terraform init and apply
- Running terraform destroy
- Classifying an apply failure as transient (worth retrying) or permanent
- Handling terraform errors and output

Terraform state is **never** cleaned up here, on any failure path. A failed
apply leaves partially-created cloud resources recorded in state; deleting it
would strand them.
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path

from .generate_deployment_summary import generate_credentials_markdown

# Transient Confluent/SR/AWS API errors (e.g. "connection reset by peer" while a
# Flink statement registers schemas) fail the apply but leave the resource
# tainted, so an immediate re-apply recovers cleanly. Retry before giving up.
#
# Permanent failures (bad credentials, a validation error, a missing variable, a
# name collision) get no retries at all: 3 attempts x 30 s used to add a minute
# of dead time to every one of them. `classify_apply_failure()` tells them apart.
APPLY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 30

UNCLASSIFIED = "unrecognised terraform/provider error"

# Permanent failures. Checked BEFORE the transient patterns: if a run's output
# holds both a permanent and a transient diagnostic, the re-apply still cannot
# succeed — the permanent resource fails identically — so sleeping is pure waste.
#
# Provenance of the patterns, since a classifier keyed on strings that never
# occur is worse than none:
#   [verified]  reproduced locally against terraform 1.15.8 with the AWS 5.x and
#               confluentinc/confluent 2.x providers, error text copied verbatim.
#   [sdk]       taken from aws-sdk-go-v2 `aws/retry/standard.go`, which is what
#               formats and classifies every AWS provider API error.
#   [expected]  the documented/known shape, not observed in this repo; these are
#               the ones a real failure should confirm.
_PERMANENT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (label, re.compile(pattern, re.IGNORECASE | re.MULTILINE))
    for label, pattern in (
        # --- credentials / authorisation -------------------------------------
        # [verified] the Confluent provider surfaces a bad Cloud API key as:
        #   Error: error reading Environment "env-abc123": 401 Unauthorized:
        #   invalid API key: make sure you're using a Cloud or Global API Key...
        ("authentication failed (401 Unauthorized)", r"\b401 Unauthorized\b"),
        ("authentication failed (invalid API key)", r"invalid API key"),
        # [expected] same provider/CC-API shape, 403 instead of 401.
        ("not authorized (403 Forbidden)", r"\b403 Forbidden\b"),
        # [verified] aws-sdk-go-v2 formats every API failure as:
        #   operation error STS: GetCallerIdentity, https response error
        #   StatusCode: 403, RequestID: ..., api error InvalidClientTokenId: ...
        ("AWS API rejected the credentials (HTTP 401/403)", r"StatusCode: 40[13]\b"),
        (
            "AWS credentials are invalid (InvalidClientTokenId)",
            r"\bInvalidClientTokenId\b",
        ),
        # [verified] ...api error InvalidClientTokenId: The security token
        #   included in the request is invalid.
        (
            "AWS security token is invalid or expired",
            r"security token included in the request is (invalid|expired)",
        ),
        # [expected] the rest of the AWS auth code family.
        (
            "AWS credentials are invalid (UnrecognizedClientException)",
            r"\bUnrecognizedClientException\b",
        ),
        ("AWS session token has expired", r"\bExpiredToken(Exception)?\b"),
        (
            "AWS request signature does not match the secret key",
            r"\bSignatureDoesNotMatch\b",
        ),
        ("AWS denied the request (AccessDenied)", r"\bAccessDenied(Exception)?\b"),
        ("AWS denied the request (AuthFailure)", r"\bAuthFailure\b"),
        (
            "AWS denied the request (UnauthorizedOperation)",
            r"\bUnauthorizedOperation\b",
        ),
        ("IAM policy does not allow this call", r"is not authorized to perform"),
        ("no AWS credentials were found", r"no valid credential sources"),
        # --- configuration / validation --------------------------------------
        # [verified] `terraform apply` with an unset root variable prints:
        #   Error: No value for required variable
        #   The root module input variable "needed" is not set, and has no
        #   default value.
        (
            "a required Terraform variable is not set",
            r"^Error: No value for required variable",
        ),
        (
            "a required Terraform variable is not set",
            r"root module input variable .* is not set",
        ),
        # [verified] a failing `validation {}` block prints:
        #   Error: Invalid value for variable
        #   ...This was checked by the validation rule at main.tf:4,3-13.
        ("a Terraform variable failed validation", r"^Error: Invalid value for "),
        (
            "a Terraform variable failed validation",
            r"was checked by the validation rule",
        ),
        # [expected] the rest of the terraform-core config diagnostics; all of
        # them are HCL/expression errors, none can clear on their own.
        (
            "invalid Terraform configuration",
            r"^Error: (Unsupported argument|Unsupported block type)",
        ),
        (
            "invalid Terraform configuration",
            r"^Error: (Unsupported attribute|Missing required argument)",
        ),
        (
            "invalid Terraform configuration",
            r"^Error: (Invalid function argument|Invalid index|Cycle:)",
        ),
        (
            "invalid Terraform configuration",
            r"^Error: (Reference to undeclared|Incorrect attribute value type)",
        ),
        (
            "invalid Terraform configuration",
            r"^Error: (Duplicate resource|Insufficient .* blocks)",
        ),
        # [expected] AWS/CC rejecting an argument value outright.
        (
            "a provider rejected an argument value",
            r"\bInvalidParameterValue(Exception)?\b",
        ),
        ("a provider rejected an argument value", r"\bValidation(Exception|Error)\b"),
        # --- collisions -------------------------------------------------------
        # [expected] re-running LAB SQL or a partially-applied lab against a
        # live environment ("table already exists", "model already exists").
        #
        # HTTP 409/Conflict is deliberately NOT here: Confluent Cloud also
        # returns it for "another operation is already in progress", which does
        # clear on its own. The prose and *AlreadyExists* forms below cover the
        # real collision without swallowing that transient case.
        ("the resource already exists", r"\balready exists\b"),
        ("the resource already exists", r"AlreadyExists"),
        ("the resource already exists", r"\bBucketAlreadyOwnedByYou\b"),
        (
            "the resource is already in Terraform state",
            r"^Error: Resource already managed by Terraform",
        ),
    )
)

# Transient failures — the network, a rate limiter, or a provider asking us to
# come back later. These are what APPLY_ATTEMPTS exists for.
_TRANSIENT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (label, re.compile(pattern, re.IGNORECASE | re.MULTILINE))
    for label, pattern in (
        # --- network / DNS / TLS ---------------------------------------------
        # [verified] pointing the AWS provider at an unresolvable endpoint gives:
        #   operation error STS: GetCallerIdentity, https response error
        #   StatusCode: 0, RequestID: , request send failed, Post "https://...":
        #   dial tcp: lookup sts....invalid: no such host
        ("DNS lookup failed", r"\bno such host\b"),
        ("the connection could not be established", r"\bdial tcp\b"),
        ("the request never reached the API", r"\brequest send failed\b"),
        # [expected] the standard Go net/http transport errors. "connection reset
        # by peer" is the one seen in practice (see APPLY_ATTEMPTS).
        ("the connection was reset", r"\bconnection reset by peer\b"),
        ("the connection was refused", r"\bconnection refused\b"),
        ("the connection dropped mid-request", r"(\bunexpected EOF\b|\bbroken pipe\b)"),
        ("the request timed out", r"(\bi/o timeout\b|\bTLS handshake timeout\b)"),
        ("the request timed out", r"\bcontext deadline exceeded\b"),
        (
            "the network was unreachable",
            r"(\bnetwork is unreachable\b|\bno route to host\b)",
        ),
        (
            "DNS lookup failed",
            r"(temporary failure in name resolution|server misbehaving)",
        ),
        # --- server-side / rate limiting --------------------------------------
        # [sdk] aws-sdk-go-v2 retries HTTP 500, 502, 503 and 504 by default; the
        # StatusCode: form is the verified AWS wire format.
        ("the API returned a 5xx", r"StatusCode: 5\d\d\b"),
        # [expected] the Confluent provider's "<status> <reason>: <body>" shape.
        (
            "the API returned a 5xx",
            r"\b50[0-4] (Internal Server Error|Bad Gateway|Service Unavailable|Gateway Time)",
        ),
        ("the API is rate limiting us", r"(StatusCode: 429\b|\bToo Many Requests\b)"),
        # [sdk] DefaultThrottleErrorCodes. LimitExceededException is on that list
        # even though AWS also uses it for hard quota exhaustion — we follow the
        # SDK and retry it; a real quota wall just costs the two sleeps.
        ("the API is throttling us", r"Throttl"),
        (
            "the API is throttling us",
            r"\b(RequestLimitExceeded|BandwidthLimitExceeded|LimitExceededException)\b",
        ),
        (
            "the API is throttling us",
            r"\b(ProvisionedThroughputExceededException|SlowDown)\b",
        ),
        (
            "a concurrent operation is in progress",
            r"\b(PriorRequestNotComplete|TransactionInProgressException)\b",
        ),
        (
            "a concurrent operation is in progress",
            r"\b(OperationAborted|ConcurrentModificationException)\b",
        ),
        # [sdk] DefaultRetryableErrorCodes.
        ("the request timed out", r"\bRequestTimeout(Exception)?\b"),
        # [expected] generic service-side failures and explicit "come back later".
        ("the service is unavailable", r"\bServiceUnavailable(Exception)?\b"),
        (
            "the service hit an internal error",
            r"\b(InternalError|InternalFailure|InternalServerError)\b",
        ),
        (
            "the service asked us to retry",
            r"(\btry again\b|\btemporarily unavailable\b)",
        ),
        # [expected] IAM role/policy propagation — the classic eventual-consistency
        # failure, and the reason MalformedPolicyDocument is NOT in the permanent
        # set above.
        ("IAM changes have not propagated yet", r"Invalid principal in policy"),
        # [expected] terraform-plugin-sdk's waiter giving up while a resource was
        # still converging; a re-apply usually finds it ready.
        (
            "a resource did not reach its target state in time",
            r"timeout while waiting for state to become",
        ),
    )
)


# The Confluent provider auto-names Flink statements `tf-<timestamp>-<uuid>` and
# can POST one twice (first POST lands, the response is lost, the retry gets 409).
# The statement exists server-side but is missing from state. That "already
# exists" is NOT a collision: the name is unique per attempt and the DDL is
# CREATE ... IF NOT EXISTS, so a re-apply submits a fresh statement and succeeds.
# Checked before the permanent table, which would otherwise match "already exists".
_ORPHANED_STATEMENT = re.compile(
    r'Statement with name "tf-[^"]*" already exists', re.IGNORECASE
)

_ANSI = re.compile(r"\x1b\[[0-9;]*m")
_GUTTER = re.compile(r"^[╷│╵][ \t]?", re.MULTILINE)
_WHITESPACE = re.compile(r"\s+")


def _normalise(output: str) -> tuple[str, str]:
    """
    Turn raw terraform stderr into the two forms the patterns are matched against.

    We do not pass `-no-color`, so what actually arrives is a coloured, boxed
    diagnostic — verified against terraform 1.15.8, every line prefixed with
    `\\x1b[31m│\\x1b[0m \\x1b[0m` and the summary split by resets:

        \\x1b[1m\\x1b[31mError: \\x1b[0m\\x1b[0m\\x1b[1mUnsupported argument\\x1b[0m

    Left alone, no `^Error:` pattern could ever match. So:

    - `lines` has the escapes and the `╷│╵` gutter removed, which is what the
      `^Error:` anchors need.
    - `flat` additionally collapses whitespace, because terraform hard-wraps
      diagnostic prose at ~78 columns and a phrase can straddle a line break.

    Every pattern is tried against both, so a match survives either.
    """
    lines = _GUTTER.sub("", _ANSI.sub("", output))
    return lines, _WHITESPACE.sub(" ", lines)


def classify_apply_failure(output: str) -> tuple[bool, str]:
    """
    Decide whether a failed terraform run is worth another attempt.

    Args:
        output: Terraform's diagnostic output (its stderr), colour codes and all.

    Returns:
        (retry, reason) — `reason` is a short human-readable label for the log.

    An error matching nothing defaults to **retryable**, which is what this
    function did for every error before it existed. An unrecognised provider
    error is more often a transient cloud hiccup than a config mistake, and the
    cost of guessing wrong here is two sleeps, where the opposite default would
    turn a recoverable blip into a failed deploy.
    """
    lines, flat = _normalise(output)
    if _ORPHANED_STATEMENT.search(lines) or _ORPHANED_STATEMENT.search(flat):
        return True, "an orphaned Flink statement (the re-apply is a no-op)"
    for label, pattern in _PERMANENT_PATTERNS:
        if pattern.search(lines) or pattern.search(flat):
            return False, label
    for label, pattern in _TRANSIENT_PATTERNS:
        if pattern.search(lines) or pattern.search(flat):
            return True, label
    return True, UNCLASSIFIED


def _run_capturing_stderr(cmd: list[str], cwd: Path) -> tuple[int, str]:
    """
    Run `cmd`, echoing its stderr through while keeping a copy to classify.

    Terraform sends progress ("confluent_kafka_topic.x: Creating...") to stdout and
    every diagnostic ("Error: ...") to stderr — verified against terraform
    1.15.8. So piping *only* stderr gets us the text to classify with none of
    the progress noise, leaves the live output the operator watches untouched,
    and keeps stdin inherited so an apply that prompts still works. One piped
    stream means reading it to EOF before `wait()` cannot deadlock.
    """
    proc = subprocess.Popen(cmd, cwd=cwd, stderr=subprocess.PIPE, text=True, bufsize=1)
    captured: list[str] = []
    if proc.stderr is not None:
        for line in proc.stderr:
            captured.append(line)
            sys.stderr.write(line)
            sys.stderr.flush()
        proc.stderr.close()
    return proc.wait(), "".join(captured)


def run_terraform(
    env_path: Path, auto_approve: bool = True, max_attempts: int = APPLY_ATTEMPTS
) -> bool:
    """
    Run terraform init and apply in the specified environment.

    Retries only transient failures. Terraform state is preserved on every
    failure path, so a retry (or a manual re-run) resumes rather than restarts.

    Args:
        env_path: Path to terraform directory
        auto_approve: Whether to auto-approve terraform apply (default: True)
        max_attempts: Total apply attempts before giving up (transient only)

    Returns:
        True if successful, False otherwise

    Raises:
        SystemExit: If terraform binary is not found
    """
    print(f"\nInitializing Terraform in {env_path}...")

    try:
        subprocess.run(["terraform", "init"], cwd=env_path, check=True)
    except subprocess.CalledProcessError:
        print(f"✗ Terraform init failed in {env_path.name}")
        return False
    except FileNotFoundError:
        print("Error: Terraform not found. Please install Terraform first.")
        sys.exit(1)

    apply_cmd = ["terraform", "apply"]
    if auto_approve:
        apply_cmd.append("-auto-approve")

    reason = UNCLASSIFIED
    for attempt in range(1, max_attempts + 1):
        suffix = f" (attempt {attempt}/{max_attempts})" if attempt > 1 else ""
        print(f"Running terraform apply in {env_path}...{suffix}")

        try:
            returncode, diagnostics = _run_capturing_stderr(apply_cmd, env_path)
        except FileNotFoundError:
            print("Error: Terraform not found. Please install Terraform first.")
            sys.exit(1)

        if returncode == 0:
            print(f"✓ Deployment successful: {env_path.name}")

            # Generate credentials markdown for Core deployments
            if env_path.name == "core":
                _generate_deployment_summary(env_path)

            return True

        retry, reason = classify_apply_failure(diagnostics)

        if not retry:
            print(f"\n✗ Terraform failed in {env_path.name} — {reason}.")
            print(
                "Not retrying: a re-apply would fail the same way. Terraform state is left"
            )
            print("in place. Fix the cause above, then re-run the same command.")
            return False

        if attempt < max_attempts:
            print(
                f"\nterraform apply failed in {env_path.name} — {reason} — retrying in "
                f"{RETRY_DELAY_SECONDS}s (state is kept, so the re-apply picks up where this left off)..."
            )
            time.sleep(RETRY_DELAY_SECONDS)

    print(
        f"✗ Terraform failed in {env_path.name} after {max_attempts} attempts — "
        f"last failure: {reason}"
    )
    print("Terraform state is left in place. Re-run the same command to resume.")
    return False


def _run_streaming(cmd: list[str], cwd: Path) -> tuple[int, str]:
    """Run a command, echoing output live and returning (returncode, output)."""
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    lines: list[str] = []
    assert proc.stdout is not None
    for line in proc.stdout:
        print(line, end="")
        lines.append(line)
    return proc.wait(), "".join(lines)


def _is_dead_flink_key(output: str) -> bool:
    return "401 Unauthorized" in output and "flink" in output.lower()


def _forget_flink_objects(env_path: Path) -> list[str]:
    """`terraform state rm` every Flink statement/connection; return what was removed."""
    listed = subprocess.run(
        ["terraform", "state", "list"],
        cwd=env_path,
        capture_output=True,
        text=True,
        check=False,
    )
    targets = [
        addr
        for addr in listed.stdout.splitlines()
        if "confluent_flink_statement." in addr or "confluent_flink_connection." in addr
    ]
    if targets:
        subprocess.run(["terraform", "state", "rm", *targets], cwd=env_path, check=True)
    return targets


def run_terraform_destroy(env_path: Path, auto_approve: bool = True) -> bool:
    """
    Run terraform destroy in the specified environment.

    Args:
        env_path: Path to terraform directory
        auto_approve: Whether to auto-approve terraform destroy (default: True)

    Returns:
        True if successful, False otherwise

    Raises:
        SystemExit: If terraform binary is not found
    """
    print(f"\nInitializing Terraform in {env_path}...")

    try:
        subprocess.run(["terraform", "init"], cwd=env_path, check=True)

        destroy_cmd = ["terraform", "destroy"]
        if auto_approve:
            destroy_cmd.append("-auto-approve")

        print(f"Running terraform destroy in {env_path}...")
        returncode, output = _run_streaming(destroy_cmd, env_path)

        if returncode != 0 and _is_dead_flink_key(output):
            # The Flink API key in state is already gone (e.g. an earlier partial
            # destroy deleted it), so refreshing/deleting Flink statements and
            # connections 401s forever. Those objects live inside the compute pool
            # and are removed with the environment, so forgetting them is safe.
            dropped = _forget_flink_objects(env_path)
            if dropped:
                print(
                    f"\nFlink API key is no longer valid (401). Removed {len(dropped)} Flink "
                    "statement/connection resource(s) from state — they are deleted with the "
                    "environment. Retrying destroy..."
                )
                returncode, output = _run_streaming(destroy_cmd, env_path)

        if returncode != 0:
            raise subprocess.CalledProcessError(returncode, destroy_cmd)

        print(f"✓ Destroy successful: {env_path.name}")

        # Clean up deployment summary for Core deployments
        if env_path.name == "core":
            _cleanup_deployment_summary(env_path)

        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ Terraform destroy failed in {env_path.name}")
        return False
    except FileNotFoundError:
        print("Error: Terraform not found. Please install Terraform first.")
        sys.exit(1)


def _generate_deployment_summary(env_path: Path) -> None:
    """
    Generate DEPLOYED_RESOURCES.md file after successful Core deployment.

    Args:
        env_path: Path to the terraform core directory (e.g., terraform/core)
    """
    try:
        # Get terraform outputs as JSON
        print("\nGenerating deployment summary...")
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=env_path,
            capture_output=True,
            text=True,
            check=True,
        )

        # Parse terraform outputs
        tf_outputs = json.loads(result.stdout)

        # Extract cloud_provider from terraform output, default to "aws"
        cloud_provider = "aws"
        if "cloud_provider" in tf_outputs:
            cloud_provider = (
                tf_outputs["cloud_provider"].get("value", "aws")
                if isinstance(tf_outputs["cloud_provider"], dict)
                else tf_outputs["cloud_provider"]
            )

        # Generate markdown file
        output_file = env_path / "DEPLOYED_RESOURCES.md"
        generate_credentials_markdown(cloud_provider, tf_outputs, output_file)

    except Exception as e:
        print(f"Warning: Failed to generate deployment summary: {e}")
        # Don't fail the deployment if summary generation fails


def _cleanup_deployment_summary(env_path: Path) -> None:
    """
    Delete DEPLOYED_RESOURCES.md file after successful Core destroy.

    Args:
        env_path: Path to the terraform core directory (e.g., terraform/core)
    """
    try:
        output_file = env_path / "DEPLOYED_RESOURCES.md"
        if output_file.exists():
            output_file.unlink()
            print(f"Removed {output_file}")
    except Exception as e:
        print(f"Warning: Failed to remove deployment summary: {e}")
