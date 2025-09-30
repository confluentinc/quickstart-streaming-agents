output "flink_connection_name" {
  value = confluent_flink_connection.bedrock_connection.display_name
}

output "flink_embedding_connection_name" {
  value = confluent_flink_connection.bedrock_embedding_connection.display_name
}

output "aws_access_key_id" {
  value = aws_iam_access_key.bedrock_user_key.id
}

output "aws_secret_access_key" {
  value     = aws_iam_access_key.bedrock_user_key.secret
  sensitive = true
}
