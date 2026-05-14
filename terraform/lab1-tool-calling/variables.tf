variable "mcp_backend" {
  description = "Remote MCP server backend: 'lambda' (Confluent-hosted AWS Lambda) or 'zapier'"
  type        = string
  default     = "lambda"

  validation {
    condition     = contains(["lambda", "zapier"], var.mcp_backend)
    error_message = "mcp_backend must be 'lambda' or 'zapier'."
  }
}

variable "mcp_token" {
  description = "Bearer token for the Lambda Remote MCP server"
  type        = string
  default     = ""
  sensitive   = true
}

variable "zapier_token" {
  description = "Bearer token for the Zapier Remote MCP server"
  type        = string
  default     = ""
  sensitive   = true
}
