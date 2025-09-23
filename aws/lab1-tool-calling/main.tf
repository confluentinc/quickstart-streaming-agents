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
# AWS-SPECIFIC RESOURCES FOR LAB1-TOOL-CALLING
# ------------------------------------------------------

# Lab1 uses the shared LLM infrastructure from core
# LLM connection and model are now available via: data.terraform_remote_state.core.outputs.llm_connection_name

# Generate MCP commands file with CLI instructions
resource "local_file" "mcp_commands" {
  filename = "${path.module}/mcp_commands.txt"
  content  = <<-EOT
# Lab1 Tool Calling - Generated Commands
#
# 🎉 AUTOMATED BY TERRAFORM:
# ✅ Core LLM infrastructure (deployed in core terraform)
# ✅ LLM connection: ${data.terraform_remote_state.core.outputs.llm_connection_name}
# ✅ LLM model: llm_textgen_model (available in core)
#
# 📋 MANUAL STEPS REQUIRED:
# Run these commands after terraform apply completes

# Step 1: Create Zapier MCP Connection (CLI only - not supported by Terraform provider)
confluent flink connection create zapier-mcp-connection \
  --cloud AWS \
  --region ${local.cloud_region} \
  --type mcp_server \
  --endpoint ${replace(var.ZAPIER_SSE_ENDPOINT, "/sse", "")} \
  --api-key api_key \
  --environment ${data.terraform_remote_state.core.outputs.confluent_environment_id} \
  --sse-endpoint ${var.ZAPIER_SSE_ENDPOINT}

# Step 2: Create Flink SQL Models (run these in Confluent Cloud SQL workspace)

# Agent 1 and 3: Flink SQL CREATE MODEL Command (with MCP)
CREATE MODEL `zapier_mcp_model`
INPUT (prompt STRING)
OUTPUT (response STRING)
WITH (
  'provider' = 'bedrock',
  'task' = 'text_generation',
  'bedrock.connection' = '${data.terraform_remote_state.core.outputs.llm_connection_name}',
  'bedrock.params.max_tokens' = '50000',
  'mcp.connection' = 'zapier-mcp-connection'
);

# Agent 2: Use the shared llm_textgen_model (already created in core terraform)
# No need to create this model - it's available as 'llm_textgen_model'

EOT
}
