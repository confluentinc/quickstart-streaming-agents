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

output "cloud_provider" {
  value       = var.cloud_provider
  description = "The cloud provider used for deployment (aws or azure)"
}

output "llm_provider" {
  value       = local.effective_llm_provider
  description = "What backs the LLM models: confluent (CSP Hosted), bedrock, or azureopenai"

  precondition {
    condition = (var.llm_provider == "confluent"
      || (var.llm_provider == "bedrock" && var.cloud_provider == "aws")
    || (var.llm_provider == "azureopenai" && var.cloud_provider == "azure"))
    error_message = "llm_provider '${var.llm_provider}' doesn't match cloud_provider '${var.cloud_provider}': use 'confluent' or 'bedrock' on AWS, 'confluent' or 'azureopenai' on Azure."
  }
}

output "csp_textgen_model" {
  value       = local.csp_textgen_model
  description = "CSP Hosted text-generation model id (used when llm_provider == confluent)"
}

output "csp_embedding_model" {
  value       = local.csp_embedding_model
  description = "CSP Hosted embedding model id (used when llm_provider == confluent)"
}

output "llm_connection_name" {
  value       = concat(confluent_flink_connection.bedrock_connection[*].display_name, confluent_flink_connection.azureopenai_connection[*].display_name, [""])[0]
  description = "The name of the LLM connection (llm-textgen-connection); empty for CSP Hosted, which has no connection"
}

output "llm_embedding_connection_name" {
  value       = concat(confluent_flink_connection.bedrock_embedding_connection[*].display_name, confluent_flink_connection.azureopenai_embedding_connection[*].display_name, [""])[0]
  description = "The name of the LLM embedding connection (llm-embedding-connection); empty for CSP Hosted"
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

output "random_id" {
  value       = random_id.resource_suffix.hex
  description = "Random ID suffix used for resource naming"
}

output "confluent_rtce_service_account_id" {
  value       = confluent_service_account.rtce-reader.id
  description = "Service account ID for the RTCE MCP server — used by setup_rtce.py to auto-create a Global API key via CLI"
}

