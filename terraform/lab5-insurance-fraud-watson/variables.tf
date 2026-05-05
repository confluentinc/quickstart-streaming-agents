variable "enable_testing_sql" {
  description = "Whether to execute testing-only SQL statements (anomaly detection, fraud analysis)"
  type        = bool
  default     = false
}

variable "zapier_token" {
  description = "Zapier MCP authentication token for tool calling"
  type        = string
  sensitive   = true
}

variable "ibmmq_password" {
  description = "IBM MQ broker password (IBM Cloud US South, CLAIMSQM)"
  type        = string
  sensitive   = true
}

variable "activemq_password" {
  description = "ActiveMQ workshop broker password"
  type        = string
  sensitive   = true
  default     = ""
}

variable "schema_registry_auth" {
  description = "Schema Registry basic auth in 'KEY:SECRET' format"
  type        = string
  sensitive   = true
  default     = ""
}
