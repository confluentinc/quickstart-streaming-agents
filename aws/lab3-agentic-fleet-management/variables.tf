variable "cloud_region" {
  description = "AWS region for deployment"
  type        = string
}

variable "workshop_mode" {
  description = "Enable workshop mode (uses pre-provided MongoDB credentials for Lab3 vector search)"
  type        = bool
  default     = false
}

variable "mongodb_connection_string_lab3" {
  description = "MongoDB connection string for Lab3 vector search"
  type        = string
  sensitive   = true
  default     = "mongodb+srv://cluster0.w9n3o45.mongodb.net/"
}

variable "mongodb_username_lab3" {
  description = "MongoDB username for Lab3 vector search"
  type        = string
  sensitive   = true
  default     = "workshop-user"
}

variable "mongodb_password_lab3" {
  description = "MongoDB password for Lab3 vector search"
  type        = string
  sensitive   = true
  default     = "xr6PvJl9xZz1uoKa"
}

variable "zapier_sse_endpoint" {
  description = "Zapier SSE endpoint for MCP connection"
  type        = string
  sensitive   = true
}
