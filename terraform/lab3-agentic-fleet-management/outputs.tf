# Lab3 Outputs
output "lab_name" {
  value = "lab3-agentic-fleet-management-${local.cloud_provider}"
}

# Core infrastructure outputs (pass-through from remote state)
output "confluent_environment_id" {
  value = data.terraform_remote_state.core.outputs.confluent_environment_id
}

output "confluent_kafka_cluster_id" {
  value = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_id
}

output "confluent_kafka_bootstrap_endpoint" {
  value = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_bootstrap_endpoint
}

output "confluent_schema_registry_id" {
  value = data.terraform_remote_state.core.outputs.confluent_schema_registry_id
}

output "confluent_schema_registry_endpoint" {
  value = data.terraform_remote_state.core.outputs.confluent_schema_registry_rest_endpoint
}

output "confluent_flink_compute_pool_id" {
  value = data.terraform_remote_state.core.outputs.confluent_flink_compute_pool_id
}

# Lab-specific outputs
output "ride_requests_table_id" {
  value       = confluent_flink_statement.ride_requests_table.id
  description = "Flink statement ID for ride_requests table"
}

output "documents_vectordb_table_id" {
  value       = confluent_flink_statement.documents_vectordb_lab3.id
  description = "Flink statement ID for documents_vectordb table"
}

output "mongodb_connection_name" {
  value       = "mongodb-connection-lab3"
  description = "MongoDB connection name for Lab3 vector search"
}
