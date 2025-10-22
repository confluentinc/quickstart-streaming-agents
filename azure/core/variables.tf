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
  description = "Azure Subscription ID"
  type        = string
}
