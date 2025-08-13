output "resource-ids" {
  value = <<-EOT
  Environment ID:   ${confluent_environment.staging.id}
  Kafka Cluster ID: ${confluent_kafka_cluster.standard.id}
  Flink Compute pool ID: ${confluent_flink_compute_pool.flinkpool-main.id}

  Service Accounts and their Kafka API Keys (API Keys inherit the permissions granted to the owner):
  ${confluent_service_account.app-manager.display_name}:                     ${confluent_service_account.app-manager.id}
  ${confluent_service_account.app-manager.display_name}'s Kafka API Key:     "${confluent_api_key.app-manager-kafka-api-key.id}"
  ${confluent_service_account.app-manager.display_name}'s Kafka API Secret:  "${confluent_api_key.app-manager-kafka-api-key.secret}"


  Service Accounts and their Flink management API Keys (API Keys inherit the permissions granted to the owner):
  ${confluent_service_account.app-manager.display_name}:                     ${confluent_service_account.app-manager.id}
  ${confluent_service_account.app-manager.display_name}'s Flink management API Key:     "${confluent_api_key.app-manager-flink-api-key.id}"
  ${confluent_service_account.app-manager.display_name}'s Flink management API Secret:  "${confluent_api_key.app-manager-flink-api-key.secret}"


  sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="${confluent_api_key.app-manager-kafka-api-key.id}" password="${confluent_api_key.app-manager-kafka-api-key.secret}";
  bootstrap.servers=${confluent_kafka_cluster.standard.bootstrap_endpoint}
  schema.registry.url= ${data.confluent_schema_registry_cluster.sr-cluster.rest_endpoint}
  schema.registry.basic.auth.user.info= "${confluent_api_key.app-manager-schema-registry-api-key.id}:${confluent_api_key.app-manager-schema-registry-api-key.secret}"


  EOT

  sensitive = true
}

# Create Shaddow Traffic Connection Files terraform varaible file based on variables used in this script
resource "local_file" "orders-json" {
filename = "${path.module}/data-gen/connections/orders.json"
  content  = <<-EOT
{
    "kind": "kafka",
    "continueOnRuleException": true,
    "producerConfigs": {
        "bootstrap.servers" : "${confluent_kafka_cluster.standard.bootstrap_endpoint}",
        "client.id": "mortgage-application-producer",
        "basic.auth.user.info": "${confluent_api_key.app-manager-schema-registry-api-key.id}:${confluent_api_key.app-manager-schema-registry-api-key.secret}",
        "schema.registry.url": "${data.confluent_schema_registry_cluster.sr-cluster.rest_endpoint}",
        "basic.auth.credentials.source": "USER_INFO",
        "key.serializer": "io.shadowtraffic.kafka.serdes.JsonSerializer",
        "value.serializer": "io.confluent.kafka.serializers.KafkaAvroSerializer",
        "sasl.jaas.config": "org.apache.kafka.common.security.plain.PlainLoginModule required username='${confluent_api_key.app-manager-kafka-api-key.id}' password='${confluent_api_key.app-manager-kafka-api-key.secret}';",
        "sasl.mechanism": "PLAIN",
        "security.protocol": "SASL_SSL"
    }
}
  EOT 
  }

resource "local_file" "customers-json" {
filename = "${path.module}/data-gen/connections/customers.json"
  content  = <<-EOT
{
    "kind": "kafka",
    "continueOnRuleException": true,
    "producerConfigs": {
        "bootstrap.servers" : "${confluent_kafka_cluster.standard.bootstrap_endpoint}",
        "client.id": "customers-producer",
        "basic.auth.user.info": "${confluent_api_key.app-manager-schema-registry-api-key.id}:${confluent_api_key.app-manager-schema-registry-api-key.secret}",
        "schema.registry.url": "${data.confluent_schema_registry_cluster.sr-cluster.rest_endpoint}",
        "basic.auth.credentials.source": "USER_INFO",
        "key.serializer": "io.shadowtraffic.kafka.serdes.JsonSerializer",
        "value.serializer": "io.confluent.kafka.serializers.KafkaAvroSerializer",
        "sasl.jaas.config": "org.apache.kafka.common.security.plain.PlainLoginModule required username='${confluent_api_key.app-manager-kafka-api-key.id}' password='${confluent_api_key.app-manager-kafka-api-key.secret}';",
        "sasl.mechanism": "PLAIN",
        "security.protocol": "SASL_SSL"
    }
}
  EOT 
  }

resource "local_file" "products-json" {
filename = "${path.module}/data-gen/connections/products.json"
  content  = <<-EOT
{
    "kind": "kafka",
    "continueOnRuleException": true,
    "producerConfigs": {
        "bootstrap.servers" : "${confluent_kafka_cluster.standard.bootstrap_endpoint}",
        "client.id": "products-producer",
        "basic.auth.user.info": "${confluent_api_key.app-manager-schema-registry-api-key.id}:${confluent_api_key.app-manager-schema-registry-api-key.secret}",
        "schema.registry.url": "${data.confluent_schema_registry_cluster.sr-cluster.rest_endpoint}",
        "basic.auth.credentials.source": "USER_INFO",
        "key.serializer": "io.shadowtraffic.kafka.serdes.JsonSerializer",
        "value.serializer": "io.confluent.kafka.serializers.KafkaAvroSerializer",
        "sasl.jaas.config": "org.apache.kafka.common.security.plain.PlainLoginModule required username='${confluent_api_key.app-manager-kafka-api-key.id}' password='${confluent_api_key.app-manager-kafka-api-key.secret}';",
        "sasl.mechanism": "PLAIN",
        "security.protocol": "SASL_SSL"
    }
}
  EOT 
  }

locals {
  ZAPIER_ENDPOINT = substr(var.ZAPIER_SSE_ENDPOINT, 0, length(var.ZAPIER_SSE_ENDPOINT) - 4)
}

output "stripped_endpoint" {
  value = local.ZAPIER_ENDPOINT
}

output "flink_mcp_connection_command" {
  description = "Flink create MCP connection command"
  value       = "confluent flink connection create zapier-mcp-connection --cloud ${local.cloud_provider} --region ${var.cloud_region} --type mcp_server --endpoint ${local.ZAPIER_ENDPOINT} --api-key api_key --environment ${confluent_environment.staging.id} --sse-endpoint ${var.ZAPIER_SSE_ENDPOINT}"
}
