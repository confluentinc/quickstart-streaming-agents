# modules/aws/main.tf
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

# AWS Bedrock Configuration (Bare minimum - no logging)
# AWS Bedrock is a fully managed service, no resources to create
# Users just need to use the Bedrock API with their AWS credentials
# Model: us.anthropic.claude-3-7-sonnet-20250219-v1:0 (Sonnet 3.7)

# AWS IAM User for Bedrock access
resource "aws_iam_user" "bedrock_user" {
  name = "bedrock-user-${var.random_id}"
}

# AWS IAM Access Key for Bedrock user
resource "aws_iam_access_key" "bedrock_user_key" {
  user = aws_iam_user.bedrock_user.name
}

# AWS IAM Policy for Bedrock permissions
resource "aws_iam_policy" "bedrock_policy" {
  name = "bedrock-policy-${var.random_id}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach policy to user
resource "aws_iam_user_policy_attachment" "bedrock_user_policy" {
  user       = aws_iam_user.bedrock_user.name
  policy_arn = aws_iam_policy.bedrock_policy.arn
}

# AWS Flink connection
resource "confluent_flink_connection" "bedrock_connection" {
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

  display_name   = "${var.prefix}-bedrock-connection"
  type           = "BEDROCK"
  endpoint       = "https://bedrock-runtime.${var.cloud_region}.amazonaws.com/model/${var.model_prefix}.anthropic.claude-3-7-sonnet-20250219-v1:0/invoke"
  aws_access_key = aws_iam_access_key.bedrock_user_key.id
  aws_secret_key = aws_iam_access_key.bedrock_user_key.secret

  lifecycle {
    prevent_destroy = false
  }
}

# Create the mcp_commands.txt file with AWS-specific commands
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
  'provider' = 'bedrock',
  'task' = 'text_generation',
  'bedrock.connection' = '${confluent_flink_connection.bedrock_connection.display_name}',
  'bedrock.params.max_tokens' = '20000',
  'mcp.connection' = 'zapier-mcp-connection'
);

# Agent 2: Flink SQL CREATE LLM-Only MODEL Command

CREATE MODEL llm_textgen_model
INPUT (prompt STRING)
OUTPUT (response STRING)
WITH(
  'provider' = 'bedrock',
  'task' = 'text_generation',
  'bedrock.connection' = '${confluent_flink_connection.bedrock_connection.display_name}',
  'bedrock.params.max_tokens' = '20000'
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

variable "model_prefix" {
  description = "Model prefix for AWS Bedrock"
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

# Outputs
output "id" {
  description = "AWS Access Key ID"
  value       = aws_iam_access_key.bedrock_user_key.id
  sensitive   = true
}

output "secret" {
  description = "AWS Secret Access Key"
  value       = aws_iam_access_key.bedrock_user_key.secret
  sensitive   = true
}

output "flink_connection_name" {
  value = confluent_flink_connection.bedrock_connection.display_name
}
