#!/usr/bin/env python3
"""
Standalone Azure OpenAI credentials test script.

Tests whether Azure OpenAI credentials can invoke the gpt-5-mini and
text-embedding-ada-002 models used in workshop labs.

Usage:
    uv run test-azure-openai --endpoint https://xxx.openai.azure.com/ --api-key xxx

    # Or call from Python:
    from scripts.common.test_azure_openai_credentials import (
        test_azure_openai_chat,
        test_azure_openai_embeddings,
        test_azure_openai_credentials,
    )
    ok, error_type = test_azure_openai_chat(endpoint, api_key)
    ok, error_type = test_azure_openai_embeddings(endpoint, api_key)

Error types returned:
    None                    - success
    "invalid_credentials"   - 401 Unauthorized
    "deployment_not_found"  - 404 (deployment name not found in this resource)
    "no_requests"           - requests library not installed
    "error"                 - unexpected error
"""

import argparse
import logging
import sys
import time
from typing import Optional, Tuple

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

_API_VERSION = "2024-08-01-preview"


def _ensure_trailing_slash(endpoint: str) -> str:
    return endpoint if endpoint.endswith("/") else endpoint + "/"


def _invoke_azure(
    url: str,
    headers: dict,
    payload: dict,
    label: str,
    logger: logging.Logger,
    max_retries: int,
    retry_delay: int,
) -> Tuple[bool, Optional[str]]:
    """Shared HTTP POST loop. Returns (success, error_type)."""
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                wait = retry_delay * (2 ** (attempt - 1))
                logger.info(f"Waiting {wait}s before retry (attempt {attempt + 1}/{max_retries})...")
                time.sleep(wait)

            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                logger.info(f"✓ {label} accessible")
                return True, None

            if response.status_code == 401:
                logger.debug(f"{label} returned 401 Unauthorized")
                return False, "invalid_credentials"

            if response.status_code == 404:
                logger.debug(f"{label} returned 404 — deployment not found")
                return False, "deployment_not_found"

            # Retry on 400/429 (rate limit / not-yet-ready)
            if response.status_code in (400, 429) and attempt < max_retries - 1:
                logger.warning(f"{label} not ready (HTTP {response.status_code}), will retry...")
                continue

            logger.debug(f"{label} returned unexpected HTTP {response.status_code}: {response.text[:200]}")
            return False, "error"

        except Exception as e:
            logger.debug(f"{label} request failed: {e}")
            return False, "error"

    return False, "error"


def test_azure_openai_chat(
    endpoint: str,
    api_key: str,
    logger: Optional[logging.Logger] = None,
    max_retries: int = 2,
    retry_delay: int = 5,
) -> Tuple[bool, Optional[str]]:
    """
    Test chat completions endpoint (gpt-5-mini deployment).

    Returns:
        (True, None) on success, or (False, error_type) on failure.
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    if not REQUESTS_AVAILABLE:
        return False, "no_requests"

    endpoint = _ensure_trailing_slash(endpoint)
    url = f"{endpoint}openai/deployments/gpt-5-mini/chat/completions?api-version={_API_VERSION}"
    headers = {"api-key": api_key, "Content-Type": "application/json"}
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'test'"},
        ],
        "max_completion_tokens": 10,
    }

    return _invoke_azure(url, headers, payload, "gpt-5-mini", logger, max_retries, retry_delay)


def test_azure_openai_embeddings(
    endpoint: str,
    api_key: str,
    logger: Optional[logging.Logger] = None,
    max_retries: int = 2,
    retry_delay: int = 5,
) -> Tuple[bool, Optional[str]]:
    """
    Test embeddings endpoint (text-embedding-ada-002 deployment).

    Returns:
        (True, None) on success, or (False, error_type) on failure.
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    if not REQUESTS_AVAILABLE:
        return False, "no_requests"

    endpoint = _ensure_trailing_slash(endpoint)
    url = f"{endpoint}openai/deployments/text-embedding-ada-002/embeddings?api-version={_API_VERSION}"
    headers = {"api-key": api_key, "Content-Type": "application/json"}
    payload = {"input": "test"}

    return _invoke_azure(url, headers, payload, "text-embedding-ada-002", logger, max_retries, retry_delay)


def test_azure_openai_credentials(
    endpoint: str,
    api_key: str,
    logger: Optional[logging.Logger] = None,
    max_retries: int = 2,
    retry_delay: int = 5,
) -> Tuple[bool, Optional[str]]:
    """
    Test both gpt-5-mini and text-embedding-ada-002. Returns on first failure.

    Returns:
        (True, None) if both pass, or (False, error_type) on first failure.
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    chat_ok, chat_err = test_azure_openai_chat(endpoint, api_key, logger, max_retries, retry_delay)
    if not chat_ok:
        return False, chat_err

    emb_ok, emb_err = test_azure_openai_embeddings(endpoint, api_key, logger, max_retries, retry_delay)
    if not emb_ok:
        return False, emb_err

    return True, None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Test Azure OpenAI credentials (gpt-5-mini + text-embedding-ada-002)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --endpoint https://workshop-openai-abc123.openai.azure.com/ --api-key xxx
  %(prog)s --endpoint https://workshop-openai-abc123.openai.azure.com/ --api-key xxx --verbose
        """,
    )
    parser.add_argument("--endpoint", required=True, help="Azure OpenAI endpoint URL")
    parser.add_argument("--api-key", required=True, help="Azure OpenAI API key")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)

    chat_ok, chat_err = test_azure_openai_chat(args.endpoint, args.api_key, logger)
    emb_ok, emb_err = test_azure_openai_embeddings(args.endpoint, args.api_key, logger)

    if chat_ok and emb_ok:
        print("\n✓ All Azure OpenAI checks passed.")
        sys.exit(0)
    else:
        if not chat_ok:
            print(f"\n✗ gpt-5-mini check failed: {chat_err}")
        if not emb_ok:
            print(f"\n✗ text-embedding-ada-002 check failed: {emb_err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
