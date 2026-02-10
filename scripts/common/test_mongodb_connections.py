#!/usr/bin/env python3
"""
Test script to validate MongoDB connections and vector search for Lab2 and Lab3.

Lab2: Should return Flink SQL documentation chunks
Lab3: Should return NOLA events and context information

Usage:
    uv run test_mongodb_connections [--cloud aws|azure] [--lab lab2|lab3]
"""

import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import argparse
from typing import Dict, List, Optional
import json


# MongoDB credentials for all labs and clouds
MONGODB_CONFIGS = {
    "lab2": {
        "aws": {
            "connection_string": "mongodb+srv://cluster0.c79vrkg.mongodb.net/",
            "username": "workshop-user",
            "password": "xr6PvJl9xZz1uoKa",
            "database": "vector_search",
            "collection": "documents",
            "expected_content": "Flink",
        },
        "azure": {
            "connection_string": "mongodb+srv://cluster0.xhgx1kr.mongodb.net/",
            "username": "public_readonly_user",
            "password": "sB948mVgIYqwUloX",
            "database": "vector_search",
            "collection": "documents",
            "expected_content": "Flink",
        },
    },
    "lab3": {
        "aws": {
            "connection_string": "mongodb+srv://cluster0.w9n3o45.mongodb.net/",
            "username": "workshop-user",
            "password": "JHcZajJzWYwKe6dt",
            "database": "vector_search",
            "collection": "documents",
            "expected_content": "New Orleans",
        },
        "azure": {
            "connection_string": "mongodb+srv://cluster0.iir6woe.mongodb.net/",
            "username": "public_readonly_user",
            "password": "pE7xOkiKth2QqTKL",
            "database": "vector_search",
            "collection": "documents",
            "expected_content": "New Orleans",
        },
    },
}


def test_connection(
    lab: str, cloud: str, config: Dict[str, str]
) -> tuple[bool, Optional[str], Optional[Dict]]:
    """
    Test MongoDB connection and retrieve sample documents.

    Returns:
        (success, error_message, sample_document)
    """
    print(f"\n{'=' * 70}")
    print(f"Testing {lab.upper()} - {cloud.upper()}")
    print(f"{'=' * 70}")
    print(f"Connection: {config['connection_string']}")
    print(f"Username:   {config['username']}")
    print(f"Database:   {config['database']}")
    print(f"Collection: {config['collection']}")
    print(f"Expected:   Documents containing '{config['expected_content']}'")

    try:
        # Build connection URI
        uri = (
            f"{config['connection_string']}"
            f"?retryWrites=true&w=majority&appName=test-script"
        )

        # Connect to MongoDB
        client = MongoClient(
            uri,
            username=config["username"],
            password=config["password"],
            serverSelectionTimeoutMS=5000,
        )

        # Test connection
        client.admin.command("ping")
        print("✅ Connection successful!")

        # Access database and collection
        db = client[config["database"]]
        collection = db[config["collection"]]

        # Get collection stats
        doc_count = collection.count_documents({})
        print(f"📊 Total documents in collection: {doc_count}")

        if doc_count == 0:
            return (
                False,
                f"Collection is empty. Documents may not have been published yet.",
                None,
            )

        # Get sample documents
        print(f"\n🔍 Fetching sample documents...")
        sample_docs = list(collection.find().limit(3))

        if not sample_docs:
            return (False, "No documents found in collection", None)

        # Display sample documents
        for i, doc in enumerate(sample_docs, 1):
            print(f"\n--- Sample Document {i} ---")
            print(f"Document ID: {doc.get('document_id', 'N/A')}")

            chunk = doc.get("chunk", "")
            chunk_preview = (
                chunk[:200] + "..." if len(chunk) > 200 else chunk
            )
            print(f"Chunk Preview: {chunk_preview}")

            # Check if expected content is present
            if config["expected_content"].lower() in chunk.lower():
                print(f"✅ Contains expected content: '{config['expected_content']}'")
            else:
                print(
                    f"⚠️  Does NOT contain expected content: '{config['expected_content']}'"
                )

            # Check for embedding
            has_embedding = "embedding" in doc
            if has_embedding:
                embedding_size = len(doc.get("embedding", []))
                print(f"✅ Has embedding vector (size: {embedding_size})")
            else:
                print("❌ Missing embedding vector")

        # Vector search index check
        print(f"\n🔍 Checking vector search index...")
        try:
            indexes = list(collection.list_indexes())
            vector_indexes = [
                idx for idx in indexes if idx.get("type") == "vectorSearch"
            ]

            if vector_indexes:
                print(
                    f"✅ Found {len(vector_indexes)} vector search index(es):"
                )
                for idx in vector_indexes:
                    print(f"   - {idx.get('name', 'unnamed')}")
            else:
                print(
                    "⚠️  No vector search indexes found (may need to be created manually)"
                )
        except Exception as e:
            print(f"⚠️  Could not check indexes: {e}")

        client.close()
        return (True, None, sample_docs[0])

    except ConnectionFailure as e:
        error_msg = f"❌ Connection failed: {e}"
        print(error_msg)
        return (False, error_msg, None)
    except OperationFailure as e:
        error_msg = f"❌ Authentication failed: {e}"
        print(error_msg)
        return (False, error_msg, None)
    except Exception as e:
        error_msg = f"❌ Unexpected error: {e}"
        print(error_msg)
        return (False, error_msg, None)


def main():
    parser = argparse.ArgumentParser(
        description="Test MongoDB connections for Lab2 and Lab3"
    )
    parser.add_argument(
        "--cloud",
        choices=["aws", "azure", "all"],
        default="all",
        help="Cloud provider to test (default: all)",
    )
    parser.add_argument(
        "--lab",
        choices=["lab2", "lab3", "all"],
        default="all",
        help="Lab to test (default: all)",
    )

    args = parser.parse_args()

    # Determine which tests to run
    labs_to_test = (
        ["lab2", "lab3"] if args.lab == "all" else [args.lab]
    )
    clouds_to_test = (
        ["aws", "azure"] if args.cloud == "all" else [args.cloud]
    )

    print("\n" + "=" * 70)
    print("MongoDB Connection & Vector Search Test")
    print("=" * 70)

    results = {}
    total_tests = 0
    passed_tests = 0

    for lab in labs_to_test:
        for cloud in clouds_to_test:
            total_tests += 1
            config = MONGODB_CONFIGS[lab][cloud]
            success, error, sample_doc = test_connection(lab, cloud, config)

            results[f"{lab}-{cloud}"] = {
                "success": success,
                "error": error,
                "sample_doc": sample_doc,
            }

            if success:
                passed_tests += 1

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for test_name, result in results.items():
        lab, cloud = test_name.split("-")
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} - {lab.upper()} ({cloud.upper()})")
        if result["error"]:
            print(f"       Error: {result['error']}")

    print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed")

    # Return exit code
    if passed_tests == total_tests:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(
            f"\n⚠️  {total_tests - passed_tests} test(s) failed. Check errors above."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
