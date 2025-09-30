---
document_id: flink_reference_queries_overview_chunk_1
source_file: flink_reference_queries_overview.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/overview.html
title: SQL Queries in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 3
---

# Flink SQL Queries in Confluent Cloud for Apache Flink¶

In Confluent Cloud for Apache Flink®, Data Manipulation Language (DML) statements, also known as _queries_ , are declarative verbs that read and modify data in Apache Flink® tables.

Unlike Data Definition Language (DDL) statements, DML statements modify only data and don’t change metadata. When you want to change metadata, use [DDL statements](../../concepts/statements.html#flink-sql-statements).

These are the available DML statements in Confluent Cloud for Flink SQL.

[Deduplication Queries in Confluent Cloud for Apache Flink](deduplication.html#flink-sql-deduplication) | [Group Aggregation Queries in Confluent Cloud for Apache Flink](group-aggregation.html#flink-sql-group-aggregation) | [INSERT INTO FROM SELECT Statement in Confluent Cloud for Apache Flink](insert-into-from-select.html#flink-sql-insert-into-from-select-statement) | [INSERT VALUES Statement in Confluent Cloud for Apache Flink](insert-values.html#flink-sql-insert-values-statement)
---|---|---|---
[Interval joins](joins.html#flink-sql-interval-joins) | [LIMIT Clause in Confluent Cloud for Apache Flink](limit.html#flink-sql-limit) | [EXECUTE STATEMENT SET in Confluent Cloud for Apache Flink](statement-set.html#flink-sql-statement-set) | [ORDER BY Clause in Confluent Cloud for Apache Flink](orderby.html#flink-sql-order-by)
[Pattern Recognition Queries in Confluent Cloud for Apache Flink](match_recognize.html#flink-sql-pattern-recognition) | [Regular joins](joins.html#flink-sql-regular-joins) | [SELECT Statement in Confluent Cloud for Apache Flink](select.html#flink-sql-select) | [Set Logic in Confluent Cloud for Apache Flink](set-logic.html#flink-sql-set-logic)
[Temporal joins](joins.html#flink-sql-temporal-joins) | [Top-N Queries in Confluent Cloud for Apache Flink](topn.html#flink-sql-top-n) | [Window Aggregation Queries in Confluent Cloud for Apache Flink](window-aggregation.html#flink-sql-window-aggregation) | [Window Deduplication Queries in Confluent Cloud for Apache Flink](window-deduplication.html#flink-sql-window-deduplication)
[Window Join Queries in Confluent Cloud for Apache Flink](window-join.html#flink-sql-window-join) | [Window Top-N Queries in Confluent Cloud for Apache Flink](window-topn.html#flink-sql-window-top-n) | [Windowing Table-Valued Functions (Windowing TVFs) in Confluent Cloud for Apache Flink](window-tvf.html#flink-sql-window-tvfs) | [WITH Clause in Confluent Cloud for Apache Flink](with.html#flink-sql-with)

## Prerequisites¶

You need the following prerequisites to use Confluent Cloud for Apache Flink.

* Access to Confluent Cloud.

* The organization ID, environment ID, and compute pool ID for your organization.

* The OrganizationAdmin, EnvironmentAdmin, or FlinkAdmin role for creating compute pools, or the FlinkDeveloper role if you already have a compute pool. If you don’t have the appropriate role, reach out to your OrganizationAdmin or EnvironmentAdmin.

* The Confluent CLI. To use the Flink SQL shell, update to the latest version of the Confluent CLI by running the following command:

        confluent update --yes

If you used homebrew to install the Confluent CLI, update the CLI by using the `brew upgrade` command, instead of `confluent update`.

For more information, see [Confluent CLI](https://docs.confluent.io/confluent-cli/current/overview.html).

## Use a workspace or the Flink SQL shell¶

You can run queries and statements either in a Confluent Cloud Console workspace or in the Flink SQL shell.

* To run queries in the Confluent Cloud Console, follow these steps.

    1. Log in to the Confluent Cloud Console.

    2. Navigate to the **Environments** page.

    3. Click the tile that has the environment where your Flink compute pools are provisioned.

    4. Click **Flink**. The **Compute Pools** list opens.

    5. In the compute pool where you want to run statements, click **Open SQL workspace**.

The workspace opens with a cell for editing SQL statements.

* To run queries in the Flink SQL shell, run the following command:

        confluent flink shell --compute-pool <compute-pool-id> --environment <env-id>

You’re ready to run your first Flink SQL query.

## Hello SQL¶

Run the following simple query to print “Hello SQL”.

    SELECT 'Hello SQL';

Your output should resemble:

    EXPR$0
    Hello SQL

Run the following query to aggregate values in a table.

    SELECT Name, COUNT(*) AS Num
    FROM
      (VALUES ('Neo'), ('Trinity'), ('Morpheus'), ('Trinity')) AS NameTable(Name)
    GROUP BY Name;

Your output should resemble:

    Name     Num
    Neo      1
    Morpheus 1
    Trinity  2
