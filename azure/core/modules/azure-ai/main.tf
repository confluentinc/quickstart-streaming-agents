resource "azurerm_resource_group" "openai_rg" {
  name     = "rg-openai-${var.random_id}"
  location = var.cloud_region
}

resource "azurerm_cognitive_account" "openai_account" {
  name                          = "openai-${var.random_id}"
  location                      = azurerm_resource_group.openai_rg.location
  resource_group_name           = azurerm_resource_group.openai_rg.name
  kind                          = "OpenAI"
  sku_name                      = "S0"
  public_network_access_enabled = true
  custom_subdomain_name         = "openai-${var.random_id}"
}

resource "azurerm_cognitive_deployment" "openai_deployment" {
  name                 = "gpt4-deployment-${var.random_id}"
  cognitive_account_id = azurerm_cognitive_account.openai_account.id

  model {
    format  = "OpenAI"
    name    = "gpt-4o"
    version = "2024-08-06"
  }

  sku {
    name     = "GlobalStandard"
    capacity = 50
  }
}

resource "azurerm_cognitive_deployment" "embedding_deployment" {
  name                 = "embedding-deployment-${var.random_id}"
  cognitive_account_id = azurerm_cognitive_account.openai_account.id

  model {
    format  = "OpenAI"
    name    = "text-embedding-ada-002"
    version = "2"
  }

  sku {
    name     = "Standard"
    capacity = 120
  }
}

resource "confluent_flink_connection" "azure_connection" {
  organization {
    id = var.confluent_organization_id
  }
  environment {
    id = var.confluent_environment_id
  }
  compute_pool {
    id = var.confluent_compute_pool_id
  }
  principal {
    id = var.confluent_service_account_id
  }
  rest_endpoint = var.confluent_flink_rest_endpoint
  credentials {
    key    = var.confluent_flink_api_key_id
    secret = var.confluent_flink_api_key_secret
  }

  display_name = "llm-textgen-connection"
  type         = "AZUREOPENAI"
  endpoint     = "${azurerm_cognitive_account.openai_account.endpoint}openai/deployments/${azurerm_cognitive_deployment.openai_deployment.name}/chat/completions?api-version=2025-01-01-preview"
  api_key      = azurerm_cognitive_account.openai_account.primary_access_key

  # lifecycle {
  #   prevent_destroy = true
  # }
}

resource "confluent_flink_connection" "azure_embedding_connection" {
  organization {
    id = var.confluent_organization_id
  }
  environment {
    id = var.confluent_environment_id
  }
  compute_pool {
    id = var.confluent_compute_pool_id
  }
  principal {
    id = var.confluent_service_account_id
  }
  rest_endpoint = var.confluent_flink_rest_endpoint
  credentials {
    key    = var.confluent_flink_api_key_id
    secret = var.confluent_flink_api_key_secret
  }

  display_name = "llm-embedding-connection"
  type         = "AZUREOPENAI"
  endpoint     = "${azurerm_cognitive_account.openai_account.endpoint}openai/deployments/${azurerm_cognitive_deployment.embedding_deployment.name}/embeddings?api-version=2023-05-15"
  api_key      = azurerm_cognitive_account.openai_account.primary_access_key

  # lifecycle {
  #   prevent_destroy = true
  # }
}
