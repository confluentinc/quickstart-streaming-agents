#!/usr/bin/env python3
"""
Test Azure CosmosDB connectivity for the workshop demo endpoint.

The CosmosDB endpoint and API key used in Lab4 are hardcoded read-only demo
credentials managed by the Confluent workshop team. This script verifies that
the demo database is reachable and the credentials remain valid.

Usage:
    uv run test-cosmosdb
    uv run test-cosmosdb --verbose

    # Or call from Python:
    from scripts.common.test_cosmosdb_credentials import test_cosmosdb_access
    ok, error_type = test_cosmosdb_access()

Error types returned:
    None                  - success
    "unreachable"         - network/timeout error, host not reachable
    "invalid_credentials" - 401/403 from the server
    "no_requests"         - requests library not installed
    "error"               - unexpected error
"""

import argparse
import base64
import hashlib
import hmac
import logging
import sys
import urllib.parse
from email.utils import formatdate
from typing import Optional, Tuple

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Hardcoded workshop CosmosDB credentials (read-only demo data for Lab4).
# These are managed by the Confluent workshop team and shared for all attendees.
WORKSHOP_COSMOSDB_ENDPOINT = "https://fema-iappg.documents.azure.com:443/"
WORKSHOP_COSMOSDB_API_KEY = (
    "KjJPts0iGXwxQhTuoOiH8FnXd8gDve3nAl5Yt1ibEEH8EL63Jyl0H14lGWieIExBD"
    "Cxo7aPErOs3ACDbYRZ1hw=="
)


def _make_auth_header(master_key: str, verb: str, resource_type: str, resource_id: str, date: str) -> str:
    """Generate a CosmosDB master-key authorization header value."""
    key_bytes = base64.b64decode(master_key)
    string_to_sign = f"{verb.lower()}\n{resource_type.lower()}\n{resource_id}\n{date.lower()}\n\n"
    digest = hmac.new(key_bytes, string_to_sign.encode("utf-8"), hashlib.sha256).digest()
    signature = base64.b64encode(digest).decode("utf-8")
    return urllib.parse.quote(f"type=master&ver=1.0&sig={signature}")


def test_cosmosdb_access(
    endpoint: Optional[str] = None,
    api_key: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
    timeout: int = 15,
) -> Tuple[bool, Optional[str]]:
    """
    Test connectivity to the CosmosDB workshop demo endpoint.

    Uses the hardcoded workshop credentials by default. Pass endpoint and
    api_key to override with custom credentials.

    Returns:
        (True, None) on success, or (False, error_type) on failure.
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    if not REQUESTS_AVAILABLE:
        logger.error("requests library is not installed — cannot test CosmosDB access")
        return False, "no_requests"

    endpoint = (endpoint or WORKSHOP_COSMOSDB_ENDPOINT).rstrip("/") + "/"
    api_key = api_key or WORKSHOP_COSMOSDB_API_KEY

    date_str = formatdate(usegmt=True)
    auth = _make_auth_header(api_key, "get", "dbs", "", date_str)

    headers = {
        "Authorization": auth,
        "x-ms-date": date_str,
        "x-ms-version": "2018-12-31",
        "Accept": "application/json",
    }

    try:
        response = requests.get(f"{endpoint}dbs", headers=headers, timeout=timeout)

        if response.status_code == 200:
            logger.info("✓ CosmosDB demo data is reachable and credentials are valid")
            return True, None
        elif response.status_code in (401, 403):
            logger.debug(f"CosmosDB authentication failed: HTTP {response.status_code}")
            return False, "invalid_credentials"
        else:
            logger.debug(f"CosmosDB returned unexpected status: {response.status_code}")
            return False, "error"

    except requests.exceptions.ConnectionError as e:
        logger.debug(f"Could not connect to CosmosDB endpoint: {e}")
        return False, "unreachable"
    except requests.exceptions.Timeout:
        logger.debug("CosmosDB connection timed out")
        return False, "unreachable"
    except Exception as e:
        logger.debug(f"Unexpected error testing CosmosDB: {e}")
        return False, "error"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Test connectivity to the CosmosDB workshop demo endpoint (Lab4)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  %(prog)s
  %(prog)s --verbose
        """,
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)

    ok, err = test_cosmosdb_access(logger=logger)
    if ok:
        print("\n✓ CosmosDB workshop demo data is accessible.")
        sys.exit(0)
    else:
        print(f"\n✗ CosmosDB check failed: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
