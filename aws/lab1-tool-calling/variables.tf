variable "cloud_region" {
  description = "AWS region for deployment"
  type        = string
}

variable "ZAPIER_SSE_ENDPOINT" {
  description = "Zapier MCP SSE Endpoint for tool calling"
  type        = string
  sensitive   = true
}
