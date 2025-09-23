---
document_id: flink_reference_statements_drop-table_chunk_1
source_file: flink_reference_statements_drop-table.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/drop-table.html
title: SQL DROP TABLE Statement in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# DROP TABLE Statement in Confluent Cloud for Apache Flink¶

The DROP TABLE statement removes a table definition from Confluent Cloud for Apache Flink® and, depending on the table type, will also delete associated resources like the Kafka topic and schemas in Schema Registry.

## Syntax¶

    DROP TABLE [IF EXISTS] table_name

## Parameters¶

`IF EXISTS`
    Optional clause that prevents an error if the table does not exist.
`table_name`
    The name of the table to drop.

## Description¶

The DROP TABLE statement behavior varies depending on the table type.

### Regular Tables¶

For tables backed by Kafka topics, which are created by using CREATE TABLE or inferred from existing topics:

* Deletes the underlying Kafka topic permanently
* When using TopicNameStrategy (default): \- Deletes all versions of the associated schemas from Schema Registry
* When using RecordNameStrategy or TopicRecordNameStrategy: \- Deletes the Kafka topic but preserves schemas in Schema Registry

### External Tables¶

Note

External tables are an Open Preview feature in Confluent Cloud.

A Preview feature is a Confluent Cloud component that is being introduced to gain early feedback from developers. Preview features can be used for evaluation and non-production testing purposes or to provide feedback to Confluent. The warranty, SLA, and Support Services provisions of your agreement with Confluent do not apply to Preview features. Confluent may discontinue providing preview releases of the Preview features at any time in Confluent’s’ sole discretion.

Confluent Cloud for Apache Flink enables [vector search](../../../ai/external-tables/vector-search.html#flink-sql-vector-search) with external tables. Use the [CREATE TABLE](create-table.html#flink-sql-create-table) statement to register an external table.

For external tables, like vector databases and lookup tables:

* Removes the table definition from Flink metadata
* Does not delete data from the external system
* Examples include vector search tables and federated search tables

## Permissions¶

To execute DROP TABLE, you need an [RBAC role](../../../security/access-control/rbac/predefined-rbac-roles.html#cloud-rbac-roles) that enables you to delete the Kafka topics and Schema Registry schema subjects.

## Important considerations¶

* The DROP TABLE operation is not atomic. If either the Kafka topic deletion or schema deletion fails, the operation may partially complete.
* Dropping a table permanently deletes the Kafka topic data.
* Running statements that depend on a dropped table will transition to DEGRADED status.
* You should stop dependent statements before dropping a table.
* When using TopicNameStrategy, dropping a table deletes schemas, even if they are used by other topics.

## Examples¶

    -- Drop a Kafka-backed table.
    DROP TABLE my_table;

    -- Drop a table if it exists.
    DROP TABLE IF EXISTS my_table;

    -- Drop an external table.
    DROP TABLE `<external-table-name>`;
