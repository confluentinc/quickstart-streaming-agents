"""
Cloud provider auto-detection utilities.

Provides functions to automatically detect the target cloud provider based on:
- Current working directory context
- Terraform state file analysis
- Environment variables
- Command-line hints
"""

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def detect_from_directory(cwd: Optional[Path] = None) -> Optional[str]:
    """
    Detect cloud provider from current working directory.

    Args:
        cwd: Current working directory (defaults to os.getcwd())

    Returns:
        'aws', 'azure', 'terraform', or None if not detected
    """
    if cwd is None:
        cwd = Path.cwd()

    cwd_str = str(cwd).lower()

    # Check if we're in the terraform directory
    if "/terraform/" in cwd_str or cwd_str.endswith("/terraform"):
        logger.debug(f"Detected terraform from directory: {cwd}")
        return "terraform"

    return None


def detect_from_state_files(project_root: Optional[Path] = None) -> Optional[str]:
    """
    Detect cloud provider by checking which terraform state files exist.

    Args:
        project_root: Project root directory (defaults to auto-detection)

    Returns:
        'aws', 'azure', 'terraform', or None if not detected
    """
    if project_root is None:
        from .terraform import get_project_root
        project_root = get_project_root()

    # Check for unified terraform directory state files
    terraform_core = project_root / "terraform" / "core" / "terraform.tfstate"
    if terraform_core.exists():
        # Read state file to determine actual cloud provider
        try:
            import json
            with open(terraform_core, 'r') as f:
                state = json.load(f)
            # Try to find cloud_provider in outputs
            outputs = state.get("outputs", {})
            if "cloud_provider" in outputs:
                cloud = outputs["cloud_provider"].get("value", "").lower()
                if cloud in ("aws", "azure"):
                    logger.debug(f"Detected {cloud} from terraform state file")
                    return cloud
        except Exception:
            pass
        logger.debug("Detected terraform from state files")
        return "terraform"

    return None


def detect_from_environment() -> Optional[str]:
    """
    Detect cloud provider from environment variables.

    Returns:
        'aws', 'azure', or None if not detected
    """
    # Check for cloud-specific environment variables
    if any(key.startswith("AWS_") for key in os.environ):
        logger.debug("Detected AWS from environment variables")
        return "aws"

    if any(key.startswith("AZURE_") for key in os.environ):
        logger.debug("Detected Azure from environment variables")
        return "azure"

    return None


def auto_detect_cloud_provider(
    cwd: Optional[Path] = None, project_root: Optional[Path] = None
) -> Optional[str]:
    """
    Automatically detect cloud provider using multiple strategies.

    Tries detection methods in this order:
    1. Directory context (most reliable)
    2. Terraform state files
    3. Environment variables

    Args:
        cwd: Current working directory (defaults to os.getcwd())
        project_root: Project root directory (defaults to auto-detection)

    Returns:
        'aws', 'azure', 'terraform', or None if not detected
    """
    logger.debug("Auto-detecting cloud provider...")

    # Strategy 1: Directory context
    cloud = detect_from_directory(cwd)
    if cloud:
        logger.info(f"Auto-detected cloud provider: {cloud} (from directory)")
        return cloud

    # Strategy 2: Terraform state files
    cloud = detect_from_state_files(project_root)
    if cloud:
        logger.info(f"Auto-detected cloud provider: {cloud} (from state files)")
        return cloud

    # Strategy 3: Environment variables
    cloud = detect_from_environment()
    if cloud:
        logger.info(f"Auto-detected cloud provider: {cloud} (from environment)")
        return cloud

    logger.warning("Could not auto-detect cloud provider")
    logger.warning("Please specify cloud provider explicitly: aws, azure, or terraform")
    return None


def validate_cloud_provider(cloud_provider: str) -> bool:
    """
    Validate that the given cloud provider is supported.

    Args:
        cloud_provider: Cloud provider name to validate

    Returns:
        True if valid, False otherwise
    """
    valid_providers = {"aws", "azure", "terraform"}
    is_valid = cloud_provider.lower() in valid_providers

    if not is_valid:
        logger.error(f"Unsupported cloud provider: {cloud_provider}")
        logger.error(f"Supported providers: {', '.join(sorted(valid_providers))}")

    return is_valid


def suggest_cloud_provider(project_root: Optional[Path] = None) -> None:
    """
    Provide helpful suggestions for specifying the cloud provider.

    Args:
        project_root: Project root directory (defaults to auto-detection)
    """
    if project_root is None:
        from .terraform import get_project_root
        try:
            project_root = get_project_root()
        except FileNotFoundError:
            logger.error("Could not find project root")
            return

    logger.info("Checking for terraform infrastructure:")

    # Check terraform directory
    terraform_dir = project_root / "terraform"
    terraform_core = terraform_dir / "core" / "terraform.tfstate"

    if terraform_core.exists():
        logger.info("  ✓ terraform infrastructure deployed (state file found)")

        # Try to detect cloud provider from state
        try:
            import json
            with open(terraform_core) as f:
                state = json.load(f)
                outputs = state.get("outputs", {})
                if "cloud_provider" in outputs:
                    cloud = outputs["cloud_provider"].get("value", "").lower()
                    logger.info(f"  ✓ Cloud provider: {cloud}")
        except Exception:
            pass
    elif terraform_dir.exists() and terraform_dir.is_dir():
        logger.info("  ✓ terraform directory found (not yet deployed)")
    else:
        logger.info("  ✗ terraform directory not found")

    logger.info("")
    logger.info("Usage examples:")
    logger.info("  uv run publish_docs    # Auto-detect")
    logger.info("  uv run lab1_datagen    # Auto-detect")