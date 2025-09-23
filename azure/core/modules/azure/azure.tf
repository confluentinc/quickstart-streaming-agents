# modules/azure/main.tf
# Provider configuration moved to root module

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    confluent = {
      source = "confluentinc/confluent"
    }
  }
}

# Azure OpenAI Configuration
resource "azurerm_resource_group" "openai_rg" {
  name     = "rg-openai-${var.random_id}"
  location = var.cloud_region
}

resource "azurerm_cognitive_account" "openai_account" {
  name                = "openai-${var.random_id}"
  location            = azurerm_resource_group.openai_rg.location
  resource_group_name = azurerm_resource_group.openai_rg.name
  kind                = "OpenAI"
  sku_name            = "S0"
  public_network_access_enabled = true 
  custom_subdomain_name = "openai-${var.random_id}"
}

resource "azurerm_cognitive_deployment" "openai_deployment" {
  name                = "gpt4-deployment-${var.random_id}"
  cognitive_account_id = azurerm_cognitive_account.openai_account.id
  model {
    format  = "OpenAI"
    name    = "gpt-4.1"
  }
  scale {
    type = "GlobalStandard"
    capacity = 100
  }
}

# Azure Flink connection
resource "confluent_flink_connection" "azure_connection" {
  organization {
    id = var.confluent_organization_id
  }
  environment {
    id = var.confluent_environment_id
  }
  compute_pool {
    id = var.confluent_compute_pool_id
  }
  principal {
    id = var.confluent_service_account_id
  }
  rest_endpoint = var.confluent_flink_rest_endpoint
  credentials {
    key    = var.confluent_flink_api_key_id
    secret = var.confluent_flink_api_key_secret
  }

  display_name = "${var.prefix}-azure-openai-connection"
  type         = "AZUREOPENAI"
  endpoint     = "${azurerm_cognitive_account.openai_account.endpoint}openai/deployments/${azurerm_cognitive_deployment.openai_deployment.name}/chat/completions?api-version=2025-01-01-preview"
  api_key      = azurerm_cognitive_account.openai_account.primary_access_key

  lifecycle {
    prevent_destroy = false
  }
}

# Create the mcp_commands.txt file with Azure-specific commands
resource "local_file" "mcp_commands" {
  filename = "${path.module}/../../mcp_commands.txt"
  content  = <<-EOT
# Confluent Flink MCP Connection Create Command

confluent flink connection create zapier-mcp-connection \
  --cloud AZURE \
  --region ${var.cloud_region} \
  --type mcp_server \
  --endpoint ${var.zapier_endpoint} \
  --api-key api_key \
  --environment ${var.confluent_environment_id} \
  --sse-endpoint ${var.zapier_sse_endpoint}

# Agent 1 and 3: Flink SQL CREATE MODEL Command (with MCP)

CREATE MODEL `zapier_mcp_model`
INPUT (prompt STRING)
OUTPUT (response STRING)
WITH (
  'provider' = 'azureopenai',
  'task' = 'text_generation',
  'azureopenai.connection' = '${confluent_flink_connection.azure_connection.display_name}',
  'mcp.connection' = 'zapier-mcp-connection'
);

# Agent 2: Flink SQL CREATE LLM-Only MODEL Command

CREATE MODEL llm_textgen_model
INPUT (prompt STRING)
OUTPUT (response STRING)
WITH(
  'provider' = 'azureopenai',
  'task' = 'text_generation',
  'azureopenai.connection' = '${confluent_flink_connection.azure_connection.display_name}',
  'azureopenai.model_version' = '2025-04-14'
);

  EOT
}

variable "cloud_region" {
  description = "Region for deployment"
  type        = string
  default     = "us-east-2"
} 

variable "random_id" {
  description = "random suffix"
  type        = string
}

variable "prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "confluent_organization_id" {
  description = "Confluent organization ID"
  type        = string
}

variable "confluent_environment_id" {
  description = "Confluent environment ID"
  type        = string
}

variable "confluent_compute_pool_id" {
  description = "Confluent compute pool ID"
  type        = string
}

variable "confluent_service_account_id" {
  description = "Confluent service account ID"
  type        = string
}

variable "confluent_flink_rest_endpoint" {
  description = "Confluent Flink REST endpoint"
  type        = string
}

variable "confluent_flink_api_key_id" {
  description = "Confluent Flink API key ID"
  type        = string
}

variable "confluent_flink_api_key_secret" {
  description = "Confluent Flink API key secret"
  type        = string
}

variable "zapier_endpoint" {
  description = "Zapier endpoint (stripped)"
  type        = string
}

variable "zapier_sse_endpoint" {
  description = "Zapier SSE endpoint"
  type        = string
}

output "endpoint" {
  value       = azurerm_cognitive_account.openai_account.endpoint
}

output "name" {
  value       = azurerm_cognitive_deployment.openai_deployment.name
}

output "primary_access_key" {
  value       = azurerm_cognitive_account.openai_account.primary_access_key
}

output "flink_connection_name" {
  value       = confluent_flink_connection.azure_connection.display_name
}

