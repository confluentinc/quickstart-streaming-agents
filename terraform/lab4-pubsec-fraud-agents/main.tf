# Reference to core infrastructure
data "terraform_remote_state" "core" {
  backend = "local"
  config = {
    path = "../core/terraform.tfstate"
  }
}

# Local values
locals {
  cloud_provider = data.terraform_remote_state.core.outputs.cloud_provider
  cloud_region   = data.terraform_remote_state.core.outputs.cloud_region

  # Azure CosmosDB credentials (read-only)
  cosmosdb_endpoint = "https://fema-iappg.documents.azure.com:443/"
  cosmosdb_api_key  = "KjJPts0iGXwxQhTuoOiH8FnXd8gDve3nAl5Yt1ibEEH8EL63Jyl0H14lGWieIExBDCxo7aPErOs3ACDbYRZ1hw=="

  # AWS MongoDB credentials (read-only)
  mongodb_conn = "mongodb+srv://cluster0.rgtlalv.mongodb.net/"
  mongodb_user = "workshop-user"
  mongodb_pass = "DGaR5XjgdMZTigMr"
}

# Get organization data
data "confluent_organization" "main" {}

# Get Flink region data
data "confluent_flink_region" "lab4_flink_region" {
  cloud  = upper(local.cloud_provider)
  region = local.cloud_region
}

# Create claims table with WATERMARK for streaming
resource "confluent_flink_statement" "claims_table" {
  organization {
    id = data.confluent_organization.main.id
  }
  environment {
    id = data.terraform_remote_state.core.outputs.confluent_environment_id
  }
  compute_pool {
    id = data.terraform_remote_state.core.outputs.confluent_flink_compute_pool_id
  }
  principal {
    id = data.terraform_remote_state.core.outputs.app_manager_service_account_id
  }
  rest_endpoint = data.confluent_flink_region.lab4_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement_name = "claims-create-table"

  statement = <<-EOT
    CREATE TABLE `claims` (
      `claim_id` STRING NOT NULL,
      `applicant_name` STRING,
      `city` STRING NOT NULL,
      `is_primary_residence` STRING,
      `damage_assessed` STRING,
      `claim_amount` STRING NOT NULL,
      `has_insurance` STRING,
      `insurance_amount` STRING,
      `claim_narrative` STRING,
      `assessment_date` STRING,
      `disaster_date` STRING,
      `previous_claims_count` STRING,
      `last_claim_date` STRING,
      `assessment_source` STRING,
      `shared_account` STRING,
      `shared_phone` STRING,
      `claim_timestamp` TIMESTAMP(3) NOT NULL,
      WATERMARK FOR `claim_timestamp` AS `claim_timestamp` - INTERVAL '5' SECOND
    );
  EOT

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
  }

  lifecycle {
    prevent_destroy = false
  }

  depends_on = [
    data.terraform_remote_state.core
  ]
}

# Create CosmosDB connection for Lab4 (Azure only)
resource "confluent_flink_statement" "cosmosdb_connection_statement_lab4" {
  count = local.cloud_provider == "azure" ? 1 : 0

  organization {
    id = data.confluent_organization.main.id
  }
  environment {
    id = data.terraform_remote_state.core.outputs.confluent_environment_id
  }
  compute_pool {
    id = data.terraform_remote_state.core.outputs.confluent_flink_compute_pool_id
  }
  principal {
    id = data.terraform_remote_state.core.outputs.app_manager_service_account_id
  }
  rest_endpoint = data.confluent_flink_region.lab4_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement_name = "cosmosdb-connection-create-lab4"

  statement = <<-EOT
    CREATE CONNECTION IF NOT EXISTS `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.`cosmosdb-connection-lab4`
    WITH (
      'type' = 'cosmosdb',
      'endpoint' = '${local.cosmosdb_endpoint}',
      'api-key' = '${local.cosmosdb_api_key}'
    );
  EOT

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
  }

  lifecycle {
    ignore_changes  = [statement]
    prevent_destroy = false
  }

  depends_on = [
    data.terraform_remote_state.core
  ]
}

# FEMA policies vectordb table for Lab4 (Azure/CosmosDB)
resource "confluent_flink_statement" "fema_policies_vectordb_azure" {
  count = local.cloud_provider == "azure" ? 1 : 0

  organization {
    id = data.confluent_organization.main.id
  }
  environment {
    id = data.terraform_remote_state.core.outputs.confluent_environment_id
  }
  compute_pool {
    id = data.terraform_remote_state.core.outputs.confluent_flink_compute_pool_id
  }
  principal {
    id = data.terraform_remote_state.core.outputs.app_manager_service_account_id
  }
  rest_endpoint = data.confluent_flink_region.lab4_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement_name = "fema-policies-vectordb-create-table-azure"

  statement = <<-EOT
    CREATE TABLE IF NOT EXISTS fema_policies_vectordb (
      document_id STRING,
      chunk STRING,
      embedding ARRAY<FLOAT>,
      pages STRING,
      section_reference STRING,
      title STRING,
      fraud_categories ARRAY<STRING>,
      policy_keywords ARRAY<STRING>,
      char_count INT
    ) WITH (
      'connector' = 'cosmosdb',
      'cosmosdb.connection' = 'cosmosdb-connection-lab4',
      'cosmosdb.database' = 'vector_search',
      'cosmosdb.container' = 'documents'
    );
  EOT

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
  }

  lifecycle {
    prevent_destroy = false
  }

  depends_on = [
    confluent_flink_statement.cosmosdb_connection_statement_lab4
  ]
}

# Create MongoDB connection for Lab4 (AWS only)
resource "confluent_flink_statement" "mongodb_connection_statement_lab4" {
  count = local.cloud_provider == "aws" ? 1 : 0

  organization {
    id = data.confluent_organization.main.id
  }
  environment {
    id = data.terraform_remote_state.core.outputs.confluent_environment_id
  }
  compute_pool {
    id = data.terraform_remote_state.core.outputs.confluent_flink_compute_pool_id
  }
  principal {
    id = data.terraform_remote_state.core.outputs.app_manager_service_account_id
  }
  rest_endpoint = data.confluent_flink_region.lab4_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement_name = "mongodb-connection-create-lab4"

  statement = <<-EOT
    CREATE CONNECTION IF NOT EXISTS `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.`mongodb-connection-lab4`
    WITH (
      'type' = 'MONGODB',
      'endpoint' = '${local.mongodb_conn}',
      'username' = '${local.mongodb_user}',
      'password' = '${local.mongodb_pass}'
    );
  EOT

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
  }

  lifecycle {
    ignore_changes  = [statement]
    prevent_destroy = false
  }

  depends_on = [
    data.terraform_remote_state.core
  ]
}

# FEMA policies vectordb table for Lab4 (AWS/MongoDB)
resource "confluent_flink_statement" "fema_policies_vectordb_aws" {
  count = local.cloud_provider == "aws" ? 1 : 0

  organization {
    id = data.confluent_organization.main.id
  }
  environment {
    id = data.terraform_remote_state.core.outputs.confluent_environment_id
  }
  compute_pool {
    id = data.terraform_remote_state.core.outputs.confluent_flink_compute_pool_id
  }
  principal {
    id = data.terraform_remote_state.core.outputs.app_manager_service_account_id
  }
  rest_endpoint = data.confluent_flink_region.lab4_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement_name = "fema-policies-vectordb-create-table-aws"

  statement = <<-EOT
    CREATE TABLE IF NOT EXISTS fema_policies_vectordb (
      document_id STRING,
      chunk STRING,
      embedding ARRAY<FLOAT>,
      pages STRING,
      section_reference STRING,
      title STRING,
      fraud_categories ARRAY<STRING>,
      policy_keywords ARRAY<STRING>,
      char_count INT
    ) WITH (
      'connector' = 'mongodb',
      'mongodb.connection' = 'mongodb-connection-lab4',
      'mongodb.database' = 'vector_search',
      'mongodb.collection' = 'documents',
      'mongodb.index' = 'vector_index',
      'mongodb.embedding_column' = 'embedding',
      'mongodb.numCandidates' = '500'
    );
  EOT

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
  }

  lifecycle {
    prevent_destroy = false
  }

  depends_on = [
    confluent_flink_statement.mongodb_connection_statement_lab4
  ]
}
