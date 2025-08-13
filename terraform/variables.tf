variable "prefix" {
  description = "Prefix for resource names"
  type        = string
  default     = "ai"
}

# Variables for cloud provider selection
variable "cloud_provider" {
  description = "Cloud provider to use (AWS or AZURE)"
  type        = string
  default     = "AWS"
  validation {
    condition     = contains(["AWS", "AZURE"], upper(var.cloud_provider))
    error_message = "Cloud provider must be either 'AWS' or 'AZURE' (case insensitive)."
  }
}

# Normalize cloud provider to uppercase for consistent usage
locals {
  cloud_provider = upper(var.cloud_provider)
}

variable "cloud_region" {
  description = "Region for deployment"
  type        = string
  default     = "us-east-2"
} 

variable "confluent_cloud_api_key"{
    description = "Confluent Cloud API Key"
    type        = string
}

variable "confluent_cloud_api_secret"{
    description = "Confluent Cloud API Secret"
    type        = string     
}

variable "ZAPIER_SSE_ENDPOINT"{
    description = "Zapier SSE Endpoint from Zapier UI"
    type        = string
}
