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
}

variable "confluent_cloud_api_secret" {
  description = "Confluent Cloud API Secret"
  type        = string
}

variable "ZAPIER_SSE_ENDPOINT" {
  description = "Zapier SSE Endpoint from Zapier UI"
  type        = string
}
