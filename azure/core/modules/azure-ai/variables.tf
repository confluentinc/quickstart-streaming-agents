variable "cloud_region" {}
variable "random_id" {}
variable "confluent_organization_id" {}
variable "confluent_environment_id" {}
variable "confluent_compute_pool_id" {}
variable "confluent_service_account_id" {}
variable "confluent_flink_rest_endpoint" {}
variable "confluent_flink_api_key_id" {}
variable "confluent_flink_api_key_secret" {}

variable "owner_email" {
  description = "Email address of the resource owner for tagging purposes"
  type        = string
  default     = ""
}

variable "project_root_path" {
  description = "Absolute path to the project root directory"
  type        = string
}
