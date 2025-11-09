---
document_id: flink_concepts_statements_chunk_3
source_file: flink_concepts_statements.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/statements.html
title: Flink SQL Statements in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 3
---

sources are bounded or unbounded.

## Data lifecycle¶

Broadly speaking, the Flink SQL lifecycle is:

  * Data is read into a Flink table from Kafka via the Flink connector for Kafka.

  * Data is processed using SQL statements.

  * Data is processed using Flink task managers (managed by Confluent and not exposed to users), which are part of the Flink runtime. Some data may be stored temporarily as state in Flink while it’s being processed

  * Data is returned to the user as a result-set.

    * The result-set may be bounded, in which case the query terminates.
    * The result-set may be unbounded, in which case the query runs until canceled manually.

OR

  * Data is written back out to one or more tables.

    * Data is stored in Kafka topics.
    * Schema for the table is stored in Flink Metastore and synchronized out to Schema Registry.

## Flink SQL Data Definition Language (DDL) statements¶

Data Definition Language (DDL) statements are imperative verbs that define metadata in Flink SQL by adding, changing, or deleting tables. Data Definition Language statements modify metadata only and don’t operate on data. Use these statements with declarative [Flink SQL Queries](../reference/queries/overview.html#flink-sql-queries) to create your Flink SQL applications.

Flink SQL makes it simple to develop streaming applications using standard SQL. It’s easy to learn Flink SQL if you’ve ever worked with a database or SQL-like system that’s ANSI-SQL 2011 compliant.

## Available DDL statements¶

These are the available DDL statements in Confluent Cloud for Flink SQL.

ALTER

  * [ALTER MODEL Statement in Confluent Cloud for Apache Flink](../reference/statements/alter-model.html#flink-sql-alter-model)
  * [ALTER TABLE Statement in Confluent Cloud for Apache Flink](../reference/statements/alter-table.html#flink-sql-alter-table)
  * [ALTER VIEW Statement in Confluent Cloud for Apache Flink](../reference/statements/alter-view.html#flink-sql-alter-view)

CREATE

  * [CREATE FUNCTION Statement](../reference/statements/create-function.html#flink-sql-create-function)
  * [CREATE MODEL Statement in Confluent Cloud for Apache Flink](../reference/statements/create-model.html#flink-sql-create-model)
  * [CREATE TABLE Statement in Confluent Cloud for Apache Flink](../reference/statements/create-table.html#flink-sql-create-table)
  * [CREATE VIEW Statement in Confluent Cloud for Apache Flink](../reference/statements/create-view.html#flink-sql-create-view)

DESCRIBE

  * [DESCRIBE Statement in Confluent Cloud for Apache Flink](../reference/statements/describe.html#flink-sql-describe)

DROP

  * [DROP MODEL Statement in Confluent Cloud for Apache Flink](../reference/statements/drop-model.html#flink-sql-drop-model)
  * [DROP TABLE Statement in Confluent Cloud for Apache Flink](../reference/statements/drop-table.html#flink-sql-drop-table)
  * [DROP VIEW Statement in Confluent Cloud for Apache Flink](../reference/statements/drop-view.html#flink-sql-drop-view)

EXPLAIN

  * [EXPLAIN Statement in Confluent Cloud for Apache Flink](../reference/statements/explain.html#flink-sql-explain)

RESET

  * [RESET Statement in Confluent Cloud for Apache Flink](../reference/statements/reset.html#flink-sql-reset-statement)

SET

  * [SET Statement in Confluent Cloud for Apache Flink](../reference/statements/set.html#flink-sql-set-statement)

SHOW

  * [SHOW Statements in Confluent Cloud for Apache Flink](../reference/statements/show.html#flink-sql-show)

USE

  * [USE CATALOG Statement in Confluent Cloud for Apache Flink](../reference/statements/use-catalog.html#flink-sql-use-catalog-statement)
  * [USE <database_name> Statement in Confluent Cloud for Apache Flink](../reference/statements/use-database.html#flink-sql-use-database-statement)
