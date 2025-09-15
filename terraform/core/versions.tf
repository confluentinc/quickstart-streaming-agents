terraform {
  required_version = ">= 1.0"
  required_providers {
    confluent = {
      source = "confluentinc/confluent"
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

# AWS Provider Configuration (conditional)
provider "aws" {
  region = lower(var.cloud_provider) == "aws" ? var.cloud_region : "us-east-1"
  skip_region_validation = lower(var.cloud_provider) != "aws"
  skip_credentials_validation = lower(var.cloud_provider) != "aws"
  skip_requesting_account_id = lower(var.cloud_provider) != "aws"
}

# Azure Provider Configuration (conditional)
provider "azurerm" {
  features {}
  subscription_id = lower(var.cloud_provider) == "azure" ? var.azure_subscription_id : null
}