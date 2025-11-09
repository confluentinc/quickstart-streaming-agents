#!/usr/bin/env python3
"""
Clear MongoDB documents collection.

Connects to MongoDB Atlas and clears all documents from the vector_search.documents collection.

Usage:
    uv run clear_mongodb              # Auto-detect cloud provider and clear collection
    uv run clear_mongodb aws          # Use AWS credentials
    uv run clear_mongodb azure        # Use Azure credentials
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Optional

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, OperationFailure
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

from .common.cloud_detection import auto_detect_cloud_provider, validate_cloud_provider, suggest_cloud_provider
from .common.terraform import get_project_root


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)


def extract_mongodb_credentials(cloud_provider: str, project_root: Path) -> Dict[str, str]:
    """
    Extract MongoDB credentials from terraform.tfvars.

    Args:
        cloud_provider: Cloud provider (aws or azure)
        project_root: Project root directory

    Returns:
        Dictionary with MongoDB connection details

    Raises:
        Exception if credentials cannot be extracted
    """
    tfvars_path = project_root / cloud_provider / "lab2-vector-search" / "terraform.tfvars"

    if not tfvars_path.exists():
        raise Exception(f"terraform.tfvars not found at {tfvars_path}")

    credentials = {}

    with open(tfvars_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or not line:
                continue

            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")

                if key == 'mongodb_connection_string':
                    credentials['connection_string'] = value
                elif key == 'mongodb_username':
                    credentials['username'] = value
                elif key == 'mongodb_password':
                    credentials['password'] = value
                elif key == 'mongodb_database':
                    credentials['database'] = value
                elif key == 'mongodb_collection':
                    credentials['collection'] = value

    # Set defaults if not found
    if 'database' not in credentials:
        credentials['database'] = 'vector_search'
    if 'collection' not in credentials:
        credentials['collection'] = 'documents'

    # Validate required credentials
    required = ['connection_string', 'username', 'password']
    missing = [key for key in required if key not in credentials]
    if missing:
        raise Exception(f"Missing required MongoDB credentials: {', '.join(missing)}")

    return credentials


def clear_mongodb_collection(
    connection_string: str,
    username: str,
    password: str,
    database: str = "vector_search",
    collection: str = "documents"
) -> int:
    """
    Clear all documents from MongoDB collection.

    Args:
        connection_string: MongoDB connection string
        username: MongoDB username
        password: MongoDB password
        database: Database name (default: vector_search)
        collection: Collection name (default: documents)

    Returns:
        Number of documents deleted

    Raises:
        ImportError if pymongo is not available
        ConnectionFailure if connection fails
        OperationFailure if delete operation fails
    """
    if not PYMONGO_AVAILABLE:
        raise ImportError(
            "pymongo is not installed. Please install it with: pip install pymongo"
        )

    # Build connection URI
    if username and password:
        # Insert credentials into connection string
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
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)

    # Test connection
    client.admin.command('ping')

    # Get database and collection
    db = client[database]
    coll = db[collection]

    # Delete all documents
    result = coll.delete_many({})

    # Close connection
    client.close()

    return result.deleted_count


def main():
    """Main entry point for MongoDB collection clearer."""
    parser = argparse.ArgumentParser(
        description="Clear MongoDB documents collection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s aws
  %(prog)s azure --verbose
        """
    )

    parser.add_argument(
        "cloud_provider",
        nargs="?",
        choices=["aws", "azure"],
        help="Cloud provider (aws or azure). If not specified, will auto-detect."
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set up logging
    logger = setup_logging(args.verbose)

    # Check if pymongo is available
    if not PYMONGO_AVAILABLE:
        print("\n" + "=" * 60)
        print("ERROR: pymongo is not installed")
        print("=" * 60)
        print("\nPlease clear your MongoDB collection manually:")
        print("1. Connect to your MongoDB Atlas cluster")
        print("2. Navigate to the 'vector_search' database")
        print("3. Delete all documents from the 'documents' collection")
        print("\nOr install pymongo with: pip install pymongo")
        print("=" * 60)
        return 1

    # Determine cloud provider
    cloud_provider = args.cloud_provider
    if not cloud_provider:
        cloud_provider = auto_detect_cloud_provider()
        if not cloud_provider:
            suggestion = suggest_cloud_provider()
            if suggestion:
                logger.info(f"Auto-detected cloud provider: {suggestion}")
                cloud_provider = suggestion
            else:
                logger.error("Could not auto-detect cloud provider. Please specify 'aws' or 'azure'.")
                return 1

    # Validate cloud provider
    if not validate_cloud_provider(cloud_provider):
        logger.error(f"Invalid cloud provider: {cloud_provider}")
        return 1

    # Get project root
    try:
        project_root = get_project_root()
    except Exception as e:
        logger.error(f"Could not find project root: {e}")
        return 1

    # Extract MongoDB credentials
    try:
        credentials = extract_mongodb_credentials(cloud_provider, project_root)
        logger.debug(f"Extracted credentials for database '{credentials['database']}', collection '{credentials['collection']}'")
    except Exception as e:
        logger.error(f"Failed to extract MongoDB credentials: {e}")
        return 1

    # Clear collection
    try:
        logger.info(f"Connecting to MongoDB ({credentials['database']}.{credentials['collection']})...")

        deleted_count = clear_mongodb_collection(
            connection_string=credentials['connection_string'],
            username=credentials['username'],
            password=credentials['password'],
            database=credentials['database'],
            collection=credentials['collection']
        )

        print(f"\n{'=' * 60}")
        print("MONGODB COLLECTION CLEARED")
        print(f"{'=' * 60}")
        print(f"Database:         {credentials['database']}")
        print(f"Collection:       {credentials['collection']}")
        print(f"Documents deleted: {deleted_count}")
        print(f"{'=' * 60}\n")

        return 0

    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        print("\nPlease clear your MongoDB collection manually.")
        return 1
    except OperationFailure as e:
        logger.error(f"Failed to delete documents: {e}")
        print("\nPlease clear your MongoDB collection manually.")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print("\nPlease clear your MongoDB collection manually.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
