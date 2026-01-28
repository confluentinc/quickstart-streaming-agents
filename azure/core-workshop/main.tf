resource "random_id" "resource_suffix" {
  byte_length = 4
}

locals {
  # Only include regions that support MongoDB Atlas M0 free tier
  region_mapping = {
    # Azure Regions - MongoDB M0 Free Tier Supported
    "eastus2"       = "eastus2"
    "westus"        = "westus"
    "canadacentral" = "canadacentral"
    "northeurope"   = "northeurope"
    "westeurope"    = "westeurope"
    "eastasia"      = "eastasia"
    "centralindia"  = "centralindia"
  }

  confluent_region  = lookup(local.region_mapping, var.cloud_region, var.cloud_region)
  cloud_provider    = "AZURE"
  prefix            = "streaming-agents"
  project_root_path = abspath("${path.root}/../..")

  # Normalize Azure OpenAI endpoint (remove trailing slash if present)
  azure_openai_endpoint = trimsuffix(var.azure_openai_endpoint_raw, "/")
}

resource "confluent_environment" "staging" {
  display_name = "${local.prefix}-env-${random_id.resource_suffix.hex}"

  stream_governance {
    package = "ADVANCED"
  }
}

data "confluent_schema_registry_cluster" "sr-cluster" {
  environment {
    id = confluent_environment.staging.id
  }

  depends_on = [
    confluent_kafka_cluster.standard
  ]
}

resource "confluent_kafka_cluster" "standard" {
  display_name = "${local.prefix}-cluster-${random_id.resource_suffix.hex}"
  availability = "SINGLE_ZONE"
  cloud        = local.cloud_provider
  region       = local.confluent_region
  standard {}
  environment {
    id = confluent_environment.staging.id
  }
}

resource "confluent_service_account" "app-manager" {
  display_name = "${local.prefix}-app-manager-${random_id.resource_suffix.hex}"
  description  = "Service account to manage 'inventory' Kafka cluster"
}

resource "confluent_role_binding" "app-manager-kafka-cluster-admin" {
  principal   = "User:${confluent_service_account.app-manager.id}"
  role_name   = "EnvironmentAdmin"
  crn_pattern = confluent_environment.staging.resource_name
}

resource "confluent_flink_compute_pool" "flinkpool-main" {
  display_name = "${local.prefix}_standard_compute_pool_${random_id.resource_suffix.hex}"
  cloud        = local.cloud_provider
  region       = local.confluent_region
  max_cfu      = 20
  environment {
    id = confluent_environment.staging.id
  }
}

resource "confluent_api_key" "app-manager-kafka-api-key" {
  display_name = "app-manager-kafka-api-key"
  description  = "Kafka API Key that is owned by 'app-manager' service account"
  owner {
    id          = confluent_service_account.app-manager.id
    api_version = confluent_service_account.app-manager.api_version
    kind        = confluent_service_account.app-manager.kind
  }

  managed_resource {
    id          = confluent_kafka_cluster.standard.id
    api_version = confluent_kafka_cluster.standard.api_version
    kind        = confluent_kafka_cluster.standard.kind

    environment {
      id = confluent_environment.staging.id
    }
  }

  depends_on = [
    confluent_role_binding.app-manager-kafka-cluster-admin
  ]
}

resource "confluent_api_key" "app-manager-schema-registry-api-key" {
  display_name = "env-manager-schema-registry-api-key"
  description  = "Schema Registry API Key that is owned by 'env-manager' service account"
  owner {
    id          = confluent_service_account.app-manager.id
    api_version = confluent_service_account.app-manager.api_version
    kind        = confluent_service_account.app-manager.kind
  }

  managed_resource {
    id          = data.confluent_schema_registry_cluster.sr-cluster.id
    api_version = data.confluent_schema_registry_cluster.sr-cluster.api_version
    kind        = data.confluent_schema_registry_cluster.sr-cluster.kind

    environment {
      id = confluent_environment.staging.id
    }
  }
  depends_on = [
    confluent_role_binding.app-manager-kafka-cluster-admin
  ]
}

data "confluent_flink_region" "demo_flink_region" {
  cloud  = local.cloud_provider
  region = local.confluent_region
}

resource "confluent_api_key" "app-manager-flink-api-key" {
  display_name = "env-manager-flink-api-key"
  description  = "Flink API Key that is owned by 'env-manager' service account"
  owner {
    id          = confluent_service_account.app-manager.id
    api_version = confluent_service_account.app-manager.api_version
    kind        = confluent_service_account.app-manager.kind
  }

  managed_resource {
    id          = data.confluent_flink_region.demo_flink_region.id
    api_version = data.confluent_flink_region.demo_flink_region.api_version
    kind        = data.confluent_flink_region.demo_flink_region.kind

    environment {
      id = confluent_environment.staging.id
    }
  }
}

data "confluent_organization" "main" {}

resource "confluent_kafka_acl" "app-manager-read-on-topic" {
  kafka_cluster {
    id = confluent_kafka_cluster.standard.id
  }
  resource_type = "TOPIC"
  resource_name = "*"
  pattern_type  = "LITERAL"
  principal     = "User:${confluent_service_account.app-manager.id}"
  host          = "*"
  operation     = "READ"
  permission    = "ALLOW"
  rest_endpoint = confluent_kafka_cluster.standard.rest_endpoint
  credentials {
    key    = confluent_api_key.app-manager-kafka-api-key.id
    secret = confluent_api_key.app-manager-kafka-api-key.secret
  }
}

resource "confluent_kafka_acl" "app-manager-describe-on-cluster" {
  kafka_cluster {
    id = confluent_kafka_cluster.standard.id
  }
  resource_type = "CLUSTER"
  resource_name = "kafka-cluster"
  pattern_type  = "LITERAL"
  principal     = "User:${confluent_service_account.app-manager.id}"
  host          = "*"
  operation     = "DESCRIBE"
  permission    = "ALLOW"
  rest_endpoint = confluent_kafka_cluster.standard.rest_endpoint
  credentials {
    key    = confluent_api_key.app-manager-kafka-api-key.id
    secret = confluent_api_key.app-manager-kafka-api-key.secret
  }
}

resource "confluent_kafka_acl" "app-manager-write-on-topic" {
  kafka_cluster {
    id = confluent_kafka_cluster.standard.id
  }
  resource_type = "TOPIC"
  resource_name = "*"
  pattern_type  = "LITERAL"
  principal     = "User:${confluent_service_account.app-manager.id}"
  host          = "*"
  operation     = "WRITE"
  permission    = "ALLOW"
  rest_endpoint = confluent_kafka_cluster.standard.rest_endpoint
  credentials {
    key    = confluent_api_key.app-manager-kafka-api-key.id
    secret = confluent_api_key.app-manager-kafka-api-key.secret
  }
}

resource "confluent_kafka_acl" "app-manager-create-topic" {
  kafka_cluster {
    id = confluent_kafka_cluster.standard.id
  }
  resource_type = "TOPIC"
  resource_name = "*"
  pattern_type  = "LITERAL"
  principal     = "User:${confluent_service_account.app-manager.id}"
  host          = "*"
  operation     = "CREATE"
  permission    = "ALLOW"
  rest_endpoint = confluent_kafka_cluster.standard.rest_endpoint
  credentials {
    key    = confluent_api_key.app-manager-kafka-api-key.id
    secret = confluent_api_key.app-manager-kafka-api-key.secret
  }
}

resource "confluent_kafka_acl" "app-manager-read-on-group" {
  kafka_cluster {
    id = confluent_kafka_cluster.standard.id
  }
  resource_type = "GROUP"
  resource_name = "*"
  pattern_type  = "LITERAL"
  principal     = "User:${confluent_service_account.app-manager.id}"
  host          = "*"
  operation     = "READ"
  permission    = "ALLOW"
  rest_endpoint = confluent_kafka_cluster.standard.rest_endpoint
  credentials {
    key    = confluent_api_key.app-manager-kafka-api-key.id
    secret = confluent_api_key.app-manager-kafka-api-key.secret
  }
}

# ------------------------------------------------------
# LLM INFRASTRUCTURE - WORKSHOP MODE
# ------------------------------------------------------
# Note: Workshop mode uses pre-provided Azure OpenAI credentials
# No Azure resources are created - only Confluent Flink connections

# Azure OpenAI Text Generation Connection
resource "confluent_flink_connection" "azureopenai_connection" {
  organization {
    id = data.confluent_organization.main.id
  }
  environment {
    id = confluent_environment.staging.id
  }
  compute_pool {
    id = confluent_flink_compute_pool.flinkpool-main.id
  }
  principal {
    id = confluent_service_account.app-manager.id
  }
  rest_endpoint = data.confluent_flink_region.demo_flink_region.rest_endpoint
  credentials {
    key    = confluent_api_key.app-manager-flink-api-key.id
    secret = confluent_api_key.app-manager-flink-api-key.secret
  }

  display_name = "llm-textgen-connection"
  type         = "AZUREOPENAI"
  endpoint     = "${local.azure_openai_endpoint}/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"
  api_key      = var.azure_openai_api_key

  depends_on = [
    confluent_flink_compute_pool.flinkpool-main,
    confluent_api_key.app-manager-flink-api-key,
    confluent_role_binding.app-manager-kafka-cluster-admin
  ]

  lifecycle {
    create_before_destroy = false
  }
}

# Azure OpenAI Embedding Connection
resource "confluent_flink_connection" "azureopenai_embedding_connection" {
  organization {
    id = data.confluent_organization.main.id
  }
  environment {
    id = confluent_environment.staging.id
  }
  compute_pool {
    id = confluent_flink_compute_pool.flinkpool-main.id
  }
  principal {
    id = confluent_service_account.app-manager.id
  }
  rest_endpoint = data.confluent_flink_region.demo_flink_region.rest_endpoint
  credentials {
    key    = confluent_api_key.app-manager-flink-api-key.id
    secret = confluent_api_key.app-manager-flink-api-key.secret
  }

  display_name = "llm-embedding-connection"
  type         = "AZUREOPENAI"
  endpoint     = "${local.azure_openai_endpoint}/openai/deployments/text-embedding-3-large/embeddings?api-version=2024-08-01-preview"
  api_key      = var.azure_openai_api_key

  depends_on = [
    confluent_flink_compute_pool.flinkpool-main,
    confluent_api_key.app-manager-flink-api-key,
    confluent_role_binding.app-manager-kafka-cluster-admin
  ]

  lifecycle {
    create_before_destroy = false
  }
}

# Core LLM Model - Text Generation (Azure)
resource "confluent_flink_statement" "llm_textgen_model" {
  organization {
    id = data.confluent_organization.main.id
  }
  environment {
    id = confluent_environment.staging.id
  }
  compute_pool {
    id = confluent_flink_compute_pool.flinkpool-main.id
  }
  principal {
    id = confluent_service_account.app-manager.id
  }
  rest_endpoint = data.confluent_flink_region.demo_flink_region.rest_endpoint
  credentials {
    key    = confluent_api_key.app-manager-flink-api-key.id
    secret = confluent_api_key.app-manager-flink-api-key.secret
  }

  statement = "CREATE MODEL `${confluent_environment.staging.display_name}`.`${confluent_kafka_cluster.standard.display_name}`.`llm_textgen_model` INPUT (prompt STRING) OUTPUT (response STRING) WITH( 'provider' = 'azureopenai', 'task' = 'text_generation', 'azureopenai.connection' = '${confluent_flink_connection.azureopenai_connection.display_name}', 'azureopenai.model_version' = '2024-08-06', 'azureopenai.PARAMS.max_tokens' = '16384' );"

  properties = {
    "sql.current-catalog"  = confluent_environment.staging.display_name
    "sql.current-database" = "default"
  }

  depends_on = [
    confluent_flink_connection.azureopenai_connection
  ]
}

# Core LLM Model - Embedding (Azure)
resource "confluent_flink_statement" "llm_embedding_model" {
  organization {
    id = data.confluent_organization.main.id
  }
  environment {
    id = confluent_environment.staging.id
  }
  compute_pool {
    id = confluent_flink_compute_pool.flinkpool-main.id
  }
  principal {
    id = confluent_service_account.app-manager.id
  }
  rest_endpoint = data.confluent_flink_region.demo_flink_region.rest_endpoint
  credentials {
    key    = confluent_api_key.app-manager-flink-api-key.id
    secret = confluent_api_key.app-manager-flink-api-key.secret
  }

  statement = "CREATE MODEL `${confluent_environment.staging.display_name}`.`${confluent_kafka_cluster.standard.display_name}`.`llm_embedding_model` INPUT (text STRING) OUTPUT (embedding ARRAY<FLOAT>) WITH( 'provider' = 'azureopenai', 'task' = 'embedding', 'azureopenai.connection' = '${confluent_flink_connection.azureopenai_embedding_connection.display_name}', 'azureopenai.PARAMS.max_tokens' = '16384' );"

  properties = {
    "sql.current-catalog"  = confluent_environment.staging.display_name
    "sql.current-database" = "default"
  }

  depends_on = [
    confluent_flink_connection.azureopenai_embedding_connection
  ]
}
