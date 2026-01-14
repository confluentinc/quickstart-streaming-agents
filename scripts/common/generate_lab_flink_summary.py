#!/usr/bin/env python3
"""
Generate Flink SQL command summary markdown files for all deployed labs.

This script automatically discovers and processes all labs in a cloud provider directory,
extracting Flink SQL from Terraform state and lab walkthrough markdown files.
Labs that aren't deployed are silently skipped.

Usage:
    uv run generate_summaries <cloud-provider>

Examples:
    uv run generate_summaries aws
    uv run generate_summaries azure
"""

import json
import subprocess
import sys
from pathlib import Path

# Add scripts/common to path for imports when run as standalone script
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

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
    project_root = Path(__file__).parent.parent.parent
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


def generate_summary_for_lab(lab_name: str, cloud_provider: str, terraform_dir: Path) -> bool:
    """Generate Flink SQL summary for a single lab. Returns True if successful."""
    if not terraform_dir.exists():
        return False

    # Get core terraform directory
    core_terraform_dir = terraform_dir.parent / "core"
    if not core_terraform_dir.exists():
        return False

    # Get terraform outputs from CORE
    try:
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=core_terraform_dir,
            capture_output=True,
            text=True,
            check=True
        )
        tf_outputs = json.loads(result.stdout)
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        return False

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
    except Exception:
        return False

    # Extract manual commands from walkthrough markdown
    manual_commands = get_manual_commands_for_lab(lab_name)
    num_headers = manual_commands.count('#') if manual_commands else 0
    num_sql = manual_commands.count('```sql') if manual_commands else 0
    num_bash = manual_commands.count('```bash') if manual_commands else 0
    print(f"  - Extracted {num_headers} headers, {num_sql} SQL blocks, and {num_bash} bash blocks from walkthrough markdown")

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

    print(f"Success! Flink SQL summary generated at: {output_file}\n")
    return True


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: uv run generate_summaries <cloud-provider>")
        print("Example: uv run generate_summaries aws")
        print("         uv run generate_summaries azure")
        sys.exit(1)

    cloud_provider = sys.argv[1].lower()

    # Validate cloud provider
    if cloud_provider not in ["aws", "azure"]:
        print(f"Error: Invalid cloud provider '{cloud_provider}'. Must be 'aws' or 'azure'")
        sys.exit(1)

    # Lab configuration
    lab_configs = {
        'lab1': 'lab1-tool-calling',
        'lab2': 'lab2-vector-search',
        'lab3': 'lab3-agentic-fleet-management'
    }

    # Get project root (two levels up from scripts/common)
    project_root = Path(__file__).parent.parent.parent

    print(f"Generating Flink SQL summaries for all deployed {cloud_provider.upper()} labs...\n")

    successful = []
    skipped = []

    # Try to generate summary for each lab
    for lab_name, lab_dir_name in lab_configs.items():
        terraform_dir = project_root / cloud_provider / lab_dir_name

        print(f"Processing {lab_name}...")
        if generate_summary_for_lab(lab_name, cloud_provider, terraform_dir):
            successful.append(lab_name)
        else:
            skipped.append(lab_name)

    # Print summary
    print("=" * 60)
    if successful:
        print(f"Generated summaries for: {', '.join(successful)}")
    if skipped:
        print(f"Skipped (not deployed): {', '.join(skipped)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
