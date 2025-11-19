output "flink_connection_name" {
  value = confluent_flink_connection.azure_connection.display_name
}

output "flink_embedding_connection_name" {
  value = confluent_flink_connection.azure_embedding_connection.display_name
}

output "azure_openai_api_key" {
  value     = azurerm_cognitive_account.openai_account.primary_access_key
  sensitive = true
}

output "azure_openai_endpoint" {
  value = azurerm_cognitive_account.openai_account.endpoint
}
