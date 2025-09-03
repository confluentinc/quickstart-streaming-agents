#!/usr/bin/env python3
"""
Streaming Agents Quickstart Setup Script

Cross-platform automated setup and deployment for the quickstart-streaming-agents project.
Designed for non-technical users to easily deploy streaming agents infrastructure.
"""

import argparse
import json
import logging
import os
import platform
import re
import shutil
import subprocess
import sys
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Confirm, Prompt
    from rich.table import Table
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None

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

class SetupLogger:
    """Custom logger for setup operations - logging disabled."""
    
    def __init__(self, log_file: str = None, verbose: bool = False):
        self.verbose = verbose
        # Logging is disabled - all methods are no-ops
    
    def info(self, message: str):
        # No-op - logging disabled
        pass
    
    def error(self, message: str, exc_info=False):
        # No-op - logging disabled
        pass
    
    def warning(self, message: str):
        # No-op - logging disabled
        pass

class SetupUI:
    """User interface handler with rich formatting when available."""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.use_rich = RICH_AVAILABLE
    
    def print_success(self, message: str):
        if self.use_rich:
            self.console.print(f"✅ {message}", style="green")
        else:
            print(f"✅ {message}")
    
    def print_error(self, message: str):
        if self.use_rich:
            self.console.print(f"❌ {message}", style="red")
        else:
            print(f"❌ {message}")
    
    def print_warning(self, message: str):
        if self.use_rich:
            self.console.print(f"⚠️  {message}", style="yellow")
        else:
            print(f"⚠️  {message}")
    
    def print_info(self, message: str):
        if self.use_rich:
            self.console.print(f"ℹ️  {message}", style="blue")
        else:
            print(f"ℹ️  {message}")
    
    def print_header(self, title: str, subtitle: str = ""):
        if self.use_rich:
            text = Text(title, style="bold magenta")
            if subtitle:
                text.append(f"\n{subtitle}", style="dim")
            panel = Panel(text, expand=False, border_style="magenta")
            self.console.print(panel)
        else:
            print(f"\n=== {title} ===")
            if subtitle:
                print(f"{subtitle}")
            print("")
    
    def prompt(self, message: str, default: str = None) -> str:
        if self.use_rich:
            return Prompt.ask(message, default=default)
        else:
            prompt_text = f"{message}"
            if default:
                prompt_text += f" [{default}]"
            prompt_text += ": "
            try:
                response = input(prompt_text).strip()
                return response if response else (default or "")
            except EOFError:
                # Return default value in non-interactive environments
                return default or ""
    
    def confirm(self, message: str, default: bool = True) -> bool:
        if self.use_rich:
            return Confirm.ask(message, default=default)
        else:
            default_text = "Y/n" if default else "y/N"
            try:
                response = input(f"{message} [{default_text}]: ").strip().lower()
                if not response:
                    return default
                return response.startswith('y')
            except EOFError:
                # Return default value in non-interactive environments
                return default

class PrerequisiteManager:
    """Manages checking and installation of required tools."""
    
    TOOLS = {
        'git': {
            'check_cmd': ['git', '--version'],
            'macos_install': 'brew install git',
            'windows_install': 'winget install --id Git.Git -e'
        },
        'terraform': {
            'check_cmd': ['terraform', '--version'],
            'macos_install': 'brew tap hashicorp/tap && brew install hashicorp/tap/terraform',
            'windows_install': 'winget install --id Hashicorp.Terraform -e'
        },
        'confluent': {
            'check_cmd': ['confluent', '--version'],
            'macos_install': 'brew install --cask confluent-cli',
            'windows_install': 'winget install --id ConfluentInc.Confluent-CLI -e'
        },
        'docker': {
            'check_cmd': ['docker', '--version'],
            'macos_install': 'brew install --cask docker-desktop',
            'windows_install': 'winget install --id Docker.DockerDesktop -e'
        }
    }
    
    def __init__(self, ui: SetupUI, logger: SetupLogger):
        self.ui = ui
        self.logger = logger
        self.system = platform.system().lower()
    
    def check_tool(self, tool_name: str) -> bool:
        """Check if a tool is installed."""
        try:
            result = subprocess.run(
                self.TOOLS[tool_name]['check_cmd'],
                capture_output=True,
                text=True,
                check=True
            )
            self.logger.info(f"{tool_name} is installed: {result.stdout.strip().split()[0]}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.info(f"{tool_name} is not installed")
            return False
    
    def install_tool(self, tool_name: str) -> bool:
        """Install a tool based on the current platform."""
        if self.system == "darwin":
            install_cmd = self.TOOLS[tool_name]['macos_install']
        elif self.system == "windows":
            install_cmd = self.TOOLS[tool_name]['windows_install']
        else:
            self.ui.print_error(f"Unsupported platform for automatic installation: {self.system}")
            return False
        
        self.ui.print_info(f"Installing {tool_name}...")
        self.logger.info(f"Running installation command: {install_cmd}")
        
        try:
            result = subprocess.run(
                install_cmd,
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            self.ui.print_success(f"{tool_name} installed successfully")
            self.logger.info(f"{tool_name} installation output: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            self.ui.print_error(f"Failed to install {tool_name}: {e}")
            self.logger.error(f"{tool_name} installation failed: {e.stderr}")
            return False
    
    def check_and_install_prerequisites(self) -> bool:
        """Check all prerequisites and offer to install missing ones."""
        self.ui.print_header("Checking Prerequisites", "Verifying required tools are installed")
        
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
        
        if not self.ui.confirm("Would you like to install missing tools automatically?"):
            self.ui.print_error("Cannot proceed without required tools. Please install manually:")
            for tool in missing_tools:
                if self.system == "darwin":
                    self.ui.print_info(f"  {tool}: {self.TOOLS[tool]['macos_install']}")
                elif self.system == "windows":
                    self.ui.print_info(f"  {tool}: {self.TOOLS[tool]['windows_install']}")
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
    
    CLOUD_REGIONS = {
        'aws': [
            'us-east-1', 'us-east-2', 'us-west-2',
            'eu-west-1', 'eu-west-2', 'eu-central-1',
            'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1'
        ],
        'azure': [
            'eastus', 'eastus2', 'centralus', 'northcentralus', 
            'southcentralus', 'westus', 'westus2', 'westus3',
            'northeurope', 'westeurope', 'uksouth', 'ukwest',
            'francecentral', 'germanywestcentral', 'eastasia',
            'southeastasia', 'japaneast', 'japanwest',
            'koreacentral', 'koreasouth'
        ]
    }
    
    def __init__(self, ui: SetupUI, logger: SetupLogger, terraform_dir: Path):
        self.ui = ui
        self.logger = logger
        self.terraform_dir = terraform_dir
        self.tfvars_file = terraform_dir / "terraform.tfvars"
        self.config_file = Path(".setup_config.json")
    
    def load_existing_config(self) -> Dict[str, str]:
        """Load existing configuration from tfvars and config files."""
        config = {}
        
        # Load from setup config file
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config.update(json.load(f))
                self.logger.info("Loaded existing setup configuration")
            except Exception as e:
                self.logger.warning(f"Could not load setup config: {e}")
        
        # Load from terraform.tfvars
        if self.tfvars_file.exists():
            try:
                with open(self.tfvars_file, 'r') as f:
                    content = f.read()
                
                # Parse simple key-value pairs
                for line in content.split('\n'):
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip(' "\'')  # Remove quotes and extra spaces
                        # Clean up comment suffixes
                        if '#' in value:
                            value = value.split('#')[0].strip(' "\'')
                        config[key] = value
                
                self.logger.info("Loaded existing terraform.tfvars configuration")
            except Exception as e:
                self.logger.warning(f"Could not parse terraform.tfvars: {e}")
        
        return config
    
    def is_placeholder_value(self, key: str, value: str) -> bool:
        """Check if a config value is a placeholder."""
        placeholders = {
            'confluent_cloud_api_key': ['your-confluent-api-key', 'CKEY-placeholder', 'test-key'],
            'confluent_cloud_api_secret': ['your-confluent-api-secret', 'secret-placeholder', 'test-secret'],
            'ZAPIER_SSE_ENDPOINT': ['https://mcp.zapier.com/api/mcp/s/<<long-API-key>>/sse', 
                                   'https://mcp.zapier.com/api/mcp/s/test-api-key/sse',
                                   'https://mcp.zapier.com/api/mcp/s/test-key/sse'],
            'prefix': ['your-prefix']
        }
        
        if key in placeholders:
            return value in placeholders[key] or value.startswith('your-') or value.startswith('<<')
        return False
    
    def is_first_run(self) -> bool:
        """Check if this is the user's first run (no confirmed config yet)."""
        # If we don't have a setup config file, this is first run
        if not self.config_file.exists():
            return True
        
        # If setup config exists but is empty/minimal, still first run
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                # Check if configuration was completed at least once
                return not config.get('_config_completed', False)
        except:
            return True
    
    def validate_config_value(self, key: str, value: str, config_context: Dict[str, str] = None) -> bool:
        """Validate a configuration value."""
        if not value or self.is_placeholder_value(key, value):
            return False
        
        config_context = config_context or {}
            
        if key == 'confluent_cloud_api_key':
            # Basic format check first
            if not (len(value) >= 10 and value.isalnum()):
                return False
            # If we have both key and secret, test them
            secret = config_context.get('confluent_cloud_api_secret')
            if secret and len(secret) >= 20:
                try:
                    valid, _ = self.test_confluent_api_keys(value, secret)
                    return valid
                except:
                    # Fall back to format validation if API test fails
                    return True
            return True
            
        elif key == 'confluent_cloud_api_secret':
            # Basic format check first
            if not (len(value) >= 20 and not value.startswith('your-')):
                return False
            # If we have both key and secret, test them
            api_key = config_context.get('confluent_cloud_api_key')
            if api_key and len(api_key) >= 10:
                try:
                    valid, _ = self.test_confluent_api_keys(api_key, value)
                    return valid
                except:
                    # Fall back to format validation if API test fails
                    return True
            return True
            
        elif key == 'ZAPIER_SSE_ENDPOINT':
            return self.validate_zapier_url(value)
        elif key == 'cloud_provider':
            return value.lower() in ['aws', 'azure']
        elif key == 'cloud_region':
            provider = config_context.get('cloud_provider') or self.load_existing_config().get('cloud_provider', 'azure')
            return value in self.CLOUD_REGIONS.get(provider.lower(), [])
        elif key == 'prefix':
            return bool(re.match(r'^[a-zA-Z0-9\-_]+$', value))
        
        return True
    
    def get_config_status(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        """Get current config with valid and invalid fields separated."""
        all_config = self.load_existing_config()
        
        # Attempt auto-repair first
        repaired_config = self.auto_repair_config(all_config)
        
        valid_config = {}
        invalid_config = {}
        
        required_fields = ['prefix', 'cloud_provider', 'cloud_region', 
                          'confluent_cloud_api_key', 'confluent_cloud_api_secret', 
                          'ZAPIER_SSE_ENDPOINT']
        
        # If this is first run, treat defaults as invalid (need confirmation)
        first_run = self.is_first_run()
        
        for field in required_fields:
            value = repaired_config.get(field, '')
            # On first run, even default values need user confirmation
            if value and self.validate_config_value(field, value, repaired_config) and not first_run:
                valid_config[field] = value
            else:
                invalid_config[field] = value
        
        return valid_config, invalid_config
    
    def detect_environment_credentials(self) -> Dict[str, str]:
        """Detect credentials from environment and CLI."""
        env_creds = {}
        
        # Check environment variables
        env_key = os.getenv('CONFLUENT_CLOUD_API_KEY')
        env_secret = os.getenv('CONFLUENT_CLOUD_API_SECRET')
        
        if env_key and env_secret:
            if self.validate_config_value('confluent_cloud_api_key', env_key):
                env_creds['confluent_cloud_api_key'] = env_key
                if self.logger.verbose:
                    self.ui.print_success("Found valid Confluent API key in environment")
            if self.validate_config_value('confluent_cloud_api_secret', env_secret):
                env_creds['confluent_cloud_api_secret'] = env_secret
                if self.logger.verbose:
                    self.ui.print_success("Found valid Confluent API secret in environment")
        
        # Check if Confluent CLI is logged in
        if self.check_confluent_login():
            env_creds['confluent_cli_logged_in'] = 'true'
            if self.logger.verbose:
                self.ui.print_success("Confluent CLI is logged in")
        
        return env_creds
    
    def is_non_interactive_environment(self) -> bool:
        """Detect if running in CI/CD or non-interactive environment."""
        ci_indicators = ['CI', 'CONTINUOUS_INTEGRATION', 'GITHUB_ACTIONS', 
                        'GITLAB_CI', 'JENKINS_URL', 'BUILD_NUMBER']
        return any(os.getenv(var) for var in ci_indicators) or not sys.stdin.isatty()
    
    def auto_repair_config(self, config: Dict[str, str]) -> Dict[str, str]:
        """Attempt to auto-repair common configuration issues."""
        repaired = config.copy()
        
        # Fix cloud provider case
        if 'cloud_provider' in repaired:
            provider = repaired['cloud_provider'].lower()
            if provider in ['aws', 'azure']:
                repaired['cloud_provider'] = provider
                if provider != config['cloud_provider'] and self.logger.verbose:
                    self.ui.print_info(f"Auto-fixed cloud_provider case: {config['cloud_provider']} → {provider}")
        
        # Clean up Zapier URL
        if 'ZAPIER_SSE_ENDPOINT' in repaired:
            url = repaired['ZAPIER_SSE_ENDPOINT']
            if url and not url.endswith('/sse'):
                if '/sse' not in url:
                    repaired['ZAPIER_SSE_ENDPOINT'] = url.rstrip('/') + '/sse'
                    if self.logger.verbose:
                        self.ui.print_info(f"Auto-fixed Zapier URL: added /sse endpoint")
        
        return repaired
    
    def save_config(self, config: Dict[str, str]):
        """Save non-sensitive configuration for future runs."""
        # Save all non-sensitive config, plus indicator that configuration was completed
        safe_config = {
            key: value for key, value in config.items()
            if key not in ['confluent_cloud_api_key', 'confluent_cloud_api_secret', 'ZAPIER_SSE_ENDPOINT']
        }
        # Add a marker to indicate configuration was completed at least once
        safe_config['_config_completed'] = True
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(safe_config, f, indent=2)
            self.logger.info("Saved configuration for future runs")
        except Exception as e:
            self.logger.warning(f"Could not save configuration: {e}")
    
    def test_confluent_api_keys(self, api_key: str, api_secret: str) -> Tuple[bool, str]:
        """Test if Confluent API keys are valid and have proper scope."""
        try:
            import base64
            import requests
            
            # Create basic auth header
            credentials = base64.b64encode(f"{api_key}:{api_secret}".encode()).decode()
            headers = {
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/json'
            }
            
            # Test by listing organizations (requires cloud scope)
            response = requests.get(
                'https://api.confluent.cloud/org/v2/organizations',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "API keys are valid and have proper cloud scope"
            elif response.status_code == 401:
                return False, "API keys are invalid or expired"
            elif response.status_code == 403:
                return False, "API keys don't have sufficient permissions (need Cloud Resource Management scope)"
            else:
                return False, f"API test failed with status {response.status_code}: {response.text}"
                
        except requests.exceptions.RequestException as e:
            return False, f"Network error testing API keys: {str(e)}"
        except Exception as e:
            return False, f"Error testing API keys: {str(e)}"
    
    def validate_zapier_url(self, url: str) -> bool:
        """Validate Zapier SSE endpoint URL format and reject placeholders."""
        if not url:
            return False
        
        # Reject known placeholder/sample URLs
        placeholder_patterns = [
            'test-key', 'test-api-key', '<<API-key>>', '<<long-API-key>>',
            'your-api-key', 'sample-key', 'placeholder'
        ]
        
        for pattern in placeholder_patterns:
            if pattern in url.lower():
                return False
        
        # Check proper format
        pattern = r'^https://mcp\.zapier\.com/api/mcp/s/[a-zA-Z0-9\-_=]{20,}/sse$'
        return bool(re.match(pattern, url))
    
    def prompt_for_configuration(self, non_interactive: bool = False) -> Dict[str, str]:
        """Interactive configuration prompting."""
        self.ui.print_header("Configuration Setup", "Please provide the following information")
        
        existing_config = self.load_existing_config()
        config = {}
        
        # In non-interactive mode, use existing config or defaults
        if non_interactive:
            self.ui.print_info("Using existing configuration for dry-run" if existing_config else "Using default configuration for dry-run")
            # Add required defaults for missing values
            defaults = {
                'prefix': 'streaming-agents',
                'cloud_provider': 'azure', 
                'cloud_region': 'East US',
                'confluent_cloud_api_key': 'test-key',
                'confluent_cloud_api_secret': 'test-secret',
                'ZAPIER_SSE_ENDPOINT': 'https://mcp.zapier.com/api/mcp/s/test-api-key/sse'
            }
            for key, default_value in defaults.items():
                config[key] = existing_config.get(key, default_value)
            return config
        
        # Prefix (using default without prompting)
        config['prefix'] = 'streaming-agents'
        
        # Cloud provider
        default_provider = existing_config.get('cloud_provider', 'azure').lower()
        while True:
            provider = self.ui.prompt("Cloud provider (aws/azure)", default_provider).lower()
            if provider in ['aws', 'azure']:
                config['cloud_provider'] = provider
                break
            self.ui.print_error("Please choose either 'aws' or 'azure'")
        
        # Cloud region
        available_regions = self.CLOUD_REGIONS[config['cloud_provider']]
        self.ui.print_info(f"Available {config['cloud_provider'].upper()} regions:")
        for i, region in enumerate(available_regions, 1):
            print(f"  {i:2d}. {region}")
        
        default_region = existing_config.get('cloud_region', available_regions[0])
        while True:
            region_input = self.ui.prompt(f"Select region (name or number)", default_region)
            
            if region_input.isdigit():
                idx = int(region_input) - 1
                if 0 <= idx < len(available_regions):
                    config['cloud_region'] = available_regions[idx]
                    break
            elif region_input in available_regions:
                config['cloud_region'] = region_input
                break
            
            self.ui.print_error("Please select a valid region")
        
        # Confluent credentials
        self.ui.print_info("Confluent Cloud credentials are required for deployment")
        
        # Check environment variables first
        env_key = os.getenv('CONFLUENT_CLOUD_API_KEY')
        env_secret = os.getenv('CONFLUENT_CLOUD_API_SECRET')
        
        if env_key and env_secret:
            self.ui.print_success("Found Confluent credentials in environment variables")
            config['confluent_cloud_api_key'] = env_key
            config['confluent_cloud_api_secret'] = env_secret
        else:
            # Check if user is logged in to Confluent CLI
            confluent_logged_in = self.check_confluent_login()
            
            if confluent_logged_in and self.ui.confirm("Auto-generate Confluent API keys using CLI?"):
                api_key, api_secret = self.generate_confluent_api_keys(config['prefix'])
                if api_key and api_secret:
                    config['confluent_cloud_api_key'] = api_key
                    config['confluent_cloud_api_secret'] = api_secret
                    self.ui.print_success("Generated Confluent API keys successfully")
                else:
                    self.ui.print_error("Failed to generate API keys, please enter manually")
            
            # Manual entry if auto-generation failed or was declined
            if 'confluent_cloud_api_key' not in config:
                config['confluent_cloud_api_key'] = self.ui.prompt("Confluent Cloud API Key")
                config['confluent_cloud_api_secret'] = self.ui.prompt("Confluent Cloud API Secret")
        
        # Zapier SSE endpoint
        while True:
            zapier_url = self.ui.prompt("Zapier SSE Endpoint (from Zapier MCP server)")
            if self.validate_zapier_url(zapier_url):
                config['ZAPIER_SSE_ENDPOINT'] = zapier_url
                break
            self.ui.print_error("Invalid Zapier SSE endpoint format. Expected: https://mcp.zapier.com/api/mcp/s/<<API-key>>/sse")
        
        return config
    
    def check_confluent_login(self) -> bool:
        """Check if user is logged into Confluent CLI."""
        try:
            # Try to list environments - this requires authentication
            result = subprocess.run(
                ['confluent', 'environment', 'list'],
                capture_output=True,
                text=True,
                check=True
            )
            # Check if we got a proper environment listing (contains ID column and at least one environment)
            return (len(result.stdout.strip()) > 0 and 
                    "ID" in result.stdout and 
                    "env-" in result.stdout)
        except subprocess.CalledProcessError:
            return False
        except FileNotFoundError:
            # Confluent CLI not installed
            return False
    
    def get_confluent_environments(self) -> List[Dict[str, str]]:
        """Get list of available Confluent environments."""
        try:
            result = subprocess.run(
                ['confluent', 'environment', 'list', '--output', 'json'],
                capture_output=True,
                text=True,
                check=True
            )
            environments = json.loads(result.stdout)
            return environments if isinstance(environments, list) else []
        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
            # Fallback to text parsing if JSON output not available
            try:
                result = subprocess.run(
                    ['confluent', 'environment', 'list'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                environments = []
                lines = result.stdout.strip().split('\n')
                for line in lines[2:]:  # Skip header lines
                    if line.strip() and '|' in line:
                        parts = [p.strip() for p in line.split('|')]
                        if len(parts) >= 3:
                            environments.append({
                                'id': parts[1],
                                'name': parts[2] if len(parts) > 2 else parts[1]
                            })
                return environments
            except:
                return []
    
    def select_confluent_environment(self) -> Optional[str]:
        """Select Confluent environment to use for this project."""
        environments = self.get_confluent_environments()
        
        if not environments:
            self.ui.print_error("No Confluent environments found. Please create one first.")
            return None
        
        if len(environments) == 1:
            env = environments[0]
            env_name = env.get('name', env.get('id', 'Unknown'))
            self.ui.print_success(f"Using environment: {env_name}")
            return env.get('id')
        
        # Multiple environments - let user choose
        self.ui.print_info("Multiple Confluent environments found:")
        for i, env in enumerate(environments, 1):
            env_name = env.get('name', env.get('id', 'Unknown'))
            env_id = env.get('id', '')
            print(f"  {i:2d}. {env_name} ({env_id})")
        
        while True:
            choice = self.ui.prompt(f"Select environment (1-{len(environments)})", "1")
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(environments):
                    selected = environments[idx]
                    env_name = selected.get('name', selected.get('id', 'Unknown'))
                    self.ui.print_success(f"Selected environment: {env_name}")
                    return selected.get('id')
                else:
                    self.ui.print_error(f"Please select a number between 1 and {len(environments)}")
            except ValueError:
                self.ui.print_error("Please enter a valid number")
    
    def generate_confluent_api_keys(self, prefix: str) -> Tuple[Optional[str], Optional[str]]:
        """Generate Confluent API keys using CLI."""
        try:
            # Create service account (no environment creation needed - Terraform handles that)
            import time
            timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
            sa_name = f"{prefix}-setup-sa-{timestamp}"
            self.ui.print_info(f"Creating service account: {sa_name}")
            
            sa_result = subprocess.run(
                ['confluent', 'iam', 'service-account', 'create', sa_name, 
                 '--description', f'Service account for {prefix} streaming agents setup'],
                capture_output=True,
                text=True,
                check=True
            )
            self.logger.info(f"Service account creation output: {sa_result.stdout}")
            
            # Extract service account ID from table format
            sa_id = None
            for line in sa_result.stdout.split('\n'):
                line = line.strip()
                if '| ID' in line and 'sa-' in line:
                    # Format: | ID          | sa-xxxxxxx |
                    parts = [p.strip() for p in line.split('|') if p.strip()]
                    if len(parts) >= 2 and 'ID' in parts[0]:
                        sa_id = parts[1]
                        break
            
            if not sa_id:
                self.logger.error("Could not extract service account ID from output")
                self.logger.error(f"Full SA output was: {sa_result.stdout}")
                return None, None
            
            self.logger.info(f"Created service account with ID: {sa_id}")
            
            # Create API key
            self.ui.print_info("Creating API key with Cloud Resource Management scope")
            
            key_result = subprocess.run(
                ['confluent', 'api-key', 'create', '--service-account', sa_id, 
                 '--resource', 'cloud', '--description', f'{prefix} setup key'],
                capture_output=True,
                text=True,
                check=True
            )
            self.logger.info(f"API key creation output: {key_result.stdout}")
            
            # Extract API key and secret
            api_key = api_secret = None
            lines = key_result.stdout.split('\n')
            for line in lines:
                line = line.strip()
                if 'API Key' in line and '|' in line:
                    # Format: | API Key    | XXXXXXXXXXXXXXXXXXXX |
                    parts = [p.strip() for p in line.split('|') if p.strip()]
                    if len(parts) >= 2 and 'API Key' in parts[0]:
                        api_key = parts[1]
                elif 'API Secret' in line and '|' in line:
                    # Format: | API Secret | XXXXXXXXXXXXXXXXXXXX |
                    parts = [p.strip() for p in line.split('|') if p.strip()]
                    if len(parts) >= 2 and 'API Secret' in parts[0]:
                        api_secret = parts[1]
            
            self.logger.info(f"Parsed API key: {api_key}")
            self.logger.info(f"Parsed API secret: {'***' + api_secret[-4:] if api_secret else None}")
            
            if api_key and api_secret:
                # Assign Organization Admin role to the service account
                try:
                    self.ui.print_info("Assigning OrganizationAdmin role...")
                    role_result = subprocess.run(
                        ['confluent', 'iam', 'rbac', 'role-binding', 'create',
                         '--principal', f'User:{sa_id}', '--role', 'OrganizationAdmin'],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    self.ui.print_success("OrganizationAdmin role assigned successfully")
                    self.logger.info("Role assignment completed")
                except subprocess.CalledProcessError as e:
                    self.ui.print_warning("Role assignment failed, but API keys were created successfully")
                    self.logger.warning(f"Role assignment failed: {e.stderr if hasattr(e, 'stderr') else str(e)}")
                
                return api_key, api_secret
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to generate API keys: {e}")
            if hasattr(e, 'stdout') and e.stdout:
                self.logger.error(f"Command stdout: {e.stdout}")
            if hasattr(e, 'stderr') and e.stderr:
                self.logger.error(f"Command stderr: {e.stderr}")
            self.ui.print_error(f"Command failed: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error generating API keys: {e}", exc_info=True)
            self.ui.print_error(f"Unexpected error: {e}")
        
        return None, None
    
    def write_terraform_tfvars(self, config: Dict[str, str]):
        """Write configuration to terraform.tfvars file."""
        # Backup existing file
        if self.tfvars_file.exists():
            backup_path = self.tfvars_file.with_suffix('.tfvars.backup')
            shutil.copy2(self.tfvars_file, backup_path)
            self.ui.print_info(f"Backed up existing terraform.tfvars to {backup_path.name}")
        
        # Write new configuration
        tfvars_content = f'''# Required: Your project name (used for resource naming)
prefix = "{config['prefix']}"

# Required: Choose your cloud provider
cloud_provider = "{config['cloud_provider']}"  # or "AWS"

# Required: Choose your region (see supported regions below)
cloud_region = "{config['cloud_region']}"

# Required: Confluent Cloud credentials (or use environment variables)
confluent_cloud_api_key = "{config['confluent_cloud_api_key']}"
confluent_cloud_api_secret = "{config['confluent_cloud_api_secret']}"

# Required: Zapier MCP SSE Endpoint required for tool calling. Get from Zapier UI and should look like this
ZAPIER_SSE_ENDPOINT = "{config['ZAPIER_SSE_ENDPOINT']}"
'''
        
        try:
            with open(self.tfvars_file, 'w') as f:
                f.write(tfvars_content)
            
            self.ui.print_success(f"Configuration written to {self.tfvars_file}")
            self.save_config(config)
            self.logger.info("terraform.tfvars written successfully")
        except Exception as e:
            self.ui.print_error(f"Failed to write terraform.tfvars: {e}")
            raise

class TerraformManager:
    """Manages Terraform operations."""
    
    def __init__(self, ui: SetupUI, logger: SetupLogger, terraform_dir: Path):
        self.ui = ui
        self.logger = logger
        self.terraform_dir = terraform_dir
    
    def run_terraform_command(self, args: List[str], show_output: bool = True) -> Tuple[bool, str]:
        """Run a terraform command with proper error handling."""
        cmd = ['terraform'] + args
        self.logger.info(f"Running: {' '.join(cmd)}")
        
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
                    universal_newlines=True
                )
                
                output_lines = []
                for line in iter(process.stdout.readline, ''):
                    print(line.rstrip())
                    output_lines.append(line.rstrip())
                
                process.wait()
                output = '\n'.join(output_lines)
                success = process.returncode == 0
            else:
                # Capture output for quiet commands
                result = subprocess.run(
                    cmd,
                    cwd=self.terraform_dir,
                    capture_output=True,
                    text=True,
                    check=True
                )
                output = result.stdout
                success = True
                
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Terraform command failed: {e}")
            output = e.stderr if hasattr(e, 'stderr') else str(e)
            success = False
        
        return success, output
    
    def enable_provider_file(self, cloud_provider: str):
        """Enable the appropriate provider file for the selected cloud provider and disable others."""
        cloud_provider = cloud_provider.lower()
        
        # Define all supported providers
        all_providers = ['aws', 'azure']
        
        # Disable all other providers first
        for provider in all_providers:
            if provider != cloud_provider:
                provider_file = self.terraform_dir / f"providers-{provider}.tf"
                disabled_file = self.terraform_dir / f"providers-{provider}.tf.disabled"
                
                if provider_file.exists():
                    try:
                        provider_file.rename(disabled_file)
                        self.ui.print_info(f"Disabled {provider} provider")
                        self.logger.info(f"Renamed {provider_file} to {disabled_file}")
                    except Exception as e:
                        self.ui.print_error(f"Failed to disable {provider} provider: {e}")
                        raise
        
        # Enable the selected provider
        provider_file = self.terraform_dir / f"providers-{cloud_provider}.tf"
        disabled_file = self.terraform_dir / f"providers-{cloud_provider}.tf.disabled"
        
        if disabled_file.exists():
            try:
                disabled_file.rename(provider_file)
                self.ui.print_success(f"Enabled {cloud_provider} provider")
                self.logger.info(f"Renamed {disabled_file} to {provider_file}")
            except Exception as e:
                self.ui.print_error(f"Failed to enable provider file: {e}")
                raise
        elif provider_file.exists():
            self.ui.print_info(f"{cloud_provider} provider already enabled")
        else:
            self.ui.print_warning(f"Provider file not found: {provider_file}")
    
    def initialize(self) -> bool:
        """Initialize Terraform."""
        self.ui.print_info("Initializing Terraform...")
        success, output = self.run_terraform_command(['init'], show_output=False)
        
        if success:
            self.ui.print_success("Terraform initialized successfully")
        else:
            self.ui.print_error("Terraform initialization failed")
            print(output)
        
        return success
    
    def plan(self) -> bool:
        """Run terraform plan."""
        self.ui.print_info("Running Terraform plan (dry-run validation)...")
        success, output = self.run_terraform_command(['plan'], show_output=True)
        
        if success:
            self.ui.print_success("Terraform plan completed successfully")
        else:
            self.ui.print_error("Terraform plan failed")
        
        return success
    
    def apply(self) -> bool:
        """Run terraform apply."""
        self.ui.print_info("Deploying infrastructure with Terraform...")
        success, output = self.run_terraform_command(['apply', '--auto-approve'], show_output=True)
        
        if success:
            self.ui.print_success("Infrastructure deployed successfully!")
        else:
            self.ui.print_error("Terraform deployment failed")
        
        return success

class StreamingAgentsSetup:
    """Main setup orchestrator."""
    
    def __init__(self, args):
        self.args = args
        self.ui = SetupUI()
        self.logger = SetupLogger(verbose=args.verbose)
        
        # Setup paths
        self.root_dir = Path(__file__).parent
        self.terraform_dir = self.root_dir / "terraform"
        
        # Initialize managers
        self.prerequisites = PrerequisiteManager(self.ui, self.logger)
        self.config_manager = ConfigurationManager(self.ui, self.logger, self.terraform_dir)
        self.terraform = TerraformManager(self.ui, self.logger, self.terraform_dir)
        
        self.logger.info(f"Setup started with args: {vars(args)}")
        
        # Check Confluent login status at startup
        self.confluent_logged_in = self._check_confluent_login_status()
    
    def detect_setup_state(self) -> SetupState:
        """Intelligently detect the current setup state."""
        # Check prerequisites first
        for tool_name in self.prerequisites.TOOLS.keys():
            if not self.prerequisites.check_tool(tool_name):
                self.logger.info(f"Missing prerequisite: {tool_name}")
                return SetupState.PREREQUISITES_NEEDED
        
        # Check if terraform directory exists
        if not self.terraform_dir.exists():
            self.logger.error("Terraform directory not found")
            return SetupState.FRESH_START
        
        # Check configuration status
        valid_config, invalid_config = self.config_manager.get_config_status()
        
        if len(valid_config) == 0:
            return SetupState.CONFIGURATION_INCOMPLETE
        elif len(invalid_config) > 0:
            return SetupState.CONFIGURATION_INVALID
        
        # Check if terraform is initialized
        if not (self.terraform_dir / '.terraform').exists():
            return SetupState.TERRAFORM_NOT_INITIALIZED
        
        # Check if we have a terraform state (deployment completed)
        terraform_state = self.terraform_dir / 'terraform.tfstate'
        if terraform_state.exists():
            try:
                with open(terraform_state, 'r') as f:
                    state_data = json.load(f)
                    if state_data.get('resources', []):
                        return SetupState.COMPLETED
            except:
                pass
        
        # If we have valid config and terraform is initialized, we're ready for deployment
        return SetupState.DEPLOYMENT_READY
    
    def install_rich_if_needed(self):
        """Install rich library for better UI if not available."""
        if not RICH_AVAILABLE:
            if self.args.verbose:
                self.ui.print_info("Installing rich library for better terminal UI...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'rich'], 
                             check=True, capture_output=True)
                if self.args.verbose:
                    self.ui.print_success("Rich library installed. Please restart the script for enhanced UI.")
                return False
            except subprocess.CalledProcessError:
                if self.args.verbose:
                    self.ui.print_warning("Could not install rich library. Continuing with basic UI.")
                pass  # Silently continue if not verbose
        return True
    
    def _check_confluent_login_status(self) -> bool:
        """Check Confluent login status and prompt for login if needed."""
        if not self.prerequisites.check_tool('confluent'):
            return False
            
        logged_in = self.config_manager.check_confluent_login()
        if not logged_in:
            self.ui.print_warning("You are not logged in to Confluent Cloud")
            if self.ui.confirm("Would you like to log in to Confluent Cloud now?", default=True):
                return self._handle_confluent_login()
            else:
                self.ui.print_info("You can log in later using: confluent login")
        else:
            if self.args.verbose:
                self.ui.print_success("Already logged in to Confluent Cloud")
        return logged_in
    
    def _handle_confluent_login(self) -> bool:
        """Handle interactive Confluent Cloud login."""
        try:
            self.ui.print_info("Opening Confluent Cloud login...")
            subprocess.run(
                ['confluent', 'login'],
                check=True,
                text=True
            )
            
            # Verify login was successful
            if self.config_manager.check_confluent_login():
                self.ui.print_success("Successfully logged in to Confluent Cloud!")
                return True
            else:
                self.ui.print_warning("Login may have failed. You can try again later with: confluent login")
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
            # Install rich if needed and available
            if not self.install_rich_if_needed():
                return True  # Exit for restart
            
            self.ui.print_header(
                "🚀 Streaming Agents Quickstart Automated Setup"
            )
            
            # Handle special flags first
            if self.args.reset:
                return self.handle_reset()
            
            if self.args.dry_run:
                return self.handle_dry_run()
            
            # Detect current setup state
            current_state = self.detect_setup_state()
            self.logger.info(f"Detected setup state: {current_state.value}")
            
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
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            return False
    
    def handle_reset(self) -> bool:
        """Handle reset flag."""
        self.ui.print_warning("Reset mode: Clearing previous configuration...")
        
        # Remove config files
        config_file = Path(".setup_config.json")
        if config_file.exists():
            config_file.unlink()
            self.ui.print_info("Removed .setup_config.json")
        
        # Backup and clear terraform.tfvars
        tfvars_file = self.terraform_dir / "terraform.tfvars"
        if tfvars_file.exists():
            backup_path = tfvars_file.with_suffix('.tfvars.reset-backup')
            shutil.copy2(tfvars_file, backup_path)
            self.ui.print_info(f"Backed up terraform.tfvars to {backup_path.name}")
        
        self.ui.print_success("Reset completed. Run setup again to start fresh.")
        return True
    
    def handle_dry_run(self) -> bool:
        """Handle dry-run mode."""
        self.ui.print_info("Running in validation mode...")
        valid_config, invalid_config = self.config_manager.get_config_status()
        
        if len(valid_config) == 6:  # All required fields
            self.ui.print_success("✅ All configuration is valid")
            return True
        else:
            self.ui.print_warning(f"⚠️ {len(invalid_config)} configuration fields need attention")
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
    
    def handle_incomplete_config(self) -> bool:
        """Handle incomplete configuration."""
        self.ui.print_info("🔧 Configuration setup needed")
        config = self.smart_configuration_prompt()
        
        if not config:
            return False
        
        self.config_manager.write_terraform_tfvars(config)
        self.ui.print_success("Configuration saved!")
        
        # Continue to next phase
        return self.run()
    
    def handle_invalid_config(self) -> bool:
        """Handle invalid configuration."""
        valid_config, invalid_config = self.config_manager.get_config_status()
        
        self.ui.print_info("🔍 Found existing configuration with some issues:")
        for field, value in valid_config.items():
            self.ui.print_success(f"  ✅ {field}: {value}")
        for field, value in invalid_config.items():
            self.ui.print_warning(f"  ⚠️  {field}: {value or '(empty)'}")
        
        if self.ui.confirm("Fix the invalid configuration values?", default=True):
            updated_config = self.smart_configuration_prompt(existing_valid=valid_config, fix_invalid=invalid_config)
            if updated_config:
                self.config_manager.write_terraform_tfvars(updated_config)
                self.ui.print_success("Configuration updated!")
                return self.run()
        
        return False
    
    def handle_terraform_setup(self) -> bool:
        """Handle Terraform initialization and planning."""
        valid_config, _ = self.config_manager.get_config_status()
        
        self.ui.print_info("🏗️  Setting up Terraform infrastructure...")
        
        # Enable appropriate provider
        self.terraform.enable_provider_file(valid_config['cloud_provider'])
        
        # Initialize Terraform
        if not self.terraform.initialize():
            return False
        
        # Run plan
        if not self.terraform.plan():
            return False
        
        # Continue to deployment
        return self.run()
    
    def handle_deployment(self) -> bool:
        """Handle infrastructure deployment."""
        self.ui.print_info("🚀 Ready to deploy infrastructure!")
        
        if self.ui.confirm("Deploy the infrastructure now?", default=True):
            if not self.terraform.apply():
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
        self.ui.print_info("🌟 Starting fresh setup...")
        
        if not self.prerequisites.check_and_install_prerequisites():
            return False
        
        # Continue with configuration
        return self.run()
    
    def show_configuration_status(self, valid_config: Dict[str, str], invalid_config: Dict[str, str]):
        """Show current configuration status."""
        config_fields = ['prefix', 'cloud_provider', 'cloud_region', 
                        'confluent_cloud_api_key', 'confluent_cloud_api_secret', 
                        'ZAPIER_SSE_ENDPOINT']
        
        print("Current configuration status:")
        for i, field in enumerate(config_fields, 1):
            if field in valid_config:
                value = valid_config[field]
                if 'api_' in field or 'ZAPIER' in field:
                    value = "***configured***"
                self.ui.print_success(f"✅   {i}. {field}: {value}")
            elif field in invalid_config:
                value = invalid_config.get(field, '(empty)')
                if value and ('api_' in field or 'ZAPIER' in field):
                    value = "***needs validation***"
                self.ui.print_error(f"❌   {i}. {field}: {value or '(missing)'}")
            else:
                self.ui.print_error(f"❌   {i}. {field}: (missing)")
    
    def show_final_config_menu(self, valid_config: Dict[str, str], invalid_config: Dict[str, str]) -> str:
        """Show final configuration menu after all values have been collected."""
        self.ui.print_header("Final Configuration Review", "All required values collected")
        
        self.show_configuration_status(valid_config, invalid_config)
        
        # Only show editing options if there are no missing/invalid fields
        all_valid = len(invalid_config) == 0 and len(valid_config) == 6
        
        print("\nOptions:")
        if all_valid:
            print("  C. Continue with deployment")
            print("  1-6. Edit specific field by number")
        else:
            print("  C. Continue setup (complete missing values first)")
        print("  R. Start completely fresh (reset all values)")
        print("  Q. Quit setup")
        
        valid_choices = ['c', 'r', 'q']
        if all_valid:
            valid_choices.extend(['1', '2', '3', '4', '5', '6'])
        
        while True:
            choice = self.ui.prompt("Select option", "C").strip().lower()
            
            if choice == 'q':
                return 'quit'
            elif choice == 'r':
                return 'reset'
            elif choice == 'c' or choice == '':
                return 'continue'
            elif all_valid and choice.isdigit() and 1 <= int(choice) <= 6:
                return f'edit_{int(choice)}'
            else:
                valid_str = ', '.join(valid_choices).upper()
                self.ui.print_error(f"Invalid option. Please choose {valid_str}.")
    
    def smart_configuration_prompt(self, existing_valid: Dict[str, str] = None, fix_invalid: Dict[str, str] = None) -> Optional[Dict[str, str]]:
        """Smart configuration prompting with enhanced menu options."""
        existing_valid = existing_valid or {}
        fix_invalid = fix_invalid or {}
        
        # Start with valid existing config
        config = existing_valid.copy()
        
        # Merge in environment credentials
        env_creds = self.config_manager.detect_environment_credentials()
        config.update(env_creds)
        
        # Check if we need to show editing menu or just proceed with configuration
        all_fields = ['prefix', 'cloud_provider', 'cloud_region', 
                     'confluent_cloud_api_key', 'confluent_cloud_api_secret', 
                     'ZAPIER_SSE_ENDPOINT']
        
        missing_fields = [f for f in all_fields if f not in existing_valid and f not in config]
        invalid_fields = list(fix_invalid.keys()) if fix_invalid else []
        
        # If we have all fields valid, show the final review menu
        if not missing_fields and not invalid_fields:
            choice = self.show_final_config_menu(existing_valid, {})
        elif len(missing_fields) + len(invalid_fields) == len(all_fields):
            # All fields need attention - start fresh
            choice = 'continue'
        else:
            # Some fields are valid, some need work - show current status and continue
            self.ui.print_header("Configuration Status", "Continuing with missing/invalid values")
            self.show_configuration_status(existing_valid, fix_invalid or {})
            if self.ui.confirm("Continue to complete the configuration?", default=True):
                choice = 'continue'
            else:
                choice = 'quit'
        
        if choice == 'quit':
            return None
        elif choice == 'reset':
            # Start completely fresh
            config = {}
            fix_invalid = {'prefix': '', 'cloud_provider': '', 'cloud_region': '', 
                          'confluent_cloud_api_key': '', 'confluent_cloud_api_secret': '', 
                          'ZAPIER_SSE_ENDPOINT': ''}
        elif choice.startswith('edit_'):
            # Edit specific field
            field_num = int(choice.split('_')[1])
            config_fields = ['prefix', 'cloud_provider', 'cloud_region', 
                            'confluent_cloud_api_key', 'confluent_cloud_api_secret', 
                            'ZAPIER_SSE_ENDPOINT']
            field_to_edit = config_fields[field_num - 1]
            
            self.ui.print_header("Edit Configuration", f"Editing: {field_to_edit}")
            new_value = self.prompt_for_field(field_to_edit, config)
            if new_value:
                config[field_to_edit] = new_value
                # Test API keys if both are now present
                if field_to_edit in ['confluent_cloud_api_key', 'confluent_cloud_api_secret']:
                    api_key = config.get('confluent_cloud_api_key')
                    api_secret = config.get('confluent_cloud_api_secret')
                    if api_key and api_secret:
                        valid, message = self.config_manager.test_confluent_api_keys(api_key, api_secret)
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
        required_fields = ['prefix', 'cloud_provider', 'cloud_region', 
                          'confluent_cloud_api_key', 'confluent_cloud_api_secret', 
                          'ZAPIER_SSE_ENDPOINT']
        
        # Show what we're using if continue mode
        if choice == 'continue' and existing_valid:
            self.ui.print_header("Configuration", "Only missing or invalid values will be prompted")
            self.ui.print_info("✅ Using existing valid configuration:")
            for key, value in existing_valid.items():
                if key not in ['confluent_cloud_api_key', 'confluent_cloud_api_secret', 'ZAPIER_SSE_ENDPOINT']:
                    self.ui.print_success(f"  {key}: {value}")
                else:
                    self.ui.print_success(f"  {key}: ***configured***")
        
        for field in required_fields:
            if field not in config or field in fix_invalid:
                value = self.prompt_for_field(field, config)
                if not value:
                    self.ui.print_error(f"❌ {field} is required. Setup cannot continue without it.")
                    return None
                config[field] = value
        
        # Final validation of API keys if both are present
        api_key = config.get('confluent_cloud_api_key')
        api_secret = config.get('confluent_cloud_api_secret')
        if api_key and api_secret:
            self.ui.print_info("🔍 Testing API keys...")
            valid, message = self.config_manager.test_confluent_api_keys(api_key, api_secret)
            if valid:
                self.ui.print_success(f"✅ {message}")
            else:
                self.ui.print_warning(f"⚠️ {message} (continuing anyway)")
        
        return config
    
    def prompt_for_field(self, field: str, config: Dict[str, str]) -> str:
        """Prompt for a specific configuration field."""
        if field == 'prefix':
            # Use default prefix without prompting
            return "streaming-agents"
        
        elif field == 'cloud_provider':
            while True:
                value = self.ui.prompt("Cloud provider (aws/azure)", "azure").lower()
                if value in ['aws', 'azure']:
                    return value
                self.ui.print_error("Please choose either 'aws' or 'azure'")
        
        elif field == 'cloud_region':
            provider = config.get('cloud_provider', 'azure').lower()
            available_regions = self.config_manager.CLOUD_REGIONS[provider]
            
            self.ui.print_info(f"Available {provider.upper()} regions:")
            for i, region in enumerate(available_regions[:8], 1):  # Show first 8
                print(f"  {i:2d}. {region}")
            if len(available_regions) > 8:
                print(f"  ... and {len(available_regions) - 8} more")
            
            while True:
                value = self.ui.prompt("Select region (exact name or number)", available_regions[0])
                if value.isdigit():
                    idx = int(value) - 1
                    if 0 <= idx < len(available_regions):
                        return available_regions[idx]
                elif value in available_regions:
                    return value
                self.ui.print_error("Please select a valid region by exact name or number")
        
        elif field == 'confluent_cloud_api_key':
            # Check if Confluent CLI is logged in
            cli_logged_in = self.config_manager.check_confluent_login()
            
            if cli_logged_in:
                self.ui.print_success("✅ Confluent CLI is logged in")
                # Show available environments
                environments = self.config_manager.get_confluent_environments()
                if environments:
                    env_count = len(environments)
                    self.ui.print_info(f"Found {env_count} Confluent environment{'s' if env_count != 1 else ''}")
                
                if self.ui.confirm("Auto-generate API keys with Cloud Resource Management scope?", default=True):
                    self.ui.print_info("🔑 Generating API keys...")
                    key, secret = self.config_manager.generate_confluent_api_keys(config.get('prefix', 'streaming-agents'))
                    if key and secret:
                        config['confluent_cloud_api_secret'] = secret  # Store secret for next prompt
                        self.ui.print_success("✅ API keys generated successfully")
                        return key
                    else:
                        self.ui.print_error("❌ Failed to generate API keys")
                
            # If auto-generation failed or user declined, prompt for manual entry
            if not cli_logged_in:
                self.ui.print_info("💡 To auto-generate keys, run: confluent login")
            
            attempts = 0
            max_attempts = 3
            while attempts < max_attempts:
                value = self.ui.prompt("Enter your Confluent Cloud API Key")
                if value and value.strip():  # Check for non-empty after strip
                    return value.strip()
                attempts += 1
                if attempts < max_attempts:
                    self.ui.print_error(f"❌ API Key cannot be empty. {max_attempts - attempts} attempts remaining.")
                else:
                    self.ui.print_error("❌ Maximum attempts reached. Setup cannot continue without API key.")
            return ""
        
        elif field == 'confluent_cloud_api_secret':
            # If we already generated both keys, return the stored secret
            if 'confluent_cloud_api_secret' in config:
                return config['confluent_cloud_api_secret']
            else:
                attempts = 0
                max_attempts = 3
                while attempts < max_attempts:
                    value = self.ui.prompt("Enter your Confluent Cloud API Secret")
                    if value and value.strip():
                        return value.strip()
                    attempts += 1
                    if attempts < max_attempts:
                        self.ui.print_error(f"❌ API Secret cannot be empty. {max_attempts - attempts} attempts remaining.")
                    else:
                        self.ui.print_error("❌ Maximum attempts reached. Setup cannot continue without API secret.")
                return ""
        
        elif field == 'ZAPIER_SSE_ENDPOINT':
            self.ui.print_info("📋 You need a real Zapier SSE endpoint URL from your Zapier MCP server setup.")
            self.ui.print_info("   It should look like: https://mcp.zapier.com/api/mcp/s/<YOUR-LONG-API-KEY>/sse")
            self.ui.print_warning("   Note: Sample URLs with 'test-key' will be rejected")
            
            while True:
                value = self.ui.prompt("Zapier SSE Endpoint URL")
                if self.config_manager.validate_zapier_url(value):
                    return value
                
                # Provide specific error messages
                if not value:
                    self.ui.print_error("❌ URL cannot be empty")
                elif 'test-key' in value.lower():
                    self.ui.print_error("❌ This appears to be a sample URL. Please use your actual Zapier SSE endpoint.")
                elif not value.startswith('https://mcp.zapier.com/api/mcp/s/'):
                    self.ui.print_error("❌ URL must start with: https://mcp.zapier.com/api/mcp/s/")
                elif not value.endswith('/sse'):
                    self.ui.print_error("❌ URL must end with: /sse")
                else:
                    self.ui.print_error("❌ Invalid Zapier SSE endpoint format. API key portion seems too short.")
        
        return ""
    
    def show_next_steps(self):
        """Show next steps after successful deployment."""
        self.ui.print_info("Next steps:")
        self.ui.print_info("1. Set up Flink MCP connection (see mcp_commands.txt)")
        self.ui.print_info("2. Generate sample data (cd terraform/data-gen && ./run.sh)")  
        self.ui.print_info("3. Proceed to Lab1: Price Matching Using Tool Calling")

def main():
    """Main entry point."""
    # Simple argument parsing - hidden advanced options
    parser = argparse.ArgumentParser(
        description="🚀 Streaming Agents Quickstart Setup\n\nJust run 'python setup.py' - the script will intelligently detect what needs to be done!",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False  # Custom help to hide advanced options
    )
    
    # Primary help
    parser.add_argument(
        '-h', '--help',
        action='store_true',
        help='Show this help message'
    )
    
    # Hidden advanced options (not shown in primary help)
    parser.add_argument('--resume', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--reset', action='store_true', help=argparse.SUPPRESS) 
    parser.add_argument('--dry-run', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--verbose', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--advanced-help', action='store_true', help=argparse.SUPPRESS)
    
    args = parser.parse_args()
    
    # Handle help
    if args.help:
        print("🚀 Streaming Agents Quickstart Setup")
        print("\nUsage:")
        print("  python setup.py          # Intelligent setup - detects current state and continues")
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
        print("\nNote: These options are rarely needed as the script auto-detects what to do.")
        return
    
    # Create setup instance with defaults for missing args
    class Args:
        def __init__(self):
            self.resume = getattr(args, 'resume', False)
            self.reset = getattr(args, 'reset', False) 
            self.dry_run = getattr(args, 'dry_run', False)
            self.verbose = getattr(args, 'verbose', False)
    
    setup = StreamingAgentsSetup(Args())
    success = setup.run()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()