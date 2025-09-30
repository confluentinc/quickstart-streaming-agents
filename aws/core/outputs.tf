output "confluent_environment_id" {
  value = confluent_environment.staging.id
}

output "confluent_kafka_cluster_id" {
  value = confluent_kafka_cluster.standard.id
}

output "confluent_kafka_cluster_bootstrap_endpoint" {
  value = confluent_kafka_cluster.standard.bootstrap_endpoint
}

output "confluent_kafka_cluster_rest_endpoint" {
  value = confluent_kafka_cluster.standard.rest_endpoint
}

output "confluent_schema_registry_id" {
  value = data.confluent_schema_registry_cluster.sr-cluster.id
}

output "confluent_schema_registry_rest_endpoint" {
  value = data.confluent_schema_registry_cluster.sr-cluster.rest_endpoint
}

output "confluent_flink_compute_pool_id" {
  value = confluent_flink_compute_pool.flinkpool-main.id
}

output "app_manager_service_account_id" {
  value = confluent_service_account.app-manager.id
}

output "app_manager_kafka_api_key" {
  value     = confluent_api_key.app-manager-kafka-api-key.id
  sensitive = true
}

output "app_manager_kafka_api_secret" {
  value     = confluent_api_key.app-manager-kafka-api-key.secret
  sensitive = true
}

output "app_manager_schema_registry_api_key" {
  value     = confluent_api_key.app-manager-schema-registry-api-key.id
  sensitive = true
}

output "app_manager_schema_registry_api_secret" {
  value     = confluent_api_key.app-manager-schema-registry-api-key.secret
  sensitive = true
}

output "app_manager_flink_api_key" {
  value     = confluent_api_key.app-manager-flink-api-key.id
  sensitive = true
}

output "app_manager_flink_api_secret" {
  value     = confluent_api_key.app-manager-flink-api-key.secret
  sensitive = true
}

output "confluent_organization_id" {
  value = data.confluent_organization.main.id
}

output "confluent_flink_rest_endpoint" {
  value = data.confluent_flink_region.demo_flink_region.rest_endpoint
}

output "confluent_cloud_api_key" {
  value     = var.confluent_cloud_api_key
  sensitive = true
}

output "confluent_cloud_api_secret" {
  value     = var.confluent_cloud_api_secret
  sensitive = true
}


output "llm_connection_name" {
  value       = module.aws_ai_services.flink_connection_name
  description = "The name of the LLM connection (llm-textgen-connection)"
}

output "llm_embedding_connection_name" {
  value       = module.aws_ai_services.flink_embedding_connection_name
  description = "The name of the LLM embedding connection (llm-embedding-connection)"
}

output "confluent_environment_display_name" {
  value       = confluent_environment.staging.display_name
  description = "The display name of the Confluent environment"
}

output "confluent_kafka_cluster_display_name" {
  value       = confluent_kafka_cluster.standard.display_name
  description = "The display name of the Confluent Kafka cluster"
}

output "cloud_region" {
  value       = var.cloud_region
  description = "The cloud region used for deployment"
}

output "aws_access_key_id" {
  value       = module.aws_ai_services.aws_access_key_id
  description = "AWS access key ID for Bedrock user"
}

output "aws_secret_access_key" {
  value       = module.aws_ai_services.aws_secret_access_key
  sensitive   = true
  description = "AWS secret access key for Bedrock user"
}
