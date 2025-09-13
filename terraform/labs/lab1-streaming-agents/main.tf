module "core" {
  source = "../../core"

  prefix         = var.prefix
  cloud_provider = var.cloud_provider
  cloud_region   = var.cloud_region
}

data "confluent_organization" "org" {}

resource "random_id" "lab" {
  byte_length = 4
}

module "aws_ai" {
  count = var.cloud_provider == "AWS" ? 1 : 0

  source = "../../modules/aws-ai"

  cloud_region                = var.cloud_region
  random_id                   = random_id.lab.hex
  prefix                      = var.prefix
  model_prefix                = "us"
  confluent_organization_id   = data.confluent_organization.org.id
  confluent_environment_id    = module.core.confluent_environment_id
  confluent_compute_pool_id   = module.core.confluent_flink_compute_pool_id
  confluent_service_account_id = module.core.app_manager_service_account_id
  confluent_flink_rest_endpoint = module.core.confluent_flink_rest_endpoint
  confluent_flink_api_key_id     = module.core.app_manager_flink_api_key
  confluent_flink_api_key_secret = module.core.app_manager_flink_api_secret
}

module "azure_ai" {
  count = var.cloud_provider == "AZURE" ? 1 : 0

  source = "../../modules/azure-ai"

  cloud_region                = var.cloud_region
  random_id                   = random_id.lab.hex
  prefix                      = var.prefix
  confluent_organization_id   = data.confluent_organization.org.id
  confluent_environment_id    = module.core.confluent_environment_id
  confluent_compute_pool_id   = module.core.confluent_flink_compute_pool_id
  confluent_service_account_id = module.core.app_manager_service_account_id
  confluent_flink_rest_endpoint = module.core.confluent_flink_rest_endpoint
  confluent_flink_api_key_id     = module.core.app_manager_flink_api_key
  confluent_flink_api_key_secret = module.core.app_manager_flink_api_secret
}

resource "local_file" "orders-json" {
  filename = "${path.module}/data-gen/connections/orders.json"
  content  = <<EOT
{
    "kind": "kafka",
    "continueOnRuleException": true,
    "producerConfigs": {
        "bootstrap.servers" : "${module.core.confluent_kafka_bootstrap_endpoint}",
        "client.id": "mortgage-application-producer",
        "basic.auth.user.info": "${module.core.app_manager_schema_registry_api_key}:${module.core.app_manager_schema_registry_api_secret}",
        "schema.registry.url": "${module.core.confluent_schema_registry_endpoint}",
        "basic.auth.credentials.source": "USER_INFO",
        "key.serializer": "io.shadowtraffic.kafka.serdes.JsonSerializer",
        "value.serializer": "io.confluent.kafka.serializers.KafkaAvroSerializer",
        "sasl.jaas.config": "org.apache.kafka.common.security.plain.PlainLoginModule required username='${module.core.app_manager_kafka_api_key}' password='${module.core.app_manager_kafka_api_secret}';",
        "sasl.mechanism": "PLAIN",
        "security.protocol": "SASL_SSL"
    }
}
EOT
}

resource "local_file" "customers-json" {
  filename = "${path.module}/data-gen/connections/customers.json"
  content  = <<EOT
{
    "kind": "kafka",
    "continueOnRuleException": true,
    "producerConfigs": {
        "bootstrap.servers" : "${module.core.confluent_kafka_bootstrap_endpoint}",
        "client.id": "customers-producer",
        "basic.auth.user.info": "${module.core.app_manager_schema_registry_api_key}:${module.core.app_manager_schema_registry_api_secret}",
        "schema.registry.url": "${module.core.confluent_schema_registry_endpoint}",
        "basic.auth.credentials.source": "USER_INFO",
        "key.serializer": "io.shadowtraffic.kafka.serdes.JsonSerializer",
        "value.serializer": "io.confluent.kafka.serializers.KafkaAvroSerializer",
        "sasl.jaas.config": "org.apache.kafka.common.security.plain.PlainLoginModule required username='${module.core.app_manager_kafka_api_key}' password='${module.core.app_manager_kafka_api_secret}';",
        "sasl.mechanism": "PLAIN",
        "security.protocol": "SASL_SSL"
    }
}
EOT
}

resource "local_file" "products-json" {
  filename = "${path.module}/data-gen/connections/products.json"
  content  = <<EOT
{
    "kind": "kafka",
    "continueOnRuleException": true,
    "producerConfigs": {
        "bootstrap.servers" : "${module.core.confluent_kafka_bootstrap_endpoint}",
        "client.id": "products-producer",
        "basic.auth.user.info": "${module.core.app_manager_schema_registry_api_key}:${module.core.app_manager_schema_registry_api_secret}",
        "schema.registry.url": "${module.core.confluent_schema_registry_endpoint}",
        "basic.auth.credentials.source": "USER_INFO",
        "key.serializer": "io.shadowtraffic.kafka.serdes.JsonSerializer",
        "value.serializer": "io.confluent.kafka.serializers.KafkaAvroSerializer",
        "sasl.jaas.config": "org.apache.kafka.common.security.plain.PlainLoginModule required username='${module.core.app_manager_kafka_api_key}' password='${module.core.app_manager_kafka_api_secret}';",
        "sasl.mechanism": "PLAIN",
        "security.protocol": "SASL_SSL"
    }
}
EOT
}