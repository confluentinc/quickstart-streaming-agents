terraform {
  required_version = ">= 1.0"
  required_providers {
    confluent = {
      source  = "confluentinc/confluent"
      version = "~> 2.38"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

# Confluent Provider Configuration
provider "confluent" {
  cloud_api_key    = var.confluent_cloud_api_key
  cloud_api_secret = var.confluent_cloud_api_secret
}

# Random Provider Configuration
provider "random" {}

# Note: No Azure provider in workshop mode!
# Workshop mode uses pre-provided Azure OpenAI credentials
# and does not create any Azure resources.
