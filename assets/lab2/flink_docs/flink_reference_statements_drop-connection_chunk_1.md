---
document_id: flink_reference_statements_drop-connection_chunk_1
source_file: flink_reference_statements_drop-connection.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/drop-connection.html
title: SQL DROP CONNECTION Statement in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# DROP CONNECTION Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® supports creating secure connections to external services and data sources. You can use these connections in your Flink statements. You remove these connections by using the DROP CONNECTION statement.

## Syntax¶

    DROP CONNECTION [IF EXISTS] [catalog_name.][db_name.]connection_name

## Description¶

Delete a connection from the Flink environment.

Dropping a connection deletes the corresponding credentials stored in the `SecretStore`.

## Example¶

    DROP CONNECTION `azure-openai-connection`;
