variable "cloud_region" {
  description = "AWS region for deployment"
  type        = string
}

variable "zapier_sse_endpoint" {
  description = "Zapier MCP SSE Endpoint for tool calling"
  type        = string
  sensitive   = true
}
