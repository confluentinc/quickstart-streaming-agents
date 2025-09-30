---
document_id: flink_reference_statements_describe_chunk_1
source_file: flink_reference_statements_describe.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/describe.html
title: SQL DESCRIBE Statement in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 3
---

# DESCRIBE Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables viewing the schema of an Apache Kafka® topic. Also, you can view details of an AI model, function, or connection.

## Syntax¶

    -- View table details.
    { DESCRIBE | DESC } [EXTENDED] [catalog_name.][db_name.]table_name

    -- View model details.
    { DESCRIBE | DESC } MODEL [[catalogname].[database_name]].model_name

    -- View function details.
    { DESCRIBE | DESC } FUNCTION [EXTENDED] [catalog_name.][db_name.]function_name

    -- View connection details.
    { DESCRIBE | DESC } CONNECTION [catalog_name.][db_name.]connection_name

## Description¶

The DESCRIBE statement shows the following properties of a table:

* Columns and their data type, including nullability constraints
* Primary keys
* Bucket keys, i.e., keys of distribution
* Implicit NOT NULL for primary key columns
* Custom [watermark](../../../_glossary.html#term-watermark)

The DESCRIBE EXTENDED statement shows all of the properties from the DESCRIBE statement and also shows system columns, like `$rowtime`, including the system watermark.

The DESCRIBE MODEL statement shows the following properties of an AI model:

* Input format
* Output format
* Model version
* isDefault version (yes or no)

The DESCRIBE FUNCTION statement shows the following properties of a function:

* System function (yes or no)
* Temporary (yes or no)
* Class name
* Function language
* Plugin ID
* Version ID
* Argument types
* Return type

The DESCRIBE FUNCTION EXTENDED statement shows all of the properties from the DESCRIBE FUNCTION statement and also shows the following properties:

* Kind i.e. SCALAR, TABLE, or AGGREGATE
* Requirements e.g an aggregate function that can only be applied in an OVER window
* Deterministic (yes or no)
* Constant folding (yes or no)
* Signature

The DESCRIBE CONNECTION statement shows the following properties of a connection:

* Name
* Type
* Endpoint
* Comment
