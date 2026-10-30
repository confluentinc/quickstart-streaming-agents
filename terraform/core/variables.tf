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

# --- LLM provider ---

variable "llm_provider" {
  description = "Backs llm_textgen_model, llm_embedding_model and remote_mcp_model: 'confluent' (CSP Hosted Flink Model Inference — no keys, the default on both clouds), 'bedrock' (AWS only, your AWS Bedrock keys) or 'azureopenai' (Azure only, your Azure OpenAI endpoint and key)"
  type        = string
  default     = "confluent"
  validation {
    condition     = contains(["bedrock", "azureopenai", "confluent"], var.llm_provider)
    error_message = "llm_provider must be 'confluent', 'bedrock' (AWS) or 'azureopenai' (Azure)."
  }
}

variable "csp_textgen_model" {
  description = "Text-generation model id for llm_provider = 'confluent'. Empty picks the per-cloud default (AWS: anthropic.claude-sonnet-4-6, Azure: openai.gpt-5.4-mini). Case-sensitive: SHOW MODELS lists it as system.<id>."
  type        = string
  default     = ""
}

variable "csp_embedding_model" {
  description = "Embedding model id for llm_provider = 'confluent'. Empty picks the per-cloud default (AWS: amazon.titan-embed-text-v2, Azure: openai.text-embedding-3-small). Case-sensitive: SHOW MODELS lists it as system.<id>."
  type        = string
  default     = ""
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

# Azure OpenAI credentials (used when cloud_provider == "azure" and llm_provider == "azureopenai")
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
