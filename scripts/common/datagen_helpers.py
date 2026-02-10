#!/usr/bin/env python3
"""
Common helper functions for data generation scripts.

Provides reusable functionality for ShadowTraffic data generation across multiple labs.
"""

import json
import logging
import subprocess
import tempfile
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


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
        elif dep == "terraform":
            logger.error("  - Terraform: https://developer.hashicorp.com/terraform/install")

    return False


def generate_connection_file(
    credentials: Dict[str, str],
    connection_name: str,
    output_path: Path
) -> None:
    """
    Generate a ShadowTraffic connection file.

    Args:
        credentials: Extracted Kafka credentials
        connection_name: Name of the connection (for logging)
        output_path: Path to write the connection file
    """
    logger = logging.getLogger(__name__)

    # Remove SASL_SSL:// prefix from bootstrap endpoint
    bootstrap_endpoint = credentials["bootstrap_servers"]
    if bootstrap_endpoint.startswith("SASL_SSL://"):
        bootstrap_endpoint = bootstrap_endpoint[11:]

    connection_config = {
        "kind": "kafka",
        "topicPolicy": {
            "policy": "create"
        },
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


def generate_all_connections(
    credentials: Dict[str, str],
    connections_dir: Path,
    connection_names: List[str]
) -> None:
    """
    Generate all required ShadowTraffic connection files.

    Args:
        credentials: Extracted Kafka credentials
        connections_dir: Directory to write connection files
        connection_names: List of connection file names (without .json extension)
    """
    logger = logging.getLogger(__name__)

    # Ensure connections directory exists
    connections_dir.mkdir(parents=True, exist_ok=True)

    logger.info("📝 Generating ShadowTraffic connection files...")

    for connection_name in connection_names:
        output_path = connections_dir / f"{connection_name}.json"
        generate_connection_file(credentials, connection_name, output_path)
        logger.info(f"✓ Created {connection_name}.json")

    logger.info(f"🎉 Successfully generated all connection files in: {connections_dir}")


def check_shadowtraffic_config(generators_dir: Path, required_generators: List[str]) -> bool:
    """
    Check that ShadowTraffic configuration files exist.

    Args:
        generators_dir: Directory containing generator files
        required_generators: List of required generator filenames

    Returns:
        True if all config files exist, False otherwise
    """
    logger = logging.getLogger(__name__)

    required_files = [generators_dir / gen for gen in required_generators]
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


def run_shadowtraffic_docker(
    datagen_dir: Path,
    connections_dir: Path,
    generators_dir: Path,
    root_config: Path,
    zones_dir: Optional[Path] = None,
    functions_dir: Optional[Path] = None,
    duration: Optional[int] = None,
    messages_per_minute: Optional[int] = None,
    dry_run: bool = False
) -> int:
    """
    Run ShadowTraffic data generation with Docker.

    Args:
        datagen_dir: Data generation directory
        connections_dir: Connections directory
        generators_dir: Generators directory
        root_config: Path to root.json configuration
        zones_dir: Optional zones directory (for lab3)
        functions_dir: Optional functions directory (for lab3)
        duration: Duration to run in seconds (optional)
        messages_per_minute: Messages per minute to generate (optional)
        dry_run: If True, validate setup but don't run

    Returns:
        Exit code (0 for success)
    """
    logger = logging.getLogger(__name__)

    # If messages_per_minute is specified, create modified root.json
    if messages_per_minute:
        throttle_ms = int(60000 / messages_per_minute)
        logger.info(f"📊 Setting message rate to {messages_per_minute} messages/minute (throttle: {throttle_ms}ms)")

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
            logger.info("📥 Deleting expired license and downloading fresh one...")

            # Delete the expired license file first to avoid permission issues
            try:
                env_file.unlink()
                logger.debug(f"Deleted expired license file: {env_file}")
            except Exception as e:
                logger.warning(f"Could not delete expired license file: {e}")
                # Continue anyway - download will attempt to overwrite

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

    # Add zones directory if it exists
    if zones_dir and zones_dir.exists():
        docker_cmd.extend(["-v", f"{zones_dir}:/home/zones"])

    # Add functions directory if it exists (for lab3)
    if functions_dir and functions_dir.exists():
        docker_cmd.extend(["-v", f"{functions_dir}:/home/functions"])

    # Add environment file if found
    if env_file:
        docker_cmd.extend(["--env-file", str(env_file)])

    # Add duration if specified
    shadowtraffic_args = ["--config", "/home/root.json"]
    if duration:
        shadowtraffic_args.extend(["--duration", str(duration)])

    docker_cmd.extend([
        "shadowtraffic/shadowtraffic:1.14.1"  # pinned for stability
    ] + shadowtraffic_args)

    logger.info(f"🚀 Starting ShadowTraffic data generation...")
    logger.info(f"   Config: {root_config}")
    logger.info(f"   Connections: {connections_dir}")
    logger.info(f"   Generators: {generators_dir}")

    if zones_dir and zones_dir.exists():
        logger.info(f"   Zones: {zones_dir}")
    if functions_dir and functions_dir.exists():
        logger.info(f"   Functions: {functions_dir}")
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
