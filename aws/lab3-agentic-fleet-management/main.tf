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

# Get organization data
data "confluent_organization" "main" {}

# Get Flink region data
data "confluent_flink_region" "lab3_flink_region" {
  cloud  = "AWS"
  region = local.cloud_region
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

# Create vessel_catalog table
resource "confluent_flink_statement" "vessel_catalog_table" {
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

  statement_name = "vessel-catalog-create-table"

  statement = <<-EOT
    CREATE TABLE IF NOT EXISTS `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.`vessel_catalog` (
      `vessel_id` STRING NOT NULL,
      `vessel_name` STRING NOT NULL,
      `base_zone` STRING NOT NULL,
      `availability` STRING NOT NULL,
      `capacity` INT NOT NULL
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
    confluent_flink_statement.ride_requests_table
  ]
}

# Generate Flink SQL command summary
resource "null_resource" "generate_flink_sql_summary" {
  # Trigger regeneration when key resources change
  triggers = {
    ride_requests_table = confluent_flink_statement.ride_requests_table.id
    vessel_catalog_table = confluent_flink_statement.vessel_catalog_table.id
  }

  provisioner "local-exec" {
    command     = "python ${path.module}/../../scripts/generate_lab_flink_summary.py lab3 aws ${path.module} || true"
    working_dir = path.module
  }

  depends_on = [
    confluent_flink_statement.ride_requests_table,
    confluent_flink_statement.vessel_catalog_table
  ]
}
