#!/usr/bin/env python3
"""
MCP Connection Setup for Lab1 Tool Calling.

Cross-platform tool for creating MCP connections via Confluent CLI.
Supports both AWS and Azure deployments with automatic credential extraction.

Usage:
    uv run lab1_mcp_setup aws          # Create MCP connection for AWS environment
    uv run lab1_mcp_setup azure        # Create MCP connection for Azure environment
    uv run lab1_mcp_setup              # Auto-detect cloud provider
    uv run mcp_setup aws               # Alias version

Traditional Python:
    pip install -e .
    lab1_mcp_setup aws
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional

from .common.cloud_detection import auto_detect_cloud_provider, suggest_cloud_provider
from .common.terraform import extract_kafka_credentials, get_project_root


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)


def read_tfvars(tfvars_path: Path) -> Dict[str, str]:
    """
    Read terraform.tfvars file and extract variables.

    Args:
        tfvars_path: Path to terraform.tfvars file

    Returns:
        Dictionary of variable names to values

    Raises:
        FileNotFoundError: If tfvars file doesn't exist
        ValueError: If required variables are missing
    """
    logger = logging.getLogger(__name__)

    if not tfvars_path.exists():
        raise FileNotFoundError(f"terraform.tfvars not found: {tfvars_path}")

    variables = {}

    with open(tfvars_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Parse variable assignment (handle = with or without spaces)
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                variables[key] = value

    logger.debug(f"Read variables from {tfvars_path}: {list(variables.keys())}")
    return variables


def create_mcp_connection(
    connection_name: str,
    cloud_provider: str,
    region: str,
    endpoint: str,
    sse_endpoint: str,
    environment_id: str
) -> bool:
    """
    Create MCP connection using Confluent CLI.

    Args:
        connection_name: Name for the MCP connection
        cloud_provider: Cloud provider (aws/azure)
        region: Cloud region
        endpoint: MCP endpoint URL
        sse_endpoint: SSE endpoint URL
        environment_id: Confluent environment ID

    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger(__name__)

    # Build confluent CLI command
    cmd = [
        "confluent", "flink", "connection", "create", connection_name,
        "--cloud", cloud_provider.upper(),
        "--region", region,
        "--type", "mcp_server",
        "--endpoint", endpoint,
        "--api-key", "api_key",
        "--environment", environment_id,
        "--sse-endpoint", sse_endpoint
    ]

    logger.info(f"Creating MCP connection '{connection_name}'...")
    logger.debug(f"Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )

        logger.info(f"✓ Successfully created MCP connection '{connection_name}'")
        if result.stdout:
            logger.debug(f"Output: {result.stdout}")

        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"✗ Failed to create MCP connection '{connection_name}'")

        if e.stderr:
            # Check if connection already exists
            if "already exists" in e.stderr.lower() or "duplicate" in e.stderr.lower():
                logger.warning(f"Connection '{connection_name}' already exists - this is OK")
                return True

            logger.error(f"Error output: {e.stderr}")

        if e.stdout:
            logger.error(f"Command output: {e.stdout}")

        return False

    except FileNotFoundError:
        logger.error("Confluent CLI not found. Please install it:")
        logger.error("  https://docs.confluent.io/confluent-cli/current/install.html")
        return False

    except subprocess.TimeoutExpired:
        logger.error("Command timed out after 60 seconds")
        return False


def run_mcp_setup(
    cloud_provider: str,
    verbose: bool = False
) -> int:
    """
    Run the complete MCP connection setup workflow.

    Args:
        cloud_provider: Target cloud provider (aws/azure)
        verbose: If True, show detailed output

    Returns:
        Exit code (0 for success)
    """
    logger = logging.getLogger(__name__)

    try:
        # Get project root
        project_root = get_project_root()
        logger.debug(f"Project root: {project_root}")

        # Find lab1 directory
        lab1_dir = project_root / cloud_provider / "lab1-tool-calling"
        if not lab1_dir.exists():
            logger.error(f"Lab1 directory not found: {lab1_dir}")
            return 1

        # Read terraform.tfvars
        tfvars_path = lab1_dir / "terraform.tfvars"
        logger.info(f"Reading configuration from {tfvars_path}...")
        tfvars = read_tfvars(tfvars_path)

        # Extract ZAPIER_SSE_ENDPOINT
        if "ZAPIER_SSE_ENDPOINT" not in tfvars:
            logger.error("ZAPIER_SSE_ENDPOINT not found in terraform.tfvars")
            return 1

        sse_endpoint = tfvars["ZAPIER_SSE_ENDPOINT"]
        # Derive endpoint by removing /sse suffix
        endpoint = sse_endpoint.replace("/sse", "")

        logger.info(f"Zapier SSE endpoint: {sse_endpoint}")

        # Extract credentials from terraform state
        logger.info(f"Extracting {cloud_provider.upper()} credentials from terraform state...")
        credentials = extract_kafka_credentials(cloud_provider, project_root)

        environment_id = credentials["environment_id"]
        region = tfvars.get("cloud_region", "us-east-1")

        logger.info(f"Environment: {credentials['environment_name']} ({environment_id})")
        logger.info(f"Region: {region}")

        # Create MCP connection
        success = create_mcp_connection(
            connection_name="zapier-mcp-connection",
            cloud_provider=cloud_provider,
            region=region,
            endpoint=endpoint,
            sse_endpoint=sse_endpoint,
            environment_id=environment_id
        )

        if success:
            logger.info("🎉 MCP connection setup completed successfully")
            return 0
        else:
            logger.error("✗ MCP connection setup failed")
            return 1

    except Exception as e:
        logger.error(f"MCP setup failed: {e}")
        if verbose:
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
        return 1


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog="lab1_mcp_setup",
        description="Create MCP connection for Lab1 Tool Calling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run lab1_mcp_setup aws          # Create MCP connection for AWS
  uv run lab1_mcp_setup azure        # Create MCP connection for Azure
  uv run lab1_mcp_setup              # Auto-detect cloud provider
  uv run mcp_setup aws               # Using alias

Traditional Python:
  pip install -e .
  lab1_mcp_setup aws
        """.strip()
    )

    parser.add_argument(
        "cloud_provider",
        nargs="?",
        choices=["aws", "azure"],
        help="Target cloud provider (auto-detected if not specified)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output and debug information"
    )

    return parser


def main() -> None:
    """Main entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()

    logger = setup_logging(args.verbose)
    logger.info("Quickstart Streaming Agents - Lab1 MCP Setup")

    try:
        # Determine cloud provider
        cloud_provider = args.cloud_provider
        if not cloud_provider:
            cloud_provider = auto_detect_cloud_provider()
            if not cloud_provider:
                logger.error("Could not auto-detect cloud provider")
                suggest_cloud_provider(get_project_root())
                sys.exit(1)

        logger.info(f"Target cloud provider: {cloud_provider.upper()}")

        # Run MCP setup
        exit_code = run_mcp_setup(
            cloud_provider=cloud_provider,
            verbose=args.verbose
        )

        sys.exit(exit_code)

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"MCP setup failed: {e}")
        if args.verbose:
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
