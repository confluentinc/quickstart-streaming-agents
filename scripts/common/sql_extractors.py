#!/usr/bin/env python3
"""
Extract Flink SQL statements from Terraform state and Lab walkthrough markdown files.

This module provides functions to automatically extract Flink SQL commands
from deployed Terraform resources and walkthrough documentation.

Usage:
    from sql_extractors import extract_sql_from_terraform, extract_sql_from_lab_walkthroughs

    # Extract from Terraform state
    automated, core_resources = extract_sql_from_terraform(
        lab_terraform_dir=Path("terraform/lab1-tool-calling"),
        core_terraform_dir=Path("terraform/core"),
        cloud_provider="aws"
    )

    # Extract from walkthrough markdown
    manual_commands = extract_sql_from_lab_walkthroughs(Path("LAB1-Walkthrough.md"))
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any


def extract_sql_from_terraform(
    lab_terraform_dir: Path,
    core_terraform_dir: Path,
    cloud_provider: str
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """
    Extract all Flink SQL commands for a lab from Terraform state.

    Args:
        lab_terraform_dir: Path to lab's terraform directory
        core_terraform_dir: Path to core terraform directory
        cloud_provider: Cloud provider ("aws" or "azure")

    Returns:
        Tuple of (automated_commands, core_resources)
        Each is a list of dicts with 'title' and 'sql' keys
    """
    # Extract automated commands from lab
    automated_commands = extract_flink_statements(lab_terraform_dir)

    # Extract core LLM resources
    core_resources = extract_core_llm_resources(core_terraform_dir, cloud_provider)

    return automated_commands, core_resources


def extract_flink_statements(terraform_dir: Path) -> List[Dict[str, str]]:
    """
    Extract confluent_flink_statement resources from Terraform state.

    Reads the terraform.tfstate file directly to get unredacted sensitive values.

    Args:
        terraform_dir: Path to terraform directory

    Returns:
        List of dicts with 'title' and 'sql' keys
    """
    commands = []

    try:
        # Read terraform.tfstate directly to get unredacted values
        state_file = terraform_dir / "terraform.tfstate"
        if not state_file.exists():
            print(f"Warning: State file not found: {state_file}")
            return commands

        with open(state_file) as f:
            state = json.load(f)

        # Extract resources from state (direct state file has different structure than terraform show)
        # State file has resources as top-level array with instances inside
        resources = []
        for resource in state.get('resources', []):
            for instance in resource.get('instances', []):
                # Create a resource dict similar to terraform show output
                resources.append({
                    'type': resource.get('type'),
                    'name': resource.get('name'),
                    'values': instance.get('attributes', {})
                })

        # Process confluent_flink_statement resources
        for resource in resources:
            if resource.get('type') == 'confluent_flink_statement':
                values = resource.get('values', {})
                statement_name = values.get('statement_name', 'Unknown')
                raw_sql = values.get('statement', '')

                # Sanitize SQL for documentation
                sanitized_sql = sanitize_sql(raw_sql)

                commands.append({
                    'title': statement_name,
                    'sql': sanitized_sql
                })

        # Process confluent_flink_connection resources (native, not SQL-based)
        for resource in resources:
            if resource.get('type') == 'confluent_flink_connection':
                values = resource.get('values', {})
                connection_sql = reconstruct_connection_sql(values)
                connection_name = values.get('display_name', 'Unknown Connection')

                commands.append({
                    'title': f"{connection_name}",
                    'sql': connection_sql
                })

    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to extract from {terraform_dir}: {e}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Warning: Failed to parse Terraform state: {e}")

    return commands


def extract_core_llm_resources(
    core_terraform_dir: Path,
    cloud_provider: str
) -> List[Dict[str, str]]:
    """
    Extract LLM connection and model resources from Core Terraform.

    Reads the terraform.tfstate file directly to get unredacted sensitive values.

    Args:
        core_terraform_dir: Path to core terraform directory
        cloud_provider: Cloud provider ("aws" or "azure")

    Returns:
        List of dicts with 'title' and 'sql' keys for LLM resources
    """
    resources = []

    try:
        # Read terraform.tfstate directly to get unredacted values
        state_file = core_terraform_dir / "terraform.tfstate"
        if not state_file.exists():
            print(f"Warning: Core state file not found: {state_file}")
            return resources

        with open(state_file) as f:
            state = json.load(f)

        # Extract resources from state (direct state file structure)
        tf_resources = []
        for resource in state.get('resources', []):
            for instance in resource.get('instances', []):
                # Create a resource dict similar to terraform show output
                tf_resources.append({
                    'type': resource.get('type'),
                    'name': resource.get('name'),
                    'values': instance.get('attributes', {})
                })

        # Look for LLM-related Flink statements
        # These typically have statement_name containing 'llm', 'model', 'textgen', or 'embedding'
        llm_keywords = ['llm', 'model', 'textgen', 'embedding', 'bedrock', 'azureopenai']

        for resource in tf_resources:
            if resource.get('type') == 'confluent_flink_statement':
                values = resource.get('values', {})
                statement_name = values.get('statement_name', '').lower()
                raw_sql = values.get('statement', '')

                # Check if this is an LLM-related resource
                if any(keyword in statement_name for keyword in llm_keywords):
                    sanitized_sql = sanitize_sql(raw_sql)

                    # Add comment to indicate it's from Core Terraform
                    commented_sql = f"-- Created in Core Terraform\n{sanitized_sql}"

                    resources.append({
                        'title': values.get('statement_name', 'Unknown'),
                        'sql': commented_sql
                    })

        # Also check for LLM connection resources
        for resource in tf_resources:
            if resource.get('type') == 'confluent_flink_connection':
                values = resource.get('values', {})
                conn_type = values.get('type', '').lower()

                # Check if this is an LLM connection (Bedrock or AzureOpenAI)
                if conn_type in ['bedrock', 'azureopenai']:
                    connection_sql = reconstruct_connection_sql(values)
                    commented_sql = f"-- Created in Core Terraform\n{connection_sql}"
                    connection_name = values.get('display_name', 'Unknown Connection')

                    resources.append({
                        'title': connection_name,
                        'sql': commented_sql
                    })

    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to extract core resources: {e}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Warning: Failed to parse core Terraform state: {e}")

    return resources


def reconstruct_connection_sql(connection_values: Dict[str, Any]) -> str:
    """
    Reconstruct CREATE CONNECTION SQL from native confluent_flink_connection resource.

    Reads all attributes from state including sensitive values.

    Args:
        connection_values: The 'values' dict from the Terraform resource

    Returns:
        SQL string for CREATE CONNECTION with actual credentials
    """
    conn_type = connection_values.get('type', 'UNKNOWN')
    display_name = connection_values.get('display_name', 'unknown-connection')
    endpoint = connection_values.get('endpoint', '')

    # Build WITH clause - start with type and endpoint
    with_clauses = [f"'type' = '{conn_type}'"]

    if endpoint:
        with_clauses.append(f"'endpoint' = '{endpoint}'")

    # Add all credential-related attributes (these come from state file unredacted)
    credential_attrs = [
        'api-key', 'api_key',
        'password',
        'connection-string', 'connection_string',
        'username',
        'aws_access_key_id',
        'aws_secret_access_key'
    ]

    for attr in credential_attrs:
        if attr in connection_values and connection_values[attr]:
            # Use the attribute name with hyphens for SQL (Flink convention)
            sql_attr_name = attr.replace('_', '-')
            with_clauses.append(f"'{sql_attr_name}' = '{connection_values[attr]}'")

    with_clause = ",\n  ".join(with_clauses)

    return f"""CREATE CONNECTION IF NOT EXISTS `{display_name}` WITH (
  {with_clause}
)"""


def sanitize_sql(sql: str) -> str:
    """
    Clean up SQL for documentation display.

    This function:
    - Removes full table qualification (env.cluster.table -> table)
    - Preserves all actual credential values as-is

    Args:
        sql: Raw SQL from Terraform state

    Returns:
        Cleaned SQL with actual credentials preserved
    """
    sanitized = sql

    # Remove full table qualification: `env`.`cluster`.`table` -> `table`
    # This regex looks for backtick-quoted identifiers with 3 parts
    sanitized = re.sub(
        r'`[^`]+`\.`[^`]+`\.`([^`]+)`',
        r'`\1`',
        sanitized
    )

    return sanitized


def extract_sql_from_lab_walkthroughs(md_path: Path) -> str:
    """
    Extract numbered headers, SQL blocks, and bash blocks from lab walkthrough markdown.

    This uses simple pattern matching to extract:
    - Numbered headers (H1/H2/H3 starting with a number, e.g., "## 1. Some Section")
    - SQL code blocks (```sql ... ```, but NOT ```sql no-parse)
    - Bash code blocks (```bash ... ```, but NOT ```bash no-parse)

    Args:
        md_path: Path to the lab walkthrough markdown file

    Returns:
        Markdown string with extracted headers, SQL blocks, and bash blocks in document order
    """
    txt = md_path.read_text()
    # Match either: numbered headers OR sql blocks (not no-parse) OR bash blocks (not no-parse)
    pattern = r'(^#{1,3}\s+\d+\.[^\n]+)|(^```sql(?!\s+no-parse)\n.*?^```)|(^```bash(?!\s+no-parse)\n.*?^```)'
    return '\n\n'.join(
        m.group(0) for m in re.finditer(pattern, txt, re.MULTILINE | re.DOTALL)
    )
