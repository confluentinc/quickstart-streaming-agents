---
document_id: flink_reference_statements_use-catalog_chunk_1
source_file: flink_reference_statements_use-catalog.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/use-catalog.html
title: SQL USE CATALOG Statement in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# USE CATALOG Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables setting the active environment with the SQL USE statement.

## Syntax¶

    USE CATALOG catalog_name;

## Description¶

Set the current catalog (Confluent Cloud environment). All subsequent commands that don’t specify a catalog use `catalog_name`.

Confluent Cloud for Apache Flink interprets your Confluent Cloud environments as catalogs. Flink can access various databases (Apache Kafka® clusters) in a catalog.

The `catalog_name` parameter is case-sensitive.

The default current catalog is named `default`.

If `catalog_name` doesn’t exist, Flink throws an exception on the next DML or DDL statement.

Important

USE CATALOG is a client-side setting statement and sets corresponding properties that are attached to future requests.

By itself, a USE CATALOG statement is a no-op. To see its effect, you must follow it with one or more DML or DDL statements, for example:

    -- Set the current catalog (environment).
    USE CATALOG my_env;

    -- Set the current database (Kafka cluster).
    USE cluster_0;

    -- Submit a DDL statement.
    SELECT * FROM my_table;

Use the [USE DATABASE statement](use-database.html#flink-sql-use-database-statement) to set the current Flink database (Kafka cluster).

## USE CATALOG in Cloud Console workspaces¶

When you run the USE CATALOG statement in a Cloud Console workspace, it sets the catalog that will be used in any subsequent CREATE statement requests for the specific editor cell. Different cells can use different catalogs within the same workspace.

The catalog parameter is unquoted, for example, `USE CATALOG catalog1;`.

Any USE statements within an editor cell take precedence over the settings in the workspace’s global **catalog** and **database** dropdown controls.
