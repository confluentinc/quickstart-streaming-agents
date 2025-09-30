variable "prefix" {
  description = "Resource name prefix"
  type        = string
  default     = "streaming-agents"
}

variable "ZAPIER_SSE_ENDPOINT" {
  description = "Zapier MCP SSE Endpoint for tool calling"
  type        = string
  sensitive   = true
}
