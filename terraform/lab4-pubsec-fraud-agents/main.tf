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
      `claim_timestamp` TIMESTAMP_LTZ(3) NOT NULL,
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

