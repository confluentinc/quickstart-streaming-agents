# modules/aws_openai/main.tf
# Provider configuration moved to root module

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    confluent = {
      source = "confluentinc/confluent"
    }
  }
}

# OpenAI Configuration for Confluent Flink
# OpenAI is a cloud-based AI service, no AWS resources needed
# Users just need to use the OpenAI API with their API key
# Model: gpt-5-mini

# OpenAI Flink connection
resource "confluent_flink_connection" "openai_connection" {
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

  display_name = "${var.prefix}-openai-connection"
  type         = "OPENAI"
  endpoint     = "https://api.openai.com/v1/chat/completions"
  api_key      = var.openai_api_key

  lifecycle {
    prevent_destroy = false
  }
}

# Create the mcp_commands.txt file with OpenAI-specific commands
resource "local_file" "mcp_commands" {
  filename = "${path.module}/../../mcp_commands.txt"
  content  = <<-EOT
# Confluent Flink MCP Connection Create Command

confluent flink connection create zapier-mcp-connection \
  --cloud AWS \
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
  'provider' = 'openai',
  'task' = 'text_generation',
  'openai.connection' = '${confluent_flink_connection.openai_connection.display_name}',
  'openai.model_version' = 'gpt-5-mini',
  'mcp.connection' = 'zapier-mcp-connection'
);

# Agent 2: Flink SQL CREATE LLM-Only MODEL Command

CREATE MODEL llm_textgen_model
INPUT (prompt STRING)
OUTPUT (response STRING)
WITH(
  'provider' = 'openai',
  'task' = 'text_generation',
  'openai.connection' = '${confluent_flink_connection.openai_connection.display_name}',
  'openai.model_version' = 'gpt-5-mini'
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

variable "openai_api_key" {
  description = "OpenAI API key for LLM access"
  type        = string
  sensitive   = true
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

# Outputs
output "openai_api_key" {
  description = "OpenAI API Key"
  value       = var.openai_api_key
  sensitive   = true
}

output "flink_connection_name" {
  value       = confluent_flink_connection.openai_connection.display_name
}
