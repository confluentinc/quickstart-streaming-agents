#!/usr/bin/env python3
"""
Validate MongoDB and Zapier configurations before deployment.

Performs soft validation checks to ensure MongoDB Atlas and Zapier MCP Server
are configured correctly. Never fails deployment - only warns users of potential issues.

Usage:
    uv run validate              # Auto-detect which services to validate
    uv run validate mongodb      # Validate MongoDB only
    uv run validate zapier       # Validate Zapier only
    uv run validate --verbose    # Show detailed logging
"""

import argparse
import logging
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Tuple, Optional

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, OperationFailure
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

from dotenv import dotenv_values
from .terraform import get_project_root


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)


def colorize(text: str, color: str) -> str:
    """
    Add ANSI color codes to text.

    Args:
        text: Text to colorize
        color: Color name (green, red, yellow, reset)

    Returns:
        Colorized text string
    """
    colors = {
        'green': '\033[92m',
        'red': '\033[91m',
        'yellow': '\033[93m',
        'reset': '\033[0m'
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"


def verify_vector_search_index(
    collection,
    expected_name: str = "vector_index",
    expected_dims: int = 1536,
    expected_similarity: str = "cosine",
    expected_path: str = "embedding"
) -> Tuple[bool, List[str]]:
    """
    Verify Atlas Vector Search index exists and is properly configured.

    Uses PyMongo's list_search_indexes() to check the index configuration.

    Args:
        collection: PyMongo collection object
        expected_name: Expected index name
        expected_dims: Expected number of dimensions
        expected_similarity: Expected similarity function
        expected_path: Expected vector field path

    Returns:
        Tuple of (success, list_of_messages)
    """
    messages = []

    try:
        # List all search indexes
        indexes = list(collection.list_search_indexes())

        # Find the vector index
        vector_index = None
        for idx in indexes:
            if idx.get('name') == expected_name:
                vector_index = idx
                break

        if not vector_index:
            available = [idx.get('name') for idx in indexes if idx.get('name')]
            if available:
                messages.append(colorize(f"✗ Vector index '{expected_name}' not found", 'red'))
                messages.append(f"   Available indexes: {', '.join(available)}")
            else:
                messages.append(colorize(f"✗ Vector index '{expected_name}' not found (no search indexes exist)", 'red'))
            messages.append("   → Create index (step 7): assets/pre-setup/MongoDB-Setup.md#step-7")
            return False, messages

        # Check type
        index_type = vector_index.get('type')
        if index_type != 'vectorSearch':
            messages.append(colorize(f"✗ Index type is '{index_type}', expected 'vectorSearch'", 'red'))
            messages.append("   → Recreate as vector search index (step 7): assets/pre-setup/MongoDB-Setup.md#step-7")
            return False, messages

        # Check status
        status = vector_index.get('status')
        if status != 'READY':
            if status in ['PENDING', 'BUILDING']:
                messages.append(colorize(f"⚠️  Index status is '{status}' - index is still being built", 'yellow'))
                messages.append("   This is normal for new indexes. Wait a few minutes and try again.")
                return True, messages  # Don't fail for pending/building
            else:
                messages.append(colorize(f"✗ Index status is '{status}', expected 'READY'", 'red'))
                messages.append("   → Check index in MongoDB Atlas UI and recreate if needed (step 7)")
                messages.append("      assets/pre-setup/MongoDB-Setup.md#step-7")
                return False, messages

        # Check configuration
        definition = vector_index.get('latestDefinition', {})
        fields = definition.get('fields', [])

        # Find vector field
        vector_field = None
        for field in fields:
            if field.get('type') == 'vector':
                vector_field = field
                break

        if not vector_field:
            messages.append(colorize("✗ No vector field found in index definition", 'red'))
            messages.append("   → Configure vector field (step 8): assets/pre-setup/MongoDB-Setup.md#step-8")
            return False, messages

        # Verify vector field configuration
        issues = []
        actual_path = vector_field.get('path')
        actual_dims = vector_field.get('numDimensions')
        actual_similarity = vector_field.get('similarity')

        if actual_path != expected_path:
            issues.append(f"field path is '{actual_path}', expected '{expected_path}'")
        if actual_dims != expected_dims:
            issues.append(f"dimensions are {actual_dims}, expected {expected_dims}")
        if actual_similarity != expected_similarity:
            issues.append(f"similarity is '{actual_similarity}', expected '{expected_similarity}'")

        if issues:
            messages.append(colorize("✗ Vector index configuration issues:", 'red'))
            for issue in issues:
                messages.append(f"   • {issue}")
            messages.append("   → Fix configuration (step 8): assets/pre-setup/MongoDB-Setup.md#step-8")
            return False, messages

        # All checks passed
        messages.append(colorize(f"✓ Vector Search index '{expected_name}' is properly configured", 'green'))
        messages.append(f"   • Type: {index_type}, Status: {status}")
        messages.append(f"   • Field: {actual_path}, Dimensions: {actual_dims}, Similarity: {actual_similarity}")
        return True, messages

    except Exception as e:
        messages.append(colorize(f"⚠️  Error checking vector search index: {e}", 'yellow'))
        messages.append("   → Verify index manually in MongoDB Atlas UI (step 7-8)")
        messages.append("      assets/pre-setup/MongoDB-Setup.md#step-7")
        return False, messages


def validate_mongodb(
    connection_string: str,
    username: str,
    password: str,
    database: str = "vector_search",
    collection: str = "documents",
    index_name: str = "vector_index"
) -> Tuple[bool, List[str]]:
    """
    Validate MongoDB Atlas configuration.

    Checks:
    - Connection string is valid and can connect
    - Database exists
    - Collection exists
    - Vector search index exists with correct configuration

    Args:
        connection_string: MongoDB connection string
        username: MongoDB username
        password: MongoDB password
        database: Database name (default: vector_search)
        collection: Collection name (default: documents)
        index_name: Vector search index name (default: vector_index)

    Returns:
        Tuple of (all_checks_passed, list_of_messages)
    """
    messages = []
    all_passed = True

    if not PYMONGO_AVAILABLE:
        messages.append("⚠️  WARNING: pymongo not installed - cannot validate MongoDB")
        messages.append("   Install with: pip install pymongo")
        return False, messages

    try:
        # Build connection URI
        if username and password:
            if "mongodb+srv://" in connection_string:
                uri = connection_string.replace(
                    "mongodb+srv://",
                    f"mongodb+srv://{username}:{password}@"
                )
            else:
                uri = connection_string.replace(
                    "mongodb://",
                    f"mongodb://{username}:{password}@"
                )
        else:
            uri = connection_string

        # Connect to MongoDB
        client = MongoClient(uri, serverSelectionTimeoutMS=10000)

        # Test connection and credentials
        try:
            client.admin.command('ping')
            messages.append(colorize("✓ Successfully connected to MongoDB", 'green'))
        except Exception as e:
            messages.append(colorize(f"✗ Failed to connect to MongoDB: {e}", 'red'))
            messages.append("   → Check connection string (step 5): assets/pre-setup/MongoDB-Setup.md#step-5")
            messages.append("   → Check username/password (step 4): assets/pre-setup/MongoDB-Setup.md#step-4")
            messages.append("   → Check network access allows 0.0.0.0/0 (step 6): assets/pre-setup/MongoDB-Setup.md#step-6")
            all_passed = False
            client.close()
            return all_passed, messages

        # Check database exists
        db_list = client.list_database_names()
        if database in db_list:
            messages.append(colorize(f"✓ Database '{database}' exists", 'green'))
        else:
            messages.append(colorize(f"✗ Database '{database}' not found", 'red'))
            messages.append("   → Create database (step 7): assets/pre-setup/MongoDB-Setup.md#step-7")
            all_passed = False

        # Check collection exists
        db = client[database]
        coll_list = db.list_collection_names()
        if collection in coll_list:
            messages.append(colorize(f"✓ Collection '{collection}' exists", 'green'))
        else:
            messages.append(colorize(f"✗ Collection '{collection}' not found", 'red'))
            messages.append("   → Create collection (step 7): assets/pre-setup/MongoDB-Setup.md#step-7")
            all_passed = False

        # Check Atlas Vector Search index using PyMongo's list_search_indexes()
        coll = db[collection]
        index_passed, index_messages = verify_vector_search_index(coll, index_name)

        for msg in index_messages:
            messages.append(msg)

        if not index_passed:
            all_passed = False

        client.close()

    except ConnectionFailure as e:
        messages.append(colorize(f"✗ MongoDB connection failed: {e}", 'red'))
        messages.append("   → Check connection string (step 5): assets/pre-setup/MongoDB-Setup.md#step-5")
        messages.append("   → Check network access (step 6): assets/pre-setup/MongoDB-Setup.md#step-6")
        all_passed = False
    except OperationFailure as e:
        messages.append(colorize(f"✗ MongoDB operation failed: {e}", 'red'))
        messages.append("   → Check username/password (step 4): assets/pre-setup/MongoDB-Setup.md#step-4")
        all_passed = False
    except Exception as e:
        messages.append(colorize(f"✗ Unexpected MongoDB error: {e}", 'red'))
        all_passed = False

    return all_passed, messages


def validate_zapier(sse_endpoint: str) -> Tuple[bool, List[str]]:
    """
    Validate Zapier MCP Server configuration.

    Checks:
    - SSE endpoint is reachable
    - Endpoint appears to be a valid SSE endpoint
    - URL format is correct (ends with /sse)

    Args:
        sse_endpoint: Zapier SSE endpoint URL

    Returns:
        Tuple of (all_checks_passed, list_of_messages)
    """
    messages = []
    all_passed = True

    # Check URL format
    if not sse_endpoint.endswith('/sse'):
        messages.append(colorize("⚠️  Warning: SSE endpoint URL should end with '/sse'", 'yellow'))
        messages.append("   → Check endpoint URL (step 4): assets/pre-setup/Zapier-Setup.md#step-4")
        all_passed = False
    else:
        messages.append(colorize("✓ SSE endpoint URL format is correct", 'green'))

    # Check endpoint reachability
    try:
        req = urllib.request.Request(sse_endpoint)
        req.add_header('Accept', 'text/event-stream')

        with urllib.request.urlopen(req, timeout=10) as response:
            # Check if it's an SSE endpoint
            content_type = response.headers.get('Content-Type', '')

            if 'text/event-stream' in content_type or 'application/json' in content_type:
                messages.append(colorize("✓ SSE endpoint is reachable", 'green'))
                messages.append("   ℹ️  Please verify these tools are enabled in your MCP server:")
                messages.append("      - webhooks_by_zapier_get")
                messages.append("      - webhooks_by_zapier_custom_request")
                messages.append("      - gmail_send_email")
                messages.append("   → Verify tools (step 3): assets/pre-setup/Zapier-Setup.md#step-3")
            else:
                messages.append(colorize(f"⚠️  Warning: Unexpected content type: {content_type}", 'yellow'))
                messages.append("   Endpoint is reachable but may not be configured correctly")
                messages.append("   → Check MCP server setup (step 2): assets/pre-setup/Zapier-Setup.md#step-2")
                all_passed = False

    except urllib.error.HTTPError as e:
        if e.code == 404:
            messages.append(colorize("✗ SSE endpoint not found (404)", 'red'))
            messages.append("   → Check endpoint URL (step 4): assets/pre-setup/Zapier-Setup.md#step-4")
        else:
            messages.append(colorize(f"✗ HTTP error accessing endpoint: {e.code} {e.reason}", 'red'))
            messages.append("   → Check MCP server setup (step 2): assets/pre-setup/Zapier-Setup.md#step-2")
        all_passed = False
    except urllib.error.URLError as e:
        messages.append(colorize(f"✗ Cannot reach SSE endpoint: {e.reason}", 'red'))
        messages.append("   → Check endpoint URL (step 4): assets/pre-setup/Zapier-Setup.md#step-4")
        messages.append("   → Verify MCP server is created (step 2): assets/pre-setup/Zapier-Setup.md#step-2")
        all_passed = False
    except TimeoutError:
        messages.append(colorize("✗ Timeout connecting to SSE endpoint", 'red'))
        messages.append("   → Check endpoint URL (step 4): assets/pre-setup/Zapier-Setup.md#step-4")
        all_passed = False
    except Exception as e:
        messages.append(colorize(f"✗ Unexpected error validating Zapier endpoint: {e}", 'red'))
        all_passed = False

    return all_passed, messages


def main():
    """Main entry point for validation script."""
    parser = argparse.ArgumentParser(
        description="Validate MongoDB and Zapier configurations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                 # Auto-detect which services to validate
  %(prog)s mongodb         # Validate MongoDB only
  %(prog)s zapier          # Validate Zapier only
  %(prog)s --verbose       # Show detailed logging
        """
    )

    parser.add_argument(
        "service",
        nargs="?",
        choices=["mongodb", "zapier"],
        help="Service to validate (mongodb or zapier). If not specified, will auto-detect based on credentials."
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set up logging
    logger = setup_logging(args.verbose)

    # Get project root and load credentials
    try:
        project_root = get_project_root()
        creds_file = project_root / "credentials.env"

        if not creds_file.exists():
            print("\n" + "=" * 70)
            print("ERROR: credentials.env not found")
            print("=" * 70)
            print("\nPlease create credentials.env file first.")
            print("Run: uv run deploy")
            print("=" * 70)
            return 0  # Soft check - don't fail

        creds = dotenv_values(creds_file)
        logger.debug(f"Loaded credentials from {creds_file}")

    except Exception as e:
        logger.error(f"Could not load credentials: {e}")
        return 0  # Soft check - don't fail

    # Determine which services to validate
    validate_mongo = False
    validate_zap = False

    if args.service == "mongodb":
        validate_mongo = True
    elif args.service == "zapier":
        validate_zap = True
    else:
        # Auto-detect based on credentials
        has_mongo = all([
            creds.get("TF_VAR_mongodb_connection_string"),
            creds.get("TF_VAR_mongodb_username"),
            creds.get("TF_VAR_mongodb_password")
        ])
        has_zapier = bool(creds.get("TF_VAR_zapier_sse_endpoint"))

        if has_mongo:
            validate_mongo = True
        if has_zapier:
            validate_zap = True

        if not validate_mongo and not validate_zap:
            print("\n" + "=" * 70)
            print("NO SERVICES TO VALIDATE")
            print("=" * 70)
            print("\nNo MongoDB or Zapier credentials found in credentials.env")
            print("Please configure these services first.")
            print("=" * 70)
            return 0  # Soft check - don't fail

    # Print header
    print("\n" + "=" * 70)
    print("CONFIGURATION VALIDATION")
    print("=" * 70)
    print("\nThis is a soft check to help identify potential configuration issues.")
    print("You can proceed with deployment even if checks fail.\n")

    all_services_passed = True

    # Validate MongoDB
    if validate_mongo:
        print("-" * 70)
        print("MONGODB VALIDATION")
        print("-" * 70)

        connection_string = creds.get("TF_VAR_mongodb_connection_string", "")
        username = creds.get("TF_VAR_mongodb_username", "")
        password = creds.get("TF_VAR_mongodb_password", "")

        if not all([connection_string, username, password]):
            print(colorize("✗ MongoDB credentials incomplete in credentials.env", 'red'))
            print("  Missing: ", end="")
            missing = []
            if not connection_string:
                missing.append("TF_VAR_mongodb_connection_string")
            if not username:
                missing.append("TF_VAR_mongodb_username")
            if not password:
                missing.append("TF_VAR_mongodb_password")
            print(", ".join(missing))
            print("\n→ See MongoDB setup guide: assets/pre-setup/MongoDB-Setup.md")
            all_services_passed = False
        else:
            passed, messages = validate_mongodb(connection_string, username, password)
            for msg in messages:
                print(msg)

            if not passed:
                all_services_passed = False

        print()

    # Validate Zapier
    if validate_zap:
        print("-" * 70)
        print("ZAPIER MCP SERVER VALIDATION")
        print("-" * 70)

        sse_endpoint = creds.get("TF_VAR_zapier_sse_endpoint", "")

        if not sse_endpoint:
            print(colorize("✗ Zapier SSE endpoint not found in credentials.env", 'red'))
            print("  Missing: TF_VAR_zapier_sse_endpoint")
            print("\n→ See Zapier setup guide: assets/pre-setup/Zapier-Setup.md")
            all_services_passed = False
        else:
            passed, messages = validate_zapier(sse_endpoint)
            for msg in messages:
                print(msg)

            if not passed:
                all_services_passed = False

        print()

    # Print summary
    print("=" * 70)
    if all_services_passed:
        print(colorize("✓ ALL VALIDATION CHECKS PASSED", 'green'))
        print("=" * 70)
        print("\nYour configuration appears to be correct!")
        print("You can proceed with deployment.")
    else:
        print(colorize("⚠️  SOME VALIDATION CHECKS FAILED", 'yellow'))
        print("=" * 70)
        print("\nPlease review the warnings above and verify your configuration.")
        print("You can still proceed with deployment if you believe the")
        print("configuration is correct, but you may encounter issues later.")
        print("\nSetup guides:")
        print("  • MongoDB: assets/pre-setup/MongoDB-Setup.md")
        print("  • Zapier:  assets/pre-setup/Zapier-Setup.md")
    print("=" * 70)

    return 0  # Always return 0 (soft check - never fail deployment)


if __name__ == "__main__":
    sys.exit(main())
