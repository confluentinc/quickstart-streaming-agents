---
document_id: flink_reference_statements_create-function_chunk_1
source_file: flink_reference_statements_create-function.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-function.html
title: Flink SQL CREATE TABLE Statement in Confluent Cloud
chunk_index: 1
total_chunks: 1
---

# CREATE FUNCTION Statement¶

Confluent Cloud for Apache Flink® enables registering customer user defined functions (UDFs) by using the CREATE FUNCTION statement. When your UDFs are registered in a Flink database, you can use it in your SQL queries.

## Syntax¶

    CREATE FUNCTION <function-name>
      AS <class-name>
      USING JAR 'confluent-artifact://<plugin-id>/<version-id>';

## Description¶

Register a user defined function (UDF) in the current database.

To remove a (UDF) from the current database, use the DROP FUNCTION statement.
