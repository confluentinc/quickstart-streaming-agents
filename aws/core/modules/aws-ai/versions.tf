terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.0"
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
