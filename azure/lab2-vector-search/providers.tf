terraform {
  required_version = ">= 1.0"
  required_providers {
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.44"
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
# Authentication options (choose one):
# 1. Azure CLI: Run 'az login' then 'az account set --subscription <subscription-id>' (recommended)
# 2. Environment variables: Set ARM_SUBSCRIPTION_ID, ARM_CLIENT_ID, ARM_CLIENT_SECRET, ARM_TENANT_ID
# 3. Managed Identity: If running on Azure resources
# 4. Service Principal: Configure with appropriate permissions
provider "azurerm" {
  features {}
  subscription_id = data.terraform_remote_state.core.outputs.azure_subscription_id
}

# Confluent Provider Configuration
provider "confluent" {
  cloud_api_key    = data.terraform_remote_state.core.outputs.confluent_cloud_api_key
  cloud_api_secret = data.terraform_remote_state.core.outputs.confluent_cloud_api_secret
}

# Local Provider Configuration
provider "local" {}
