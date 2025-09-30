terraform {
  required_version = ">= 1.0"
  required_providers {
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.12"
    }
    confluent = {
      source  = "confluentinc/confluent"
      version = "~> 2.38"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

# Random Provider Configuration
provider "random" {}

# AWS Provider Configuration
provider "aws" {
  region = var.cloud_region
}

# Confluent Provider Configuration
provider "confluent" {
  cloud_api_key    = data.terraform_remote_state.core.outputs.confluent_cloud_api_key
  cloud_api_secret = data.terraform_remote_state.core.outputs.confluent_cloud_api_secret
}

# Local Provider Configuration
provider "local" {}
