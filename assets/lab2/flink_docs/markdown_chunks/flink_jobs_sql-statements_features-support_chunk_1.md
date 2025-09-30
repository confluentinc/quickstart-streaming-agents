---
document_id: flink_jobs_sql-statements_features-support_chunk_1
source_file: flink_jobs_sql-statements_features-support.md
source_url: https://docs.confluent.io/platform/current/flink/jobs/sql-statements/features-support.html
title: Features and Support for Statements in Confluent Manager for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Features & Support for Statements in Confluent Manager for Apache Flink¶

This section describes features and limitations of the current version of Flink SQL in Confluent Manager for Apache Flink (CMF).

Important

Flink SQL support in is available as an open preview. A Preview feature is a feature that is being introduced to gain early feedback from developers. Preview features can be used for evaluation and non-production testing purposes or to provide feedback to Confluent. The warranty, SLA, and Support Services provisions of your agreement with Confluent do not apply to Preview features. Confluent may discontinue providing releases of Preview features at any time at Confluent’s’ sole discretion. Comments, questions, and suggestions related to preview features are encouraged and can be submitted to your account representative.

## Supported features¶

CMF provides support for the following Flink SQL features:

Kafka Cluster Integration:
    Kafka clusters can be configured as databases. Each non-compacted topic within a configured Kafka cluster is exposed as an append-only Flink table and can be queried.
Table Schema Derivation:
    Table schemas are derived from the topic’s schema information provided by Schema Registry. All formats supported by Schema Registry (Avro, JSON, Protobuf) are also supported. Topics without schema information are exposed as tables with raw BYTE columns for the topic’s key and value records.
Supported Statement Types:
    Following are the supported statement types: * `LIST TABLES;` * `LIST DATABASES;` * `LIST CATALOGS;` * `SHOW CURRENT DATABASE;` * `SHOW CURRENT CATALOG;` * `DESCRIBE <table>;` * `SELECT ...;` (only append-only results are supported) * `INSERT INTO ...;` (only append-only results are supported)

## Limitations¶

The following limitations exist in the current version:

  * Table Inference: Tables are always exposed using the default inference mechanism. CMF does not support `ALTER TABLE` statements, preventing users from customizing how a topic is exposed as a table.
  * Unsupported Table DDL: `CREATE TABLE`, `CREATE TABLE AS`, and `DROP TABLE` statements are not supported.
  * Compacted Topics: Compacted Kafka topics are not exposed as tables. All tables have append-only semantics.
  * Updating Results: `SELECT` and `INSERT INTO` statements with updating results are not supported.
  * Statement Complexity: Very large statements might not be supported because there is a limit on the size of the query execution plan produced by the optimizer. Since the plan size depends on many factors and the plan is also compressed, it is not possible to give clear guidance for the supported size or complexity of SQL statements. If you run into error messages regarding plan size, try to decompose the complex statement into multiple smaller statements.
  * Views: Views are not supported.
  * EXPLAIN Statements: `EXPLAIN` statements are not supported.
  * Functions: Only Flink SQL built-in functions are supported. User-defined functions are not supported.
  * Custom Formats: Only Schema Registry supported formats are supported. CDC-specific formats or other custom formats are not supported.
  * Custom Connectors: Custom connectors for tables backed by other storage systems are not supported.
  * Custom Catalogs: Custom catalogs are not supported.
  * Deployment modes: Only application-deployment mode is supported. Each statement runs on a dedicated Flink cluster with dedicated JobManager and TaskManager pods. Session-cluster deployment mode is not supported.
