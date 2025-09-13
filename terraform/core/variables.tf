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
