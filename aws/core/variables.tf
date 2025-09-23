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
  description = "Region for deployment (must support MongoDB Atlas M0 free tier)"
  type        = string
  default     = "us-east-1"

  validation {
    condition = upper(var.cloud_provider) == "AWS" ? contains([
      "us-east-1",
      "us-west-2",
      "sa-east-1",
      "ap-southeast-1",
      "ap-southeast-2",
      "ap-south-1",
      "ap-east-1",
      "ap-northeast-1",
      "ap-northeast-2"
      ], var.cloud_region) : contains([
      "eastus2",
      "westus",
      "canadacentral",
      "northeurope",
      "westeurope",
      "eastasia",
      "centralindia"
    ], var.cloud_region)
    error_message = "The selected region does not support MongoDB Atlas M0 free tier. For AWS, use: us-east-1, us-west-2, sa-east-1, ap-southeast-1, ap-southeast-2, ap-south-1, ap-east-1, ap-northeast-1, ap-northeast-2. For Azure, use: eastus2, westus, canadacentral, northeurope, westeurope, eastasia, centralindia."
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
