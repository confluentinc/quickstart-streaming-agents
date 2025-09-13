terraform {
  required_version = ">= 1.0"
  required_providers {
    confluent = {
      source = "confluentinc/confluent"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
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
provider "aws" {
  region = var.cloud_region
}

# Azure Provider Configuration
provider "azurerm" {
  features {}
}
