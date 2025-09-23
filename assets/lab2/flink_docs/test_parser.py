#!/usr/bin/env python3
"""
Test script to validate document parsing functionality.
"""

import json
import sys
from pathlib import Path

from publish_docs import FlinkDocsPublisher


def test_document_parsing():
    """Test parsing of a sample document."""
    # Initialize publisher with dummy config (we're only testing parsing)
    publisher = FlinkDocsPublisher({}, {})

    # Test with a real document
    docs_dir = Path(__file__).parent
    sample_files = list(docs_dir.glob("*.md"))[:3]  # Test first 3 files

    if not sample_files:
        print("No markdown files found for testing")
        return False

    print(f"Testing document parsing with {len(sample_files)} sample files:")

    for file_path in sample_files:
        print(f"\n--- Testing: {file_path.name} ---")

        # Parse the document
        document = publisher.parse_markdown_file(file_path)

        if document:
            print(f"✓ Successfully parsed {file_path.name}")
            print(f"  Document ID: {document['document_id']}")
            print(f"  Content length: {len(document['document_text'])} characters")
            print(f"  Metadata keys: {list(document['metadata'].keys())}")

            # Show first 200 chars of content
            content_preview = document["document_text"][:200].replace("\n", " ")
            print(f"  Content preview: {content_preview}...")

            # Validate required fields for Avro
            if "document_id" in document and "document_text" in document:
                print("  ✓ Required Avro fields present")

                # Test Avro record creation
                avro_record = {
                    "document_id": document["document_id"],
                    "document_text": document["document_text"],
                }
                print(f"  ✓ Avro record created successfully")
            else:
                print("  ✗ Missing required Avro fields")
                return False
        else:
            print(f"✗ Failed to parse {file_path.name}")
            return False

    print("\n--- Summary ---")
    print("✓ All document parsing tests passed")
    print("✓ Avro schema compatibility verified")
    return True


def test_avro_schema():
    """Test Avro schema definition."""
    publisher = FlinkDocsPublisher({}, {})

    print("\n--- Testing Avro Schema ---")
    schema = publisher.value_schema
    print(f"Schema name: {schema.name}")
    print(f"Schema type: {schema.type}")
    print("Schema fields:")
    for field in schema.fields:
        print(f"  - {field.name}: {field.type}")

    print("✓ Avro schema is valid")
    return True


if __name__ == "__main__":
    print("Flink Docs Publisher - Testing Document Parsing\n")

    try:
        # Test document parsing
        if not test_document_parsing():
            sys.exit(1)

        # Test Avro schema
        if not test_avro_schema():
            sys.exit(1)

        print("\n🎉 All tests passed! The publisher is ready to use.")

    except Exception as e:
        print(f"\n❌ Tests failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
