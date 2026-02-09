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

  # Cloud-specific MongoDB defaults
  mongodb_defaults = {
    aws   = { conn = "mongodb+srv://cluster0.w9n3o45.mongodb.net/", user = "workshop-user", pass = "xr6PvJl9xZz1uoKa" }
    azure = { conn = "mongodb+srv://cluster0.iir6woe.mongodb.net/", user = "public_readonly_user", pass = "pE7xOkiKth2QqTKL" }
  }

  effective_mongodb_conn = var.mongodb_connection_string_lab3 != "" ? var.mongodb_connection_string_lab3 : local.mongodb_defaults[local.cloud_provider].conn
  effective_mongodb_user = var.mongodb_username_lab3 != "" ? var.mongodb_username_lab3 : local.mongodb_defaults[local.cloud_provider].user
  effective_mongodb_pass = var.mongodb_password_lab3 != "" ? var.mongodb_password_lab3 : local.mongodb_defaults[local.cloud_provider].pass
}

# Get organization data
data "confluent_organization" "main" {}

# Get Flink region data
data "confluent_flink_region" "lab3_flink_region" {
  cloud  = upper(local.cloud_provider)
  region = local.cloud_region
}

# MongoDB connection for Lab3 vector search
resource "confluent_flink_connection" "mongodb_connection_lab3" {
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
  endpoint     = local.effective_mongodb_conn
  username     = local.effective_mongodb_user
  password     = local.effective_mongodb_pass
}

# MongoDB vector database table for Lab3
resource "confluent_flink_statement" "documents_vectordb_lab3" {
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

# Zapier MCP model for Lab3 (AWS/Bedrock)
resource "confluent_flink_statement" "zapier_mcp_model_lab3_aws" {
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

# Zapier MCP model for Lab3 (Azure/OpenAI)
resource "confluent_flink_statement" "zapier_mcp_model_lab3_azure" {
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
      'provider' = 'azureopenai',
      'task' = 'text_generation',
      'azureopenai.connection' = '${data.terraform_remote_state.core.outputs.llm_connection_name}',
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
    zapier_mcp_model_aws  = local.cloud_provider == "aws" ? confluent_flink_statement.zapier_mcp_model_lab3_aws[0].id : ""
    zapier_mcp_model_azure = local.cloud_provider == "azure" ? confluent_flink_statement.zapier_mcp_model_lab3_azure[0].id : ""
    ride_requests_table   = confluent_flink_statement.ride_requests_table.id
  }

  provisioner "local-exec" {
    command     = "cd ${path.module}/../.. && uv run generate_summaries ${local.cloud_provider}"
    working_dir = path.module
  }

  depends_on = [
    confluent_flink_statement.zapier_mcp_connection_lab3,
    confluent_flink_statement.zapier_mcp_model_lab3_aws,
    confluent_flink_statement.zapier_mcp_model_lab3_azure,
    confluent_flink_statement.ride_requests_table
  ]
}
