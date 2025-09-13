output "confluent_environment_id" {
  value = confluent_environment.staging.id
}

output "confluent_kafka_cluster_id" {
  value = confluent_kafka_cluster.standard.id
}

output "confluent_kafka_bootstrap_endpoint" {
  value = confluent_kafka_cluster.standard.bootstrap_endpoint
}

output "confluent_schema_registry_id" {
  value = data.confluent_schema_registry_cluster.sr-cluster.id
}

output "confluent_schema_registry_endpoint" {
  value = data.confluent_schema_registry_cluster.sr-cluster.rest_endpoint
}

output "confluent_flink_compute_pool_id" {
  value = confluent_flink_compute_pool.flinkpool-main.id
}

output "app_manager_service_account_id" {
  value = confluent_service_account.app-manager.id
}

output "app_manager_kafka_api_key" {
  value = confluent_api_key.app-manager-kafka-api-key.id
  sensitive = true
}

output "app_manager_kafka_api_secret" {
  value = confluent_api_key.app-manager-kafka-api-key.secret
  sensitive = true
}

output "app_manager_schema_registry_api_key" {
  value = confluent_api_key.app-manager-schema-registry-api-key.id
  sensitive = true
}

output "app_manager_schema_registry_api_secret" {
  value = confluent_api_key.app-manager-schema-registry-api-key.secret
  sensitive = true
}

output "app_manager_flink_api_key" {
  value = confluent_api_key.app-manager-flink-api-key.id
  sensitive = true
}

output "app_manager_flink_api_secret" {
  value = confluent_api_key.app-manager-flink-api-key.secret
  sensitive = true
}
