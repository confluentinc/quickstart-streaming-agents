variable "cloud_region" {
  description = "Region for deployment (must support MongoDB Atlas M0 free tier)"
  type        = string
  default     = "us-east-1"

  validation {
    condition = contains([
      "us-east-1",
      "us-west-2",
      "sa-east-1",
      "ap-southeast-1",
      "ap-southeast-2",
      "ap-south-1",
      "ap-east-1",
      "ap-northeast-1",
      "ap-northeast-2"
    ], var.cloud_region)
    error_message = "The selected AWS region does not support MongoDB Atlas M0 free tier. Use: us-east-1, us-west-2, sa-east-1, ap-southeast-1, ap-southeast-2, ap-south-1, ap-east-1, ap-northeast-1, ap-northeast-2."
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

variable "aws_bedrock_access_key" {
  description = "AWS Access Key ID for Bedrock (pre-created for hackathon)"
  type        = string
  sensitive   = true
}

variable "aws_bedrock_secret_key" {
  description = "AWS Secret Access Key for Bedrock (pre-created for hackathon)"
  type        = string
  sensitive   = true
}
