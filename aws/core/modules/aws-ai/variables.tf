variable "cloud_region" {}
variable "random_id" {}
variable "prefix" {}
variable "model_prefix" {}
variable "confluent_organization_id" {}
variable "confluent_environment_id" {}
variable "confluent_compute_pool_id" {}
variable "confluent_service_account_id" {}
variable "confluent_flink_rest_endpoint" {}
variable "confluent_flink_api_key_id" {}
variable "confluent_flink_api_key_secret" {}
variable "confluent_flink_api_key_resource" {
  description = "The confluent_api_key resource for Flink API key to establish proper dependencies"
  type        = any
}
