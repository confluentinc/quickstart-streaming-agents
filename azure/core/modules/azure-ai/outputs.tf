output "flink_connection_name" {
  value = confluent_flink_connection.azure_connection.display_name
}

output "flink_embedding_connection_name" {
  value = confluent_flink_connection.azure_embedding_connection.display_name
}
