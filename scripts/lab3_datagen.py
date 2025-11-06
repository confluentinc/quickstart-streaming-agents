#!/usr/bin/env python3
"""
Lab3 Anomaly Detection Data Generation Script

Generates streaming data for Lab3 using ShadowTraffic and Docker.
Creates ride_requests and vessel_catalog topics on Confluent Cloud.

Usage:
    uv run lab3_datagen                      # Auto-detect cloud provider
    uv run lab3_datagen aws                  # Generate data for AWS environment
    uv run lab3_datagen azure                # Generate data for Azure environment
    uv run lab3_datagen --dry-run            # Validate setup without running
    uv run lab3_datagen --duration 300       # Run for 5 minutes
"""

import argparse
import logging
import sys
from pathlib import Path

from .common.cloud_detection import auto_detect_cloud_provider, suggest_cloud_provider
from .common.terraform import extract_kafka_credentials, validate_terraform_state, get_project_root
from .common.datagen_helpers import (
    check_dependencies,
    validate_dependencies,
    generate_all_connections,
    check_shadowtraffic_config,
    run_shadowtraffic_docker
)


# Lab3-Specific Configuration
LAB3_CONNECTION_NAMES = ["ride-requests", "vessel-catalog"]
LAB3_REQUIRED_GENERATORS = ["base-rides.json", "steady-state-rides.json", "surge-rides.json", "vesselcatalog.json"]
LAB3_DIR_NAME = "lab3-anomaly-detection"


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)


def run_lab3_datagen(
    cloud_provider: str,
    duration: int = None,
    messages_per_minute: int = None,
    dry_run: bool = False,
    verbose: bool = False
) -> int:
    """
    Run Lab3 data generation workflow.

    Args:
        cloud_provider: Target cloud provider (aws/azure)
        duration: Duration to run in seconds
        messages_per_minute: Ride requests per minute to generate
        dry_run: If True, validate setup but don't run
        verbose: If True, show detailed output

    Returns:
        Exit code (0 for success)
    """
    logger = logging.getLogger(__name__)

    try:
        # Get project root and build lab3 paths
        project_root = get_project_root()
        lab3_dir = project_root / cloud_provider / LAB3_DIR_NAME
        datagen_dir = lab3_dir / "data-gen"

        if not datagen_dir.exists():
            logger.error(f"Lab3 data-gen directory not found: {datagen_dir}")
            return 1

        connections_dir = datagen_dir / "connections"
        generators_dir = datagen_dir / "generators"
        zones_dir = datagen_dir / "zones"
        functions_dir = datagen_dir / "functions"
        root_config = datagen_dir / "root.json"

        # Check dependencies
        logger.info("🔧 Checking dependencies...")
        deps = check_dependencies()
        if not validate_dependencies(deps):
            return 1

        # Extract credentials from terraform
        logger.info(f"📡 Extracting {cloud_provider.upper()} credentials...")
        credentials = extract_kafka_credentials(cloud_provider, project_root)

        # Generate connection files
        generate_all_connections(credentials, connections_dir, ["ride-requests", "vessel-telemetry"])

        # Check ShadowTraffic configuration
        if not check_shadowtraffic_config(generators_dir, LAB3_REQUIRED_GENERATORS):
            return 1

        # Run ShadowTraffic with lab3-specific volumes (includes zones and functions)
        return run_shadowtraffic_docker(
            datagen_dir=datagen_dir,
            connections_dir=connections_dir,
            generators_dir=generators_dir,
            root_config=root_config,
            zones_dir=zones_dir,
            functions_dir=functions_dir,
            duration=duration,
            messages_per_minute=messages_per_minute,
            dry_run=dry_run
        )

    except Exception as e:
        logger.error(f"Data generation failed: {e}")
        if verbose:
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
        return 1


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog="lab3_datagen",
        description="Generate streaming data for Lab3 with ShadowTraffic and Docker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run lab3_datagen                      # Auto-detect cloud provider
  uv run lab3_datagen aws                  # Generate data for AWS environment
  uv run lab3_datagen azure                # Generate data for Azure environment
  uv run lab3_datagen --duration 300       # Run for 5 minutes
  uv run lab3_datagen -m 20                # Generate 20 ride requests per minute
  uv run lab3_datagen --dry-run            # Validate setup only

Dependencies:
  - Docker: https://docs.docker.com/get-docker/
  - jq: https://jqlang.github.io/jq/download/
  - Terraform: https://developer.hashicorp.com/terraform/install
        """.strip()
    )

    parser.add_argument(
        "cloud_provider",
        nargs="?",
        choices=["aws", "azure"],
        help="Target cloud provider (auto-detected if not specified)"
    )

    parser.add_argument(
        "--duration",
        type=int,
        help="Duration to run data generation in seconds"
    )

    parser.add_argument(
        "--messages-per-minute", "-m",
        type=int,
        help="Ride requests per minute to generate"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate setup and generate connection files without running ShadowTraffic"
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
    logger.info("Lab3 Anomaly Detection - Data Generation")

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

        logger.info(f"Target cloud provider: {cloud_provider.upper()}")

        # Validate terraform state
        if not validate_terraform_state(cloud_provider, project_root):
            logger.error(f"Terraform state validation failed for {cloud_provider}")
            logger.error(f"Please run 'terraform apply' in {cloud_provider}/core/ and {cloud_provider}/{LAB3_DIR_NAME}/")
            sys.exit(1)

        # Run data generation
        exit_code = run_lab3_datagen(
            cloud_provider=cloud_provider,
            duration=args.duration,
            messages_per_minute=args.messages_per_minute,
            dry_run=args.dry_run,
            verbose=args.verbose
        )

        if args.dry_run:
            logger.info("Dry run completed")
        else:
            logger.info(f"Data generation completed with exit code {exit_code}")

        sys.exit(exit_code)

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Data generation failed: {e}")
        if args.verbose:
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
