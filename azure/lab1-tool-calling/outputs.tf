# Core infrastructure outputs (passed through from remote state)
output "confluent_environment_id" {
  value = data.terraform_remote_state.core.outputs.confluent_environment_id
}

output "confluent_kafka_cluster_id" {
  value = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_id
}

output "confluent_kafka_cluster_bootstrap_endpoint" {
  value = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_bootstrap_endpoint
}

output "confluent_kafka_cluster_rest_endpoint" {
  value = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_rest_endpoint
}

output "confluent_flink_compute_pool_id" {
  value = data.terraform_remote_state.core.outputs.confluent_flink_compute_pool_id
}

output "confluent_flink_rest_endpoint" {
  value = data.terraform_remote_state.core.outputs.confluent_flink_rest_endpoint
}

output "app_manager_service_account_id" {
  value = data.terraform_remote_state.core.outputs.app_manager_service_account_id
}

output "app_manager_kafka_api_key" {
  value     = data.terraform_remote_state.core.outputs.app_manager_kafka_api_key
  sensitive = true
}

output "app_manager_kafka_api_secret" {
  value     = data.terraform_remote_state.core.outputs.app_manager_kafka_api_secret
  sensitive = true
}

output "app_manager_schema_registry_api_key" {
  value     = data.terraform_remote_state.core.outputs.app_manager_schema_registry_api_key
  sensitive = true
}

output "app_manager_schema_registry_api_secret" {
  value     = data.terraform_remote_state.core.outputs.app_manager_schema_registry_api_secret
  sensitive = true
}

output "app_manager_flink_api_key" {
  value     = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
  sensitive = true
}

output "app_manager_flink_api_secret" {
  value     = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  sensitive = true
}

output "confluent_schema_registry_id" {
  value = data.terraform_remote_state.core.outputs.confluent_schema_registry_id
}

output "confluent_schema_registry_rest_endpoint" {
  value = data.terraform_remote_state.core.outputs.confluent_schema_registry_rest_endpoint
}

output "confluent_organization_id" {
  value = data.terraform_remote_state.core.outputs.confluent_organization_id
}

# Lab-specific outputs
output "lab1_commands_file" {
  value = local_file.mcp_commands.filename
}

output "lab_suffix" {
  value = random_id.lab_suffix.hex
}

output "zapier_mcp_connection_name" {
  value       = "zapier-mcp-connection"
  description = "Name for the Zapier MCP connection (must be created manually via CLI)"
}

output "mcp_commands_file" {
  value = local_file.mcp_commands.filename
}
