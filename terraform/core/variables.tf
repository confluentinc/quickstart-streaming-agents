variable "cloud_provider" {
  description = "Cloud provider for deployment (aws or azure)"
  type        = string

  validation {
    condition     = contains(["aws", "azure"], var.cloud_provider)
    error_message = "cloud_provider must be 'aws' or 'azure'."
  }
}

variable "cloud_region" {
  description = "Cloud region for deployment (must support MongoDB Atlas M0 free tier)"
  type        = string
  default     = "us-east-1"
}

variable "confluent_cloud_api_key" {
  description = "Confluent Cloud API Key"
  type        = string
  sensitive   = true
}

variable "confluent_cloud_api_secret" {
  description = "Confluent Cloud API Secret"
  type        = string
  sensitive   = true
}

# --- LLM provider (AWS only; Azure always uses its Azure OpenAI connections) ---

variable "llm_provider" {
  description = "Backs llm_textgen_model, llm_embedding_model and remote_mcp_model on AWS: 'confluent' (CSP Hosted Flink Model Inference — no keys, the default) or 'bedrock' (your AWS Bedrock keys)"
  type        = string
  default     = "confluent"
  validation {
    condition     = contains(["bedrock", "confluent"], var.llm_provider)
    error_message = "llm_provider must be 'bedrock' or 'confluent'."
  }
}

variable "csp_textgen_model" {
  description = "Text-generation model id for llm_provider = 'confluent'. Case-sensitive: SHOW MODELS lists it as system.<id>."
  type        = string
  default     = "anthropic.claude-sonnet-4-6"
}

variable "csp_embedding_model" {
  description = "Embedding model id for llm_provider = 'confluent'. Case-sensitive: SHOW MODELS lists it as system.<id>."
  type        = string
  default     = "amazon.titan-embed-text-v2"
}

# AWS Bedrock credentials (used when cloud_provider == "aws" and llm_provider == "bedrock")
variable "aws_bedrock_access_key" {
  description = "AWS Access Key ID for Bedrock"
  type        = string
  sensitive   = true
  default     = ""
}

variable "aws_bedrock_secret_key" {
  description = "AWS Secret Access Key for Bedrock"
  type        = string
  sensitive   = true
  default     = ""
}

variable "aws_session_token" {
  description = "AWS Session Token for temporary credentials (required when access key starts with ASIA)"
  type        = string
  sensitive   = true
  default     = ""
}

# Azure OpenAI credentials (used when cloud_provider == "azure")
variable "azure_openai_api_key" {
  description = "Azure OpenAI API Key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "azure_openai_endpoint_raw" {
  description = "Azure OpenAI Endpoint URL"
  type        = string
  default     = ""
}
