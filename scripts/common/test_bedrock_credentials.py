#!/usr/bin/env python3
"""
Standalone Bedrock credentials test script.

Tests whether AWS credentials can invoke the Claude Sonnet 4.5 model
and the Titan Embed Text v1 model used in workshop labs.

Usage:
    uv run test-bedrock --access-key AKIA... --secret-key xxx --region us-east-1

    # Or call from Python:
    from scripts.common.test_bedrock_credentials import test_bedrock_credentials, test_titan_embeddings
    ok, error_type = test_bedrock_credentials(access_key_id, secret_access_key, region)
    ok, error_type = test_titan_embeddings(access_key_id, secret_access_key, region)

Error types returned:
    None                - success
    "invalid_keys"      - credentials not recognized by AWS
    "model_not_enabled" - credentials valid but model not enabled in this region
    "permission_denied" - credentials valid but lack bedrock:InvokeModel permission
    "no_boto3"          - boto3 not installed
    "error"             - unexpected error
"""

import argparse
import json
import logging
import sys
import time
from typing import Optional, Tuple

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

# Titan Embeddings model ID (no region prefix)
TITAN_EMBED_MODEL_ID = "amazon.titan-embed-text-v1"


def get_sonnet_model_id(region: str) -> str:
    """Get the Claude Sonnet 4.5 model ID for the given region."""
    if region.startswith('us-'):
        prefix = 'us'
    elif region.startswith('eu-'):
        prefix = 'eu'
    else:
        prefix = 'apac'
    return f"{prefix}.anthropic.claude-sonnet-4-5-20250929-v1:0"


def _invoke_model(
    bedrock_client,
    model_id: str,
    request_body: dict,
    logger: logging.Logger,
    max_retries: int,
    retry_delay: int,
) -> Tuple[bool, Optional[str]]:
    """
    Shared invoke loop. Returns (success, error_type).
    error_type is None on success, otherwise one of the documented strings.
    """
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                wait_time = retry_delay * (2 ** (attempt - 1))
                logger.info(f"Waiting {wait_time}s before retry (attempt {attempt + 1}/{max_retries})...")
                time.sleep(wait_time)

            response = bedrock_client.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body),
            )
            response['body'].read()  # consume the stream
            return True, None

        except ClientError as e:
            error_code = e.response['Error']['Code']

            if error_code == 'UnrecognizedClientException' and attempt < max_retries - 1:
                logger.warning(f"Credentials not yet recognized (attempt {attempt + 1}/{max_retries})")
                continue

            logger.debug(f"Bedrock error for {model_id}: {error_code} — {e.response['Error']['Message']}")

            if error_code == 'UnrecognizedClientException':
                return False, "invalid_keys"
            elif error_code in ('ResourceNotFoundException', 'ValidationException'):
                return False, "model_not_enabled"
            elif error_code == 'AccessDeniedException':
                return False, "model_not_enabled"
            else:
                return False, "error"

        except Exception as e:
            logger.debug(f"Unexpected error invoking {model_id}: {e}")
            return False, "error"

    return False, "invalid_keys"


def test_bedrock_credentials(
    access_key_id: str,
    secret_access_key: str,
    region: str,
    logger: Optional[logging.Logger] = None,
    max_retries: int = 3,
    retry_delay: int = 5,
) -> Tuple[bool, Optional[str]]:
    """
    Test if credentials can invoke Claude Sonnet 4.5 on Bedrock.

    Returns:
        (True, None) on success, or (False, error_type) on failure.
        error_type is one of: "invalid_keys", "model_not_enabled",
        "permission_denied", "no_boto3", "error"
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    if not BOTO3_AVAILABLE:
        logger.error("boto3 is not installed — cannot test Bedrock access")
        return False, "no_boto3"

    model_id = get_sonnet_model_id(region)
    logger.info(f"Testing Claude Sonnet 4.5 ({model_id}) in {region}")

    client = boto3.client(
        'bedrock-runtime',
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=region,
    )

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "Say 'test'"}],
    }

    ok, error_type = _invoke_model(client, model_id, body, logger, max_retries, retry_delay)
    if ok:
        logger.info("✓ Claude Sonnet 4.5 access confirmed")
    return ok, error_type


def test_titan_embeddings(
    access_key_id: str,
    secret_access_key: str,
    region: str,
    logger: Optional[logging.Logger] = None,
    max_retries: int = 1,
    retry_delay: int = 5,
) -> Tuple[bool, Optional[str]]:
    """
    Test if credentials can invoke the Titan Embed Text v1 model on Bedrock.

    Returns:
        (True, None) on success, or (False, error_type) on failure.
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    if not BOTO3_AVAILABLE:
        logger.error("boto3 is not installed — cannot test Bedrock access")
        return False, "no_boto3"

    logger.info(f"Testing Titan Embeddings ({TITAN_EMBED_MODEL_ID}) in {region}")

    client = boto3.client(
        'bedrock-runtime',
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=region,
    )

    body = {"inputText": "test"}

    ok, error_type = _invoke_model(client, TITAN_EMBED_MODEL_ID, body, logger, max_retries, retry_delay)
    if ok:
        logger.info("✓ Titan Embeddings access confirmed")
    return ok, error_type


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Test AWS Bedrock credentials (Claude Sonnet 4.5 + Titan Embeddings)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --access-key AKIA... --secret-key xxx
  %(prog)s --access-key AKIA... --secret-key xxx --region eu-west-1 --verbose
        """
    )
    parser.add_argument('--access-key', required=True, help='AWS access key ID')
    parser.add_argument('--secret-key', required=True, help='AWS secret access key')
    parser.add_argument('--region', default='us-east-1', help='AWS region (default: us-east-1)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)

    sonnet_ok, sonnet_err = test_bedrock_credentials(
        args.access_key, args.secret_key, args.region, logger
    )
    titan_ok, titan_err = test_titan_embeddings(
        args.access_key, args.secret_key, args.region, logger
    )

    if sonnet_ok and titan_ok:
        print("\n✓ All Bedrock credential checks passed.")
        sys.exit(0)
    else:
        if not sonnet_ok:
            print(f"\n✗ Claude Sonnet 4.5 check failed: {sonnet_err}")
        if not titan_ok:
            print(f"\n✗ Titan Embeddings check failed: {titan_err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
