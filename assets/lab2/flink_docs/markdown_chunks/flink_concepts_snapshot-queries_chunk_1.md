---
document_id: flink_concepts_snapshot-queries_chunk_1
source_file: flink_concepts_snapshot-queries.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/snapshot-queries.html
title: Snapshot Queries in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 2
---

# Snapshot Queries in Confluent Cloud for Apache Flink¶

In Confluent Cloud for Apache Flink®, a _snapshot query_ is a query that reads data from a table at a specific point in time. In contrast with a streaming query, which runs continuously and returns results incrementally, a snapshot query runs, returns results, and then exits. Snapshot queries are also known as _point-in-time_ or _pull queries_.

You can query Kafka topics as well as Apache Iceberg™ tables by using Confluent [Tableflow](../../topics/tableflow/overview.html#cloud-tableflow).

Note

Snapshot query is an Early Access Program feature in Confluent Cloud for Apache Flink.

An Early Access feature is a component of Confluent Cloud introduced to gain feedback. This feature should be used only for evaluation and non-production testing purposes or to provide feedback to Confluent, particularly as it becomes more widely available in follow-on preview editions.

Early Access Program features are intended for evaluation use in development and testing environments only, and not for production use. Early Access Program features are provided: (a) without support; (b) “AS IS”; and (c) without indemnification, warranty, or condition of any kind. No service level commitment will apply to Early Access Program features. Early Access Program features are considered to be a Proof of Concept as defined in the Confluent Cloud Terms of Service. Confluent may discontinue providing preview releases of the Early Access Program features at any time in Confluent’s sole discretion.

## Snapshot query uses¶

A snapshot query returns a consistent view of your data at the current point in time, similar to taking a photograph of your data at that moment. This is particularly useful when you need to:

  * Generate reports that reflect your data’s state at a specific time
  * Analyze historical data for auditing or compliance purposes
  * Compare data states across different points in time
  * Debug or investigate issues by examining past data states

For example, if you want to know the total number of orders in your system at the current time, you can use a snapshot query.

## Snapshot mode¶

A snapshot query is an ordinary Flink SQL statement that has one additional property, named `sql.snapshot.mode`.

To enable snapshot queries, set the `sql.snapshot.mode` property to `now`. You can set this property in the following ways:

  * **SQL Workspace:** Toggle the **Mode** dropdown to **Snapshot**.
  * **Flink SQL:** Prepend your query with `SET 'sql.snapshot.mode' = 'now';`.
  * **Table API:** In the `Cloud.Properties` project file, add `sql.snapshot.mode = now`.
  * **REST API:** In the statement’s `spec.properties` map, add `"sql.snapshot.mode": "now"`.
  * **Terraform:** In the statement properties, add `"sql.snapshot.mode" = "now"`.

Snapshot queries use Flink’s batch execution mode, which enables you to run batch processing jobs beside your existing stream processing workloads, within the same Confluent Cloud environment.

Also, Confluent Cloud for Apache Flink bounds all sources, which means that Flink processes only a finite set of records up to a specific point in time, rather than continuously processing an infinite stream of incoming data.

## How snapshot queries work¶

When you execute a snapshot query, Flink performs the following steps:

  1. Determines the Kafka offsets corresponding to your current timestamp across all partitions
  2. Reads data from the source topics up to these offsets
  3. Processes the records to build the state of your tables at this point in time
  4. Returns the query results based on this state

The query execution is optimized to use Kafka’s time index for efficient offset lookup, to leverage parallel processing across partitions, and to minimize the amount of data that needs to be processed.

## Snapshot queries and Tableflow¶

If [Tableflow](../../topics/tableflow/overview.html#cloud-tableflow) is enabled on a topic, snapshot queries on the topic run in a hybrid mode.

  * If Tableflow is not enabled on a topic, the query reads from Kafka.
  * If Tableflow is enabled on a topic, the query reads from both Kafka and Parquet, for Confluent Managed Storage and custom storage (BYOS).

## Run a snapshot query¶

To run a snapshot query, in a Flink workspace or the Flink SQL shell, prepend your query with the following SET statement:

    SET 'sql.snapshot.mode' = 'now';

Also, in a Flink workspace, you can change the **Mode** dropdown setting to **Snapshot**.

For more information, see [Run a Snapshot Query](../how-to-guides/run-snapshot-query.html#flink-sql-run-snapshot-query).
