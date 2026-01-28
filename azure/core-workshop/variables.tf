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

variable "owner_email" {
  description = "Email address of the resource owner for tagging purposes"
  type        = string
  default     = ""
}

variable "azure_openai_api_key" {
  description = "Azure OpenAI API Key (pre-provided by workshop organizer)"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.azure_openai_api_key) > 0
    error_message = "azure_openai_api_key is required in workshop mode"
  }
}

variable "azure_openai_endpoint_raw" {
  description = "Azure OpenAI Endpoint URL (pre-provided by workshop organizer)"
  type        = string

  validation {
    condition     = length(var.azure_openai_endpoint_raw) > 0
    error_message = "azure_openai_endpoint_raw is required in workshop mode"
  }
}
