#!/usr/bin/env python3
"""
Standalone Bedrock credentials test script.

Tests whether AWS credentials can invoke the Claude Sonnet 4.5 model
used in workshop labs.

Usage:
    uv run test-bedrock --access-key AKIA... --secret-key xxx --region us-east-1

    # Or call from Python:
    from scripts.common.test_bedrock_credentials import test_bedrock_credentials
    success = test_bedrock_credentials(access_key_id, secret_access_key, region)
"""

import argparse
import json
import logging
import sys
from typing import Optional

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


def get_model_id(region: str) -> str:
    """
    Get the Claude Sonnet 4.5 model ID for the given region.

    Model ID pattern from aws/core/main.tf:311:
    ${model_prefix}.anthropic.claude-sonnet-4-5-20250929-v1:0

    Args:
        region: AWS region (e.g., 'us-east-1')

    Returns:
        Model ID for the region
    """
    if region.startswith('us-'):
        prefix = 'us'
    elif region.startswith('eu-'):
        prefix = 'eu'
    else:
        prefix = 'apac'

    return f"{prefix}.anthropic.claude-sonnet-4-5-20250929-v1:0"


def test_bedrock_credentials(
    access_key_id: str,
    secret_access_key: str,
    region: str,
    logger: Optional[logging.Logger] = None
) -> bool:
    """
    Test if credentials can invoke Claude Sonnet 4.5 on Bedrock.

    Args:
        access_key_id: AWS access key ID
        secret_access_key: AWS secret access key
        region: AWS region
        logger: Optional logger instance

    Returns:
        True if test succeeded, False otherwise
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    if not BOTO3_AVAILABLE:
        logger.error("boto3 is not installed - cannot test Bedrock access")
        return False

    try:
        model_id = get_model_id(region)

        logger.info(f"Testing credentials in region: {region}")
        logger.info(f"Model: {model_id}")

        # Create Bedrock Runtime client
        bedrock_client = boto3.client(
            'bedrock-runtime',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region
        )

        # Minimal test message
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 10,
            "messages": [
                {
                    "role": "user",
                    "content": "Say 'test'"
                }
            ]
        }

        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )

        response_body = json.loads(response['body'].read())

        logger.info("✓ Bedrock access test passed!")
        logger.debug(f"Model response: {response_body.get('content', [{}])[0].get('text', 'N/A')}")

        return True

    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']

        logger.error(f"✗ Bedrock test failed: {error_code}")
        logger.debug(f"Error details: {error_msg}")

        if error_code == 'UnrecognizedClientException':
            logger.warning("Credentials may be invalid or haven't propagated yet (wait 30-60s)")
        elif error_code == 'ResourceNotFoundException':
            logger.warning(f"Model '{model_id}' not available in region {region}")
            logger.warning("You may need to enable Claude models in AWS Bedrock console")
        elif error_code == 'AccessDeniedException':
            logger.warning("Credentials lack bedrock:InvokeModel permission")

        return False

    except Exception as e:
        logger.error(f"✗ Unexpected error: {e}")
        return False


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Test AWS Bedrock credentials with Claude Sonnet 4.5 (us-east-1)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test workshop credentials
  %(prog)s --access-key AKIA... --secret-key xxx

  # Test with verbose output
  %(prog)s --access-key AKIA... --secret-key xxx --verbose

Note: Workshop mode always uses us-east-1 region
        """
    )

    parser.add_argument(
        '--access-key',
        required=True,
        help='AWS access key ID'
    )
    parser.add_argument(
        '--secret-key',
        required=True,
        help='AWS secret access key'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    # Workshop mode always uses us-east-1
    region = 'us-east-1'

    # Test credentials
    success = test_bedrock_credentials(
        args.access_key,
        args.secret_key,
        region,
        logger
    )

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
