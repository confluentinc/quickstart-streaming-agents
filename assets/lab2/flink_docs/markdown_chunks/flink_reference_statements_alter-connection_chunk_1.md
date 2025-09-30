---
document_id: flink_reference_statements_alter-connection_chunk_1
source_file: flink_reference_statements_alter-connection.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/alter-connection.html
title: SQL ALTER CONNECTION Statement in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# ALTER CONNECTION Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® supports creating secure connections to external services and data sources. You can use these connections in your Flink statements. Use the ALTER CONNECTION statement to change the API key or credentials of an existing connection.

## Syntax¶

    ALTER CONNECTION [IF EXISTS] [catalog_name.][db_name.]connection_name
    SET (key1=val1[, key2=val2]...)

## Description¶

Change the API key or credentials of a connection.

Secrets are extracted to the secret store and aren’t displayed in subsequent [DESCRIBE CONNECTION](describe.html#flink-sql-describe) statements, the Flink SQL shell, or the Confluent Cloud Console.

Confluent Cloud for Apache Flink makes a best-effort attempt to redact sensitive values from the CREATE CONNECTION and ALTER CONNECTION statements by masking the values for the known sensitive keys. In Confluent Cloud Console, the sensitive values are redacted in the Flink SQL workspace if you navigate away from the workspace and return, or if you reload the page in the browser. Alternatively, you can use the Confluent CLI commands to create and manage connections.

In addition, if syntax in the CREATE CONNECTION statement is incorrect, Confluent Cloud for Apache Flink may not detect the secrets. For example, if you type `CREATE CONNECTION my_conn WITH ('ap-key' = 'x')`, Flink won’t redact the `x`, because `api-key` is misspelled.

## Examples¶

    -- Update the API key for a connection.
    ALTER CONNECTION `conn-one` SET ('api-key' = '<new-api-key>');

    -- Update the credentials for a connection.
    ALTER CONNECTION `my-couchbase-conn` SET (
      'username' = '<user-name>',
      'password' = '<new-password>'
    );
