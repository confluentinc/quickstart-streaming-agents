# Reference to core infrastructure
# In workshop mode, points to core-workshop (no Azure provider)
# In production mode, points to core (with Azure provider)
data "terraform_remote_state" "core" {
  backend = "local"
  config = {
    path = var.workshop_mode ? "../core-workshop/terraform.tfstate" : "../core/terraform.tfstate"
  }
}

# Use cloud_region from core infrastructure
locals {
  cloud_region = data.terraform_remote_state.core.outputs.cloud_region
}

# Random ID for unique resource names for this lab
resource "random_id" "lab_suffix" {
  byte_length = 4
}

# ------------------------------------------------------
# AZURE-SPECIFIC RESOURCES FOR LAB1-TOOL-CALLING
# ------------------------------------------------------

# Lab1 uses the shared LLM infrastructure from core
# LLM connection and model are now available via: data.terraform_remote_state.core.outputs.llm_connection_name

# Get organization data
data "confluent_organization" "main" {}

# Get Flink region data
data "confluent_flink_region" "lab1_flink_region" {
  cloud  = "AZURE"
  region = local.cloud_region
}

# Create MCP connection using Flink SQL
resource "confluent_flink_statement" "zapier_mcp_connection" {
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
  rest_endpoint = data.confluent_flink_region.lab1_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement = "CREATE CONNECTION `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.`zapier-mcp-connection` WITH ( 'type' = 'MCP_SERVER', 'endpoint' = 'https://mcp.zapier.com/api/v1/connect', 'token' = '${var.zapier_token}', 'transport-type' = 'STREAMABLE_HTTP' );"

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

# Create the Zapier MCP Model via Flink SQL
resource "confluent_flink_statement" "zapier_mcp_model" {
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
  rest_endpoint = data.confluent_flink_region.lab1_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement = "CREATE MODEL `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.`zapier_mcp_model` INPUT (prompt STRING) OUTPUT (response STRING) WITH ( 'provider' = 'azureopenai', 'task' = 'text_generation', 'azureopenai.connection' = '${data.terraform_remote_state.core.outputs.llm_connection_name}', 'mcp.connection' = 'zapier-mcp-connection' );"

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = "default"
  }

  # Ensure MCP connection is created first
  depends_on = [
    confluent_flink_statement.zapier_mcp_connection
  ]
}

# Generate Flink SQL command summary
resource "null_resource" "generate_flink_sql_summary" {
  # Trigger regeneration when key resources change
  triggers = {
    mcp_connection = confluent_flink_statement.zapier_mcp_connection.id
    mcp_model      = confluent_flink_statement.zapier_mcp_model.id
  }

  provisioner "local-exec" {
    command     = "python ${path.module}/../../scripts/common/generate_lab_flink_summary.py lab1 azure ${path.module} || true"
    working_dir = path.module
  }

  depends_on = [
    confluent_flink_statement.zapier_mcp_connection,
    confluent_flink_statement.zapier_mcp_model
  ]
}

# ------------------------------------------------------
# CREATE KAFKA TABLES FOR LAB1 DATAGEN
# ------------------------------------------------------

# Create orders table
# resource "confluent_flink_statement" "orders_table" {
#   organization {
#     id = data.confluent_organization.main.id
#   }
#   environment {
#     id = data.terraform_remote_state.core.outputs.confluent_environment_id
#   }
#   compute_pool {
#     id = data.terraform_remote_state.core.outputs.confluent_flink_compute_pool_id
#   }
#   principal {
#     id = data.terraform_remote_state.core.outputs.app_manager_service_account_id
#   }
#   rest_endpoint = data.confluent_flink_region.lab1_flink_region.rest_endpoint
#   credentials {
#     key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
#     secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
#   }
# 
#   statement_name = "orders-create-table"
# 
#   statement = <<-EOT
#     CREATE TABLE `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.`orders` (
#       `key` VARBINARY(2147483647),
#       `order_id` VARCHAR(2147483647) NOT NULL,
#       `customer_id` VARCHAR(2147483647) NOT NULL,
#       `product_id` VARCHAR(2147483647) NOT NULL,
#       `price` DOUBLE NOT NULL,
#       `order_ts` TIMESTAMP(3) WITH LOCAL TIME ZONE NOT NULL
#     )
#     DISTRIBUTED BY HASH(`key`) INTO 6 BUCKETS
#     WITH (
#       'changelog.mode' = 'append',
#       'connector' = 'confluent',
#       'kafka.cleanup-policy' = 'delete',
#       'kafka.compaction.time' = '0 ms',
#       'kafka.max-message-size' = '2097164 bytes',
#       'kafka.retention.size' = '0 bytes',
#       'kafka.retention.time' = '7 d',
#       'key.format' = 'raw',
#       'scan.bounded.mode' = 'unbounded',
#       'scan.startup.mode' = 'earliest-offset',
#       'value.format' = 'avro-registry'
#     );
#   EOT
# 
#   properties = {
#     "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
#     "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
#   }
# 
#   depends_on = [
#     confluent_flink_statement.zapier_mcp_model
#   ]
# }

# Create products table
# resource "confluent_flink_statement" "products_table" {
#   organization {
#     id = data.confluent_organization.main.id
#   }
#   environment {
#     id = data.terraform_remote_state.core.outputs.confluent_environment_id
#   }
#   compute_pool {
#     id = data.terraform_remote_state.core.outputs.confluent_flink_compute_pool_id
#   }
#   principal {
#     id = data.terraform_remote_state.core.outputs.app_manager_service_account_id
#   }
#   rest_endpoint = data.confluent_flink_region.lab1_flink_region.rest_endpoint
#   credentials {
#     key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
#     secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
#   }
# 
#   statement_name = "products-create-table"
# 
#   statement = <<-EOT
#     CREATE TABLE `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.`products` (
#       `key` VARBINARY(2147483647),
#       `product_id` VARCHAR(2147483647) NOT NULL,
#       `product_name` VARCHAR(2147483647) NOT NULL,
#       `price` DOUBLE NOT NULL,
#       `department` VARCHAR(2147483647) NOT NULL,
#       `updated_at` TIMESTAMP(3) WITH LOCAL TIME ZONE NOT NULL
#     )
#     DISTRIBUTED BY HASH(`key`) INTO 6 BUCKETS
#     WITH (
#       'changelog.mode' = 'append',
#       'connector' = 'confluent',
#       'kafka.cleanup-policy' = 'delete',
#       'kafka.compaction.time' = '0 ms',
#       'kafka.max-message-size' = '2097164 bytes',
#       'kafka.retention.size' = '0 bytes',
#       'kafka.retention.time' = '7 d',
#       'key.format' = 'raw',
#       'scan.bounded.mode' = 'unbounded',
#       'scan.startup.mode' = 'earliest-offset',
#       'value.format' = 'avro-registry'
#     );
#   EOT
# 
#   properties = {
#     "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
#     "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
#   }
# 
#   depends_on = [
#     confluent_flink_statement.zapier_mcp_model
#   ]
# }

# Create customers table
# resource "confluent_flink_statement" "customers_table" {
#   organization {
#     id = data.confluent_organization.main.id
#   }
#   environment {
#     id = data.terraform_remote_state.core.outputs.confluent_environment_id
#   }
#   compute_pool {
#     id = data.terraform_remote_state.core.outputs.confluent_flink_compute_pool_id
#   }
#   principal {
#     id = data.terraform_remote_state.core.outputs.app_manager_service_account_id
#   }
#   rest_endpoint = data.confluent_flink_region.lab1_flink_region.rest_endpoint
#   credentials {
#     key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
#     secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
#   }
# 
#   statement_name = "customers-create-table"
# 
#   statement = <<-EOT
#     CREATE TABLE `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.`customers` (
#       `key` VARBINARY(2147483647),
#       `customer_id` VARCHAR(2147483647) NOT NULL,
#       `customer_email` VARCHAR(2147483647) NOT NULL,
#       `customer_name` VARCHAR(2147483647) NOT NULL,
#       `state` VARCHAR(2147483647) NOT NULL,
#       `updated_at` TIMESTAMP(3) WITH LOCAL TIME ZONE NOT NULL
#     )
#     DISTRIBUTED BY HASH(`key`) INTO 6 BUCKETS
#     WITH (
#       'changelog.mode' = 'append',
#       'connector' = 'confluent',
#       'kafka.cleanup-policy' = 'delete',
#       'kafka.compaction.time' = '0 ms',
#       'kafka.max-message-size' = '2097164 bytes',
#       'kafka.retention.size' = '0 bytes',
#       'kafka.retention.time' = '7 d',
#       'key.format' = 'raw',
#       'scan.bounded.mode' = 'unbounded',
#       'scan.startup.mode' = 'earliest-offset',
#       'value.format' = 'avro-registry'
#     );
#   EOT
# 
#   properties = {
#     "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
#     "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
#   }
# 
#   depends_on = [
#     confluent_flink_statement.zapier_mcp_model
#   ]
# }
