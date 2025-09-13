locals {
  ZAPIER_ENDPOINT = substr(var.ZAPIER_SSE_ENDPOINT, 0, length(var.ZAPIER_SSE_ENDPOINT) - 4)

  aws_sql = <<EOT
### AWS Bedrock Models

-- Model 1: For Tool Calling with Zapier
CREATE MODEL `zapier_mcp_model`
INPUT (prompt STRING)
OUTPUT (response STRING)
WITH (
  'provider' = 'bedrock',
  'task' = 'text_generation',
  'bedrock.connection' = '${module.aws_ai[0].flink_connection_name}',
  'bedrock.params.max_tokens' = '20000',
  'mcp.connection' = 'zapier-mcp-connection'
);

-- Model 2: For Text Generation
CREATE MODEL `llm_textgen_model`
INPUT (prompt STRING)
OUTPUT (response STRING)
WITH(
   'provider' = 'bedrock',
   'task' = 'text_generation',
   'bedrock.connection' = '${module.aws_ai[0].flink_connection_name}',
   'bedrock.params.max_tokens' = '20000'
);
EOT

  azure_sql = <<EOT
### Azure OpenAI Models

-- Model 1: For Tool Calling with Zapier
CREATE MODEL `zapier_mcp_model`
INPUT (prompt STRING)
OUTPUT (response STRING)
WITH (
  'provider' = 'azureopenai',
  'task' = 'text_generation',
  'azureopenai.connection' = '${module.azure_ai[0].flink_connection_name}',
  'mcp.connection' = 'zapier-mcp-connection'
);

-- Model 2: For Text Generation
CREATE MODEL `llm_textgen_model`
INPUT (prompt STRING)
OUTPUT (response STRING)
WITH(
   'provider' = 'azureopenai',
   'task' = 'text_generation',
   'azureopenai.connection' = '${module.azure_ai[0].flink_connection_name}',
   'azureopenai.model_version' = '2025-04-14'
);
EOT
}

resource "local_file" "mcp_commands" {
  filename = "${path.module}/mcp_commands.md"
  content  = <<EOT
# Flink Commands for Lab 1

This file contains the commands and SQL statements needed to complete Lab 1.

## 1. Create Flink MCP Connection

Run the following command to create the Flink connection to your Zapier MCP server.

```bash
confluent flink connection create zapier-mcp-connection \
  --cloud ${var.cloud_provider} \
  --region ${var.cloud_region} \
  --type mcp_server \
  --endpoint ${local.ZAPIER_ENDPOINT} \
  --api-key api_key \
  --environment ${module.core.confluent_environment_id} \
  --sse-endpoint ${var.ZAPIER_SSE_ENDPOINT}
```

## 2. Create Flink Models

Run the following SQL statements in your Flink SQL Workspace to create the AI models.

---

${var.cloud_provider == "AWS" ? local.aws_sql : local.azure_sql}

---
EOT
}

output "resource-ids" {
  value = <<EOT
  Environment ID:   ${module.core.confluent_environment_id}
  Kafka Cluster ID: ${module.core.confluent_kafka_cluster_id}
  Flink Compute pool ID: ${module.core.confluent_flink_compute_pool_id}

  Service Accounts and their Kafka API Keys (API Keys inherit the permissions granted to the owner):
  ${module.core.app_manager_service_account_id}:                     ${module.core.app_manager_service_account_id}
  ${module.core.app_manager_service_account_id}'s Kafka API Key:     "${module.core.app_manager_kafka_api_key}"
  ${module.core.app_manager_service_account_id}'s Kafka API Secret:  "${module.core.app_manager_kafka_api_secret}"


  Service Accounts and their Flink management API Keys (API Keys inherit the permissions granted to the owner):
  ${module.core.app_manager_service_account_id}:                     ${module.core.app_manager_service_account_id}
  ${module.core.app_manager_service_account_id}'s Flink management API Key:     "${module.core.app_manager_flink_api_key}"
  ${module.core.app_manager_service_account_id}'s Flink management API Secret:  "${module.core.app_manager_flink_api_secret}"


  sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="${module.core.app_manager_kafka_api_key}" password="${module.core.app_manager_kafka_api_secret}";
  bootstrap.servers=${module.core.confluent_kafka_bootstrap_endpoint}
  schema.registry.url= ${module.core.confluent_schema_registry_endpoint}
  schema.registry.basic.auth.user.info= "${module.core.app_manager_schema_registry_api_key}:${module.core.app_manager_schema_registry_api_secret}"


EOT

  sensitive = true
}