variable "mcp_token" {
  description = "Bearer token for the remote MCP server"
  type        = string
  sensitive   = true
}

variable "mcp_endpoint" {
  description = "Endpoint URL for the remote MCP server"
  type        = string
  default     = "https://z04yuqut2a.execute-api.us-east-1.amazonaws.com/mcp"
}
