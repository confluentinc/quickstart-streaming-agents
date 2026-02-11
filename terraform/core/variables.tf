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

variable "owner_email" {
  description = "Email address of the resource owner for tagging purposes"
  type        = string
  default     = ""
}

# AWS Bedrock credentials (used when cloud_provider == "aws")
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
