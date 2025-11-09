#!/usr/bin/env python3
"""
Generate Flink SQL command summary markdown files for labs.

This script extracts Flink SQL from Terraform state and lab walkthrough markdown files,
ensuring the documentation automatically stays in sync with deployed infrastructure.

Usage:
    python scripts/generate_lab_flink_summary.py <lab-name> <cloud-provider> <terraform-dir> [key=value...]

Examples:
    python scripts/generate_lab_flink_summary.py lab1 aws aws/lab1-tool-calling
    python scripts/generate_lab_flink_summary.py lab2 azure azure/lab2-vector-search
    python scripts/generate_lab_flink_summary.py lab3 aws aws/lab3-agentic-fleet-management

Note: Additional key=value arguments are accepted for backward compatibility but not currently used.
"""

import json
import subprocess
import sys
from pathlib import Path

# Add scripts/common to the path so we can import from it
sys.path.insert(0, str(Path(__file__).parent / "common"))

from generate_deployment_summary import generate_flink_sql_summary
from sql_extractors import extract_sql_from_terraform, extract_sql_from_lab_walkthroughs


def get_manual_commands_for_lab(lab_name: str) -> str:
    """
    Get manual commands from lab walkthrough markdown.

    Uses simple pattern matching to extract numbered headers and SQL blocks
    from the walkthrough, ensuring 100% accuracy with documentation.

    Args:
        lab_name: Name of the lab (e.g., "lab1")

    Returns:
        Markdown string with extracted headers and SQL blocks
    """
    # Map lab names to markdown files
    markdown_files = {
        'lab1': 'LAB1-Walkthrough.md',
        'lab2': 'LAB2-Walkthrough.md',
        'lab3': 'Lab3-Walkthrough.md'
    }

    if lab_name not in markdown_files:
        print(f"Warning: Unknown lab name '{lab_name}'")
        return ""

    # Get the project root (parent directory of scripts/)
    project_root = Path(__file__).parent.parent
    markdown_path = project_root / markdown_files[lab_name]

    if not markdown_path.exists():
        print(f"Warning: Walkthrough file not found: {markdown_path}")
        return ""

    # Extract and return markdown
    try:
        return extract_sql_from_lab_walkthroughs(markdown_path)
    except Exception as e:
        print(f"Warning: Failed to extract from markdown: {e}")
        return ""


def main():
    """Main entry point."""
    if len(sys.argv) < 4:
        print("Usage: python scripts/generate_lab_flink_summary.py <lab-name> <cloud-provider> <terraform-dir> [key=value...]")
        print("Example: python scripts/generate_lab_flink_summary.py lab1 aws aws/lab1-tool-calling")
        sys.exit(1)

    lab_name = sys.argv[1]  # e.g., "lab1"
    cloud_provider = sys.argv[2]  # e.g., "aws"
    terraform_dir = Path(sys.argv[3])  # e.g., "aws/lab1-tool-calling"

    # Parse additional key=value arguments
    credentials = {}
    for arg in sys.argv[4:]:
        if '=' in arg:
            key, value = arg.split('=', 1)
            credentials[key] = value

    # Validate inputs
    if cloud_provider not in ["aws", "azure"]:
        print(f"Error: Invalid cloud provider '{cloud_provider}'. Must be 'aws' or 'azure'")
        sys.exit(1)

    if not terraform_dir.exists():
        print(f"Error: Terraform directory not found: {terraform_dir}")
        sys.exit(1)

    # Get core terraform directory
    core_terraform_dir = terraform_dir.parent / "core"
    if not core_terraform_dir.exists():
        print(f"Error: Core terraform directory not found: {core_terraform_dir}")
        print("The extraction approach requires Core Terraform to be deployed.")
        sys.exit(1)

    # Get terraform outputs from CORE
    try:
        print(f"Reading Terraform outputs from {core_terraform_dir}...")
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=core_terraform_dir,
            capture_output=True,
            text=True,
            check=True
        )
        tf_outputs = json.loads(result.stdout)
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error: Failed to read core terraform outputs: {e}")
        sys.exit(1)

    # EXTRACTION: Get commands from Terraform state
    print(f"Extracting Flink SQL from Terraform state in {terraform_dir}...")
    try:
        automated_commands, core_resources = extract_sql_from_terraform(
            lab_terraform_dir=terraform_dir,
            core_terraform_dir=core_terraform_dir,
            cloud_provider=cloud_provider
        )
        print(f"  - Extracted {len(automated_commands)} automated commands")
        print(f"  - Extracted {len(core_resources)} core resources")
    except Exception as e:
        print(f"Error: Failed to extract SQL from Terraform: {e}")
        sys.exit(1)

    # Extract manual commands from walkthrough markdown
    manual_commands = get_manual_commands_for_lab(lab_name)
    num_headers = manual_commands.count('#') if manual_commands else 0
    num_sql = manual_commands.count('```sql') if manual_commands else 0
    print(f"  - Extracted {num_headers} headers and {num_sql} SQL blocks from walkthrough markdown")

    # Generate the summary
    output_file = terraform_dir / "FLINK_SQL_COMMANDS.md"
    lab_full_name = f"{lab_name}-tool-calling" if lab_name == "lab1" else f"{lab_name}-vector-search" if lab_name == "lab2" else f"{lab_name}-anomaly-detection"

    generate_flink_sql_summary(
        lab_name=lab_full_name,
        cloud_provider=cloud_provider,
        tf_outputs=tf_outputs,
        output_path=output_file,
        automated_commands=automated_commands,
        manual_commands=manual_commands,
        core_resources=core_resources
    )

    print(f"\nSuccess! Flink SQL summary generated at: {output_file}")


if __name__ == "__main__":
    main()
