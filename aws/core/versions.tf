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
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.12"
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

# AWS Provider Configuration
# In workshop mode: AWS provider is declared but not used (module count = 0)
# In production mode: AWS provider is used to create IAM resources
provider "aws" {
  region = var.cloud_region

  # In workshop mode, skip credential checks since we don't need AWS access
  # The provider won't be used anyway (aws_ai_services module has count = 0)
  skip_credentials_validation = var.workshop_mode
  skip_metadata_api_check     = var.workshop_mode
  skip_requesting_account_id  = var.workshop_mode

  # Provide dummy credentials in workshop mode to prevent provider initialization errors
  # These are never actually used since the module won't be created
  access_key = var.workshop_mode ? "dummy" : null
  secret_key = var.workshop_mode ? "dummy" : null
}
