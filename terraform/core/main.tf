resource "random_id" "resource_suffix" {
  byte_length = 4
}

locals {
  region_mapping = {
    # AWS Regions
    "us-east-1"      = "us-east-1"
    "us-east-2"      = "us-east-2"
    "us-west-1"      = "us-west-1"
    "us-west-2"      = "us-west-2"
    "eu-west-1"      = "eu-west-1"
    "eu-west-2"      = "eu-west-2"
    "eu-central-1"   = "eu-central-1"
    "ap-southeast-1" = "ap-southeast-1"
    "ap-southeast-2" = "ap-southeast-2"
    "ap-northeast-1" = "ap-northeast-1"
    "sa-east-1"      = "sa-east-1"

    # Azure Regions
    "East US"             = "eastus"
    "East US 2"           = "eastus2"
    "Central US"          = "centralus"
    "North Central US"    = "northcentralus"
    "South Central US"    = "southcentralus"
    "West US"             = "westus"
    "West US 2"           = "westus2"
    "West US 3"           = "westus3"
    "West Central US"     = "westcentralus"
    "Canada Central"      = "canadacentral"
    "Canada East"         = "canadaeast"
    "Brazil South"        = "brazilsouth"
    "Brazil Southeast"    = "brazilsoutheast"
    "North Europe"        = "northeurope"
    "West Europe"         = "westeurope"
    "France Central"      = "francecentral"
    "France South"        = "francesouth"
    "Germany West Central"= "germanywestcentral"
    "Germany North"       = "germanynorth"
    "Sweden Central"      = "swedencentral"
    "UK South"            = "uksouth"
    "UK West"             = "ukwest"
    "Norway East"         = "norwayeast"
    "Norway West"         = "norwaywest"
    "Switzerland North"   = "switzerlandnorth"
    "Switzerland West"    = "switzerlandwest"
    "UAE North"           = "uaenorth"
    "UAE Central"         = "uaecentral"
    "South Africa North"  = "southafricanorth"
    "South Africa West"   = "southafricawest"
    "East Asia"           = "eastasia"
    "Southeast Asia"      = "southeastasia"
    "Japan East"          = "japaneast"
    "Japan West"          = "japanwest"
    "Korea Central"       = "koreacentral"
    "Korea South"         = "koreasouth"
    "Central India"       = "centralindia"
    "South India"         = "southindia"
    "West India"          = "westindia"
    "Australia East"      = "australiaeast"
    "Australia Southeast" = "australiasoutheast"
    "Australia Central"   = "australiacentral"
    "Australia Central 2" = "australiacentral2"
    "Chile Central"       = "chilecentral"
  }

  confluent_region = lookup(local.region_mapping, var.cloud_region, var.cloud_region)
  cloud_provider = upper(var.cloud_provider)
}

resource "confluent_environment" "staging" {
  display_name = "${var.prefix}-env-${random_id.resource_suffix.hex}"

  stream_governance {
    package = "ADVANCED"
  }

  lifecycle {
    prevent_destroy = true
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
  display_name = "${var.prefix}-cluster-${random_id.resource_suffix.hex}"
  availability = "SINGLE_ZONE"
  cloud        = local.cloud_provider
  region       = local.confluent_region
  standard {}
  environment {
    id = confluent_environment.staging.id
  }

  lifecycle {
    prevent_destroy = true
  }
}

resource "confluent_service_account" "app-manager" {
  display_name = "${var.prefix}-app-manager-${random_id.resource_suffix.hex}"
  description  = "Service account to manage 'inventory' Kafka cluster"

  lifecycle {
    prevent_destroy = true
  }
}

resource "confluent_role_binding" "app-manager-kafka-cluster-admin" {
  principal   = "User:${confluent_service_account.app-manager.id}"
  role_name   = "EnvironmentAdmin"
  crn_pattern = confluent_environment.staging.resource_name
}

resource "confluent_flink_compute_pool" "flinkpool-main" {
  display_name     = "${var.prefix}_standard_compute_pool_${random_id.resource_suffix.hex}"
  cloud            = local.cloud_provider
  region           = local.confluent_region
  max_cfu          = 20
  environment {
    id = confluent_environment.staging.id
  }

  lifecycle {
    prevent_destroy = true
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
  cloud   = local.cloud_provider
  region  = local.confluent_region
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
# LLM INFRASTRUCTURE - SHARED ACROSS ALL LABS
# ------------------------------------------------------

# AWS AI Services Module (conditional based on cloud provider)
module "aws_ai_services" {
  source = "../modules/aws-ai"
  count  = lower(var.cloud_provider) == "aws" ? 1 : 0

  prefix                         = var.prefix
  cloud_region                  = var.cloud_region
  random_id                     = random_id.resource_suffix.hex
  model_prefix                  = "core"
  confluent_organization_id     = data.confluent_organization.main.id
  confluent_environment_id      = confluent_environment.staging.id
  confluent_compute_pool_id     = confluent_flink_compute_pool.flinkpool-main.id
  confluent_service_account_id  = confluent_service_account.app-manager.id
  confluent_flink_rest_endpoint = data.confluent_flink_region.demo_flink_region.rest_endpoint
  confluent_flink_api_key_id    = confluent_api_key.app-manager-flink-api-key.id
  confluent_flink_api_key_secret = confluent_api_key.app-manager-flink-api-key.secret
}

# Azure AI Services Module (conditional based on cloud provider)
module "azure_ai_services" {
  source = "../modules/azure-ai"
  count  = lower(var.cloud_provider) == "azure" ? 1 : 0

  prefix                         = var.prefix
  cloud_region                  = var.cloud_region
  random_id                     = random_id.resource_suffix.hex
  confluent_organization_id     = data.confluent_organization.main.id
  confluent_environment_id      = confluent_environment.staging.id
  confluent_compute_pool_id     = confluent_flink_compute_pool.flinkpool-main.id
  confluent_service_account_id  = confluent_service_account.app-manager.id
  confluent_flink_rest_endpoint = data.confluent_flink_region.demo_flink_region.rest_endpoint
  confluent_flink_api_key_id    = confluent_api_key.app-manager-flink-api-key.id
  confluent_flink_api_key_secret = confluent_api_key.app-manager-flink-api-key.secret
}

# Core LLM Model - Text Generation (AWS)
resource "confluent_flink_statement" "llm_textgen_model_aws" {
  count = lower(var.cloud_provider) == "aws" ? 1 : 0

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

  statement = "CREATE MODEL `${confluent_environment.staging.display_name}`.`${confluent_kafka_cluster.standard.display_name}`.`llm_textgen_model` INPUT (prompt STRING) OUTPUT (response STRING) WITH ( 'provider' = 'bedrock', 'task' = 'text_generation', 'bedrock.connection' = 'llm-textgen-connection', 'bedrock.model_version' = '2024-02-29', 'bedrock.params.max_tokens' = '4096' );"

  properties = {
    "sql.current-catalog"  = confluent_environment.staging.display_name
    "sql.current-database" = "default"
  }

  lifecycle {
    prevent_destroy = true
  }

  depends_on = [module.aws_ai_services]
}

# Core LLM Model - Text Generation (Azure)
resource "confluent_flink_statement" "llm_textgen_model_azure" {
  count = lower(var.cloud_provider) == "azure" ? 1 : 0

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

  statement = "CREATE MODEL `${confluent_environment.staging.display_name}`.`${confluent_kafka_cluster.standard.display_name}`.`llm_textgen_model` INPUT (prompt STRING) OUTPUT (response STRING) WITH( 'provider' = 'azureopenai', 'task' = 'text_generation', 'azureopenai.connection' = 'llm-textgen-connection', 'azureopenai.model_version' = '2024-08-06' );"

  properties = {
    "sql.current-catalog"  = confluent_environment.staging.display_name
    "sql.current-database" = "default"
  }

  lifecycle {
    prevent_destroy = true
  }

  depends_on = [module.azure_ai_services]
}

# Core LLM Model - Embedding (AWS)
resource "confluent_flink_statement" "llm_embedding_model_aws" {
  count = lower(var.cloud_provider) == "aws" ? 1 : 0

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

  statement = "CREATE MODEL `${confluent_environment.staging.display_name}`.`${confluent_kafka_cluster.standard.display_name}`.`llm_embedding_model` INPUT (text STRING) OUTPUT (embedding ARRAY<FLOAT>) WITH ( 'provider' = 'bedrock', 'task' = 'embedding', 'bedrock.connection' = 'llm-embedding-connection' );"

  properties = {
    "sql.current-catalog"  = confluent_environment.staging.display_name
    "sql.current-database" = "default"
  }

  lifecycle {
    prevent_destroy = true
  }

  depends_on = [module.aws_ai_services]
}

# Core LLM Model - Embedding (Azure)
resource "confluent_flink_statement" "llm_embedding_model_azure" {
  count = lower(var.cloud_provider) == "azure" ? 1 : 0

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

  statement = "CREATE MODEL `${confluent_environment.staging.display_name}`.`${confluent_kafka_cluster.standard.display_name}`.`llm_embedding_model` INPUT (text STRING) OUTPUT (embedding ARRAY<FLOAT>) WITH( 'provider' = 'azureopenai', 'task' = 'embedding', 'azureopenai.connection' = 'llm-embedding-connection' );"

  properties = {
    "sql.current-catalog"  = confluent_environment.staging.display_name
    "sql.current-database" = "default"
  }

  # lifecycle {
  #   prevent_destroy = true
  # }

  depends_on = [module.azure_ai_services]
}
