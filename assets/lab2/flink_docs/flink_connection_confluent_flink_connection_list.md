---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/connection/confluent_flink_connection_list.html
title: confluent flink connection list
hierarchy: ['confluent-cli', 'command-reference', 'connection', 'confluent_flink_connection_list.html']
scraped_date: 2025-09-05T13:49:51.311119
---

# confluent flink connection list¶

## Description¶

List Flink connections.

    confluent flink connection list [flags]

## Flags¶

        --cloud string         REQUIRED: Specify the cloud provider as "aws", "azure", or "gcp".
        --region string        REQUIRED: Cloud region for Flink (use "confluent flink region list" to see all).
        --environment string   Environment ID.
        --type string          Specify the connection type as "openai", "azureml", "azureopenai", "bedrock", "sagemaker", "googleai", "vertexai", "mongodb", "elastic", "pinecone", "couchbase", "confluent_jdbc", "rest", or "mcp_server".
    -o, --output string        Specify the output format as "human", "json", or "yaml". (default "human")

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## See Also¶

  * [confluent flink connection](index.html#confluent-flink-connection) \- Manage Flink connections.
