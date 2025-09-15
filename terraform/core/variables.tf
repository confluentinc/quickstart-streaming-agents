variable "prefix" {
  description = "Prefix for resource names"
  type        = string
  default     = "ai"
}

variable "cloud_provider" {
  description = "Cloud provider to use (AWS or AZURE)"
  type        = string
  default     = "AWS"
}

variable "cloud_region" {
  description = "Region for deployment"
  type        = string
  default     = "us-east-2"
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

variable "azure_subscription_id" {
  description = "Azure Subscription ID"
  type        = string
}
