---
document_id: flink_reference_overview_chunk_1
source_file: flink_reference_overview.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/overview.html
title: Flink SQL and Table API Reference in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Flink SQL and Table API Reference in Confluent Cloud for Apache Flink¶

This section describes the SQL language support in Confluent Cloud for Apache Flink®, including [Data Definition Language (DDL) statements](../concepts/statements.html#flink-sql-statements), [Data Manipulation Language (DML) statements](queries/overview.html#flink-sql-queries), [built-in functions](functions/overview.html#flink-sql-functions-overview), and the [Table API](table-api.html#flink-table-api).

Apache Flink® SQL is based on [Apache Calcite](https://calcite.apache.org/), which implements the SQL standard.

## Data Types¶

Flink SQL has a rich set of native data types that you can use in SQL statements and queries.

  * [Data Types](datatypes.html#flink-sql-datatypes)

## Serialize and deserialize data¶

  * [Data Type Mappings](serialization.html#flink-sql-serialization)

## Reserved keywords¶

Some string combinations are reserved as keywords for future use.

  * [Flink SQL Reserved Keywords](keywords.html#flink-sql-keywords)
