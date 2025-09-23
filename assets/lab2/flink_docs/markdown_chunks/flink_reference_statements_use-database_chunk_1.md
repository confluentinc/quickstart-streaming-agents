---
document_id: flink_reference_statements_use-database_chunk_1
source_file: flink_reference_statements_use-database.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/use-database.html
title: SQL USE database_name Statement in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# USE <database_name> Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables setting the current Apache Kafka® cluster with the `USE <database_name>` statement.

## Syntax¶

    USE database_name;

## Description¶

Set the current database (Kafka cluster). The `USE <database_name>` statement enables you to access tables in various databases without specifying the full paths.

In Confluent Cloud, Apache Flink® databases are equivalent to Kafka clusters. All Kafka clusters in the region where Flink is running are registered automatically as databases and can be accessed by Flink, when using the correct catalog/environment.

All subsequent commands that don’t specify a database use `<database_name>`.

If `<database_name>` doesn’t exist, Flink throws an exception on the next DML or DDL statement.

Important

`USE <database_name>` is a client-side setting statement and sets corresponding properties that are attached to future requests.

By itself, a `USE <database_name>` statement is a no-op. To see its effect, you must follow it with one or more DML or DDL statements, for example:

    -- Set the current catalog (environment).
    USE CATALOG my_env;

    -- Set the current database (Kafka cluster).
    USE cluster_0;

    -- Submit a DDL statement.
    SELECT * FROM my_table;

Run the [USE CATALOG statement](use-catalog.html#flink-sql-use-catalog-statement) to set the current Flink catalog (Confluent Cloud environment).

## USE database_name in Cloud Console workspaces¶

When you run the `USE <database_name>` statement in a Cloud Console workspace, it sets the database that will be used in any subsequent CREATE statement requests for the specific editor cell. Different cells can use different databases within the same workspace.

The `<database_name>` parameter is unquoted, for example, `USE database1;`.

Any USE statements within an editor cell take precedence over the settings in the workspace’s global **catalog** and **database** dropdown controls.

## Example¶

In the Flink SQL shell, run the following commands to see an example of the `USE <database_name>` statement.

  1. View the existing databases.

         SHOW DATABASES;

Your output should resemble:

         +---------------+-------------+
         | database name | database id |
         +---------------+-------------+
         | cluster_0     | lkc-a123c4  |
         +---------------+-------------+

  2. Set the current database to `cluster_0`.

         USE cluster_0;

Your output should resemble:

         +----------------------+-----------+
         |         Key          |   Value   |
         +----------------------+-----------+
         | sql.current-database | cluster_0 |
         +----------------------+-----------+

  3. Run the SHOW CURRENT DATABASE to check the database change.

         SHOW CURRENT DATABASE;

Your output should resemble:

         +-----------------------+
         | current database name |
         +-----------------------+
         | cluster_0             |
         +-----------------------+
