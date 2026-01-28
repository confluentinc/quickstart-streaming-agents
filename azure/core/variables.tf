variable "cloud_region" {
  description = "Azure region for deployment (must support MongoDB Atlas M0 free tier)"
  type        = string
  default     = "eastus2"

  validation {
    condition = contains([
      "eastus2",
      "westus",
      "canadacentral",
      "northeurope",
      "westeurope",
      "eastasia",
      "centralindia"
    ], var.cloud_region)
    error_message = "The selected region does not support MongoDB Atlas M0 free tier. Use: eastus2, westus, canadacentral, northeurope, westeurope, eastasia, centralindia."
  }
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
  description = "Azure Subscription ID (placeholder value used in workshop mode since no Azure resources are created)"
  type        = string
  default     = "00000000-0000-0000-0000-000000000000"
}

variable "owner_email" {
  description = "Email address of the resource owner for tagging purposes"
  type        = string
  default     = ""
}

variable "workshop_mode" {
  description = "Enable workshop mode (uses pre-provided Azure OpenAI credentials instead of creating Azure AI resources)"
  type        = bool
  default     = false
}

variable "azure_openai_api_key" {
  description = "Azure OpenAI API Key (workshop mode only)"
  type        = string
  sensitive   = true
  default     = ""

  validation {
    condition     = var.workshop_mode ? length(var.azure_openai_api_key) > 0 : true
    error_message = "azure_openai_api_key is required when workshop_mode is enabled"
  }
}

variable "azure_openai_endpoint" {
  description = "Azure OpenAI Endpoint URL (workshop mode only)"
  type        = string
  default     = ""

  validation {
    condition     = var.workshop_mode ? length(var.azure_openai_endpoint) > 0 : true
    error_message = "azure_openai_endpoint is required when workshop_mode is enabled"
  }
}
