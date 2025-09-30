#!/usr/bin/env python3
"""
Document chunking script that processes markdown files with YAML frontmatter.
Chunks documents using character-based splitting with heading boundaries.

Parameters based on ML_CHARACTER_TEXT_SPLITTER:
- chunk_size: 5000 characters per chunk
- overlap: 200 characters overlap between chunks
- separator: Split on "#" and "##" headings (but not "###" and smaller)
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List

import yaml


def parse_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith("---\n"):
        return {}, content

    try:
        # Split on the second --- boundary
        parts = content.split("---\n", 2)
        if len(parts) < 3:
            return {}, content

        frontmatter = yaml.safe_load(parts[1])
        markdown_content = parts[2]
        return frontmatter or {}, markdown_content
    except yaml.YAMLError:
        return {}, content


def split_on_headings(text: str) -> List[str]:
    """Split text on # and ## headings, but not ### and smaller."""
    lines = text.split("\n")
    sections = []
    current_section = []

    for line in lines:
        # Check if this line is a major heading (# or ##, but not ### or more)
        if re.match(r"^#{1,2}(?!#)\s+", line):
            # If we have content in current section, save it
            if current_section:
                sections.append("\n".join(current_section).strip())
                current_section = []
            # Start new section with this heading
            current_section.append(line)
        else:
            # Add line to current section
            current_section.append(line)

    # Add the final section
    if current_section:
        sections.append("\n".join(current_section).strip())

    return [section for section in sections if section.strip()]


def chunk_text(
    text: str, chunk_size: int = 5000, overlap: int = 200, min_chunk_size: int = 1000
) -> List[str]:
    """
    Chunk text into pieces respecting heading boundaries.

    Args:
        text: Input text to chunk
        chunk_size: Maximum characters per chunk (default 5000)
        overlap: Characters to overlap between chunks (default 200)
        min_chunk_size: Minimum characters per chunk (default 1000)

    Returns:
        List of text chunks
    """
    # First split on major headings (# and ##)
    sections = split_on_headings(text)

    chunks = []
    current_chunk = ""

    for section in sections:
        # If adding this section would exceed chunk size, finalize current chunk
        if (
            current_chunk and len(current_chunk) + len(section) + 2 > chunk_size
        ):  # +2 for \n\n
            chunks.append(current_chunk.strip())

            # Start new chunk with overlap from previous chunk (word-based overlap)
            if overlap > 0 and len(current_chunk) > overlap:
                # Get overlap text and clean it up
                overlap_text = current_chunk[-overlap:].strip()
                # Find a good break point in the overlap (avoid breaking mid-word)
                words = overlap_text.split()
                if len(words) > 5:  # Only use overlap if we have enough words
                    overlap_text = " ".join(words[-5:])  # Use last 5 words
                    current_chunk = overlap_text + "\n\n" + section
                else:
                    current_chunk = section
            else:
                current_chunk = section
        else:
            # Add section to current chunk
            if current_chunk:
                current_chunk += "\n\n" + section
            else:
                current_chunk = section

        # If current chunk exceeds size significantly, split it at paragraph breaks
        while (
            len(current_chunk) > chunk_size * 1.2
        ):  # Allow 20% overage before splitting
            # Find a good split point (paragraph break)
            split_point = chunk_size

            # Look for paragraph breaks within reasonable range
            for i in range(chunk_size - 200, min(chunk_size + 200, len(current_chunk))):
                if i < len(current_chunk) - 1 and current_chunk[i : i + 2] == "\n\n":
                    split_point = i
                    break

            # If no good break found, split at word boundary
            if split_point == chunk_size:
                for i in range(
                    chunk_size - 50, min(chunk_size + 50, len(current_chunk))
                ):
                    if i < len(current_chunk) and current_chunk[i] == " ":
                        split_point = i
                        break

            chunk_part = current_chunk[:split_point].strip()
            if chunk_part:
                chunks.append(chunk_part)

            # Continue with remainder (with minimal overlap to avoid duplication)
            current_chunk = current_chunk[split_point:].strip()

    # Add final chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    # Filter out chunks that are too small or empty
    filtered_chunks = []
    for chunk in chunks:
        if chunk.strip() and len(chunk.strip()) >= min_chunk_size:
            filtered_chunks.append(chunk.strip())
        elif chunk.strip():
            # For very small chunks, try to merge with previous chunk if possible
            if (
                filtered_chunks
                and len(filtered_chunks[-1]) + len(chunk) < chunk_size * 1.2
            ):
                filtered_chunks[-1] += "\n\n" + chunk.strip()
            # Otherwise, only keep if it's a complete section (has a heading)
            elif chunk.strip().startswith("#"):
                filtered_chunks.append(chunk.strip())

    return filtered_chunks


def process_document(
    file_path: Path,
    chunk_size: int = 5000,
    overlap: int = 200,
    min_chunk_size: int = 1000,
) -> List[Dict[str, Any]]:
    """
    Process a single markdown document and return chunks.

    Args:
        file_path: Path to the markdown file

    Returns:
        List of dictionaries containing chunk data
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse frontmatter and content
        frontmatter, markdown_content = parse_frontmatter(content)

        # If document is smaller than minimum chunk size, don't chunk it
        if len(markdown_content.strip()) < min_chunk_size:
            chunks = [markdown_content.strip()] if markdown_content.strip() else []
        else:
            # Generate chunks
            chunks = chunk_text(markdown_content, chunk_size, overlap, min_chunk_size)

        # Create chunk documents
        chunk_docs = []
        for i, chunk in enumerate(chunks):
            chunk_doc = {
                "document_id": f"{file_path.stem}_chunk_{i+1}",
                "source_file": str(file_path.name),
                "source_url": frontmatter.get("source_url", ""),
                "title": frontmatter.get("title", ""),
                "chunk_index": i + 1,
                "total_chunks": len(chunks),
                "chunk_text": chunk,
                "frontmatter": frontmatter,
            }
            chunk_docs.append(chunk_doc)

        return chunk_docs

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []


def process_directory(
    docs_dir: str = None,
    chunk_size: int = 5000,
    overlap: int = 200,
    min_chunk_size: int = 1000,
) -> List[Dict[str, Any]]:
    """
    Process all markdown files in the flink_docs directory.

    Args:
        docs_dir: Directory containing markdown files (defaults to current script directory)

    Returns:
        List of all chunk documents
    """
    if docs_dir is None:
        docs_dir = Path(__file__).parent
    else:
        docs_dir = Path(docs_dir)

    all_chunks = []
    processed_count = 0

    # Process all .md files except README.md
    for md_file in docs_dir.glob("*.md"):
        if md_file.name == "README.md":
            continue

        print(f"Processing: {md_file.name}")
        chunks = process_document(md_file, chunk_size, overlap, min_chunk_size)
        all_chunks.extend(chunks)
        processed_count += 1

        if chunks:
            print(f"  → Generated {len(chunks)} chunks")

    print(
        f"\nTotal: Processed {processed_count} documents, generated {len(all_chunks)} chunks"
    )
    return all_chunks


def save_chunks_as_markdown(chunks: List[Dict[str, Any]], output_dir: str):
    """Save chunks as individual markdown files."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    for chunk in chunks:
        # Create filename from document_id
        filename = f"{chunk['document_id']}.md"
        filepath = output_path / filename

        # Create markdown content with metadata header
        content = f"""---
document_id: {chunk['document_id']}
source_file: {chunk['source_file']}
source_url: {chunk['source_url']}
title: {chunk['title']}
chunk_index: {chunk['chunk_index']}
total_chunks: {chunk['total_chunks']}
---

{chunk['chunk_text']}
"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"Saved {len(chunks)} markdown files to {output_dir}")


def main():
    """Main function to demonstrate chunking."""
    import argparse

    parser = argparse.ArgumentParser(description="Chunk Flink documentation")
    parser.add_argument("--docs-dir", help="Directory containing markdown files")
    parser.add_argument("--output", help="Output file for chunks (JSON format)")
    parser.add_argument(
        "--output-md-dir", help="Output directory for individual markdown files"
    )
    parser.add_argument(
        "--chunk-size", type=int, default=5000, help="Chunk size in characters"
    )
    parser.add_argument(
        "--overlap", type=int, default=200, help="Overlap between chunks"
    )
    parser.add_argument(
        "--min-chunk-size",
        type=int,
        default=1000,
        help="Minimum chunk size in characters",
    )

    args = parser.parse_args()

    # Process documents
    chunks = process_directory(
        args.docs_dir, args.chunk_size, args.overlap, args.min_chunk_size
    )

    # Optionally save to file
    if args.output:
        import json
        from datetime import datetime

        def json_serializer(obj):
            """JSON serializer for datetime objects."""
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(
                f"Object of type {obj.__class__.__name__} is not JSON serializable"
            )

        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False, default=json_serializer)
        print(f"Saved {len(chunks)} chunks to {args.output}")

    # Optionally save as markdown files
    if args.output_md_dir:
        save_chunks_as_markdown(chunks, args.output_md_dir)

    # Print sample
    if chunks:
        print("\nSample chunk:")
        sample = chunks[0]
        print(f"Document ID: {sample['document_id']}")
        print(f"Source: {sample['source_file']}")
        print(f"Chunk {sample['chunk_index']}/{sample['total_chunks']}")
        print(f"Text length: {len(sample['chunk_text'])} characters")
        print("Text preview:")
        print(
            sample["chunk_text"][:300] + "..."
            if len(sample["chunk_text"]) > 300
            else sample["chunk_text"]
        )


if __name__ == "__main__":
    main()
