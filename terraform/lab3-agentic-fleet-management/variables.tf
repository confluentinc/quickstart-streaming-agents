variable "mongodb_connection_string_lab3" {
  description = "MongoDB connection string for Lab3 vector search (leave empty to use cloud-specific default)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "mongodb_username_lab3" {
  description = "MongoDB username for Lab3 vector search (leave empty to use cloud-specific default)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "mongodb_password_lab3" {
  description = "MongoDB password for Lab3 vector search (leave empty to use cloud-specific default)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "zapier_token" {
  description = "Zapier MCP authentication token for tool calling"
  type        = string
  sensitive   = true
}
