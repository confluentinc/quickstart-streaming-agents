# Reference to core infrastructure
data "terraform_remote_state" "core" {
  backend = "local"
  config = {
    path = "../core/terraform.tfstate"
  }
}

# Reference to Lab2 infrastructure (non-workshop mode only)
data "terraform_remote_state" "lab2" {
  count   = var.workshop_mode ? 0 : 1
  backend = "local"
  config = {
    path = "../lab2-vector-search/terraform.tfstate"
  }
}

# Use cloud_region from core infrastructure
locals {
  cloud_region = data.terraform_remote_state.core.outputs.cloud_region
}

# Get organization data
data "confluent_organization" "main" {}

# Get Flink region data
data "confluent_flink_region" "lab3_flink_region" {
  cloud  = "AWS"
  region = local.cloud_region
}

# MongoDB connection for Lab3 vector search (workshop mode only)
resource "confluent_flink_connection" "mongodb_connection_lab3" {
  count = var.workshop_mode ? 1 : 0

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
  rest_endpoint = data.confluent_flink_region.lab3_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  display_name = "mongodb-connection-lab3"
  type         = "MONGODB"
  endpoint     = var.mongodb_connection_string_lab3
  username     = var.mongodb_username_lab3
  password     = var.mongodb_password_lab3
}

# MongoDB vector database table for Lab3 (workshop mode only)
resource "confluent_flink_statement" "documents_vectordb_lab3" {
  count = var.workshop_mode ? 1 : 0

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
  rest_endpoint = data.confluent_flink_region.lab3_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement_name = "documents-vectordb-lab3-create-table"

  statement = <<-EOT
    CREATE TABLE IF NOT EXISTS documents_vectordb_lab3 (
      document_id STRING,
      chunk STRING,
      embedding ARRAY<FLOAT>
    ) WITH (
      'connector' = 'mongodb',
      'mongodb.connection' = 'mongodb-connection-lab3',
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
    confluent_flink_connection.mongodb_connection_lab3
  ]
}

# Zapier MCP connection for Lab3
resource "confluent_flink_statement" "zapier_mcp_connection_lab3" {
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
  rest_endpoint = data.confluent_flink_region.lab3_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement_name = "zapier-mcp-connection-create-lab3"

  statement = <<-EOT
    CREATE CONNECTION IF NOT EXISTS `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.`zapier-mcp-connection`
    WITH (
      'type' = 'MCP_SERVER',
      'endpoint' = 'https://mcp.zapier.com/api/v1/connect',
      'token' = '${var.zapier_token}',
      'transport-type' = 'STREAMABLE_HTTP'
    );
  EOT

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
  }

  lifecycle {
    ignore_changes = [statement]
  }

  depends_on = [
    data.terraform_remote_state.core
  ]
}

# Zapier MCP model for Lab3
resource "confluent_flink_statement" "zapier_mcp_model_lab3" {
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
  rest_endpoint = data.confluent_flink_region.lab3_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement_name = "zapier-mcp-model-create-lab3"

  statement = <<-EOT
    CREATE MODEL IF NOT EXISTS `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.`zapier_mcp_model`
    INPUT (prompt STRING)
    OUTPUT (response STRING)
    WITH (
      'provider' = 'bedrock',
      'task' = 'text_generation',
      'bedrock.connection' = '${data.terraform_remote_state.core.outputs.llm_connection_name}',
      'bedrock.params.max_tokens' = '50000',
      'mcp.connection' = 'zapier-mcp-connection'
    );
  EOT

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = "default"
  }

  depends_on = [
    confluent_flink_statement.zapier_mcp_connection_lab3
  ]
}

# Create ride_requests table with WATERMARK
resource "confluent_flink_statement" "ride_requests_table" {
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
  rest_endpoint = data.confluent_flink_region.lab3_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement_name = "ride-requests-create-table"

  statement = <<-EOT
    CREATE TABLE IF NOT EXISTS `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.`ride_requests` (
      `request_id` STRING NOT NULL,
      `customer_email` STRING NOT NULL,
      `pickup_zone` STRING NOT NULL,
      `drop_off_zone` STRING NOT NULL,
      `price` DOUBLE NOT NULL,
      `number_of_passengers` INT NOT NULL,
      `request_ts` TIMESTAMP(3) WITH LOCAL TIME ZONE NOT NULL,
      WATERMARK FOR `request_ts` AS `request_ts` - INTERVAL '5' SECOND
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


# Generate Flink SQL command summary
resource "null_resource" "generate_flink_sql_summary" {
  # Trigger regeneration when key resources change
  triggers = {
    zapier_mcp_connection = confluent_flink_statement.zapier_mcp_connection_lab3.id
    zapier_mcp_model      = confluent_flink_statement.zapier_mcp_model_lab3.id
    ride_requests_table   = confluent_flink_statement.ride_requests_table.id
  }

  provisioner "local-exec" {
    command     = "python ${path.module}/../../scripts/common/generate_lab_flink_summary.py lab3 aws ${path.module} || true"
    working_dir = path.module
  }

  depends_on = [
    confluent_flink_statement.zapier_mcp_connection_lab3,
    confluent_flink_statement.zapier_mcp_model_lab3,
    confluent_flink_statement.ride_requests_table
  ]
}
