variable "cloud_region" {
  description = "AWS region for deployment"
  type        = string
}

variable "zapier_token" {
  description = "Zapier MCP authentication token for tool calling"
  type        = string
  sensitive   = true
}
