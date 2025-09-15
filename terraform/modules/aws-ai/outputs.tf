output "flink_connection_name" {
  value = confluent_flink_connection.bedrock_connection.display_name
}

output "flink_embedding_connection_name" {
  value = confluent_flink_connection.bedrock_embedding_connection.display_name
}
