#!/usr/bin/env python3
"""
Unified data generation tool for quickstart-streaming-agents.

Cross-platform tool for generating streaming data with ShadowTraffic and Docker.
Supports AWS, Azure, and terraform deployments with automatic credential extraction
and connection file generation.

Usage:
    uv run lab1_datagen                      # Auto-detect cloud provider
    uv run lab1_datagen aws                  # Generate data for AWS environment
    uv run lab1_datagen azure                # Generate data for Azure environment
    uv run lab1_datagen --dry-run            # Validate setup without running
    uv run lab1_datagen --duration 300       # Run for 5 minutes
    uv run lab1_datagen -m 10                # Generate 10 orders per minute
    uv run lab1_datagen -m 30 --duration 120 # Generate 30 orders/min for 2 minutes

Traditional Python:
    python scripts/lab1_datagen.py
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

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


def check_dependencies() -> Dict[str, bool]:
    """
    Check if required dependencies are available.

    Returns:
        Dictionary with dependency availability status
    """
    dependencies = {}

    # Check Docker
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        dependencies["docker"] = True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        dependencies["docker"] = False

    # Check jq
    try:
        result = subprocess.run(
            ["jq", "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        dependencies["jq"] = True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        dependencies["jq"] = False

    # Check terraform
    try:
        result = subprocess.run(
            ["terraform", "version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        dependencies["terraform"] = True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        dependencies["terraform"] = False

    return dependencies


def validate_dependencies(dependencies: Dict[str, bool]) -> bool:
    """
    Validate that all required dependencies are available.

    Args:
        dependencies: Dictionary with dependency availability status

    Returns:
        True if all dependencies are available, False otherwise
    """
    logger = logging.getLogger(__name__)

    missing = [name for name, available in dependencies.items() if not available]

    if not missing:
        logger.info("✓ All required dependencies are available")
        return True

    logger.error("✗ Missing required dependencies:")
    for dep in missing:
        if dep == "docker":
            logger.error("  - Docker: https://docs.docker.com/get-docker/")
        elif dep == "jq":
            logger.error("  - jq: https://jqlang.github.io/jq/download/")
        elif dep == "terraform":
            logger.error("  - Terraform: https://developer.hashicorp.com/terraform/install")

    return False


def find_datagen_directories(cloud_provider: str, project_root: Path) -> Dict[str, Path]:
    """
    Find the relevant directories for data generation.

    Args:
        cloud_provider: Target cloud provider (aws/azure/terraform)
        project_root: Project root directory

    Returns:
        Dictionary with relevant paths

    Raises:
        FileNotFoundError: If required directories are not found
    """
    paths = {}

    if cloud_provider in ["aws", "azure"]:
        base_dir = project_root / cloud_provider
        core_dir = base_dir / "core"
        lab1_dir = base_dir / "lab1-tool-calling"
        datagen_dir = lab1_dir / "data-gen"

        if not core_dir.exists():
            raise FileNotFoundError(f"Core directory not found: {core_dir}")
        if not datagen_dir.exists():
            raise FileNotFoundError(f"Data generation directory not found: {datagen_dir}")

        paths.update({
            "core_dir": core_dir,
            "lab1_dir": lab1_dir,
            "datagen_dir": datagen_dir,
            "connections_dir": datagen_dir / "connections",
            "generators_dir": datagen_dir / "generators",
            "root_config": datagen_dir / "root.json",
        })

    elif cloud_provider == "terraform":
        terraform_dir = project_root / "terraform"
        core_dir = terraform_dir / "core"
        datagen_dir = terraform_dir / "data-gen"

        if not terraform_dir.exists():
            raise FileNotFoundError(f"Terraform directory not found: {terraform_dir}")
        if not datagen_dir.exists():
            raise FileNotFoundError(f"Terraform data generation directory not found: {datagen_dir}")

        paths.update({
            "core_dir": core_dir,
            "datagen_dir": datagen_dir,
            "connections_dir": datagen_dir / "connections",
            "generators_dir": datagen_dir / "generators",
            "root_config": datagen_dir / "root.json",
        })

    else:
        raise ValueError(f"Unsupported cloud provider: {cloud_provider}")

    return paths


def generate_connection_file(
    credentials: Dict[str, str],
    connection_name: str,
    output_path: Path
) -> None:
    """
    Generate a ShadowTraffic connection file.

    Args:
        credentials: Extracted Kafka credentials
        connection_name: Name of the connection (customers/products/orders)
        output_path: Path to write the connection file
    """
    logger = logging.getLogger(__name__)

    # Remove SASL_SSL:// prefix from bootstrap endpoint
    bootstrap_endpoint = credentials["bootstrap_servers"]
    if bootstrap_endpoint.startswith("SASL_SSL://"):
        bootstrap_endpoint = bootstrap_endpoint[11:]

    connection_config = {
        "kind": "kafka",
        "producerConfigs": {
            "bootstrap.servers": bootstrap_endpoint,
            "security.protocol": "SASL_SSL",
            "sasl.mechanism": "PLAIN",
            "sasl.jaas.config": f"org.apache.kafka.common.security.plain.PlainLoginModule required username='{credentials['kafka_api_key']}' password='{credentials['kafka_api_secret']}';",
            "key.serializer": "io.confluent.kafka.serializers.KafkaAvroSerializer",
            "value.serializer": "io.confluent.kafka.serializers.KafkaAvroSerializer",
            "schema.registry.url": credentials["schema_registry_url"],
            "basic.auth.credentials.source": "USER_INFO",
            "basic.auth.user.info": f"{credentials['schema_registry_api_key']}:{credentials['schema_registry_api_secret']}"
        }
    }

    with open(output_path, 'w') as f:
        json.dump(connection_config, f, indent=2)

    logger.debug(f"Generated connection file: {output_path}")


def generate_all_connections(credentials: Dict[str, str], connections_dir: Path) -> None:
    """
    Generate all required ShadowTraffic connection files.

    Args:
        credentials: Extracted Kafka credentials
        connections_dir: Directory to write connection files
    """
    logger = logging.getLogger(__name__)

    # Ensure connections directory exists
    connections_dir.mkdir(parents=True, exist_ok=True)

    connection_files = ["customers.json", "products.json", "orders.json"]

    logger.info("📝 Generating ShadowTraffic connection files...")

    for connection_name in ["customers", "products", "orders"]:
        output_path = connections_dir / f"{connection_name}.json"
        generate_connection_file(credentials, connection_name, output_path)
        logger.info(f"✓ Created {connection_name}.json")

    logger.info(f"🎉 Successfully generated all connection files in: {connections_dir}")


def check_shadowtraffic_config(paths: Dict[str, Path]) -> bool:
    """
    Check that ShadowTraffic configuration files exist.

    Args:
        paths: Dictionary with relevant paths

    Returns:
        True if all config files exist, False otherwise
    """
    logger = logging.getLogger(__name__)

    required_files = [
        paths["root_config"],
        paths["generators_dir"] / "customers.json",
        paths["generators_dir"] / "products.json",
        paths["generators_dir"] / "orders.json",
    ]

    missing_files = [f for f in required_files if not f.exists()]

    if missing_files:
        logger.error("✗ Missing ShadowTraffic configuration files:")
        for f in missing_files:
            logger.error(f"  - {f}")
        return False

    logger.info("✓ All ShadowTraffic configuration files found")
    return True


def check_docker_env_file(datagen_dir: Path) -> Optional[Path]:
    """
    Check for ShadowTraffic Docker environment file.

    Args:
        datagen_dir: Data generation directory

    Returns:
        Path to environment file if found, None otherwise
    """
    env_files = [
        "free-trial-license-docker.env",
        "shadowtraffic.env",
        ".env"
    ]

    for env_file in env_files:
        env_path = datagen_dir / env_file
        if env_path.exists():
            return env_path

    return None


def download_shadowtraffic_license(datagen_dir: Path) -> Optional[Path]:
    """
    Download ShadowTraffic free trial license file if not present.

    Args:
        datagen_dir: Data generation directory

    Returns:
        Path to the downloaded license file, or None if download failed
    """
    logger = logging.getLogger(__name__)

    license_url = "https://raw.githubusercontent.com/ShadowTraffic/shadowtraffic-examples/master/free-trial-license-docker.env"
    license_path = datagen_dir / "free-trial-license-docker.env"

    try:
        logger.info("📥 Downloading ShadowTraffic license file...")

        with urllib.request.urlopen(license_url, timeout=30) as response:
            license_content = response.read()

        with open(license_path, 'wb') as f:
            f.write(license_content)

        logger.info(f"✓ License file downloaded to: {license_path}")
        return license_path

    except Exception as e:
        logger.warning(f"⚠️  Failed to download license file: {e}")
        logger.warning("   Continuing with trial limits")
        return None


def get_license_expiration(license_path: Path) -> Optional[datetime]:
    """
    Extract expiration date from ShadowTraffic license file.

    Args:
        license_path: Path to the license file

    Returns:
        Expiration datetime if found and valid, None otherwise
    """
    logger = logging.getLogger(__name__)

    try:
        with open(license_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('LICENSE_EXPIRATION='):
                    expiration_str = line.split('=', 1)[1]
                    # Parse YYYY-MM-DD format
                    return datetime.strptime(expiration_str, '%Y-%m-%d')

        logger.debug(f"No LICENSE_EXPIRATION found in {license_path}")
        return None

    except Exception as e:
        logger.debug(f"Failed to parse license expiration from {license_path}: {e}")
        return None


def is_license_expired(license_path: Path) -> bool:
    """
    Check if a ShadowTraffic license is expired.

    Args:
        license_path: Path to the license file

    Returns:
        True if license is expired or expiration cannot be determined, False otherwise
    """
    expiration = get_license_expiration(license_path)

    if expiration is None:
        # Cannot determine expiration, assume not expired
        return False

    # Compare with today's date (ignore time component)
    today = datetime.now().date()
    expiration_date = expiration.date()

    return expiration_date < today


def run_shadowtraffic(
    paths: Dict[str, Path],
    duration: Optional[int] = None,
    messages_per_minute: Optional[int] = None,
    dry_run: bool = False
) -> int:
    """
    Run ShadowTraffic data generation with Docker.

    Args:
        paths: Dictionary with relevant paths
        duration: Duration to run in seconds (optional)
        messages_per_minute: Orders per minute to generate (optional)
        dry_run: If True, validate setup but don't run

    Returns:
        Exit code (0 for success)
    """
    logger = logging.getLogger(__name__)

    datagen_dir = paths["datagen_dir"]
    connections_dir = paths["connections_dir"]
    generators_dir = paths["generators_dir"]
    root_config = paths["root_config"]

    # If messages_per_minute is specified, create modified root.json
    if messages_per_minute:
        throttle_ms = int(60000 / messages_per_minute)
        logger.info(f"📊 Setting order rate to {messages_per_minute} messages/minute (throttle: {throttle_ms}ms)")

        # Load original root.json
        with open(root_config, 'r') as f:
            root_json = json.load(f)

        # Update the throttleMs in schedule overrides
        if "schedule" in root_json and "stages" in root_json["schedule"]:
            for stage in root_json["schedule"]["stages"]:
                if "generators" in stage and "orders" in stage["generators"]:
                    if "overrides" not in stage:
                        stage["overrides"] = {}
                    if "orders" not in stage["overrides"]:
                        stage["overrides"]["orders"] = {}
                    if "localConfigs" not in stage["overrides"]["orders"]:
                        stage["overrides"]["orders"]["localConfigs"] = {}

                    # Set fixed throttle (remove randomization for predictability)
                    stage["overrides"]["orders"]["localConfigs"]["throttleMs"] = throttle_ms

        # Create temp directory for modified config
        temp_dir = tempfile.mkdtemp(prefix="shadowtraffic_")
        temp_root_config = Path(temp_dir) / "root.json"

        # Write modified root.json
        with open(temp_root_config, 'w') as f:
            json.dump(root_json, f, indent=2)

        logger.debug(f"Created temporary root.json at: {temp_root_config}")
        root_config = temp_root_config

    # Check for environment file, download if missing or expired
    env_file = check_docker_env_file(datagen_dir)

    if env_file:
        # Check if existing license is expired
        if is_license_expired(env_file):
            expiration = get_license_expiration(env_file)
            expiration_str = expiration.strftime('%Y-%m-%d') if expiration else "unknown"

            logger.warning(f"⚠️  ShadowTraffic license expired on {expiration_str}")
            logger.info("📥 Attempting to download a fresh license file...")

            # Try to download a new license
            new_license = download_shadowtraffic_license(datagen_dir)
            if new_license:
                env_file = new_license
                logger.info("✓ Updated to fresh license file")
            else:
                logger.error("✗ Failed to download a new license file")
                logger.error("")
                logger.error("Please download a fresh license manually:")
                logger.error("  1. Visit: https://github.com/ShadowTraffic/shadowtraffic-examples")
                logger.error("  2. Download: free-trial-license-docker.env")
                logger.error(f"  3. Save to: {datagen_dir}/free-trial-license-docker.env")
                logger.error("")
                logger.error("Alternatively, get a full license at: https://shadowtraffic.io")
                return 1
    else:
        logger.info("📄 No ShadowTraffic license file found, attempting to download...")
        env_file = download_shadowtraffic_license(datagen_dir)
        if not env_file:
            logger.warning("⚠️  No ShadowTraffic environment file available")
            logger.warning("   ShadowTraffic will use trial limits")

    # Build Docker command
    docker_cmd = [
        "docker", "run",
        "--rm",
        "--net=host",
        "-v", f"{root_config}:/home/root.json",
        "-v", f"{generators_dir}:/home/generators",
        "-v", f"{connections_dir}:/home/connections",
    ]

    # Add environment file if found
    if env_file:
        docker_cmd.extend(["--env-file", str(env_file)])

    # Add duration if specified
    shadowtraffic_args = ["--config", "/home/root.json"]
    if duration:
        shadowtraffic_args.extend(["--duration", str(duration)])

    docker_cmd.extend([
        "shadowtraffic/shadowtraffic:1.1.9"
    ] + shadowtraffic_args)

    logger.info(f"🚀 Starting ShadowTraffic data generation...")
    logger.info(f"   Config: {root_config}")
    logger.info(f"   Connections: {connections_dir}")
    logger.info(f"   Generators: {generators_dir}")

    if env_file:
        logger.info(f"   Environment: {env_file}")

    if duration:
        logger.info(f"   Duration: {duration} seconds")

    if dry_run:
        logger.info("✓ Dry run - Docker command would be:")
        logger.info(f"   {' '.join(docker_cmd)}")
        return 0

    try:
        # Change to datagen directory for relative path resolution
        result = subprocess.run(
            docker_cmd,
            cwd=datagen_dir,
            check=True
        )

        logger.info("✓ ShadowTraffic data generation completed successfully")
        return result.returncode

    except subprocess.CalledProcessError as e:
        logger.error(f"✗ ShadowTraffic failed with exit code {e.returncode}")

        # Provide helpful error messages
        if e.returncode == 125:  # Docker daemon not running
            logger.error("Docker daemon may not be running. Try:")
            logger.error("  - Start Docker Desktop")
            logger.error("  - Or run: sudo systemctl start docker")
        elif e.returncode == 127:  # Docker not found
            logger.error("Docker command not found. Please install Docker:")
            logger.error("  - https://docs.docker.com/get-docker/")

        return e.returncode

    except KeyboardInterrupt:
        logger.info("⏹️  Data generation interrupted by user")
        return 130


def run_datagen(
    cloud_provider: str,
    duration: Optional[int] = None,
    messages_per_minute: Optional[int] = None,
    dry_run: bool = False,
    verbose: bool = False
) -> int:
    """
    Run the complete data generation workflow.

    Args:
        cloud_provider: Target cloud provider (aws/azure/terraform)
        duration: Duration to run in seconds
        messages_per_minute: Orders per minute to generate
        dry_run: If True, validate setup but don't run
        verbose: If True, show detailed output

    Returns:
        Exit code (0 for success)
    """
    logger = logging.getLogger(__name__)

    try:
        # Get project root and find directories
        project_root = get_project_root()
        paths = find_datagen_directories(cloud_provider, project_root)

        # Check dependencies
        logger.info("🔧 Checking dependencies...")
        deps = check_dependencies()
        if not validate_dependencies(deps):
            return 1

        # Extract credentials from terraform
        logger.info(f"📡 Extracting {cloud_provider.upper()} credentials...")
        credentials = extract_kafka_credentials(cloud_provider, project_root)

        # Generate connection files
        generate_all_connections(credentials, paths["connections_dir"])

        # Check ShadowTraffic configuration
        if not check_shadowtraffic_config(paths):
            return 1

        # Run ShadowTraffic
        return run_shadowtraffic(paths, duration, messages_per_minute, dry_run)

    except Exception as e:
        logger.error(f"Data generation failed: {e}")
        if verbose:
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
        return 1


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog="datagen",
        description="Generate streaming data with ShadowTraffic and Docker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run lab1_datagen                      # Auto-detect cloud provider
  uv run lab1_datagen aws                  # Generate data for AWS environment
  uv run lab1_datagen azure                # Generate data for Azure environment
  uv run lab1_datagen --duration 300       # Run for 5 minutes
  uv run lab1_datagen -m 10                # Generate 10 orders per minute
  uv run lab1_datagen -m 30 --duration 120 # Generate 30 orders/min for 2 minutes
  uv run lab1_datagen --dry-run            # Validate setup only

Traditional Python:
  python scripts/lab1_datagen.py

Dependencies:
  - Docker: https://docs.docker.com/get-docker/
  - jq: https://jqlang.github.io/jq/download/
  - Terraform: https://developer.hashicorp.com/terraform/install
        """.strip()
    )

    parser.add_argument(
        "cloud_provider",
        nargs="?",
        choices=["aws", "azure", "terraform"],
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
        help="Orders per minute to generate (default: ~0.65/min, roughly 1 per 90 seconds)"
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
    logger.info("Quickstart Streaming Agents - Data Generation")

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
                # For datagen, also suggest terraform option
                logger.info("  ✓ terraform (if using terraform/data-gen directory)")
                sys.exit(1)
        else:
            # For datagen, validate includes terraform option
            if cloud_provider not in ["aws", "azure", "terraform"]:
                logger.error(f"Unsupported cloud provider: {cloud_provider}")
                logger.error("Supported providers: aws, azure, terraform")
                sys.exit(1)

        logger.info(f"Target cloud provider: {cloud_provider.upper()}")

        # For aws/azure, validate terraform state
        if cloud_provider in ["aws", "azure"]:
            if not validate_terraform_state(cloud_provider, project_root):
                logger.error(f"Terraform state validation failed for {cloud_provider}")
                logger.error(f"Please run 'terraform apply' in {cloud_provider}/core/ and {cloud_provider}/lab1-tool-calling/")
                sys.exit(1)

        # Run data generation
        exit_code = run_datagen(
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