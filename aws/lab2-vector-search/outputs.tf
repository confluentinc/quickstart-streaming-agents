output "lab_suffix" {
  value       = random_id.lab_suffix.hex
  description = "Random suffix for this lab instance"
}

output "confluent_environment_id" {
  value       = data.terraform_remote_state.core.outputs.confluent_environment_id
  description = "Confluent Environment ID from core infrastructure"
}

output "confluent_kafka_cluster_id" {
  value       = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_id
  description = "Confluent Kafka Cluster ID from core infrastructure"
}

output "confluent_flink_compute_pool_id" {
  value       = data.terraform_remote_state.core.outputs.confluent_flink_compute_pool_id
  description = "Confluent Flink Compute Pool ID from core infrastructure"
}

output "documents_table_id" {
  value       = confluent_flink_statement.documents_table.id
  description = "Flink statement ID for documents table"
}

output "documents_embed_table_id" {
  value       = confluent_flink_statement.documents_embed_table.id
  description = "Flink statement ID for documents_embed table"
}

output "queries_table_id" {
  value       = confluent_flink_statement.queries_table.id
  description = "Flink statement ID for queries table"
}

output "queries_embed_table_id" {
  value       = confluent_flink_statement.queries_embed_table.id
  description = "Flink statement ID for queries_embed table"
}


# MongoDB connector outputs
output "mongodb_sink_connector_id" {
  description = "MongoDB Sink Connector ID"
  value       = confluent_connector.mongodb_sink.id
}

output "mongodb_sink_connector_status" {
  description = "MongoDB Sink Connector Status"
  value       = confluent_connector.mongodb_sink.status
}

output "mongodb_connection_details" {
  description = "MongoDB connection configuration details"
  value = {
    database   = var.MONGODB_DATABASE
    collection = var.MONGODB_COLLECTION
    index_name = var.MONGODB_INDEX_NAME
    host       = local.mongodb_host
    username   = var.mongodb_username
  }
  sensitive = true
}
