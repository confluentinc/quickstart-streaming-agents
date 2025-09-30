# Reference to core infrastructure
data "terraform_remote_state" "core" {
  backend = "local"
  config = {
    path = "../core/terraform.tfstate"
  }
}

# Use cloud_region from core infrastructure
locals {
  cloud_region = data.terraform_remote_state.core.outputs.cloud_region
}

# Random ID for unique resource names for this lab
resource "random_id" "lab_suffix" {
  byte_length = 4
}

# ------------------------------------------------------
# AZURE-SPECIFIC RESOURCES FOR LAB1-TOOL-CALLING
# ------------------------------------------------------

# Lab1 uses the shared LLM infrastructure from core
# LLM connection and model are now available via: data.terraform_remote_state.core.outputs.llm_connection_name

# Get organization data
data "confluent_organization" "main" {}

# Get Flink region data
data "confluent_flink_region" "lab1_flink_region" {
  cloud  = "AZURE"
  region = local.cloud_region
}

# Automatically create MCP connection using Python script
resource "null_resource" "create_mcp_connection" {
  # This runs the Python script to create the MCP connection via Confluent CLI
  provisioner "local-exec" {
    command     = "uv run mcp_setup azure"
    working_dir = "${path.module}/../.."
  }

  # Re-run if the Zapier endpoint changes
  triggers = {
    zapier_endpoint = var.ZAPIER_SSE_ENDPOINT
    environment_id  = data.terraform_remote_state.core.outputs.confluent_environment_id
  }

  depends_on = [
    data.terraform_remote_state.core
  ]
}

# Create the Zapier MCP Model via Flink SQL
resource "confluent_flink_statement" "zapier_mcp_model" {
  organization {
    id = data.confluent_organization.main.id
  }
  environment {
    id = data.terraform_remote_state.core.outputs.confluent_environment_id
  }
  compute_pool {
    id = data.terraform_remote_state.core.outputs.confluent_flink_compute_pool_id
  }
  principal {
    id = data.terraform_remote_state.core.outputs.app_manager_service_account_id
  }
  rest_endpoint = data.confluent_flink_region.lab1_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement = "CREATE MODEL `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.`zapier_mcp_model` INPUT (prompt STRING) OUTPUT (response STRING) WITH ( 'provider' = 'azureopenai', 'task' = 'text_generation', 'azureopenai.connection' = '${data.terraform_remote_state.core.outputs.llm_connection_name}', 'mcp.connection' = 'zapier-mcp-connection' );"

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = "default"
  }

  # Ensure MCP connection is created first
  depends_on = [
    null_resource.create_mcp_connection
  ]
}

# Generate MCP commands file with CLI instructions (kept for reference/manual fallback)
resource "local_file" "mcp_commands" {
  filename = "${path.module}/mcp_commands.txt"
  content  = <<-EOT
# Lab1 Tool Calling - Setup Status
#
# 🎉 FULLY AUTOMATED BY TERRAFORM:
# ✅ Core LLM infrastructure (deployed in core terraform)
# ✅ LLM connection: ${data.terraform_remote_state.core.outputs.llm_connection_name}
# ✅ LLM model: llm_textgen_model (available in core)
# ✅ MCP connection: zapier-mcp-connection (created automatically via uv script)
# ✅ MCP model: zapier_mcp_model (created automatically via Terraform)
#
# ℹ️ NO MANUAL STEPS REQUIRED
# All setup is handled automatically during 'terraform apply'
#
# 📋 MANUAL COMMANDS (for reference only, if you need to recreate manually):

# Step 1: Create Zapier MCP Connection (automated via: uv run mcp_setup azure)
confluent flink connection create zapier-mcp-connection \
  --cloud AZURE \
  --region ${local.cloud_region} \
  --type mcp_server \
  --endpoint ${replace(var.ZAPIER_SSE_ENDPOINT, "/sse", "")} \
  --api-key api_key \
  --environment ${data.terraform_remote_state.core.outputs.confluent_environment_id} \
  --sse-endpoint ${var.ZAPIER_SSE_ENDPOINT}

# Step 2: Create Flink SQL Models (automated via Terraform confluent_flink_statement)

# Agent 1 and 3: Flink SQL CREATE MODEL Command (with MCP)
CREATE MODEL `zapier_mcp_model`
INPUT (prompt STRING)
OUTPUT (response STRING)
WITH (
  'provider' = 'azureopenai',
  'task' = 'text_generation',
  'azureopenai.connection' = '${data.terraform_remote_state.core.outputs.llm_connection_name}',
  'mcp.connection' = 'zapier-mcp-connection'
);

# Agent 2: Use the shared llm_textgen_model (already created in core terraform)
# No need to create this model - it's available as 'llm_textgen_model'

EOT
}
