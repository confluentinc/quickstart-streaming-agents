"""
Generate a comprehensive DEPLOYED_RESOURCES.md file from Terraform outputs.

This module creates a markdown file containing all deployed resources, credentials,
and configuration details for easy reference after Core deployment.

Usage:
    # From terraform_runner (automatic)
    generate_credentials_markdown(cloud_provider, tf_outputs, output_path)

    # Standalone (manual)
    uv run deployment-summary aws/core
    uv run deployment-summary azure/core
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Union, Optional


def generate_credentials_markdown(cloud_provider: str, tf_outputs: Dict[str, Any], output_path: Path) -> None:
    """
    Generate DEPLOYED_RESOURCES.md file from Terraform outputs.

    Args:
        cloud_provider: Cloud provider ("aws" or "azure")
        tf_outputs: Dictionary of terraform outputs (from terraform output -json)
        output_path: Path where the markdown file should be saved
    """
    try:
        # Extract values from terraform outputs (handle sensitive values)
        def get_output(key: str, default: str = "") -> str:
            """Extract value from terraform output, handling sensitive values."""
            if key not in tf_outputs:
                return default
            output = tf_outputs[key]
            # If it's a dict with 'value' key (terraform output format)
            if isinstance(output, dict) and 'value' in output:
                return str(output['value']) if output['value'] is not None else default
            return str(output) if output is not None else default

        # Build markdown sections
        sections = [
            _build_header(),
            _build_account_section(tf_outputs, get_output),
            _build_cloud_details_section(cloud_provider, tf_outputs, get_output),
            _build_cloud_resources_section(cloud_provider, get_output),
            _build_credentials_section(tf_outputs, get_output),
            _build_resource_inventory_section(tf_outputs, get_output),
            _build_llm_configuration_section(cloud_provider, tf_outputs, get_output),
        ]

        # Combine all sections
        markdown_content = "\n\n".join(sections)

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown_content)

        print(f"Resource summary saved to: {output_path}")

    except Exception as e:
        print(f"Warning: Failed to generate DEPLOYED_RESOURCES.md: {e}")
        # Don't fail the deployment if markdown generation fails


def _build_header() -> str:
    """Build the warning header."""
    return """# Confluent Cloud Resources

**WARNING: This file contains API keys, secrets, and other sensitive credentials. Do not commit to version control or share publicly.**

---"""


def _build_account_section(tf_outputs: Dict[str, Any], get_output: callable) -> str:
    """Build the Account Information section."""
    owner_email = get_output("owner_email", "Not provided")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    region = get_output("cloud_region")
    env_name = get_output("confluent_environment_display_name")
    env_id = get_output("confluent_environment_id")

    return f"""## Account Information

**Owner Email**: `{owner_email}`
**Deployed**: {timestamp}
**Region**: {region}
**Environment**: {env_name}
**Environment ID**: `{env_id}`

---"""


def _build_cloud_details_section(cloud_provider: str, tf_outputs: Dict[str, Any], get_output: callable) -> str:
    """Build the Cloud Details section."""
    region = get_output("cloud_region")

    if cloud_provider == "azure":
        subscription = get_output("azure_subscription_id")
        return f"""## Cloud Details

- **Provider**: Azure
- **Region**: `{region}`
- **Subscription**: `{subscription}`

---"""
    else:  # AWS
        return f"""## Cloud Details

- **Provider**: AWS
- **Region**: `{region}`

---"""


def _build_cloud_resources_section(cloud_provider: str, get_output: callable) -> str:
    """Build the cloud-specific resources section."""
    random_id = get_output("random_id")

    if cloud_provider == "azure":
        resource_group = f"rg-openai-{random_id}"
        cognitive_account = f"openai-{random_id}"
        cognitive_endpoint = f"https://openai-{random_id}.openai.azure.com/"
        gpt4_deployment = f"gpt4-deployment-{random_id}"
        embedding_deployment = f"embedding-deployment-{random_id}"

        return f"""## Azure Resources Created

The following Azure resources were created in this deployment:

| Resource Type | Name | Purpose |
|---------------|------|---------|
| **Resource Group** | `{resource_group}` | Container for OpenAI resources |
| **Cognitive Account** | `{cognitive_account}` | Azure OpenAI service |
| **Cognitive Endpoint** | `{cognitive_endpoint}` | API endpoint |
| **GPT-4 Deployment** | `{gpt4_deployment}` | Text generation model |
| **Embedding Deployment** | `{embedding_deployment}` | Text embedding model |

---"""
    else:  # AWS
        iam_user = f"bedrock-user-{random_id}"
        iam_policy = f"bedrock-policy-{random_id}"
        access_key_id = get_output("aws_access_key_id")

        return f"""## AWS Resources Created

The following AWS resources were created in this deployment:

| Resource Type | Name/ID | Purpose |
|---------------|---------|---------|
| **IAM User** | `{iam_user}` | Bedrock API access |
| **IAM Policy** | `{iam_policy}` | Bedrock permissions |
| **IAM Access Key** | `{access_key_id}` | Bedrock credentials |

---"""


def _build_credentials_section(tf_outputs: Dict[str, Any], get_output: callable) -> str:
    """Build the Service Credentials section."""
    # Primary credentials
    org_id = get_output("confluent_organization_id")
    env_id = get_output("confluent_environment_id")
    cloud_key = get_output("confluent_cloud_api_key")
    cloud_secret = get_output("confluent_cloud_api_secret")

    # Additional credentials
    kafka_bootstrap = get_output("confluent_kafka_cluster_bootstrap_endpoint")
    kafka_key = get_output("app_manager_kafka_api_key")
    kafka_secret = get_output("app_manager_kafka_api_secret")

    sr_endpoint = get_output("confluent_schema_registry_rest_endpoint")
    sr_key = get_output("app_manager_schema_registry_api_key")
    sr_secret = get_output("app_manager_schema_registry_api_secret")

    flink_endpoint = get_output("confluent_flink_rest_endpoint")
    flink_pool = get_output("confluent_flink_compute_pool_id")
    flink_key = get_output("app_manager_flink_api_key")
    flink_secret = get_output("app_manager_flink_api_secret")

    return f"""## Service Credentials

### Primary Credentials (Organization Admin)

| Service | Endpoint/Resource | API Key | API Secret |
|---------|-------------------|---------|------------|
| **Confluent Cloud** | Org: `{org_id}`<br>Env: `{env_id}` | `{cloud_key}` | `{cloud_secret}` |

**Note**: These are your Organization Admin credentials - use these for CLI access and overall account management.

### Additional Service Credentials

| Service | Endpoint/Resource | API Key | API Secret |
|---------|-------------------|---------|------------|
| **Kafka Cluster** | `{kafka_bootstrap}` | `{kafka_key}` | `{kafka_secret}` |
| **Schema Registry** | `{sr_endpoint}` | `{sr_key}` | `{sr_secret}` |
| **Flink** | `{flink_endpoint}`<br>Pool: `{flink_pool}` | `{flink_key}` | `{flink_secret}` |

---"""


def _build_resource_inventory_section(tf_outputs: Dict[str, Any], get_output: callable) -> str:
    """Build the Resource Inventory section."""
    env_id = get_output("confluent_environment_id")
    env_name = get_output("confluent_environment_display_name")

    cluster_id = get_output("confluent_kafka_cluster_id")
    cluster_name = get_output("confluent_kafka_cluster_display_name")
    cluster_rest = get_output("confluent_kafka_cluster_rest_endpoint")

    sr_id = get_output("confluent_schema_registry_id")
    sr_endpoint = get_output("confluent_schema_registry_rest_endpoint")

    flink_pool_id = get_output("confluent_flink_compute_pool_id")

    sa_id = get_output("app_manager_service_account_id")

    return f"""## Resource Inventory

| Resource Type | ID | Display Name / Details |
|---------------|----|-----------------------|
| Environment | `{env_id}` | {env_name} |
| Kafka Cluster | `{cluster_id}` | {cluster_name}<br>REST: `{cluster_rest}` |
| Schema Registry | `{sr_id}` | `{sr_endpoint}` |
| Flink Pool | `{flink_pool_id}` | - |
| Service Account | `{sa_id}` | Role: EnvironmentAdmin |

---"""


def _build_llm_configuration_section(cloud_provider: str, tf_outputs: Dict[str, Any], get_output: callable) -> str:
    """Build the LLM Configuration section."""
    textgen_connection = get_output("llm_connection_name")
    embedding_connection = get_output("llm_embedding_connection_name")
    env_name = get_output("confluent_environment_display_name")
    cluster_name = get_output("confluent_kafka_cluster_display_name")

    # Determine provider-specific details
    if cloud_provider == "azure":
        provider = "azureopenai"
        provider_name = "Azure OpenAI"
    else:  # AWS
        provider = "bedrock"
        provider_name = "AWS Bedrock"

    return f"""## LLM Configuration

### Flink Connections

The following Flink AI connections were created via Terraform ({provider_name}):

- **Text Generation Connection**: `{textgen_connection}`
- **Embedding Connection**: `{embedding_connection}`

### Flink Models

The following Flink AI models were created and are ready to use:

#### Text Generation Model

**Model Name**: `llm_textgen_model`

```sql
CREATE MODEL `{env_name}`.`{cluster_name}`.`llm_textgen_model`
INPUT (prompt STRING)
OUTPUT (response STRING)
WITH(
  'provider' = '{provider}',
  'task' = 'text_generation',
  '{provider}.connection' = '{textgen_connection}',
  '{provider}.model_version' = '2024-08-06',
  '{provider}.PARAMS.max_tokens' = '50000'
);
```

#### Embedding Model

**Model Name**: `llm_embedding_model`

```sql
CREATE MODEL `{env_name}`.`{cluster_name}`.`llm_embedding_model`
INPUT (text STRING)
OUTPUT (embedding ARRAY<FLOAT>)
WITH(
  'provider' = '{provider}',
  'task' = 'embedding',
  '{provider}.connection' = '{embedding_connection}',
  '{provider}.PARAMS.max_tokens' = '50000'
);
```

### Usage Example

```sql
-- Generate text with the LLM
SELECT response
FROM my_table,
LATERAL TABLE(ML_PREDICT('llm_textgen_model', prompt_column));

-- Generate embeddings
SELECT embedding
FROM my_table,
LATERAL TABLE(ML_PREDICT('llm_embedding_model', text_column));
```"""


def main():
    """
    Main entry point for standalone script execution.

    Usage:
        uv run deployment-summary terraform/core
    """
    if len(sys.argv) != 2:
        print("Usage: uv run deployment-summary <terraform-core-path>")
        print("Example: uv run deployment-summary terraform/core")
        sys.exit(1)

    # Parse arguments
    terraform_dir = Path(sys.argv[1])

    # Validate path
    if not terraform_dir.exists():
        print(f"Error: Directory not found: {terraform_dir}")
        sys.exit(1)

    if not (terraform_dir / "main.tf").exists():
        print(f"Error: Not a valid terraform directory (no main.tf found): {terraform_dir}")
        sys.exit(1)

    # Detect cloud provider from terraform state file
    state_file = terraform_dir / "terraform.tfstate"
    cloud_provider = None

    if state_file.exists():
        try:
            import json
            with open(state_file) as f:
                state = json.load(f)
                outputs = state.get("outputs", {})
                if "cloud_provider" in outputs:
                    cloud_provider = outputs["cloud_provider"].get("value", "").lower()
        except Exception as e:
            print(f"Warning: Could not read cloud provider from state file: {e}")

    if not cloud_provider or cloud_provider not in ["aws", "azure"]:
        print(f"Error: Could not determine cloud provider from terraform state")
        print(f"Expected 'cloud_provider' output in {state_file}")
        sys.exit(1)

    # Run terraform output -json
    print(f"Reading Terraform outputs from {terraform_dir}...")
    try:
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
            check=True
        )
        tf_outputs = json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to run terraform output: {e}")
        print("Make sure terraform has been initialized and applied in this directory.")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: terraform command not found. Please install Terraform.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse terraform output JSON: {e}")
        sys.exit(1)

    # Generate markdown
    output_file = terraform_dir / "DEPLOYED_RESOURCES.md"
    generate_credentials_markdown(cloud_provider, tf_outputs, output_file)
    print(f"\nSuccess! Deployment summary generated at: {output_file}")


def generate_flink_sql_summary(
    lab_name: str,
    cloud_provider: str,
    tf_outputs: Dict[str, Any],
    output_path: Path,
    automated_commands: Optional[list] = None,
    manual_commands: Union[list, str, None] = None,
    core_resources: Optional[list] = None
) -> None:
    """
    Generate a Flink SQL command summary markdown file for a lab.

    Args:
        lab_name: Name of the lab (e.g., "lab1-tool-calling")
        cloud_provider: Cloud provider ("aws" or "azure")
        tf_outputs: Dictionary of terraform outputs
        output_path: Path where the markdown file should be saved
        automated_commands: List of dicts with 'title' and 'sql' keys for Terraform-created resources
        manual_commands: Either a markdown string OR list of dicts with 'title' and 'sql' keys for manual walkthrough steps
        core_resources: List of dicts with 'title' and 'sql' keys for Core infrastructure resources used by this lab
    """
    try:
        # Helper function to get terraform outputs
        def get_output(key: str, default: str = "") -> str:
            """Extract value from terraform output."""
            if key not in tf_outputs:
                return default
            output = tf_outputs[key]
            if isinstance(output, dict) and 'value' in output:
                return str(output['value']) if output['value'] is not None else default
            return str(output) if output is not None else default

        # Build markdown content
        content = f"""# {lab_name.replace('-', ' ').title()} - Flink SQL Commands

This file contains the Flink SQL commands used in {lab_name.replace('-', ' ').title()}.

**Environment**: {get_output("confluent_environment_display_name")}
**Cluster**: {get_output("confluent_kafka_cluster_display_name")}
**Cloud Provider**: {cloud_provider.upper()}
**Region**: {get_output("cloud_region")}

---

"""

        # Add core resources section first if applicable
        if core_resources:
            content += "## Shared Resources from Core Infrastructure\n\n"
            content += "The following LLM connections and models were created in Core Terraform and are used by this lab:\n\n"

            for idx, cmd in enumerate(core_resources, 1):
                content += f"### {idx}. {cmd['title']}\n\n"
                content += f"```sql\n{cmd['sql']}\n```\n\n"

            content += "---\n\n"

        # Add automated commands
        content += "## Automated Commands (Created by Terraform)\n\n"
        content += "The following Flink SQL commands were automatically executed during Terraform deployment:\n\n"

        if automated_commands:
            for idx, cmd in enumerate(automated_commands, 1):
                content += f"### {idx}. {cmd['title']}\n\n"
                content += f"```sql\n{cmd['sql']}\n```\n\n"
        else:
            content += "_No automated SQL commands for this lab._\n\n"

        content += "---\n\n## Manual Commands (From Walkthrough)\n\n"
        content += "The following commands are meant to be run manually as part of the lab walkthrough:\n\n"

        # Add manual commands (handle both string and list formats)
        if manual_commands:
            if isinstance(manual_commands, str):
                # Markdown string from walkthrough extraction
                content += manual_commands + "\n\n"
            else:
                # Legacy list of dicts format
                for idx, cmd in enumerate(manual_commands, 1):
                    content += f"### {idx}. {cmd['title']}\n\n"
                    content += f"```sql\n{cmd['sql']}\n```\n\n"
        else:
            content += "_No manual SQL commands for this lab._\n\n"

        # Add footer
        content += f"""---

## Notes

- This file is auto-generated during Terraform deployment
- Commands shown without full table qualification for readability
- Refer to the lab walkthrough for complete usage instructions and context
- This file will be automatically removed when running `uv run destroy`

**Generated**: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}
"""

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content)

        print(f"Flink SQL summary saved to: {output_path}")

    except Exception as e:
        # Don't fail the deployment if markdown generation fails
        print(f"Warning: Failed to generate Flink SQL summary: {e}")


if __name__ == "__main__":
    main()
