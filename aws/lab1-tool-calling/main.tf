# Reference to core infrastructure
data "terraform_remote_state" "core" {
  backend = "local"
  config = {
    path = "../core/terraform.tfstate"
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
# AWS-SPECIFIC RESOURCES FOR LAB1-TOOL-CALLING
# ------------------------------------------------------

# Lab1 uses the shared LLM infrastructure from core
# LLM connection and model are now available via: data.terraform_remote_state.core.outputs.llm_connection_name

# Get organization data
data "confluent_organization" "main" {}

# Get Flink region data
data "confluent_flink_region" "lab1_flink_region" {
  cloud  = "AWS"
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

  statement = "CREATE CONNECTION `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.`zapier-mcp-connection` WITH ( 'type' = 'MCP_SERVER', 'endpoint' = '${var.ZAPIER_SSE_ENDPOINT}', 'api-key' = 'api_key' );"

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
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

  statement = "CREATE MODEL `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.`zapier_mcp_model` INPUT (prompt STRING) OUTPUT (response STRING) WITH ( 'provider' = 'bedrock', 'task' = 'text_generation', 'bedrock.connection' = '${data.terraform_remote_state.core.outputs.llm_connection_name}', 'bedrock.params.max_tokens' = '50000', 'mcp.connection' = 'zapier-mcp-connection' );"

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = "default"
  }

  # Ensure MCP connection is created first
  depends_on = [
    confluent_flink_statement.zapier_mcp_connection
  ]
}

# Generate MCP commands file with SQL reference
resource "local_file" "mcp_commands" {
  filename = "${path.module}/mcp_commands.txt"
  content  = <<-EOT
# Lab1 Tool Calling - Setup Status
#
# 🎉 FULLY AUTOMATED BY TERRAFORM (SQL-Based):
# ✅ Core LLM infrastructure (deployed in core terraform)
# ✅ LLM connection: ${data.terraform_remote_state.core.outputs.llm_connection_name}
# ✅ LLM model: llm_textgen_model (available in core)
# ✅ MCP connection: zapier-mcp-connection (created via Terraform SQL statement)
# ✅ MCP model: zapier_mcp_model (created via Terraform SQL statement)
#
# ℹ️ NO MANUAL STEPS REQUIRED
# All setup is handled automatically during 'terraform apply'
#
# 📋 MANUAL SQL COMMANDS (for reference only, if you need to recreate manually):

# Step 1: Create Zapier MCP Connection (automated via Terraform)
CREATE CONNECTION `zapier-mcp-connection`
WITH (
  'type' = 'MCP_SERVER',
  'endpoint' = '${var.ZAPIER_SSE_ENDPOINT}',
  'api-key' = 'api_key'
);

# Step 2: Create Zapier MCP Model (automated via Terraform)
CREATE MODEL `zapier_mcp_model`
INPUT (prompt STRING)
OUTPUT (response STRING)
WITH (
  'provider' = 'bedrock',
  'task' = 'text_generation',
  'bedrock.connection' = '${data.terraform_remote_state.core.outputs.llm_connection_name}',
  'bedrock.params.max_tokens' = '50000',
  'mcp.connection' = 'zapier-mcp-connection'
);

# Agent 2: Use the shared llm_textgen_model (already created in core terraform)
# No need to create this model - it's available as 'llm_textgen_model'

# 📌 NOTE: Old CLI approach (deprecated):
# The previous approach used Python script + Confluent CLI which required:
# - Python + uv installation
# - Confluent CLI installation
# - Two separate endpoint parameters (--endpoint and --sse-endpoint)
#
# New SQL approach is simpler, fully declarative, and requires only Terraform.

EOT
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
