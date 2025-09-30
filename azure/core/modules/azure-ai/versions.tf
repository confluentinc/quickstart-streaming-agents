terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 4.0"
    }
    confluent = {
      source  = "confluentinc/confluent"
      version = ">= 2.38"
    }
    local = {
      source  = "hashicorp/local"
      version = ">= 2.0"
    }
  }
}
