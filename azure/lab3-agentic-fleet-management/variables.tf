variable "cloud_region" {
  description = "Azure region for deployment"
  type        = string
}

variable "azure_subscription_id" {
  description = "Azure Subscription ID"
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
  default     = "mongodb+srv://cluster0.iir6woe.mongodb.net/"
}

variable "mongodb_username_lab3" {
  description = "MongoDB username for Lab3 vector search"
  type        = string
  sensitive   = true
  default     = "public_readonly_user"
}

variable "mongodb_password_lab3" {
  description = "MongoDB password for Lab3 vector search"
  type        = string
  sensitive   = true
  default     = "pE7xOkiKth2QqTKL"
}

variable "zapier_sse_endpoint" {
  description = "Zapier SSE endpoint for MCP connection"
  type        = string
  sensitive   = true
}
