---
document_id: flink_reference_statements_create-connection_chunk_1
source_file: flink_reference_statements_create-connection.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-connection.html
title: SQL CREATE CONNECTION Statement in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 2
---

# CREATE CONNECTION Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® supports creating secure connections to external services and data sources. You can use these connections in your Flink statements.

Connections are resources that you define to configure parameters needed for connecting to third-party services. Connections include endpoint and authentication information. They provide a way to handle sensitive information such as credentials while ensuring security.

Connections are essential for secure communications in [Confluent AI](../../../ai/overview.html#ai-overview) and [Flink UDFs](../../concepts/user-defined-functions.html#flink-sql-udfs) to make secure calls to external services. For more information, see [Reuse Confluent Cloud Connections With External Services](../../../integrations/connections/overview.html#connections-overview).

A connection has its own lifecycle and can be created, managed, updated, or deleted by users with appropriate permissions. For more information, see [Manage Connections](../../operate-and-deploy/manage-connections.html#flink-sql-manage-connections).

Confluent Cloud for Apache Flink makes a best-effort attempt to redact sensitive values from the CREATE CONNECTION and ALTER CONNECTION statements by masking the values for the known sensitive keys. In Confluent Cloud Console, the sensitive values are redacted in the Flink SQL workspace if you navigate away from the workspace and return, or if you reload the page in the browser. Alternatively, you can use the Confluent CLI commands to create and manage connections.

In addition, if syntax in the CREATE CONNECTION statement is incorrect, Confluent Cloud for Apache Flink may not detect the secrets. For example, if you type `CREATE CONNECTION my_conn WITH ('ap-key' = 'x')`, Flink won’t redact the `x`, because `api-key` is misspelled.

Note

Connection resources are an Open Preview feature in Confluent Cloud.

A Preview feature is a Confluent Cloud component that is being introduced to gain early feedback from developers. Preview features can be used for evaluation and non-production testing purposes or to provide feedback to Confluent. The warranty, SLA, and Support Services provisions of your agreement with Confluent do not apply to Preview features. Confluent may discontinue providing preview releases of the Preview features at any time in Confluent’s’ sole discretion.

## Syntax¶

    CREATE [OR REPLACE] CONNECTION [IF NOT EXISTS] [catalog_name.][db_name.]connection_name
    [COMMENT connection_comment]
    WITH (
        'type' = '<connection-type>',
        'endpoint' = '<endpoint-url>',
        ['sse-endpoint' = '<sse-endpoint-url>'],
        ['api-key' = 'api_key'] |
        ['username' = 'user_name', 'password' = 'user_password'] |
        ['aws-access-key' = '<aws-access-key-id>', 'aws-secret-key' = '<aws-secret-access-key>', 'aws-session-token' = '<aws-session-token>'] |
    );

## Description¶

Create a new secure connection to an external service or data source.

Change the authorization settings of an existing connection by using the [ALTER CONNECTION](alter-connection.html#flink-sql-alter-connection) statement.

To remove a connection from the current database, use the [DROP CONNECTION](drop-connection.html#flink-sql-drop-connection) statement.

Confluent Cloud for Apache Flink supports these authentication methods:

  * **Basic:** `username` and `password`. The credentials are added to the HTTP request as a BASIC header.
  * **Bearer:** `token`. The credentials are added to the HTTP request as a BEARER header.
  * **OAuth:** `token-endpoint`, `client-id`, `client-secret`, and `scope`. The provided options are used to retrieve the OAuth token from the token endpoint and add the token to the HTTP request as a BEARER token.

### Connection types¶

The following connection types are supported:

  * azureml
  * azureopenai
  * bedrock
  * confluent_jdbc
  * couchbase
  * elastic
  * googleai
  * mcp_server
  * mongodb
  * openai
  * pinecone
  * rest
  * sagemaker
  * vertexai

### Authorization¶

Depending on the connection type, the following authorization methods are supported:

  * **API key:** azureml, azureopenai, elastic, googleai, mcp_server, openai, pinecone
  * **basic:** mongodb, couchbase, confluent_jdbc, or rest
  * **bearer:** rest or mcp_server connections
  * **oauth:** rest or mcp_server connections

Secrets are extracted to the secret store and aren’t displayed in subsequent [DESCRIBE CONNECTION](describe.html#flink-sql-describe) statements, the Flink SQL shell, or the Confluent Cloud Console.

The maximum secret length is 4000 bytes, which is checked after the string is converted to bytes.
