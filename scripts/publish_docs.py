#!/usr/bin/env python3
"""
Unified document publisher for quickstart-streaming-agents.

Cross-platform tool for publishing Flink documentation to Kafka topics.
Supports both AWS and Azure deployments with automatic cloud provider detection.

Usage:
    uv run publish-docs aws          # Publish to AWS environment
    uv run publish-docs azure        # Publish to Azure environment
    uv run publish-docs              # Auto-detect from current directory
    uv run publish-docs --dry-run    # Test without actually publishing

Traditional Python:
    pip install -e .
    publish-docs aws
"""

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

from .common.cloud_detection import auto_detect_cloud_provider, validate_cloud_provider, suggest_cloud_provider
from .common.terraform import extract_kafka_credentials, validate_terraform_state, get_project_root


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)


def find_main_publisher_script(project_root: Path) -> Path:
    """
    Find the main publisher script in the assets directory.

    Args:
        project_root: Project root directory

    Returns:
        Path to the main publisher script

    Raises:
        FileNotFoundError: If the main script is not found
    """
    main_script = project_root / "assets/lab2/flink_docs/publish_docs.py"

    if not main_script.exists():
        raise FileNotFoundError(
            f"Main publisher script not found: {main_script}\n"
            f"Expected location: assets/lab2/flink_docs/publish_docs.py"
        )

    return main_script


def test_dependencies(python_executable: str, env: dict) -> bool:
    """
    Test that all required dependencies are available.

    Args:
        python_executable: Path to Python executable
        env: Environment variables

    Returns:
        True if dependencies are available, False otherwise
    """
    logger = logging.getLogger(__name__)
    logger.info("Testing required dependencies...")

    test_imports = [
        "yaml",
        "confluent_kafka.avro",
        "requests",
    ]

    try:
        import_test = "; ".join([f"import {module}" for module in test_imports])
        result = subprocess.run(
            [python_executable, "-c", f"{import_test}; print('Dependencies OK')"],
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("✓ All required dependencies are available")
        return True
    except subprocess.CalledProcessError as e:
        logger.error("✗ Missing required dependencies!")
        logger.error(f"Dependency test failed: {e.stderr}")
        logger.error("To install required packages:")
        logger.error("  uv pip install -r requirements.txt")
        logger.error("  # Or with traditional Python:")
        logger.error("  pip install -r requirements.txt")
        return False


def get_python_executable(project_root: Path) -> str:
    """
    Find the best Python executable to use.

    Args:
        project_root: Project root directory

    Returns:
        Path to Python executable
    """
    logger = logging.getLogger(__name__)

    # Try UV virtual environment first
    uv_venv_python = project_root / ".venv/bin/python"
    if uv_venv_python.exists():
        logger.info("Using UV virtual environment python")
        return str(uv_venv_python)

    # Fall back to current Python executable
    logger.info("Using current Python executable")
    return sys.executable


def run_publisher(
    cloud_provider: str,
    project_root: Path,
    dry_run: bool = False,
    verbose: bool = False
) -> int:
    """
    Run the main publisher script with extracted credentials.

    Args:
        cloud_provider: Target cloud provider (aws/azure)
        project_root: Project root directory
        dry_run: If True, validate setup but don't publish
        verbose: If True, show detailed output

    Returns:
        Exit code (0 for success)
    """
    logger = logging.getLogger(__name__)

    try:
        # Extract credentials from terraform state
        credentials = extract_kafka_credentials(cloud_provider, project_root)

        # Find the main publisher script
        main_script = find_main_publisher_script(project_root)

        # Get Python executable
        python_executable = get_python_executable(project_root)

        # Set environment variables for the main script
        env = os.environ.copy()
        env.update({
            "KAFKA_BOOTSTRAP_SERVERS": credentials["bootstrap_servers"],
            "KAFKA_API_KEY": credentials["kafka_api_key"],
            "KAFKA_API_SECRET": credentials["kafka_api_secret"],
            "SCHEMA_REGISTRY_URL": credentials["schema_registry_url"],
            "SCHEMA_REGISTRY_API_KEY": credentials["schema_registry_api_key"],
            "SCHEMA_REGISTRY_API_SECRET": credentials["schema_registry_api_secret"],
            "KAFKA_TOPIC": "documents",  # Standard topic name
        })

        # Test dependencies first
        if not test_dependencies(python_executable, env):
            return 1

        if dry_run:
            logger.info("✓ Dry run successful - all dependencies and credentials are ready")
            logger.info(f"Would publish to topic 'documents' in cluster '{credentials['cluster_name']}'")
            logger.info(f"Environment: {credentials['environment_name']}")
            logger.info(f"Bootstrap servers: {credentials['bootstrap_servers']}")
            return 0

        # Run the main script
        logger.info(f"Running main publisher script: {main_script}")
        logger.info(f"Publishing to topic 'documents' in cluster '{credentials['cluster_name']}'")

        result = subprocess.run(
            [python_executable, str(main_script)],
            env=env,
            capture_output=True,
            text=True
        )

        # Log the output
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line.strip():  # Skip empty lines
                    if verbose:
                        logger.info(f"Publisher: {line}")
                    else:
                        # Show only important messages for non-verbose mode
                        if any(keyword in line.lower() for keyword in ['error', 'success', 'complete', 'published']):
                            logger.info(f"Publisher: {line}")

        if result.stderr:
            for line in result.stderr.strip().split('\n'):
                if line.strip():
                    logger.warning(f"Publisher stderr: {line}")

        if result.returncode == 0:
            logger.info("✓ Document publishing completed successfully")
        else:
            logger.error(f"✗ Publisher failed with exit code {result.returncode}")

        return result.returncode

    except Exception as e:
        logger.error(f"Publisher failed: {e}")
        if verbose:
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
        return 1


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog="publish-docs",
        description="Publish Flink documentation to Kafka topics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run publish-docs aws          # Publish to AWS environment
  uv run publish-docs azure        # Publish to Azure environment
  uv run publish-docs              # Auto-detect cloud provider
  uv run publish-docs aws --dry-run --verbose

Traditional Python:
  pip install -e .
  publish-docs aws
        """.strip()
    )

    parser.add_argument(
        "cloud_provider",
        nargs="?",
        choices=["aws", "azure"],
        help="Target cloud provider (auto-detected if not specified)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate setup and credentials without publishing documents"
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
    logger.info("Quickstart Streaming Agents - Document Publisher")

    try:
        # Get project root
        project_root = get_project_root()
        logger.debug(f"Project root: {project_root}")

        # Determine cloud provider
        cloud_provider = args.cloud_provider
        if not cloud_provider:
            cloud_provider = auto_detect_cloud_provider()
            if not cloud_provider:
                logger.error("Could not auto-detect cloud provider")
                suggest_cloud_provider(project_root)
                sys.exit(1)
        else:
            if not validate_cloud_provider(cloud_provider):
                sys.exit(1)

        logger.info(f"Target cloud provider: {cloud_provider.upper()}")

        # Validate terraform state
        if not validate_terraform_state(cloud_provider, project_root):
            logger.error(f"Terraform state validation failed for {cloud_provider}")
            logger.error(f"Please run 'terraform apply' in {cloud_provider}/core/ and {cloud_provider}/lab2-vector-search/")
            sys.exit(1)

        # Run the publisher
        exit_code = run_publisher(
            cloud_provider=cloud_provider,
            project_root=project_root,
            dry_run=args.dry_run,
            verbose=args.verbose
        )

        if args.dry_run:
            logger.info("Dry run completed")
        else:
            logger.info(f"Document publishing completed with exit code {exit_code}")

        sys.exit(exit_code)

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Document publisher failed: {e}")
        if args.verbose:
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()