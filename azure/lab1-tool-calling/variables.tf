variable "zapier_token" {
  description = "Zapier MCP authentication token for tool calling"
  type        = string
  sensitive   = true
}

variable "workshop_mode" {
  description = "Enable workshop mode (uses workshop-core instead of core)"
  type        = bool
  default     = false
}
