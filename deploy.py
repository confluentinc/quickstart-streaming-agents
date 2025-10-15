#!/usr/bin/env python3
"""
Streaming Agents Quickstart Setup Script

Cross-platform automated setup and deployment for the quickstart-streaming-agents project.
Designed for non-technical users to easily deploy streaming agents infrastructure.
"""

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class SetupState(Enum):
    """Enum tracking the current setup state."""

    FRESH_START = "fresh_start"
    PREREQUISITES_NEEDED = "prerequisites_needed"
    CONFIGURATION_INCOMPLETE = "configuration_incomplete"
    CONFIGURATION_INVALID = "configuration_invalid"
    TERRAFORM_NOT_INITIALIZED = "terraform_not_initialized"
    TERRAFORM_PLAN_NEEDED = "terraform_plan_needed"
    DEPLOYMENT_READY = "deployment_ready"
    DEPLOYMENT_FAILED = "deployment_failed"
    COMPLETED = "completed"


class SetupUI:
    """Simple user interface handler."""

    def print_success(self, message: str):
        print(f"✅ {message}")

    def print_error(self, message: str):
        print(f"❌ {message}")

    def print_warning(self, message: str):
        print(f"⚠️  {message}")

    def print_info(self, message: str):
        print(f"ℹ️  {message}")

    def print_header(self, title: str, subtitle: str = ""):
        print(f"\n=== {title} ===")
        if subtitle:
            print(f"{subtitle}")
        print("")

    def prompt(self, message: str, default: str = None) -> str:
        prompt_text = f"{message}"
        if default:
            prompt_text += f" [{default}]"
        prompt_text += ": "
        try:
            response = input(prompt_text).strip()
            return response if response else (default or "")
        except EOFError:
            return default or ""

    def confirm(self, message: str, default: bool = True) -> bool:
        default_text = "Y/n" if default else "y/N"
        try:
            response = input(f"{message} [{default_text}]: ").strip().lower()
            if not response:
                return default
            return response.startswith("y")
        except EOFError:
            return default


class PrerequisiteManager:
    """Manages checking and installation of required tools."""

    TOOLS = {
        "git": {
            "check_cmd": ["git", "--version"],
            "macos_install": "brew install git",
            "windows_install": "winget install --id Git.Git -e",
        },
        "terraform": {
            "check_cmd": ["terraform", "--version"],
            "macos_install": "brew tap hashicorp/tap && brew install hashicorp/tap/terraform",
            "windows_install": "winget install --id Hashicorp.Terraform -e",
        },
        "confluent": {
            "check_cmd": ["confluent", "--version"],
            "macos_install": "brew install --cask confluent-cli",
            "windows_install": "winget install --id ConfluentInc.Confluent-CLI -e",
        },
        "docker": {
            "check_cmd": ["docker", "--version"],
            "macos_install": "brew install --cask docker-desktop",
            "windows_install": "winget install --id Docker.DockerDesktop -e",
        },
    }

    def __init__(self, ui: SetupUI):
        self.ui = ui
        self.system = platform.system().lower()

    def check_tool(self, tool_name: str) -> bool:
        """Check if a tool is installed."""
        try:
            result = subprocess.run(
                self.TOOLS[tool_name]["check_cmd"],
                capture_output=True,
                text=True,
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def install_tool(self, tool_name: str) -> bool:
        """Install a tool based on the current platform."""
        if self.system == "darwin":
            install_cmd = self.TOOLS[tool_name]["macos_install"]
        elif self.system == "windows":
            install_cmd = self.TOOLS[tool_name]["windows_install"]
        else:
            self.ui.print_error(
                f"Unsupported platform for automatic installation: {self.system}"
            )
            return False

        self.ui.print_info(f"Installing {tool_name}...")
        try:
            subprocess.run(
                install_cmd, shell=True, check=True, capture_output=True, text=True
            )
            self.ui.print_success(f"{tool_name} installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.ui.print_error(f"Failed to install {tool_name}: {e}")
            return False

    def check_and_install_prerequisites(self) -> bool:
        """Check all prerequisites and offer to install missing ones."""
        self.ui.print_header(
            "Checking Prerequisites", "Verifying required tools are installed"
        )

        missing_tools = []
        for tool_name in self.TOOLS.keys():
            if not self.check_tool(tool_name):
                missing_tools.append(tool_name)
            else:
                self.ui.print_success(f"{tool_name} is installed")

        if not missing_tools:
            self.ui.print_success("All prerequisites are installed!")
            return True

        self.ui.print_warning(f"Missing tools: {', '.join(missing_tools)}")

        if not self.ui.confirm(
            "Would you like to install missing tools automatically?"
        ):
            self.ui.print_error(
                "Cannot proceed without required tools. Please install manually:"
            )
            for tool in missing_tools:
                if self.system == "darwin":
                    self.ui.print_info(f"  {tool}: {self.TOOLS[tool]['macos_install']}")
                elif self.system == "windows":
                    self.ui.print_info(
                        f"  {tool}: {self.TOOLS[tool]['windows_install']}"
                    )
            return False

        # Install missing tools
        failed_installs = []
        for tool in missing_tools:
            if not self.install_tool(tool):
                failed_installs.append(tool)

        if failed_installs:
            self.ui.print_error(f"Failed to install: {', '.join(failed_installs)}")
            return False

        # Verify installations
        for tool in missing_tools:
            if not self.check_tool(tool):
                self.ui.print_error(f"Installation verification failed for {tool}")
                return False

        self.ui.print_success("All prerequisites installed successfully!")
        return True


class ConfigurationManager:
    """Manages configuration file creation and validation."""

    # Only regions that support MongoDB Atlas M0 free tier
    CLOUD_REGIONS = {
        "aws": [
            "us-east-1",
            "us-west-2",
            "sa-east-1",
            "ap-southeast-1",
            "ap-southeast-2",
            "ap-south-1",
            "ap-east-1",
            "ap-northeast-1",
            "ap-northeast-2",
        ],
        "azure": [
            "eastus2",
            "westus",
            "canadacentral",
            "northeurope",
            "westeurope",
            "eastasia",
            "centralindia",
        ],
    }

    def __init__(self, ui: SetupUI, terraform_dir: Path, root_dir: Path = None):
        self.ui = ui
        self.terraform_dir = terraform_dir
        self.root_dir = root_dir or terraform_dir
        self.tfvars_file = terraform_dir / "terraform.tfvars"
        self.config_file = None  # Will be set dynamically based on cloud provider
        self.cloud_provider = None  # Will be set when cloud provider is selected

    def set_config_file_path(self, cloud_provider: str):
        """Set config file path and cloud provider."""
        self.cloud_provider = cloud_provider.lower()
        self.config_file = (
            self.root_dir / self.cloud_provider / "core" / ".setup_config.json"
        )

    def prompt_for_lab_selection(self) -> str:
        """Prompt user to select which lab(s) to deploy."""
        self.ui.print_header("Lab Selection", "Choose which lab(s) to deploy")

        lab_options = {
            "1": ("lab1", "Lab1 - Tool Calling"),
            "2": ("lab2", "Lab2 - Vector Search/RAG"),
            "3": ("all", "All Labs"),
        }

        self.ui.print_info("Available labs:")
        for key, (_, description) in lab_options.items():
            print(f"  {key}. {description}")

        while True:
            choice = self.ui.prompt("Select lab (1-3)", "3").strip()
            if choice in lab_options:
                selection = lab_options[choice][0]
                description = lab_options[choice][1]
                self.ui.print_success(f"Selected: {description}")

                # Show Lab2-specific notes if selected
                if selection in ["lab2", "all"]:
                    self.ui.print_header("LAB2 Important Notes", "MongoDB Requirements")
                    self.ui.print_warning(
                        "LAB2 NOTE: You MUST run MongoDB in the same region as Confluent Cloud. Make sure that you select a MongoDB Free Tier (M0) Cluster in the same region as Confluent Cloud."
                    )
                    self.ui.print_info("")
                    self.ui.print_warning(
                        "LAB2 NOTE: You MUST set the following values:"
                    )
                    print("")
                    print("```sh")
                    print('MONGODB_DATABASE   = "vector_search"')
                    print('MONGODB_COLLECTION = "documents"')
                    print('MONGODB_INDEX_NAME = "vector_index"')
                    print("```")
                    print("")

                return selection
            self.ui.print_error("Please select 1, 2, or 3")

    def load_existing_config(self) -> Dict[str, str]:
        """Load existing configuration from tfvars and config files for selected cloud provider."""
        config = {}

        # Load from setup config file for selected cloud provider
        if self.config_file and self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config.update(json.load(f))
            except Exception:
                pass

        # Load credentials from terraform.tfvars files for selected cloud provider
        if self.cloud_provider:
            tfvars_configs = self.load_cloud_terraform_configs(self.cloud_provider)
            config.update(tfvars_configs)

        return config

    def load_cloud_terraform_configs(self, cloud_provider: str) -> Dict[str, str]:
        """Load configuration from terraform.tfvars files for specific cloud provider."""
        config = {}

        # Load from core terraform.tfvars for selected cloud provider
        core_tfvars = self.root_dir / cloud_provider / "core" / "terraform.tfvars"
        if core_tfvars.exists():
            core_config = self.parse_tfvars_file(core_tfvars)
            config.update(core_config)

        # Load from lab-specific terraform.tfvars files for selected cloud provider
        for lab in ["lab1-tool-calling", "lab2-vector-search"]:
            lab_tfvars = self.root_dir / cloud_provider / lab / "terraform.tfvars"
            if lab_tfvars.exists():
                lab_config = self.parse_tfvars_file(lab_tfvars)
                config.update(lab_config)

        return config

    def load_all_terraform_configs(self) -> Dict[str, str]:
        """Load configuration from all terraform.tfvars files (backward compatibility)."""
        if self.cloud_provider:
            return self.load_cloud_terraform_configs(self.cloud_provider)
        else:
            # Fallback to old behavior if cloud provider not set
            config = {}
            for cloud_provider in ["aws", "azure"]:
                cloud_config = self.load_cloud_terraform_configs(cloud_provider)
                config.update(cloud_config)
            return config

    def parse_tfvars_file(self, file_path: Path) -> Dict[str, str]:
        """Parse a terraform.tfvars file and return key-value pairs."""
        config = {}
        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Parse simple key-value pairs
            for line in content.split("\n"):
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip(" \"'")  # Remove quotes and extra spaces
                    # Clean up comment suffixes
                    if "#" in value:
                        value = value.split("#")[0].strip(" \"'")
                    # Only store non-empty values
                    if value:
                        config[key] = value
        except Exception:
            pass

        return config

    def is_placeholder_value(self, key: str, value: str) -> bool:
        """Simplified placeholder check."""
        return not value or value.startswith("your-") or value.startswith("<<")

    def is_first_run(self) -> bool:
        """Check if this is the user's first run based on existing valid configs."""
        if not self.cloud_provider:
            return True

        # Check if we have valid terraform.tfvars with real credentials
        config = self.load_existing_config()

        # Core required fields that indicate a real setup
        core_fields = [
            "prefix",
            "cloud_provider",
            "confluent_cloud_api_key",
            "confluent_cloud_api_secret",
        ]

        for field in core_fields:
            value = config.get(field, "")
            if not value or self.is_placeholder_value(field, value):
                return True  # Missing or placeholder values = first run

        return False  # All core fields have real values = not first run

    def validate_config_value(
        self, key: str, value: str, config_context: Dict[str, str] = None
    ) -> bool:
        """Validate a configuration value."""
        if not value or self.is_placeholder_value(key, value):
            return False

        config_context = config_context or {}

        if key == "confluent_cloud_api_key":
            # Basic format check first
            if not (len(value) >= 10 and value.isalnum()):
                return False
            # If we have both key and secret, test them
            secret = config_context.get("confluent_cloud_api_secret")
            if secret and len(secret) >= 20:
                try:
                    valid, _ = self.test_confluent_api_keys(value, secret)
                    return valid
                except:
                    # Fall back to format validation if API test fails
                    return True
            return True

        elif key == "confluent_cloud_api_secret":
            # Basic format check first
            if not (len(value) >= 20 and not value.startswith("your-")):
                return False
            # If we have both key and secret, test them
            api_key = config_context.get("confluent_cloud_api_key")
            if api_key and len(api_key) >= 10:
                try:
                    valid, _ = self.test_confluent_api_keys(api_key, value)
                    return valid
                except:
                    # Fall back to format validation if API test fails
                    return True
            return True

        elif key == "ZAPIER_SSE_ENDPOINT":
            return self.validate_zapier_url(value)
        elif key == "cloud_provider":
            return value.lower() in ["aws", "azure"]
        elif key == "cloud_region":
            provider = config_context.get(
                "cloud_provider"
            ) or self.load_existing_config().get("cloud_provider", "azure")
            return value in self.CLOUD_REGIONS.get(provider.lower(), [])
        elif key == "prefix":
            return bool(re.match(r"^[a-zA-Z0-9\-_]+$", value))

        return True

    def get_config_status(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        """Get current config with valid and invalid fields separated."""
        repaired_config = self.load_existing_config()

        valid_config = {}
        invalid_config = {}

        # Core required fields - always needed
        required_fields = [
            "prefix",
            "cloud_provider",
            "cloud_region",
            "confluent_cloud_api_key",
            "confluent_cloud_api_secret",
        ]

        # If this is first run, treat defaults as invalid (need confirmation)
        first_run = self.is_first_run()

        for field in required_fields:
            value = repaired_config.get(field, "")
            # On first run, even default values need user confirmation
            if (
                value
                and self.validate_config_value(field, value, repaired_config)
                and not first_run
            ):
                valid_config[field] = value
            else:
                invalid_config[field] = value

        return valid_config, invalid_config

    def detect_environment_credentials(self) -> Dict[str, str]:
        """Detect credentials from environment and CLI."""
        env_creds = {}

        # Check environment variables
        env_key = os.getenv("CONFLUENT_CLOUD_API_KEY")
        env_secret = os.getenv("CONFLUENT_CLOUD_API_SECRET")

        if env_key and env_secret:
            if self.validate_config_value("confluent_cloud_api_key", env_key):
                env_creds["confluent_cloud_api_key"] = env_key
            if self.validate_config_value("confluent_cloud_api_secret", env_secret):
                env_creds["confluent_cloud_api_secret"] = env_secret

        # Check if Confluent CLI is logged in
        if self.check_confluent_login():
            env_creds["confluent_cli_logged_in"] = "true"

        return env_creds

    def save_config(self, config: Dict[str, str]):
        """Save non-sensitive configuration for future runs."""
        # Save all non-sensitive config, plus indicator that configuration was completed
        safe_config = {
            key: value
            for key, value in config.items()
            if key
            not in [
                "confluent_cloud_api_key",
                "confluent_cloud_api_secret",
                "ZAPIER_SSE_ENDPOINT",
            ]
        }
        # Add a marker to indicate configuration was completed at least once
        safe_config["_config_completed"] = True

        try:
            with open(self.config_file, "w") as f:
                json.dump(safe_config, f, indent=2)
        except Exception:
            pass

    def save_field_incrementally(
        self, field: str, value: str, lab_selection: str = None
    ):
        """Simplified - just pass through (removed incremental complexity)."""
        pass

    def save_credentials_to_tfvars(self, config: Dict[str, str]):
        """Save configuration (including credentials) to terraform.tfvars files immediately."""
        try:
            # Load existing tfvars if it exists to merge with new config
            core_tfvars_file = self.terraform_dir / "core/terraform.tfvars"
            existing_core_config = {}

            if core_tfvars_file.exists():
                try:
                    existing_core_config = self._read_existing_tfvars(core_tfvars_file)
                except:
                    pass  # Continue with empty dict if read fails

            # Merge existing config with new config
            merged_config = {**existing_core_config, **config}

            # Always save what we have so far to core terraform.tfvars
            # Only include fields that have values
            core_config = {}
            core_fields = [
                "prefix",
                "cloud_provider",
                "cloud_region",
                "confluent_cloud_api_key",
                "confluent_cloud_api_secret",
                "azure_subscription_id",
            ]

            for field in core_fields:
                if field in merged_config and merged_config[field]:
                    core_config[field] = merged_config[field]

            if core_config:  # Only save if we have at least one field
                self._write_tfvars_file(core_tfvars_file.resolve(), core_config, "Core")

        except Exception:
            pass

    def _read_existing_tfvars(self, tfvars_file: Path) -> Dict[str, str]:
        """Read existing terraform.tfvars file and return as dict."""
        config = {}
        try:
            with open(tfvars_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"')
                        config[key] = value
        except Exception:
            pass  # Return empty dict if read fails
        return config

    def _write_tfvars_file(
        self, tfvars_file: Path, config: Dict[str, str], module_name: str
    ):
        """Helper to write terraform.tfvars content."""
        try:
            # Generate content based on module type
            if module_name == "Core":
                content = f"""# Core Infrastructure Configuration
prefix = "{config['prefix']}"
cloud_provider = "{config['cloud_provider']}"
cloud_region = "{config['cloud_region']}"
confluent_cloud_api_key = "{config['confluent_cloud_api_key']}"
confluent_cloud_api_secret = "{config['confluent_cloud_api_secret']}"
"""
                if "azure_subscription_id" in config:
                    content += (
                        f'azure_subscription_id = "{config["azure_subscription_id"]}"\n'
                    )
            else:
                # Lab-specific content would go here
                content = f"""# {module_name} Configuration
prefix = "{config['prefix']}"
cloud_region = "{config['cloud_region']}"
"""

            # Backup existing file
            if tfvars_file.exists():
                backup_path = tfvars_file.with_suffix(".tfvars.backup")
                shutil.copy2(tfvars_file, backup_path)

            # Write new content
            with open(tfvars_file, "w") as f:
                f.write(content)

        except Exception:
            pass

    def test_confluent_api_keys(
        self, api_key: str, api_secret: str
    ) -> Tuple[bool, str]:
        """Test if Confluent API keys are valid and have proper scope."""
        try:
            import base64

            try:
                import requests
            except ImportError:
                # If requests is not available, skip validation but assume keys are valid
                return (
                    True,
                    "API keys format looks valid (network validation skipped - requests module not available)",
                )

            # Create basic auth header
            credentials = base64.b64encode(f"{api_key}:{api_secret}".encode()).decode()
            headers = {
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/json",
            }

            # Test by listing organizations (requires cloud scope)
            response = requests.get(
                "https://api.confluent.cloud/org/v2/organizations",
                headers=headers,
                timeout=10,
            )

            if response.status_code == 200:
                return True, "API keys are valid and have proper cloud scope"
            elif response.status_code == 401:
                return False, "API keys are invalid or expired"
            elif response.status_code == 403:
                return (
                    False,
                    "API keys don't have sufficient permissions (need Cloud Resource Management scope)",
                )
            else:
                return (
                    False,
                    f"API test failed with status {response.status_code}: {response.text}",
                )

        except Exception as e:
            # Check if it's a requests-related error
            if "requests" in str(e).lower():
                return True, "API keys format looks valid (network validation failed)"
            return False, f"Error testing API keys: {str(e)}"

    def validate_zapier_url(self, url: str) -> bool:
        """Validate Zapier SSE endpoint URL format and reject placeholders."""
        if not url:
            return False

        # Reject known placeholder/sample URLs
        placeholder_patterns = [
            "test-key",
            "test-api-key",
            "<<API-key>>",
            "<<long-API-key>>",
            "your-api-key",
            "sample-key",
            "placeholder",
        ]

        for pattern in placeholder_patterns:
            if pattern in url.lower():
                return False

        # Check proper format
        pattern = r"^https://mcp\.zapier\.com/api/mcp/s/[a-zA-Z0-9\-_=]{20,}/sse$"
        return bool(re.match(pattern, url))

    def prompt_for_configuration(self, non_interactive: bool = False) -> Dict[str, str]:
        """Interactive configuration prompting."""
        self.ui.print_header(
            "Configuration Setup", "Please provide the following information"
        )

        existing_config = self.load_existing_config()
        config = {}

        # In non-interactive mode, use existing config or defaults
        if non_interactive:
            self.ui.print_info(
                "Using existing configuration for dry-run"
                if existing_config
                else "Using default configuration for dry-run"
            )
            # Add required defaults for missing values
            defaults = {
                "prefix": "streaming-agents",
                "cloud_provider": "azure",
                "cloud_region": "East US",
                "confluent_cloud_api_key": "test-key",  # pragma: allowlist secret
                "confluent_cloud_api_secret": "test-secret",  # pragma: allowlist secret
                "ZAPIER_SSE_ENDPOINT": "https://mcp.zapier.com/api/mcp/s/test-api-key/sse",
                "owner_email": "",
            }
            for key, default_value in defaults.items():
                config[key] = existing_config.get(key, default_value)
            return config

        # Prefix (using default without prompting)
        config["prefix"] = "streaming-agents"

        # Cloud provider
        default_provider = existing_config.get("cloud_provider", "azure").lower()
        while True:
            provider = self.ui.prompt(
                "Cloud provider (aws/azure)", default_provider
            ).lower()
            if provider in ["aws", "azure"]:
                config["cloud_provider"] = provider
                # Save basic config immediately
                self.save_credentials_to_tfvars(config)
                break
            self.ui.print_error("Please choose either 'aws' or 'azure'")

        # Cloud region
        available_regions = self.CLOUD_REGIONS[config["cloud_provider"]]
        self.ui.print_info(f"Available {config['cloud_provider'].upper()} regions:")
        for i, region in enumerate(available_regions, 1):
            print(f"  {i:2d}. {region}")

        default_region = existing_config.get("cloud_region", available_regions[0])
        while True:
            region_input = self.ui.prompt(
                f"Select region (name or number)", default_region
            )

            if region_input.isdigit():
                idx = int(region_input) - 1
                if 0 <= idx < len(available_regions):
                    config["cloud_region"] = available_regions[idx]
                    # Save config with region immediately
                    self.save_credentials_to_tfvars(config)
                    break
            elif region_input in available_regions:
                config["cloud_region"] = region_input
                # Save config with region immediately
                self.save_credentials_to_tfvars(config)
                break

            self.ui.print_error("Please select a valid region")

        # Confluent credentials
        self.ui.print_info("Confluent Cloud credentials are required for deployment")

        # Check environment variables first
        env_key = os.getenv("CONFLUENT_CLOUD_API_KEY")
        env_secret = os.getenv("CONFLUENT_CLOUD_API_SECRET")

        if env_key and env_secret:
            self.ui.print_success(
                "Found Confluent credentials in environment variables"
            )
            config["confluent_cloud_api_key"] = env_key
            config["confluent_cloud_api_secret"] = env_secret
            # Save credentials immediately
            self.save_credentials_to_tfvars(config)
        else:
            # Check if user is logged in to Confluent CLI
            confluent_logged_in = self.check_confluent_login()

            if confluent_logged_in and self.ui.confirm(
                "Auto-generate Confluent API keys using CLI?"
            ):
                api_key, api_secret = self.generate_confluent_api_keys(config["prefix"])
                if api_key and api_secret:
                    config["confluent_cloud_api_key"] = api_key
                    config["confluent_cloud_api_secret"] = api_secret
                    self.ui.print_success("Generated Confluent API keys successfully")
                    # Save credentials immediately
                    self.save_credentials_to_tfvars(config)
                else:
                    self.ui.print_error(
                        "Failed to generate API keys, please enter manually"
                    )

            # Manual entry if auto-generation failed or was declined
            if "confluent_cloud_api_key" not in config:
                config["confluent_cloud_api_key"] = self.ui.prompt(
                    "Confluent Cloud API Key"
                )
                config["confluent_cloud_api_secret"] = self.ui.prompt(
                    "Confluent Cloud API Secret"
                )
                # Save credentials immediately after manual entry
                self.save_credentials_to_tfvars(config)

        # Zapier SSE endpoint
        default_zapier_url = existing_config.get("ZAPIER_SSE_ENDPOINT", "")
        while True:
            zapier_url = self.ui.prompt(
                "Zapier SSE Endpoint (from Zapier MCP server)", default_zapier_url
            )
            if self.validate_zapier_url(zapier_url):
                config["ZAPIER_SSE_ENDPOINT"] = zapier_url
                # Save config immediately after Zapier endpoint
                self.save_credentials_to_tfvars(config)
                break
            self.ui.print_error(
                "Invalid Zapier SSE endpoint format. Expected: https://mcp.zapier.com/api/mcp/s/<<API-key>>/sse"
            )

        # Owner email (optional, for tagging cloud resources)
        self.ui.print_info("For proper tagging of cloud resources (optional)")
        default_email = existing_config.get("owner_email", "")
        owner_email = self.ui.prompt("Email", default_email)
        config["owner_email"] = owner_email
        # Save config immediately after owner email
        self.save_credentials_to_tfvars(config)

        return config

    def check_confluent_login(self) -> bool:
        """Check if user is logged into Confluent CLI."""
        try:
            # Try to list environments - this requires authentication
            result = subprocess.run(
                ["confluent", "environment", "list"],
                capture_output=True,
                text=True,
                check=True,
            )
            # Check if we got a proper environment listing (contains ID column and at least one environment)
            return (
                len(result.stdout.strip()) > 0
                and "ID" in result.stdout
                and "env-" in result.stdout
            )
        except subprocess.CalledProcessError:
            return False
        except FileNotFoundError:
            # Confluent CLI not installed
            return False

    def get_confluent_environments(self) -> List[Dict[str, str]]:
        """Get list of available Confluent environments."""
        try:
            result = subprocess.run(
                ["confluent", "environment", "list", "--output", "json"],
                capture_output=True,
                text=True,
                check=True,
            )
            environments = json.loads(result.stdout)
            return environments if isinstance(environments, list) else []
        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
            # Fallback to text parsing if JSON output not available
            try:
                result = subprocess.run(
                    ["confluent", "environment", "list"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                environments = []
                lines = result.stdout.strip().split("\n")
                for line in lines[2:]:  # Skip header lines
                    if line.strip() and "|" in line:
                        parts = [p.strip() for p in line.split("|")]
                        if len(parts) >= 3:
                            environments.append(
                                {
                                    "id": parts[1],
                                    "name": parts[2] if len(parts) > 2 else parts[1],
                                }
                            )
                return environments
            except:
                return []

    def select_confluent_environment(self) -> Optional[str]:
        """Select Confluent environment to use for this project."""
        environments = self.get_confluent_environments()

        if not environments:
            self.ui.print_error(
                "No Confluent environments found. Please create one first."
            )
            return None

        if len(environments) == 1:
            env = environments[0]
            env_name = env.get("name", env.get("id", "Unknown"))
            self.ui.print_success(f"Using environment: {env_name}")
            return env.get("id")

        # Multiple environments - let user choose
        self.ui.print_info("Multiple Confluent environments found:")
        for i, env in enumerate(environments, 1):
            env_name = env.get("name", env.get("id", "Unknown"))
            env_id = env.get("id", "")
            print(f"  {i:2d}. {env_name} ({env_id})")

        while True:
            choice = self.ui.prompt(f"Select environment (1-{len(environments)})", "1")
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(environments):
                    selected = environments[idx]
                    env_name = selected.get("name", selected.get("id", "Unknown"))
                    self.ui.print_success(f"Selected environment: {env_name}")
                    return selected.get("id")
                else:
                    self.ui.print_error(
                        f"Please select a number between 1 and {len(environments)}"
                    )
            except ValueError:
                self.ui.print_error("Please enter a valid number")

    def generate_confluent_api_keys(
        self, prefix: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """Generate Confluent API keys using CLI."""
        try:
            # Create service account (no environment creation needed - Terraform handles that)
            import time

            timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
            sa_name = f"{prefix}-setup-sa-{timestamp}"
            self.ui.print_info(f"Creating service account: {sa_name}")

            sa_result = subprocess.run(
                [
                    "confluent",
                    "iam",
                    "service-account",
                    "create",
                    sa_name,
                    "--description",
                    f"Service account for {prefix} streaming agents setup",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            # Extract service account ID from table format
            sa_id = None
            for line in sa_result.stdout.split("\n"):
                line = line.strip()
                if "| ID" in line and "sa-" in line:
                    # Format: | ID          | sa-xxxxxxx |
                    parts = [p.strip() for p in line.split("|") if p.strip()]
                    if len(parts) >= 2 and "ID" in parts[0]:
                        sa_id = parts[1]
                        break

            if not sa_id:
                return None, None

            # Create API key
            self.ui.print_info("Creating API key with Cloud Resource Management scope")

            key_result = subprocess.run(
                [
                    "confluent",
                    "api-key",
                    "create",
                    "--service-account",
                    sa_id,
                    "--resource",
                    "cloud",
                    "--description",
                    f"{prefix} setup key",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            # Extract API key and secret
            api_key = api_secret = None
            lines = key_result.stdout.split("\n")
            for line in lines:
                line = line.strip()
                if "API Key" in line and "|" in line:
                    # Format: | API Key    | XXXXXXXXXXXXXXXXXXXX |
                    parts = [p.strip() for p in line.split("|") if p.strip()]
                    if len(parts) >= 2 and "API Key" in parts[0]:
                        api_key = parts[1]
                elif "API Secret" in line and "|" in line:
                    # Format: | API Secret | XXXXXXXXXXXXXXXXXXXX |
                    parts = [p.strip() for p in line.split("|") if p.strip()]
                    if len(parts) >= 2 and "API Secret" in parts[0]:
                        api_secret = parts[1]

            if api_key and api_secret:
                # Assign Organization Admin role to the service account
                try:
                    self.ui.print_info("Assigning OrganizationAdmin role...")
                    role_result = subprocess.run(
                        [
                            "confluent",
                            "iam",
                            "rbac",
                            "role-binding",
                            "create",
                            "--principal",
                            f"User:{sa_id}",
                            "--role",
                            "OrganizationAdmin",
                        ],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    self.ui.print_success(
                        "OrganizationAdmin role assigned successfully"
                    )
                except subprocess.CalledProcessError as e:
                    self.ui.print_warning(
                        "Role assignment failed, but API keys were created successfully"
                    )

                return api_key, api_secret

        except subprocess.CalledProcessError as e:
            self.ui.print_error(f"Command failed: {e}")
        except Exception as e:
            self.ui.print_error(f"Unexpected error: {e}")

        return None, None


class TerraformManager:
    """Manages Terraform operations."""

    def __init__(self, ui: SetupUI, terraform_dir: Path):
        self.ui = ui
        self.terraform_dir = terraform_dir

    def run_terraform_command(
        self, args: List[str], show_output: bool = True, cloud_provider: str = None
    ) -> Tuple[bool, str]:
        """Run a terraform command with proper error handling."""
        cmd = ["terraform"] + args

        # Set environment variables to prevent Azure provider authentication when using AWS
        env = os.environ.copy()
        if cloud_provider and cloud_provider.lower() == "aws":
            # Set dummy Azure credentials to prevent authentication attempts
            env["ARM_SKIP_PROVIDER_REGISTRATION"] = "true"
            env["ARM_USE_CLI"] = "false"
            env["ARM_USE_MSI"] = "false"
            env["ARM_USE_OIDC"] = "false"
            # Provide dummy credentials to satisfy the provider
            env["ARM_SUBSCRIPTION_ID"] = "00000000-0000-0000-0000-000000000000"
            env["ARM_CLIENT_ID"] = "00000000-0000-0000-0000-000000000000"
            env["ARM_CLIENT_SECRET"] = "dummy"  # pragma: allowlist secret
            env["ARM_TENANT_ID"] = "00000000-0000-0000-0000-000000000000"

        try:
            if show_output:
                # Stream output for long-running commands
                process = subprocess.Popen(
                    cmd,
                    cwd=self.terraform_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    env=env,
                )

                output_lines = []
                for line in iter(process.stdout.readline, ""):
                    print(line.rstrip())
                    output_lines.append(line.rstrip())

                process.wait()
                output = "\n".join(output_lines)
                success = process.returncode == 0
            else:
                # Capture output for quiet commands
                result = subprocess.run(
                    cmd,
                    cwd=self.terraform_dir,
                    capture_output=True,
                    text=True,
                    check=True,
                    env=env,
                )
                output = result.stdout
                success = True

        except subprocess.CalledProcessError as e:
            output = e.stderr if hasattr(e, "stderr") else str(e)
            success = False

        return success, output

    def enable_provider_file(self, cloud_provider: str):
        """Enable the appropriate provider file for the selected cloud provider and disable others."""
        cloud_provider = cloud_provider.lower()

        # Define all supported providers
        all_providers = ["aws", "azure"]

        # Disable all other providers first
        for provider in all_providers:
            if provider != cloud_provider:
                provider_file = self.terraform_dir / f"providers-{provider}.tf"
                disabled_file = self.terraform_dir / f"providers-{provider}.tf.disabled"

                if provider_file.exists():
                    try:
                        provider_file.rename(disabled_file)
                        self.ui.print_info(f"Disabled {provider} provider")
                    except Exception as e:
                        self.ui.print_error(
                            f"Failed to disable {provider} provider: {e}"
                        )
                        raise

        # Enable the selected provider
        provider_file = self.terraform_dir / f"providers-{cloud_provider}.tf"
        disabled_file = self.terraform_dir / f"providers-{cloud_provider}.tf.disabled"

        if disabled_file.exists():
            try:
                disabled_file.rename(provider_file)
                self.ui.print_success(f"Enabled {cloud_provider} provider")
            except Exception as e:
                self.ui.print_error(f"Failed to enable provider file: {e}")
                raise
        elif provider_file.exists():
            self.ui.print_info(f"{cloud_provider} provider already enabled")
        else:
            self.ui.print_warning(f"Provider file not found: {provider_file}")

    def initialize(self, cloud_provider: str = None) -> bool:
        """Initialize Terraform."""
        # Enable the appropriate provider file for the selected cloud provider
        if cloud_provider:
            self.enable_provider_file(cloud_provider)

        self.ui.print_info("Initializing Terraform...")
        success, output = self.run_terraform_command(
            ["init"], show_output=False, cloud_provider=cloud_provider
        )

        if success:
            self.ui.print_success("Terraform initialized successfully")
        else:
            self.ui.print_error("Terraform initialization failed")
            print(output)

        return success

    def plan(self, cloud_provider: str = None) -> bool:
        """Run terraform plan."""
        self.ui.print_info("Running Terraform plan (dry-run validation)...")
        success, output = self.run_terraform_command(
            ["plan"], show_output=True, cloud_provider=cloud_provider
        )

        if success:
            self.ui.print_success("Terraform plan completed successfully")
        else:
            self.ui.print_error("Terraform plan failed")

        return success

    def apply(self, cloud_provider: str = None) -> bool:
        """Run terraform apply."""
        self.ui.print_info("Deploying infrastructure with Terraform...")
        success, output = self.run_terraform_command(
            ["apply", "--auto-approve"], show_output=True, cloud_provider=cloud_provider
        )

        if success:
            self.ui.print_success("Infrastructure deployed successfully!")
        else:
            self.ui.print_error("Terraform deployment failed")

        return success

    def destroy(self, cloud_provider: str = None) -> bool:
        """Run terraform destroy."""
        self.ui.print_info("Destroying infrastructure with Terraform...")
        success, output = self.run_terraform_command(
            ["destroy", "--auto-approve"], show_output=True, cloud_provider=cloud_provider
        )

        if success:
            self.ui.print_success("Infrastructure destroyed successfully!")
        else:
            self.ui.print_error("Terraform destruction failed")

        return success


class StreamingAgentsSetup:
    """Main setup orchestrator."""

    def __init__(self, args):
        self.args = args
        self.ui = SetupUI()
        self.verbose = args.verbose

        # Setup paths
        self.root_dir = Path(__file__).parent
        self.terraform_dir = self.root_dir
        self.core_terraform_dir = None  # Will be set based on cloud provider

        # Initialize managers
        self.prerequisites = PrerequisiteManager(self.ui)
        self.config_manager = ConfigurationManager(
            self.ui, self.terraform_dir, self.root_dir
        )
        self.terraform = TerraformManager(self.ui, self.terraform_dir)

        # Check Confluent login status at startup
        self.confluent_logged_in = self._check_confluent_login_status()

    def set_terraform_dirs(self, cloud_provider: str):
        """Set terraform directories based on cloud provider."""
        cloud_provider = cloud_provider.lower()
        self.core_terraform_dir = self.root_dir / cloud_provider / "core"
        self.terraform_dir = self.root_dir / cloud_provider
        # Update config manager paths
        self.config_manager.set_config_file_path(cloud_provider)
        self.config_manager.terraform_dir = self.terraform_dir

    def check_core_deployment(self) -> bool:
        """Check if Core Terraform infrastructure is deployed with required outputs."""
        terraform_state = self.core_terraform_dir / "terraform.tfstate"

        if not terraform_state.exists():
            return False

        try:
            with open(terraform_state, "r") as f:
                state_data = json.load(f)

                # Check if state has resources (indicating successful deployment)
                resources = state_data.get("resources", [])
                if len(resources) == 0:
                    return False

                # Check if required outputs exist for labs to reference
                outputs = state_data.get("outputs", {})
                required_outputs = [
                    "confluent_environment_id",
                    "confluent_kafka_cluster_id",
                    "confluent_kafka_cluster_bootstrap_endpoint",
                    "confluent_schema_registry_id",
                    "confluent_schema_registry_rest_endpoint",
                    "confluent_flink_compute_pool_id",
                    "cloud_region",
                ]

                # Verify all required outputs exist and have values
                for output_name in required_outputs:
                    if output_name not in outputs:
                        return False

                    output_value = outputs[output_name].get("value")
                    if not output_value:
                        return False

                return True

        except Exception as e:
            return False

    def deploy_core_if_needed(self, config: Dict[str, str]) -> bool:
        """Deploy Core infrastructure if not already deployed."""
        if self.check_core_deployment():
            self.ui.print_success("Core infrastructure is already deployed")
            return True

        self.ui.print_info("Core infrastructure not found - deploying Core first...")

        # Write core terraform.tfvars
        core_tfvars_file = self.core_terraform_dir / "terraform.tfvars"
        core_config = {
            "prefix": config["prefix"],
            "cloud_provider": config["cloud_provider"],
            "cloud_region": config["cloud_region"],
            "confluent_cloud_api_key": config["confluent_cloud_api_key"],
            "confluent_cloud_api_secret": config["confluent_cloud_api_secret"],
        }

        # Add Azure subscription ID if Azure
        if config["cloud_provider"].lower() == "azure":
            # Use environment variable or prompt
            azure_sub_id = os.getenv("ARM_SUBSCRIPTION_ID")
            if not azure_sub_id:
                azure_sub_id = self.ui.prompt("Azure Subscription ID")
            core_config["azure_subscription_id"] = azure_sub_id

        self.write_terraform_tfvars(core_tfvars_file, core_config, "Core")

        # Deploy core
        core_terraform = TerraformManager(self.ui, self.core_terraform_dir)

        if not core_terraform.initialize(config["cloud_provider"]):
            return False

        if not core_terraform.plan(config["cloud_provider"]):
            return False

        # Apply core terraform
        if not core_terraform.apply(config["cloud_provider"]):
            self.ui.print_error("Core terraform deployment failed")
            return False

        # Verify deployment completed successfully with all required outputs
        if not self.check_core_deployment():
            self.ui.print_error(
                "Core deployment completed but required outputs are missing"
            )
            self.ui.print_info("This may indicate a partial deployment failure")
            return False

        self.ui.print_success(
            "✅ Core infrastructure deployed successfully with all required outputs"
        )
        return True

    def write_terraform_tfvars(
        self, tfvars_file: Path, config: Dict[str, str], module_name: str
    ):
        """Write configuration to a terraform.tfvars file."""
        # Backup existing file
        if tfvars_file.exists():
            backup_path = tfvars_file.with_suffix(".tfvars.backup")
            shutil.copy2(tfvars_file, backup_path)
            self.ui.print_info(
                f"Backed up existing {module_name} terraform.tfvars to {backup_path.name}"
            )

        # Create directory if needed
        tfvars_file.parent.mkdir(parents=True, exist_ok=True)

        # Generate tfvars content based on module type
        if module_name == "Core":
            tfvars_content = self.generate_core_tfvars_content(config)
        else:
            tfvars_content = self.generate_lab_tfvars_content(config, module_name)

        try:
            with open(tfvars_file, "w") as f:
                f.write(tfvars_content)

            self.ui.print_success(
                f"{module_name} configuration written to {tfvars_file}"
            )
        except Exception as e:
            self.ui.print_error(f"Failed to write {module_name} terraform.tfvars: {e}")
            raise

    def generate_core_tfvars_content(self, config: Dict[str, str]) -> str:
        """Generate terraform.tfvars content for Core module."""
        content = f"""# Core Infrastructure Configuration
prefix = "{config['prefix']}"
cloud_provider = "{config['cloud_provider']}"
cloud_region = "{config['cloud_region']}"
confluent_cloud_api_key = "{config['confluent_cloud_api_key']}"
confluent_cloud_api_secret = "{config['confluent_cloud_api_secret']}"
"""
        if "owner_email" in config and config["owner_email"]:
            content += f'owner_email = "{config["owner_email"]}"\n'

        if "azure_subscription_id" in config:
            content += f'azure_subscription_id = "{config["azure_subscription_id"]}"\n'

        return content

    def generate_lab_tfvars_content(self, config: Dict[str, str], lab_type: str) -> str:
        """Generate terraform.tfvars content for lab modules."""
        base_content = f"""# {lab_type} Configuration
prefix = "{config['prefix']}"
cloud_region = "{config['cloud_region']}"
"""

        if lab_type == "Lab1":
            base_content += f'ZAPIER_SSE_ENDPOINT = "{config["ZAPIER_SSE_ENDPOINT"]}"\n'
        elif lab_type == "Lab2":
            base_content += f"""MONGODB_CONNECTION_STRING = "{config["MONGODB_CONNECTION_STRING"]}"
mongodb_username = "{config["mongodb_username"]}"
mongodb_password = "{config["mongodb_password"]}"

# Default MongoDB settings (using defaults, not prompted)
MONGODB_DATABASE = "vector_search"
MONGODB_COLLECTION = "documents"
MONGODB_INDEX_NAME = "vector_index"
"""

        return base_content

    def deploy_labs(self, lab_selection: str, config: Dict[str, str]) -> bool:
        """Deploy selected lab(s) after Core is deployed."""
        cloud_provider = config["cloud_provider"].lower()

        labs_to_deploy = []
        if lab_selection == "lab1":
            labs_to_deploy = ["lab1-tool-calling"]
        elif lab_selection == "lab2":
            labs_to_deploy = ["lab2-vector-search"]
        elif lab_selection == "all":
            labs_to_deploy = ["lab1-tool-calling", "lab2-vector-search"]

        for lab_name in labs_to_deploy:
            lab_dir = self.root_dir / cloud_provider / lab_name
            if not lab_dir.exists():
                self.ui.print_error(f"Lab directory not found: {lab_dir}")
                return False

            self.ui.print_info(f"Deploying {lab_name}...")

            # Write lab-specific terraform.tfvars
            lab_tfvars_file = lab_dir / "terraform.tfvars"
            lab_config = {
                "prefix": config["prefix"],
                "cloud_region": config["cloud_region"],
            }

            # Add lab-specific credentials
            if "lab1" in lab_name:
                if "ZAPIER_SSE_ENDPOINT" not in config:
                    self.ui.print_error("❌ ZAPIER_SSE_ENDPOINT is required for Lab1 deployment but not found in configuration.")
                    self.ui.print_info("Please run the setup again to configure the Zapier SSE endpoint.")
                    return False
                lab_config["ZAPIER_SSE_ENDPOINT"] = config["ZAPIER_SSE_ENDPOINT"]
            elif "lab2" in lab_name:
                for key in [
                    "MONGODB_CONNECTION_STRING",
                    "mongodb_username",
                    "mongodb_password",
                ]:
                    if key in config:
                        lab_config[key] = config[key]

            lab_type = "Lab1" if "lab1" in lab_name else "Lab2"
            self.write_terraform_tfvars(lab_tfvars_file, lab_config, lab_type)

            # Deploy lab
            lab_terraform = TerraformManager(self.ui, lab_dir)

            if not lab_terraform.initialize(config["cloud_provider"]):
                return False

            if not lab_terraform.plan(config["cloud_provider"]):
                return False

            if not lab_terraform.apply(config["cloud_provider"]):
                return False

            self.ui.print_success(f"{lab_name} deployed successfully!")

        return True

    def detect_setup_state(self) -> SetupState:
        """Intelligently detect the current setup state."""
        # Check prerequisites first
        for tool_name in self.prerequisites.TOOLS.keys():
            if not self.prerequisites.check_tool(tool_name):
                return SetupState.PREREQUISITES_NEEDED

        # Check if aws or azure directories exist
        aws_dir = self.root_dir / "aws"
        azure_dir = self.root_dir / "azure"
        if not (aws_dir.exists() or azure_dir.exists()):
            return SetupState.FRESH_START

        # Check configuration status
        valid_config, invalid_config = self.config_manager.get_config_status()

        if len(valid_config) == 0:
            return SetupState.CONFIGURATION_INCOMPLETE
        elif len(invalid_config) > 0:
            return SetupState.CONFIGURATION_INVALID

        # Check if terraform is initialized
        if not (self.terraform_dir / ".terraform").exists():
            return SetupState.TERRAFORM_NOT_INITIALIZED

        # Check if we have a terraform state (deployment completed)
        terraform_state = self.terraform_dir / "terraform.tfstate"
        if terraform_state.exists():
            try:
                with open(terraform_state, "r") as f:
                    state_data = json.load(f)
                    if state_data.get("resources", []):
                        return SetupState.COMPLETED
            except:
                pass

        # If we have valid config and terraform is initialized, we're ready for deployment
        return SetupState.DEPLOYMENT_READY

    def _check_confluent_login_status(self) -> bool:
        """Check Confluent login status and prompt for login if needed."""
        if not self.prerequisites.check_tool("confluent"):
            return False

        logged_in = self.config_manager.check_confluent_login()
        if not logged_in:
            self.ui.print_warning("You are not logged in to Confluent Cloud")
            if self.ui.confirm(
                "Would you like to log in to Confluent Cloud now?", default=True
            ):
                return self._handle_confluent_login()
            else:
                self.ui.print_info("You can log in later using: confluent login")
        else:
            self.ui.print_success("Already logged in to Confluent Cloud")
        return logged_in

    def get_cloud_provider_selection(self) -> str:
        """Get cloud provider selection early in the setup process."""
        # First, try to detect from existing terraform.tfvars files
        aws_config = self.root_dir / "aws" / "core" / "terraform.tfvars"
        azure_config = self.root_dir / "azure" / "core" / "terraform.tfvars"

        detected_provider = None
        aws_tfvars = {}
        azure_tfvars = {}

        # Check AWS config
        if aws_config.exists():
            aws_tfvars = self.config_manager.parse_tfvars_file(aws_config)

        # Check Azure config
        if azure_config.exists():
            azure_tfvars = self.config_manager.parse_tfvars_file(azure_config)

        # Determine which config is more complete and valid
        aws_valid = aws_tfvars.get("cloud_provider") == "aws" and len(aws_tfvars) > 1
        azure_valid = (
            azure_tfvars.get("cloud_provider") == "azure" and len(azure_tfvars) > 1
        )

        if aws_valid and azure_valid:
            # Both are valid, prefer the one with more complete configuration
            if len(aws_tfvars) > len(azure_tfvars):
                detected_provider = "aws"
            elif len(azure_tfvars) > len(aws_tfvars):
                detected_provider = "azure"
            else:
                detected_provider = None  # Equal completeness, ask user
        elif aws_valid:
            detected_provider = "aws"
        elif azure_valid:
            detected_provider = "azure"

        # If we detected a provider with existing config, confirm with user
        if detected_provider:
            self.ui.print_info(
                f"Found existing {detected_provider.upper()} configuration"
            )
            if self.ui.confirm(
                f"Continue with {detected_provider.upper()}?", default=True
            ):
                return detected_provider

        # Ask user to select cloud provider
        self.ui.print_info("Select your cloud provider:")
        while True:
            choice = self.ui.prompt("Cloud provider (aws/azure)", "azure").lower()
            if choice in ["aws", "azure"]:
                return choice
            self.ui.print_error("Please choose either 'aws' or 'azure'")

    def _handle_confluent_login(self) -> bool:
        """Handle interactive Confluent Cloud login."""
        try:
            self.ui.print_info("Opening Confluent Cloud login...")
            subprocess.run(["confluent", "login"], check=True, text=True)

            # Verify login was successful
            if self.config_manager.check_confluent_login():
                self.ui.print_success("Successfully logged in to Confluent Cloud!")
                return True
            else:
                self.ui.print_warning(
                    "Login may have failed. You can try again later with: confluent login"
                )
                return False

        except subprocess.CalledProcessError as e:
            self.ui.print_error(f"Login failed: {e}")
            return False
        except KeyboardInterrupt:
            self.ui.print_warning("Login cancelled by user")
            return False

    def run(self) -> bool:
        """Main setup execution with intelligent state detection."""
        try:
            self.ui.print_header("🚀 Streaming Agents Quickstart Automated Setup")

            # Handle special flags first
            if self.args.reset:
                return self.handle_reset()

            if self.args.dry_run:
                return self.handle_dry_run()

            # Get cloud provider selection early (before config loading)
            cloud_provider = self.get_cloud_provider_selection()
            self.config_manager.set_config_file_path(cloud_provider)
            self.set_terraform_dirs(cloud_provider)

            # Detect current setup state
            current_state = self.detect_setup_state()

            # Handle each state appropriately
            if current_state == SetupState.PREREQUISITES_NEEDED:
                return self.handle_prerequisites()

            elif current_state == SetupState.CONFIGURATION_INCOMPLETE:
                return self.handle_incomplete_config()

            elif current_state == SetupState.CONFIGURATION_INVALID:
                return self.handle_invalid_config()

            elif current_state == SetupState.TERRAFORM_NOT_INITIALIZED:
                return self.handle_terraform_setup()

            elif current_state == SetupState.DEPLOYMENT_READY:
                return self.handle_deployment()

            elif current_state == SetupState.COMPLETED:
                return self.handle_completed_setup()

            else:  # FRESH_START or unknown state
                return self.handle_fresh_start()

        except KeyboardInterrupt:
            self.ui.print_warning("Setup interrupted by user")
            return False
        except Exception as e:
            self.ui.print_error(f"Setup failed with error: {e}")
            return False

    def handle_reset(self) -> bool:
        """Handle reset flag."""
        # Get cloud provider selection first
        cloud_provider = self.get_cloud_provider_selection()
        self.config_manager.set_config_file_path(cloud_provider)
        self.set_terraform_dirs(cloud_provider)

        self.ui.print_warning("Reset mode: Clearing previous configuration...")

        # Remove config files
        config_file = self.terraform_dir / "core" / ".setup_config.json"
        if config_file.exists():
            config_file.unlink()
            self.ui.print_info("Removed terraform/core/.setup_config.json")

        # Backup and clear terraform.tfvars
        tfvars_file = self.terraform_dir / "terraform.tfvars"
        if tfvars_file.exists():
            backup_path = tfvars_file.with_suffix(".tfvars.reset-backup")
            shutil.copy2(tfvars_file, backup_path)
            self.ui.print_info(f"Backed up terraform.tfvars to {backup_path.name}")

        self.ui.print_success("Reset completed. Run setup again to start fresh.")
        return True

    def handle_dry_run(self) -> bool:
        """Handle dry-run mode."""
        # Get cloud provider selection first
        cloud_provider = self.get_cloud_provider_selection()
        self.config_manager.set_config_file_path(cloud_provider)
        self.set_terraform_dirs(cloud_provider)

        self.ui.print_info("Running in validation mode...")
        valid_config, invalid_config = self.config_manager.get_config_status()

        # Core required fields are: prefix, cloud_provider, cloud_region, confluent_cloud_api_key, confluent_cloud_api_secret
        core_required_count = 5
        if len(valid_config) >= core_required_count and len(invalid_config) == 0:
            self.ui.print_success("✅ All configuration is valid")
            return True
        else:
            self.ui.print_warning(
                f"⚠️ {len(invalid_config)} configuration fields need attention"
            )
            for field in invalid_config:
                self.ui.print_error(f"  - {field}")
            return False

    def handle_prerequisites(self) -> bool:
        """Handle missing prerequisites."""
        self.ui.print_info("⚡ Installing missing prerequisites...")
        if not self.prerequisites.check_and_install_prerequisites():
            return False

        # After installing prerequisites, continue with next phase
        return self.run()

    def handle_config_and_deploy(self, message: str, **config_args) -> bool:
        """Generic handler for configuration and deployment."""
        self.ui.print_info(message)

        # Get lab selection if not provided
        if "lab_selection" not in config_args:
            config_args[
                "lab_selection"
            ] = self.config_manager.prompt_for_lab_selection()

        # Get configuration
        config = self.smart_configuration_prompt(**config_args)
        if not config:
            return False

        # Deploy Core first
        if not self.deploy_core_if_needed(config):
            return False

        # Deploy selected labs
        if not self.deploy_labs(config_args.get("lab_selection", "all"), config):
            return False

        self.ui.print_success("🎉 All deployments completed successfully!")
        self.show_next_steps()
        return True

    def handle_incomplete_config(self) -> bool:
        """Handle incomplete configuration."""
        return self.handle_config_and_deploy("🔧 Configuration setup needed")

    def handle_invalid_config(self) -> bool:
        """Handle invalid configuration."""
        valid_config, invalid_config = self.config_manager.get_config_status()
        return self.handle_config_and_deploy(
            "🔍 Fixing configuration issues...",
            existing_valid=valid_config,
            fix_invalid=invalid_config,
        )

    def handle_terraform_setup(self) -> bool:
        """Handle Terraform infrastructure deployment with existing credentials."""
        valid_config, _ = self.config_manager.get_config_status()

        self.ui.print_info("🏗️  Setting up Terraform infrastructure...")
        self.ui.print_info("✅ Using existing valid configuration:")

        # Show current config (masked)
        for key, value in valid_config.items():
            if "api_" in key.lower() or "secret" in key.lower():
                self.ui.print_success(
                    f"  {key}: ***{value[-4:] if len(value) > 4 else '***'}"
                )
            else:
                self.ui.print_success(f"  {key}: {value}")

        # Get lab selection
        lab_selection = self.config_manager.prompt_for_lab_selection()

        # Load complete config including lab-specific credentials from terraform files
        complete_config = self.config_manager.load_existing_config()

        # Validate that lab-specific required fields exist
        missing_lab_fields = []
        if lab_selection in ["lab1", "all"]:
            if "ZAPIER_SSE_ENDPOINT" not in complete_config or not complete_config["ZAPIER_SSE_ENDPOINT"]:
                missing_lab_fields.append("ZAPIER_SSE_ENDPOINT")
        if lab_selection in ["lab2", "all"]:
            for field in ["MONGODB_CONNECTION_STRING", "mongodb_username", "mongodb_password"]:
                if field not in complete_config or not complete_config[field]:
                    missing_lab_fields.append(field)

        # If lab-specific fields are missing, redirect to configuration flow
        if missing_lab_fields:
            self.ui.print_warning(f"⚠️ Missing required configuration for selected lab(s): {', '.join(missing_lab_fields)}")
            return self.handle_config_and_deploy(
                "🔧 Lab-specific configuration needed...",
                existing_valid=valid_config,
                lab_selection=lab_selection,
            )

        # Deploy Core first
        if not self.deploy_core_if_needed(complete_config):
            return False

        # Deploy selected labs
        if not self.deploy_labs(lab_selection, complete_config):
            return False

        self.ui.print_success("🎉 All deployments completed successfully!")
        self.show_next_steps()
        return True

    def handle_deployment(self) -> bool:
        """Handle infrastructure deployment."""
        self.ui.print_info("🚀 Ready to deploy infrastructure!")

        valid_config, _ = self.config_manager.get_config_status()

        if self.ui.confirm("Deploy the infrastructure now?", default=True):
            if not self.terraform.apply(valid_config.get("cloud_provider")):
                return False

            self.ui.print_success("🎉 Setup completed successfully!")
            self.show_next_steps()
            return True
        else:
            self.ui.print_info("Deployment cancelled. Run the script again when ready.")
            return True

    def handle_completed_setup(self) -> bool:
        """Handle already completed setup."""
        self.ui.print_success("🎉 Infrastructure is already deployed!")

        if self.ui.confirm("Would you like to see the next steps?", default=True):
            self.show_next_steps()

        if self.ui.confirm("Redeploy infrastructure?", default=False):
            return self.handle_deployment()

        return True

    def handle_fresh_start(self) -> bool:
        """Handle completely fresh setup."""
        if not self.prerequisites.check_and_install_prerequisites():
            return False
        return self.handle_config_and_deploy("🌟 Starting fresh setup...")

    def show_configuration_status(
        self, valid_config: Dict[str, str], invalid_config: Dict[str, str]
    ):
        """Simplified configuration status display."""
        if valid_config:
            self.ui.print_success(f"✅ {len(valid_config)} fields configured")
        if invalid_config:
            self.ui.print_warning(f"⚠️ {len(invalid_config)} fields need attention")

    def show_final_config_menu(
        self, valid_config: Dict[str, str], invalid_config: Dict[str, str]
    ) -> str:
        """Simplified configuration review."""
        self.show_configuration_status(valid_config, invalid_config)
        if self.ui.confirm("Continue with deployment?", default=True):
            return "continue"
        return "quit"

    def smart_configuration_prompt(
        self,
        lab_selection: str = None,
        existing_valid: Dict[str, str] = None,
        fix_invalid: Dict[str, str] = None,
    ) -> Optional[Dict[str, str]]:
        """Smart configuration prompting with enhanced menu options."""
        existing_valid = existing_valid or {}
        fix_invalid = fix_invalid or {}

        # Start with valid existing config
        config = existing_valid.copy()

        # Merge in environment credentials
        env_creds = self.config_manager.detect_environment_credentials()
        config.update(env_creds)

        # Determine required fields based on lab selection
        core_fields = [
            "prefix",
            "cloud_provider",
            "cloud_region",
            "confluent_cloud_api_key",
            "confluent_cloud_api_secret",
        ]

        lab_fields = []
        if lab_selection in ["lab1", "all"]:
            lab_fields.append("ZAPIER_SSE_ENDPOINT")
        if lab_selection in ["lab2", "all"]:
            lab_fields.extend(
                ["MONGODB_CONNECTION_STRING", "mongodb_username", "mongodb_password"]
            )

        all_fields = core_fields + lab_fields

        missing_fields = [
            f for f in all_fields if f not in existing_valid and f not in config
        ]
        invalid_fields = list(fix_invalid.keys()) if fix_invalid else []

        # If we have all fields valid, show the final review menu
        if not missing_fields and not invalid_fields:
            choice = self.show_final_config_menu(existing_valid, {})
        elif len(missing_fields) + len(invalid_fields) == len(all_fields):
            # All fields need attention - start fresh
            choice = "continue"
        else:
            # Some fields are valid, some need work - show current status and continue
            self.ui.print_header(
                "Configuration Status", "Continuing with missing/invalid values"
            )
            self.show_configuration_status(existing_valid, fix_invalid or {})
            if self.ui.confirm("Continue to complete the configuration?", default=True):
                choice = "continue"
            else:
                choice = "quit"

        if choice == "quit":
            return None
        elif choice == "reset":
            # Start completely fresh
            config = {}
            fix_invalid = {
                "prefix": "",
                "cloud_provider": "",
                "cloud_region": "",
                "confluent_cloud_api_key": "",
                "confluent_cloud_api_secret": "",
                "ZAPIER_SSE_ENDPOINT": "",
            }
        elif choice.startswith("edit_"):
            # Edit specific field
            field_num = int(choice.split("_")[1])
            config_fields = [
                "prefix",
                "cloud_provider",
                "cloud_region",
                "confluent_cloud_api_key",
                "confluent_cloud_api_secret",
                "ZAPIER_SSE_ENDPOINT",
            ]
            field_to_edit = config_fields[field_num - 1]

            self.ui.print_header("Edit Configuration", f"Editing: {field_to_edit}")
            new_value = self.prompt_for_field(field_to_edit, config, lab_selection)
            if new_value:
                config[field_to_edit] = new_value
                # Test API keys if both are now present
                if field_to_edit in [
                    "confluent_cloud_api_key",
                    "confluent_cloud_api_secret",
                ]:
                    api_key = config.get("confluent_cloud_api_key")
                    api_secret = config.get("confluent_cloud_api_secret")
                    if api_key and api_secret:
                        valid, message = self.config_manager.test_confluent_api_keys(
                            api_key, api_secret
                        )
                        if valid:
                            self.ui.print_success(f"✅ {message}")
                        else:
                            self.ui.print_error(f"❌ {message}")

                self.ui.print_success(f"Updated {field_to_edit}")
                return config
            else:
                self.ui.print_error("❌ Invalid value entered")
                return None

        # Continue mode: Handle each required field that needs attention
        required_fields = [
            "prefix",
            "cloud_provider",
            "cloud_region",
            "confluent_cloud_api_key",
            "confluent_cloud_api_secret",
        ] + lab_fields

        # Show what we're using if continue mode
        if choice == "continue" and existing_valid:
            self.ui.print_header(
                "Configuration", "Only missing or invalid values will be prompted"
            )
            self.ui.print_info("✅ Using existing valid configuration:")
            for key, value in existing_valid.items():
                if key not in [
                    "confluent_cloud_api_key",
                    "confluent_cloud_api_secret",
                    "ZAPIER_SSE_ENDPOINT",
                ]:
                    self.ui.print_success(f"  {key}: {value}")
                else:
                    self.ui.print_success(f"  {key}: ***configured***")

        for field in required_fields:
            if field not in config or field in fix_invalid:
                value = self.prompt_for_field(field, config, lab_selection)
                if not value:
                    self.ui.print_error(
                        f"❌ {field} is required. Setup cannot continue without it."
                    )
                    return None
                config[field] = value

                # Set terraform directories when cloud_provider is determined
                if field == "cloud_provider":
                    self.set_terraform_dirs(value)

        # Final validation of API keys if both are present
        api_key = config.get("confluent_cloud_api_key")
        api_secret = config.get("confluent_cloud_api_secret")
        if api_key and api_secret:
            self.ui.print_info("🔍 Testing API keys...")
            valid, message = self.config_manager.test_confluent_api_keys(
                api_key, api_secret
            )
            if valid:
                self.ui.print_success(f"✅ {message}")
            else:
                self.ui.print_warning(f"⚠️ {message} (continuing anyway)")

        # Save credentials to terraform.tfvars immediately once we have them
        self.config_manager.save_credentials_to_tfvars(config)

        return config

    def prompt_for_field(
        self, field: str, config: Dict[str, str], lab_selection: str = None
    ) -> str:
        """Prompt for a specific configuration field with existing value support."""
        existing_value = config.get(field, "")
        if field == "prefix":
            # Use default prefix without prompting
            value = "streaming-agents"
            self.config_manager.save_field_incrementally(field, value, lab_selection)
            return value

        elif field == "cloud_provider":
            default_value = (
                existing_value
                if existing_value and existing_value in ["aws", "azure"]
                else "azure"
            )
            while True:
                if existing_value:
                    prompt_text = f"Cloud provider (aws/azure) [current: {existing_value}] (press enter to keep, or type 'edit' to change)"
                    response = self.ui.prompt(prompt_text, "")
                    if not response:
                        # User pressed enter, keep existing value
                        return existing_value
                    elif response.lower() == "edit":
                        # User wants to edit
                        value = self.ui.prompt(
                            "Cloud provider (aws/azure)", existing_value
                        ).lower()
                    else:
                        value = response.lower()
                else:
                    value = self.ui.prompt(
                        "Cloud provider (aws/azure)", default_value
                    ).lower()

                if value in ["aws", "azure"]:
                    self.config_manager.save_field_incrementally(
                        field, value, lab_selection
                    )
                    return value
                self.ui.print_error("Please choose either 'aws' or 'azure'")

        elif field == "cloud_region":
            provider = config.get("cloud_provider", "azure").lower()
            available_regions = self.config_manager.CLOUD_REGIONS[provider]

            if existing_value and existing_value in available_regions:
                prompt_text = f"Cloud region [current: {existing_value}] (press enter to keep, or type 'edit' to change)"
                response = self.ui.prompt(prompt_text, "")
                if not response:
                    return existing_value
                elif response.lower() != "edit":
                    # User entered a region directly
                    if response in available_regions:
                        self.config_manager.save_field_incrementally(
                            field, response, lab_selection
                        )
                        return response
                    else:
                        self.ui.print_error(
                            "Invalid region. Showing available options:"
                        )

            self.ui.print_info(f"Available {provider.upper()} regions:")
            for i, region in enumerate(available_regions[:8], 1):  # Show first 8
                print(f"  {i:2d}. {region}")
            if len(available_regions) > 8:
                print(f"  ... and {len(available_regions) - 8} more")

            default_region = (
                existing_value
                if existing_value in available_regions
                else available_regions[0]
            )
            while True:
                value = self.ui.prompt(
                    "Select region (exact name or number)", default_region
                )
                if value.isdigit():
                    idx = int(value) - 1
                    if 0 <= idx < len(available_regions):
                        selected_region = available_regions[idx]
                        self.config_manager.save_field_incrementally(
                            field, selected_region, lab_selection
                        )
                        return selected_region
                elif value in available_regions:
                    self.config_manager.save_field_incrementally(
                        field, value, lab_selection
                    )
                    return value
                self.ui.print_error(
                    "Please select a valid region by exact name or number"
                )

        elif field == "confluent_cloud_api_key":
            # Check if we have an existing valid API key
            if existing_value and self.config_manager.validate_config_value(
                field, existing_value, config
            ):
                prompt_text = f"Confluent Cloud API Key [current: ***{existing_value[-4:]}] (press enter to keep, or type 'edit' to change)"
                response = self.ui.prompt(prompt_text, "")
                if not response:
                    return existing_value
                elif response.lower() != "edit":
                    # User entered a new key directly
                    if self.config_manager.validate_config_value(
                        field, response.strip(), config
                    ):
                        return response.strip()
                    else:
                        self.ui.print_error(
                            "Invalid API key format. Continuing with manual entry."
                        )

            # Check if Confluent CLI is logged in
            cli_logged_in = self.config_manager.check_confluent_login()

            if cli_logged_in:
                self.ui.print_success("✅ Confluent CLI is logged in")
                # Show available environments
                environments = self.config_manager.get_confluent_environments()
                if environments:
                    env_count = len(environments)
                    self.ui.print_info(
                        f"Found {env_count} Confluent environment{'s' if env_count != 1 else ''}"
                    )

                if self.ui.confirm(
                    "Auto-generate API keys with Cloud Resource Management scope?",
                    default=True,
                ):
                    self.ui.print_info("🔑 Generating API keys...")
                    key, secret = self.config_manager.generate_confluent_api_keys(
                        config.get("prefix", "streaming-agents")
                    )
                    if key and secret:
                        config[
                            "confluent_cloud_api_secret"
                        ] = secret  # Store secret for next prompt
                        self.ui.print_success("✅ API keys generated successfully")
                        return key
                    else:
                        self.ui.print_error("❌ Failed to generate API keys")

            # If auto-generation failed or user declined, prompt for manual entry
            if not cli_logged_in:
                self.ui.print_info("💡 To auto-generate keys, run: confluent login")

            attempts = 0
            max_attempts = 3
            default_key = existing_value if existing_value else ""
            while attempts < max_attempts:
                value = self.ui.prompt(
                    "Enter your Confluent Cloud API Key", default_key
                )
                if value and value.strip():  # Check for non-empty after strip
                    return value.strip()
                attempts += 1
                if attempts < max_attempts:
                    self.ui.print_error(
                        f"❌ API Key cannot be empty. {max_attempts - attempts} attempts remaining."
                    )
                else:
                    self.ui.print_error(
                        "❌ Maximum attempts reached. Setup cannot continue without API key."
                    )
            return ""

        elif field == "confluent_cloud_api_secret":
            # If we already generated both keys, return the stored secret
            if "confluent_cloud_api_secret" in config:
                return config["confluent_cloud_api_secret"]

            # Check if we have an existing valid API secret
            if existing_value and self.config_manager.validate_config_value(
                field, existing_value, config
            ):
                prompt_text = f"Confluent Cloud API Secret [current: ***{existing_value[-4:]}] (press enter to keep, or type 'edit' to change)"
                response = self.ui.prompt(prompt_text, "")
                if not response:
                    return existing_value
                elif response.lower() != "edit":
                    # User entered a new secret directly
                    if self.config_manager.validate_config_value(
                        field, response.strip(), config
                    ):
                        return response.strip()
                    else:
                        self.ui.print_error(
                            "Invalid API secret format. Continuing with manual entry."
                        )

            attempts = 0
            max_attempts = 3
            default_secret = existing_value if existing_value else ""
            while attempts < max_attempts:
                value = self.ui.prompt(
                    "Enter your Confluent Cloud API Secret", default_secret
                )
                if value and value.strip():
                    return value.strip()
                attempts += 1
                if attempts < max_attempts:
                    self.ui.print_error(
                        f"❌ API Secret cannot be empty. {max_attempts - attempts} attempts remaining."
                    )
                else:
                    self.ui.print_error(
                        "❌ Maximum attempts reached. Setup cannot continue without API secret."
                    )
            return ""

        elif field == "ZAPIER_SSE_ENDPOINT":
            # Check if we have an existing valid Zapier URL
            if existing_value and self.config_manager.validate_zapier_url(
                existing_value
            ):
                # Mask the API key portion for display
                masked_url = existing_value
                if "/s/" in existing_value and "/sse" in existing_value:
                    start = existing_value.find("/s/") + 3
                    end = existing_value.find("/sse")
                    if start < end:
                        api_key = existing_value[start:end]
                        masked_key = (
                            api_key[:4] + "***" + api_key[-4:]
                            if len(api_key) > 8
                            else "***"
                        )
                        masked_url = (
                            existing_value[:start] + masked_key + existing_value[end:]
                        )

                prompt_text = f"Zapier SSE Endpoint [current: {masked_url}] (press enter to keep, or type 'edit' to change)"
                response = self.ui.prompt(prompt_text, "")
                if not response:
                    return existing_value
                elif response.lower() != "edit":
                    # User entered a new URL directly
                    if self.config_manager.validate_zapier_url(response):
                        return response
                    else:
                        self.ui.print_error(
                            "Invalid Zapier URL format. Continuing with manual entry."
                        )

            self.ui.print_info(
                "📋 You need a real Zapier SSE endpoint URL from your Zapier MCP server setup."
            )
            self.ui.print_info(
                "   It should look like: https://mcp.zapier.com/api/mcp/s/<YOUR-LONG-API-KEY>/sse"
            )

            attempts = 0
            max_attempts = 5
            default_url = existing_value if existing_value else ""
            while attempts < max_attempts:
                value = self.ui.prompt("Zapier SSE Endpoint URL", default_url)
                if self.config_manager.validate_zapier_url(value):
                    return value

                attempts += 1
                # Provide specific error messages
                if not value:
                    self.ui.print_error("❌ URL cannot be empty")
                elif "test-key" in value.lower():
                    self.ui.print_error(
                        "❌ This appears to be a sample URL. Please use your actual Zapier SSE endpoint."
                    )
                elif not value.startswith("https://mcp.zapier.com/api/mcp/s/"):
                    self.ui.print_error(
                        "❌ URL must start with: https://mcp.zapier.com/api/mcp/s/"
                    )
                elif not value.endswith("/sse"):
                    self.ui.print_error("❌ URL must end with: /sse")
                else:
                    self.ui.print_error(
                        "❌ Invalid Zapier SSE endpoint format. API key portion seems too short."
                    )

                if attempts < max_attempts:
                    self.ui.print_error(
                        f"❌ {max_attempts - attempts} attempts remaining."
                    )
                else:
                    self.ui.print_error(
                        "❌ Maximum attempts reached. Setup cannot continue without Zapier endpoint."
                    )
            return ""

        # MongoDB credentials with detailed context
        elif field == "MONGODB_CONNECTION_STRING":
            # Check if we have an existing valid MongoDB connection string
            if (
                existing_value
                and existing_value.startswith("mongodb+srv://")
                and "mongodb.net" in existing_value
            ):
                # Mask part of the connection string for display
                masked_url = existing_value
                if ".mongodb.net" in existing_value:
                    parts = existing_value.split(".")
                    if len(parts) >= 2:
                        cluster_part = parts[0].split("//")[
                            -1
                        ]  # Get cluster name after mongodb+srv://
                        if len(cluster_part) > 8:
                            masked_cluster = (
                                cluster_part[:4] + "***" + cluster_part[-4:]
                            )
                            masked_url = existing_value.replace(
                                cluster_part, masked_cluster
                            )

                prompt_text = f"MongoDB Connection String [current: {masked_url}] (press enter to keep, or type 'edit' to change)"
                response = self.ui.prompt(prompt_text, "")
                if not response:
                    return existing_value
                elif response.lower() != "edit":
                    # User entered a new connection string directly
                    if (
                        response
                        and response.startswith("mongodb+srv://")
                        and "mongodb.net" in response
                    ):
                        self.config_manager.save_field_incrementally(
                            field, response, lab_selection
                        )
                        return response
                    else:
                        self.ui.print_error(
                            "Invalid MongoDB connection string format. Continuing with manual entry."
                        )

            self.ui.print_header(
                "MongoDB Connection String", "Atlas cluster connection details"
            )
            self.ui.print_info(
                "📍 Location: MongoDB Atlas UI → Your Cluster → Connect → Connect your application -> Shell -> Copy from step 2"
            )
            self.ui.print_info("📋 Format: mongodb+srv://cluster0.abc123.mongodb.net")
            self.ui.print_warning(
                "⚠️  Do NOT include username/password in connection string - provide those separately"
            )

            default_value = existing_value if existing_value else ""
            while True:
                value = self.ui.prompt("MongoDB Connection String", default_value)
                if (
                    value
                    and value.startswith("mongodb+srv://")
                    and "mongodb.net" in value
                ):
                    self.config_manager.save_field_incrementally(
                        field, value, lab_selection
                    )
                    return value
                self.ui.print_error("❌ Invalid MongoDB connection string format")

        elif field == "mongodb_username":
            # Check if we have an existing MongoDB username
            if existing_value:
                prompt_text = f"MongoDB Database Username [current: {existing_value}] (press enter to keep, or type 'edit' to change)"
                response = self.ui.prompt(prompt_text, "")
                if not response:
                    return existing_value
                elif response.lower() != "edit":
                    # User entered a new username directly
                    if response.strip():
                        self.config_manager.save_field_incrementally(
                            field, response.strip(), lab_selection
                        )
                        return response.strip()

            self.ui.print_header(
                "MongoDB Database User", "Project-specific database access credentials"
            )
            self.ui.print_info(
                "📍 Location: MongoDB Atlas UI → Database Access → Database Users"
            )
            self.ui.print_info(
                "📋 This is the database username you created for your project (e.g., 'confluent-user')"
            )
            self.ui.print_warning(
                "⚠️  NOT your Atlas account username - this is project-specific"
            )
            self.ui.print_info(
                "💡 To create: Click 'Add New Database User' → Set privileges to 'Read and write to any database'"
            )

            default_value = existing_value if existing_value else ""
            value = self.ui.prompt("MongoDB Database Username", default_value)
            if value:
                self.config_manager.save_field_incrementally(
                    field, value, lab_selection
                )
            return value if value else ""

        elif field == "mongodb_password":
            # Check if we have an existing MongoDB password
            if existing_value:
                masked_password = (
                    "***" + existing_value[-3:] if len(existing_value) > 3 else "***"
                )
                prompt_text = f"MongoDB Database Password [current: {masked_password}] (press enter to keep, or type 'edit' to change)"
                response = self.ui.prompt(prompt_text, "")
                if not response:
                    return existing_value
                elif response.lower() != "edit":
                    # User entered a new password directly
                    if response.strip():
                        self.config_manager.save_field_incrementally(
                            field, response.strip(), lab_selection
                        )
                        return response.strip()

            self.ui.print_header(
                "MongoDB Database Password", "Password for the database user above"
            )
            self.ui.print_info(
                "📍 This is the password for the database user you just entered"
            )
            self.ui.print_info(
                "📋 You set this when creating the database user in Atlas"
            )
            self.ui.print_warning(
                "⚠️  NOT your Atlas account password - this is for the database user"
            )

            default_value = existing_value if existing_value else ""
            value = self.ui.prompt("MongoDB Database User Password", default_value)
            if value:
                self.config_manager.save_field_incrementally(
                    field, value, lab_selection
                )
            return value if value else ""

        return ""

    def show_next_steps(self):
        """Show next steps after successful deployment."""
        self.ui.print_info("Next steps:")
        self.ui.print_info("1. Set up Flink MCP connection (see mcp_commands.txt)")
        self.ui.print_info(
            "2. Generate sample data (cd terraform/data-gen && ./run.sh)"
        )
        self.ui.print_info("3. Proceed to Lab1: Price Matching Using Tool Calling")


def main():
    """Main entry point."""
    # Simple argument parsing - hidden advanced options
    parser = argparse.ArgumentParser(
        description="🚀 Streaming Agents Quickstart Setup\n\nJust run 'python setup.py' - the script will intelligently detect what needs to be done!",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,  # Custom help to hide advanced options
    )

    # Primary help
    parser.add_argument(
        "-h", "--help", action="store_true", help="Show this help message"
    )

    # Hidden advanced options (not shown in primary help)
    parser.add_argument("--resume", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--reset", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--dry-run", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--verbose", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--advanced-help", action="store_true", help=argparse.SUPPRESS)

    args = parser.parse_args()

    # Handle help
    if args.help:
        print("🚀 Streaming Agents Quickstart Setup")
        print("\nUsage:")
        print(
            "  python setup.py          # Intelligent setup - detects current state and continues"
        )
        print("\nThe script will automatically:")
        print("  • Install missing prerequisites")
        print("  • Resume interrupted configurations")
        print("  • Only prompt for missing/invalid values")
        print("  • Deploy infrastructure when ready")
        print("\nFor advanced options: python setup.py --advanced-help")
        return

    if args.advanced_help:
        print("🚀 Streaming Agents Quickstart Setup - Advanced Options")
        print("\nBasic usage:")
        print("  python setup.py          # Intelligent setup (recommended)")
        print("\nAdvanced options:")
        print("  --reset                  # Clear all configuration and start fresh")
        print("  --dry-run                # Validate configuration without deploying")
        print("  --resume                 # Force resume mode (usually auto-detected)")
        print("  --verbose                # Show detailed output and logs")
        print(
            "\nNote: These options are rarely needed as the script auto-detects what to do."
        )
        return

    # Create setup instance with defaults for missing args
    class Args:
        def __init__(self):
            self.resume = getattr(args, "resume", False)
            self.reset = getattr(args, "reset", False)
            self.dry_run = getattr(args, "dry_run", False)
            self.verbose = getattr(args, "verbose", False)

    setup = StreamingAgentsSetup(Args())
    success = setup.run()

    sys.exit(0 if success else 1)


def destroy_main():
    """Main entry point for destroy command."""
    ui = SetupUI()
    root_dir = Path(__file__).parent

    ui.print_header("🗑️  Streaming Agents Infrastructure Destruction")
    ui.print_warning(
        "This will destroy Terraform infrastructure and cannot be undone!"
    )

    # Prompt for cloud provider
    ui.print_info("\nSelect cloud provider:")
    print("  1) AWS")
    print("  2) Azure")

    choice = ui.prompt("Enter choice (1-2)", "1").strip()
    if choice == "1":
        cloud_provider = "aws"
    elif choice == "2":
        cloud_provider = "azure"
    else:
        ui.print_error("Invalid choice. Exiting.")
        sys.exit(1)

    provider_dir = root_dir / cloud_provider
    if not provider_dir.exists():
        ui.print_error(f"Cloud provider directory not found: {provider_dir}")
        sys.exit(1)

    # Detect what's deployed by checking terraform.tfstate files
    labs = ["lab2-vector-search", "lab1-tool-calling", "core"]
    deployed_resources = []

    for lab in labs:
        lab_dir = provider_dir / lab
        state_file = lab_dir / "terraform.tfstate"
        if state_file.exists():
            try:
                with open(state_file, "r") as f:
                    state_data = json.load(f)
                    resources = state_data.get("resources", [])
                    if resources:
                        deployed_resources.append((lab, lab_dir))
            except Exception:
                # If we can't read the state, assume it's deployed
                if state_file.stat().st_size > 0:
                    deployed_resources.append((lab, lab_dir))

    if not deployed_resources:
        ui.print_info("No deployed resources found. Nothing to destroy.")
        sys.exit(0)

    # Show what will be destroyed
    ui.print_info(f"\nFound {len(deployed_resources)} deployed resource(s):")
    for lab, _ in deployed_resources:
        print(f"  • {lab}")

    # Final confirmation
    if not ui.confirm("\nAre you sure you want to destroy all resources?", default=False):
        ui.print_info("Destruction cancelled.")
        sys.exit(0)

    # Destroy in reverse order (labs first, then core)
    terraform = TerraformManager(ui, root_dir)
    all_success = True

    for lab, lab_dir in deployed_resources:
        ui.print_header(f"Destroying {lab}")

        # Update terraform directory for this resource
        terraform.terraform_dir = lab_dir

        # Initialize terraform if needed
        if not (lab_dir / ".terraform").exists():
            ui.print_info("Initializing Terraform...")
            if not terraform.initialize(cloud_provider=cloud_provider):
                ui.print_error(f"Failed to initialize Terraform for {lab}")
                all_success = False
                continue

        # Destroy
        if not terraform.destroy(cloud_provider=cloud_provider):
            ui.print_error(f"Failed to destroy {lab}")
            all_success = False
        else:
            ui.print_success(f"Successfully destroyed {lab}")

    if all_success:
        ui.print_header("✅ All Resources Destroyed Successfully")
        ui.print_info(
            "\nYou can safely delete terraform.tfstate* files if you want a clean slate."
        )
        sys.exit(0)
    else:
        ui.print_header("⚠️  Destruction Completed with Errors")
        ui.print_warning("Some resources may not have been destroyed successfully.")
        ui.print_info("Check the output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
