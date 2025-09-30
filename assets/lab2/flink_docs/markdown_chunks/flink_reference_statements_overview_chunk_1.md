---
document_id: flink_reference_statements_overview_chunk_1
source_file: flink_reference_statements_overview.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/overview.html
title: SQL Statements in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# DDL Statements in Confluent Cloud for Apache Flink¶

In Confluent Cloud for Apache Flink®, a [statement](../../concepts/statements.html#flink-sql-statements) is a high-level resource that’s created when you enter a SQL query.

Data Definition Language (DDL) statements are imperative verbs that define metadata in Flink SQL by adding, changing, or deleting tables.

Unlike Data Manipulation Language (DML) statements, DDL statements modify only metadata and don’t change data. When you want to change data, use [DML statements](../queries/overview.html#flink-sql-queries).

For valid lexical structure of statements, see [Flink SQL Syntax in Confluent Cloud for Apache Flink](../sql-syntax.html#flink-sql-syntax).

## Available DDL statements¶

These are the available DDL statements in Confluent Cloud for Flink SQL.

ALTER

  * [ALTER TABLE](alter-table.html#flink-sql-alter-table): Change properties of an existing table.
  * [ALTER MODEL](alter-model.html#flink-sql-alter-model): Rename an [AI model](../../../ai/overview.html#ai-overview) or change model options.

CREATE

  * [CREATE TABLE](create-table.html#flink-sql-create-table): Register a table into the current or specified catalog (Confluent Cloud environment).
  * [CREATE FUNCTION](create-function.html#flink-sql-create-function): Register a user-defined function (UDF) in the current database (Apache Kafka® cluster).
  * [CREATE MODEL](create-model.html#flink-sql-create-model): Create a new AI model.

DESCRIBE

  * [DESCRIBE](describe.html#flink-sql-describe): Show properties of a table, AI model, or UDF.

DROP

  * [DROP MODEL](drop-model.html#flink-sql-drop-model): Remove an AI model.
  * [DROP TABLE](drop-table.html#flink-sql-drop-table): Remove a table.
  * [DROP VIEW](drop-view.html#flink-sql-drop-view): Remove a view from a catalog.

EXPLAIN

  * [EXPLAIN](explain.html#flink-sql-explain): View the query plan of a Flink SQL statement.

RESET

  * [RESET](reset.html#flink-sql-reset-statement): Reset the Flink SQL shell configuration to default settings.

SET

  * [SET](set.html#flink-sql-set-statement): Modify or list the Flink SQL shell configuration.

SHOW

  * [SHOW CATALOGS](show.html#flink-sql-show-catalogs): List all catalogs.
  * [SHOW CREATE MODEL](show.html#flink-sql-show-create-model): Show details about an AI inference model.
  * [SHOW CREATE TABLE](show.html#flink-sql-show-create-table): Show details about a table.
  * [SHOW CURRENT CATALOG](show.html#flink-sql-show-current-catalog): Show the current catalog.
  * [SHOW CURRENT DATABASE](show.html#flink-sql-show-current-database): Show the current database.
  * [SHOW DATABASES](show.html#flink-sql-show-databases): List all databases in the current catalog.
  * [SHOW FUNCTIONS](show.html#flink-sql-show-functions): List all functions in the current catalog and database.
  * [SHOW JOBS](show.html#flink-sql-show-jobs): List the status of all statements in the current catalog.
  * [SHOW MODELS](show.html#flink-sql-show-models): List all AI models that are registered in the current catalog.
  * [SHOW TABLES](show.html#flink-sql-show-tables): List all tables for the current database.

USE

  * [USE CATALOG](use-catalog.html#flink-sql-use-catalog-statement): Set the current catalog.
  * [USE [database_name]](use-database.html#flink-sql-use-database-statement): Set the current database.
