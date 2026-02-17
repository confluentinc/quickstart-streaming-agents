terraform {
  required_version = ">= 1.0"
  required_providers {
    confluent = {
      source  = "confluentinc/confluent"
      version = "~> 2.38"
    }
  }
}

# Confluent Provider Configuration (for module use)
provider "confluent" {
  cloud_api_key    = data.terraform_remote_state.core.outputs.confluent_cloud_api_key
  cloud_api_secret = data.terraform_remote_state.core.outputs.confluent_cloud_api_secret
}
