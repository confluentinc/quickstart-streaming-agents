---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/connection/confluent_flink_connection_update.html
title: confluent flink connection update
hierarchy: ['confluent-cli', 'command-reference', 'connection', 'confluent_flink_connection_update.html']
scraped_date: 2025-09-05T13:49:55.553658
---

# confluent flink connection update¶

## Description¶

Update a Flink connection. Only secret can be updated.

    confluent flink connection update <name> [flags]

## Flags¶

        --cloud string               REQUIRED: Specify the cloud provider as "aws", "azure", or "gcp".
        --region string              REQUIRED: Cloud region for Flink (use "confluent flink region list" to see all).
        --api-key string             Specify API key for the type: "openai", "azureml", "azureopenai", "googleai", "elastic", "pinecone", or "mcp_server".
        --aws-access-key string      Specify access key for the type: "bedrock" or "sagemaker".
        --aws-secret-key string      Specify secret key for the type: "bedrock" or "sagemaker".
        --aws-session-token string   Specify session token for the type: "bedrock" or "sagemaker".
        --service-key string         Specify service key for the type: "vertexai".
        --username string            Specify username for the type: "mongodb", "couchbase", "confluent_jdbc", or "rest".
        --password string            Specify password for the type: "mongodb", "couchbase", "confluent_jdbc", or "rest".
        --token string               Specify bearer token for the type: "rest" or "mcp_server".
        --token-endpoint string      Specify OAuth2 token endpoint for the type: "rest" or "mcp_server".
        --client-id string           Specify OAuth2 client ID for the type: "rest" or "mcp_server".
        --client-secret string       Specify OAuth2 client secret for the type: "rest" or "mcp_server".
        --scope string               Specify OAuth2 scope for the type: "rest" or "mcp_server".
        --sse-endpoint string        Specify SSE endpoint for the type: "mcp_server".
        --environment string         Environment ID.
    -o, --output string              Specify the output format as "human", "json", or "yaml". (default "human")

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## Examples¶

Update API key of Flink connection “my-connection”.

    confluent flink connection update my-connection --cloud aws --region us-west-2 --api-key new-key

## See Also¶

  * [confluent flink connection](index.html#confluent-flink-connection) \- Manage Flink connections.
