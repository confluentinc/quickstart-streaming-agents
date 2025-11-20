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
  description = "Azure Subscription ID (not required in workshop mode)"
  type        = string
  default     = ""
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
}

variable "azure_openai_endpoint" {
  description = "Azure OpenAI Endpoint URL (workshop mode only)"
  type        = string
  default     = ""
}
