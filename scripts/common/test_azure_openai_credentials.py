#!/usr/bin/env python3
"""
Standalone Azure OpenAI credentials test script.

Tests whether Azure OpenAI credentials can invoke the gpt-5-mini and
text-embedding-ada-002 models used in workshop labs.

Usage:
    uv run test-azure-openai --endpoint https://xxx.openai.azure.com/ --api-key xxx

    # Or call from Python:
    from scripts.common.test_azure_openai_credentials import test_azure_openai_credentials
    success = test_azure_openai_credentials(endpoint, api_key, logger)
"""

import argparse
import logging
import sys
import time
from typing import Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


def test_azure_openai_credentials(
    endpoint: str,
    api_key: str,
    logger: Optional[logging.Logger] = None,
    max_retries: int = 3,
    retry_delay: int = 5
) -> bool:
    """
    Test if credentials can invoke Azure OpenAI models.

    Tests both:
    1. Chat completions (gpt-5-mini)
    2. Embeddings (text-embedding-ada-002)

    Args:
        endpoint: Azure OpenAI endpoint URL
        api_key: Azure OpenAI API key
        logger: Optional logger instance
        max_retries: Maximum number of retry attempts (default: 3)
        retry_delay: Initial delay between retries in seconds (default: 5)

    Returns:
        True if both tests succeeded, False otherwise
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    if not REQUESTS_AVAILABLE:
        logger.error("requests library is not installed - cannot test Azure OpenAI access")
        return False

    # Ensure endpoint ends with /
    if not endpoint.endswith('/'):
        endpoint = endpoint + '/'

    success = True

    # Test 1: Chat completions with gpt-5-mini
    logger.info("Testing chat completions (gpt-5-mini)...")

    chat_url = f"{endpoint}openai/deployments/gpt-5-mini/chat/completions?api-version=2024-08-01-preview"

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'test'"}
        ],
        "max_completion_tokens": 10
    }

    chat_success = False
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                wait_time = retry_delay * (2 ** (attempt - 1))
                logger.info(f"Waiting {wait_time}s for deployment to be ready (attempt {attempt + 1}/{max_retries})...")
                time.sleep(wait_time)

            response = requests.post(chat_url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if data.get('choices') and len(data['choices']) > 0:
                    logger.info("✓ Chat completions test passed (gpt-5-mini)")
                    logger.debug(f"Response: {data['choices'][0].get('message', {}).get('content', 'N/A')}")
                    chat_success = True
                    break
                else:
                    logger.error("✗ Chat completions test failed: empty response")
                    break
            else:
                # Retry on certain errors (deployment not ready)
                # Include 401 as newly created deployments may temporarily return this during propagation
                if response.status_code in [400, 401, 429] and attempt < max_retries - 1:
                    logger.warning(f"Chat completions not ready (HTTP {response.status_code}), will retry...")
                    continue

                logger.error(f"✗ Chat completions test failed: {response.status_code}")
                logger.debug(f"Error details: {response.text}")

                if response.status_code == 401:
                    logger.warning("Invalid API key or endpoint (or deployment not fully propagated)")
                elif response.status_code == 404:
                    logger.warning("Deployment 'gpt-5-mini' not found - ensure it exists")
                elif response.status_code == 429:
                    logger.warning("Rate limit exceeded - deployments may still be initializing")
                elif response.status_code == 400:
                    logger.warning("Bad request - deployment may not be fully initialized")

                break

        except Exception as e:
            logger.error(f"✗ Chat completions test failed: {e}")
            break

    if not chat_success:
        success = False

    # Test 2: Embeddings with text-embedding-ada-002
    logger.info("Testing embeddings (text-embedding-ada-002)...")

    embeddings_url = f"{endpoint}openai/deployments/text-embedding-ada-002/embeddings?api-version=2024-08-01-preview"

    payload = {
        "input": "test embedding"
    }

    embeddings_success = False
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                wait_time = retry_delay * (2 ** (attempt - 1))
                logger.info(f"Waiting {wait_time}s for deployment to be ready (attempt {attempt + 1}/{max_retries})...")
                time.sleep(wait_time)

            response = requests.post(embeddings_url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    logger.info("✓ Embeddings test passed (text-embedding-ada-002)")
                    logger.debug(f"Embedding dimensions: {len(data['data'][0].get('embedding', []))}")
                    embeddings_success = True
                    break
                else:
                    logger.error("✗ Embeddings test failed: empty response")
                    break
            else:
                # Retry on certain errors (deployment not ready)
                # Include 401 as newly created deployments may temporarily return this during propagation
                if response.status_code in [400, 401, 429] and attempt < max_retries - 1:
                    logger.warning(f"Embeddings not ready (HTTP {response.status_code}), will retry...")
                    continue

                logger.error(f"✗ Embeddings test failed: {response.status_code}")
                logger.debug(f"Error details: {response.text}")

                if response.status_code == 401:
                    logger.warning("Invalid API key or endpoint (or deployment not fully propagated)")
                elif response.status_code == 404:
                    logger.warning("Deployment 'text-embedding-ada-002' not found - ensure it exists")
                elif response.status_code == 429:
                    logger.warning("Rate limit exceeded - deployments may still be initializing")
                elif response.status_code == 400:
                    logger.warning("Bad request - deployment may not be fully initialized")

                break

        except Exception as e:
            logger.error(f"✗ Embeddings test failed: {e}")
            break

    if not embeddings_success:
        success = False

    if success:
        logger.info("✓ All Azure OpenAI tests passed!")
    else:
        logger.warning("⚠ Some Azure OpenAI tests failed")

    return success


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Test Azure OpenAI credentials with gpt-5-mini and text-embedding-ada-002",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test workshop credentials
  %(prog)s --endpoint https://workshop-openai-abc123.openai.azure.com/ --api-key xxx

  # Test with verbose output
  %(prog)s --endpoint https://workshop-openai-abc123.openai.azure.com/ --api-key xxx --verbose
        """
    )

    parser.add_argument(
        '--endpoint',
        required=True,
        help='Azure OpenAI endpoint URL'
    )
    parser.add_argument(
        '--api-key',
        required=True,
        help='Azure OpenAI API key'
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

    # Test credentials
    success = test_azure_openai_credentials(
        args.endpoint,
        args.api_key,
        logger
    )

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
