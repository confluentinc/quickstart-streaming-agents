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
from typing import Optional

try:
    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import HttpResponseError
    AZURE_INFERENCE_AVAILABLE = True
except ImportError:
    AZURE_INFERENCE_AVAILABLE = False


def test_azure_openai_credentials(
    endpoint: str,
    api_key: str,
    logger: Optional[logging.Logger] = None
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

    Returns:
        True if both tests succeeded, False otherwise
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    if not AZURE_INFERENCE_AVAILABLE:
        logger.error("azure-ai-inference is not installed - cannot test Azure OpenAI access")
        return False

    # Ensure endpoint ends with /
    if not endpoint.endswith('/'):
        endpoint = endpoint + '/'

    success = True

    # Test 1: Chat completions with gpt-5-mini
    try:
        logger.info("Testing chat completions (gpt-5-mini)...")

        # Use the azure-ai-inference SDK for testing
        # Note: We need to construct the deployment-specific endpoint
        chat_endpoint = f"{endpoint}openai/deployments/gpt-5-mini"

        client = ChatCompletionsClient(
            endpoint=chat_endpoint,
            credential=AzureKeyCredential(api_key)
        )

        response = client.complete(
            messages=[
                SystemMessage(content="You are a helpful assistant."),
                UserMessage(content="Say 'test'")
            ],
            max_tokens=10
        )

        if response and response.choices:
            logger.info("✓ Chat completions test passed (gpt-5-mini)")
            logger.debug(f"Response: {response.choices[0].message.content}")
        else:
            logger.error("✗ Chat completions test failed: empty response")
            success = False

    except HttpResponseError as e:
        logger.error(f"✗ Chat completions test failed: {e.status_code}")
        logger.debug(f"Error details: {e.message}")

        if e.status_code == 401:
            logger.warning("Invalid API key or endpoint")
        elif e.status_code == 404:
            logger.warning("Deployment 'gpt-5-mini' not found - ensure it exists")
        elif e.status_code == 429:
            logger.warning("Rate limit exceeded - deployments may still be initializing")

        success = False

    except Exception as e:
        logger.error(f"✗ Chat completions test failed: {e}")
        success = False

    # Test 2: Embeddings with text-embedding-ada-002
    try:
        logger.info("Testing embeddings (text-embedding-ada-002)...")

        # For embeddings, we need to use the REST API directly
        # as azure-ai-inference doesn't have a dedicated embeddings client yet
        import requests

        embeddings_url = f"{endpoint}openai/deployments/text-embedding-ada-002/embeddings?api-version=2024-08-01-preview"

        headers = {
            "api-key": api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "input": "test embedding"
        }

        response = requests.post(embeddings_url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()
            if data.get('data') and len(data['data']) > 0:
                logger.info("✓ Embeddings test passed (text-embedding-ada-002)")
                logger.debug(f"Embedding dimensions: {len(data['data'][0].get('embedding', []))}")
            else:
                logger.error("✗ Embeddings test failed: empty response")
                success = False
        else:
            logger.error(f"✗ Embeddings test failed: {response.status_code}")
            logger.debug(f"Error details: {response.text}")

            if response.status_code == 401:
                logger.warning("Invalid API key or endpoint")
            elif response.status_code == 404:
                logger.warning("Deployment 'text-embedding-ada-002' not found - ensure it exists")
            elif response.status_code == 429:
                logger.warning("Rate limit exceeded - deployments may still be initializing")

            success = False

    except Exception as e:
        logger.error(f"✗ Embeddings test failed: {e}")
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
