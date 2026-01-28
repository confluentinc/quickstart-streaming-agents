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
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.44"
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

# Azure Provider Configuration
# Note: In workshop mode, subscription_id is a placeholder since no Azure resources are created
# In workshop mode, dummy ARM_* environment variables are provided by deploy.py to allow
# participants without Azure access to run Terraform (no actual Azure API calls are made)
provider "azurerm" {
  features {}
  subscription_id                 = var.azure_subscription_id
  resource_provider_registrations = "none"
  use_cli                         = false
  use_msi                         = false
  use_oidc                        = false
}
