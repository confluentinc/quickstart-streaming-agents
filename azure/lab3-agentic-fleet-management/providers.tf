terraform {
  required_version = ">= 1.0"
  required_providers {
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
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

# Azure Provider Configuration
# In workshop mode, dummy ARM_* environment variables are provided by deploy.py to allow
# participants without Azure access to run Terraform (no actual Azure API calls are made)
provider "azurerm" {
  features {}
  subscription_id                 = data.terraform_remote_state.core.outputs.azure_subscription_id
  resource_provider_registrations = "none"
  use_cli                         = false
  use_msi                         = false
  use_oidc                        = false
}

# Confluent Provider Configuration (for module use)
provider "confluent" {
  cloud_api_key    = data.terraform_remote_state.core.outputs.confluent_cloud_api_key
  cloud_api_secret = data.terraform_remote_state.core.outputs.confluent_cloud_api_secret
}

# Local Provider Configuration
provider "local" {}
