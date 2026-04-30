variable "mcp_token" {
  description = "MCP server authentication token for tool calling"
  type        = string
  sensitive   = true
}

variable "mcp_endpoint" {
  description = "MCP server endpoint URL (e.g. https://<IP>.sslip.io/mcp/sse)"
  type        = string
}
