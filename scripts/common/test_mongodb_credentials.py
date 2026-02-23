#!/usr/bin/env python3
"""
Test MongoDB connection credentials.

Tests user-provided MongoDB connection string and credentials,
or verifies access to the pre-populated workshop MongoDB instances.

Usage:
    uv run test-mongodb-creds --connection-string mongodb+srv://... --username user --password pass
    uv run test-mongodb-creds --workshop --lab lab2 --cloud aws

    # Or call from Python:
    from scripts.common.test_mongodb_credentials import test_mongodb_connection, test_workshop_mongodb
    ok, error_type = test_mongodb_connection(conn_str, username, password)
    ok, error_type = test_workshop_mongodb("lab2", "aws")

Error types returned:
    None                  - success
    "invalid_credentials" - authentication failed
    "connection_failed"   - could not reach the host
    "no_pymongo"          - pymongo not installed
    "error"               - unexpected error
"""

import argparse
import logging
import sys
import urllib.parse
from typing import Optional, Tuple

try:
    from pymongo import MongoClient
    from pymongo.errors import ConfigurationError, ConnectionFailure, OperationFailure
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False


# Pre-populated workshop MongoDB instances (read-only demo data managed by Confluent).
# Used when the user has not provided their own MongoDB credentials.
WORKSHOP_MONGODB = {
    "lab2": {
        "aws": {
            "connection_string": "mongodb+srv://cluster0.c79vrkg.mongodb.net/",
            "username": "workshop-user",
            "password": "xr6PvJl9xZz1uoKa",
        },
        "azure": {
            "connection_string": "mongodb+srv://cluster0.xhgx1kr.mongodb.net/",
            "username": "public_readonly_user",
            "password": "sB948mVgIYqwUloX",
        },
    },
    "lab3": {
        "aws": {
            "connection_string": "mongodb+srv://cluster0.w9n3o45.mongodb.net/",
            "username": "workshop-user",
            "password": "JHcZajJzWYwKe6dt",
        },
        "azure": {
            "connection_string": "mongodb+srv://cluster0.iir6woe.mongodb.net/",
            "username": "public_readonly_user",
            "password": "pE7xOkiKth2QqTKL",
        },
    },
    "lab4": {
        "aws": {
            "connection_string": "mongodb+srv://cluster0.rgtlalv.mongodb.net/",
            "username": "workshop-user",
            "password": "DGaR5XjgdMZTigMr",
        },
    },
}


def test_mongodb_connection(
    connection_string: str,
    username: str,
    password: str,
    logger: Optional[logging.Logger] = None,
    timeout_ms: int = 8000,
) -> Tuple[bool, Optional[str]]:
    """
    Test if credentials can connect to MongoDB (ping only, no data checks).

    Returns:
        (True, None) on success, or (False, error_type) on failure.
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    if not PYMONGO_AVAILABLE:
        logger.error("pymongo is not installed — cannot test MongoDB connection")
        return False, "no_pymongo"

    if username and password:
        enc_user = urllib.parse.quote_plus(username)
        enc_pass = urllib.parse.quote_plus(password)
        if "mongodb+srv://" in connection_string:
            uri = connection_string.replace("mongodb+srv://", f"mongodb+srv://{enc_user}:{enc_pass}@")
        else:
            uri = connection_string.replace("mongodb://", f"mongodb://{enc_user}:{enc_pass}@")
    else:
        uri = connection_string

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=timeout_ms)
        client.admin.command("ping")
        client.close()
        logger.info("✓ MongoDB connection successful")
        return True, None

    except OperationFailure as e:
        code = getattr(e, "code", None)
        if code in (18, 8000):
            logger.debug(f"MongoDB authentication failed: {e}")
            return False, "invalid_credentials"
        logger.debug(f"MongoDB operation failed: {e}")
        return False, "connection_failed"

    except (ConnectionFailure, ConfigurationError) as e:
        logger.debug(f"MongoDB connection failed: {e}")
        return False, "connection_failed"

    except Exception as e:
        logger.debug(f"Unexpected MongoDB error: {e}")
        return False, "error"


def test_workshop_mongodb(
    lab: str,
    cloud: str,
    logger: Optional[logging.Logger] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Test connectivity to the pre-populated workshop MongoDB instance for a given lab/cloud.

    Returns:
        (True, None) on success, or (False, error_type) on failure.
        Returns (False, "no_config") if no workshop default exists for this lab/cloud.
    """
    config = WORKSHOP_MONGODB.get(lab, {}).get(cloud)
    if not config:
        return False, "no_config"

    return test_mongodb_connection(
        config["connection_string"],
        config["username"],
        config["password"],
        logger=logger,
        timeout_ms=8000,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Test MongoDB connection credentials",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test user-provided credentials
  %(prog)s --connection-string mongodb+srv://cluster0.xxx.mongodb.net/ --username user --password pass

  # Test workshop demo data connectivity
  %(prog)s --workshop --lab lab2 --cloud aws
        """,
    )
    parser.add_argument("--connection-string", help="MongoDB connection string")
    parser.add_argument("--username", default="", help="MongoDB username")
    parser.add_argument("--password", default="", help="MongoDB password")
    parser.add_argument("--workshop", action="store_true",
                        help="Test the pre-populated workshop credentials instead")
    parser.add_argument("--lab", choices=["lab2", "lab3", "lab4"], default="lab2",
                        help="Lab to test (--workshop mode only)")
    parser.add_argument("--cloud", choices=["aws", "azure"], default="aws",
                        help="Cloud provider (--workshop mode only)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)

    if args.workshop:
        ok, err = test_workshop_mongodb(args.lab, args.cloud, logger)
    elif args.connection_string:
        ok, err = test_mongodb_connection(
            args.connection_string, args.username, args.password, logger
        )
    else:
        parser.error("Provide --connection-string or use --workshop")
        return

    if ok:
        print("\n✓ MongoDB connection successful.")
        sys.exit(0)
    else:
        print(f"\n✗ MongoDB connection failed: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
