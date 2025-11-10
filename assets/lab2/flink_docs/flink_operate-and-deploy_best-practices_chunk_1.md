---
document_id: flink_operate-and-deploy_best-practices_chunk_1
source_file: flink_operate-and-deploy_best-practices.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/best-practices.html
title: Best Practices for Moving SQL Statements to Production in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 2
---

# Move SQL Statements to Production in Confluent Cloud for Apache Flink¶

When you move your Flink SQL statements to production in Confluent Cloud for Apache Flink®, consider the following recommendations and best practices.

  * Validate your watermark strategy
  * Validate or disable idleness handling
  * Choose the correct Schema Registry compatibility type
  * Separate workloads of different priorities into separate compute pools
  * Use event-time temporal joins instead of streaming joins
  * Implement state time-to-live (TTL)
  * Use service account API keys for production
  * Assign custom names to Flink SQL statements

## Validate your watermark strategy¶

When moving your Flink SQL statements to production, it’s crucial to validate your [watermark](../../_glossary.html#term-watermark) strategy. [Watermarks](../concepts/timely-stream-processing.html#flink-sql-timely-stream-processing) in Flink track the progress of event time and provide a way to trigger time-based operations.

Confluent Cloud for Apache Flink provides a [default watermark strategy](../reference/functions/datetime-functions.html#flink-sql-source-watermark-function) for all tables, whether they’re created automatically from a Kafka topic or from a [CREATE TABLE](../reference/statements/create-table.html#flink-sql-create-table) statement. The default watermark strategy is applied on the [$rowtime](../reference/statements/create-table.html#flink-sql-system-columns-rowtime) system column, which is mapped to the associated timestamp of a Kafka record. Watermarks for this default strategy are calculated per Kafka partition, and at least 250 events are required per partition.

Here are some situations when you need to define your own [custom watermark strategy](../reference/statements/create-table.html#flink-sql-watermark-clause):

  * When the event time needs to be based on data from the payload and not the timestamp of the Kafka record.
  * If a delay of longer than 7 days can occur.
  * When events might not arrive in the exact order they were generated.
  * When data may arrive late due to network latency or processing delays.

## Validate or disable idleness handling¶

One critical aspect to consider when moving your Flink SQL statements to production is the handling of idleness in data streams. If no events arrive within a certain time (timeout duration) on a Kafka partition, that partition is marked as idle and does not contribute to the watermark calculation until a new event comes in. This situation creates a problem: if some partitions continue to receive events while others are idle, the overall watermark computation, which is based on the minimum across all parallel watermarks, may be inaccurately held back.

Confluent Cloud for Apache Flink dynamically adjusts the consideration of idle partitions in watermark calculations with Confluent’s Progressive Idleness feature. The idle-time detection starts small at 15 seconds but grows linearly with the age of the statement up to a maximum of 5 minutes. Progressive Idleness can cause wrong watermarks if a partition is marked as idle too quickly, and this can cause the system to move ahead too quickly, impacting data processing.

When you move your Flink SQL statement into production, make sure that you have validated how you want to handle idleness. You can configure or disable this behavior by using the [sql.tables.scan.idle-timeout](../reference/statements/set.html#flink-sql-set-statement-config-options) option.

## Choose the correct Schema Registry compatibility type¶

The Confluent Schema Registry plays a pivotal role in ensuring that the schemas of the data flowing through your Kafka topics are consistent, compatible, and evolve in a controlled manner. One of the key decisions in this process is selecting the appropriate [schema compatibility type](../../sr/fundamentals/schema-evolution.html#sr-compatibility-types).

Consider using `FULL_TRANSITIVE` compatibility to ensure that any new schema is fully compatible with all previous versions of the schema. This comprehensive check minimizes the risk of introducing changes that could disrupt data-processing applications relying on the data. When choosing any of the other compatibility modes, you need to consider the consequences on currently-running statements, especially since a Flink statement is both a producer and a consumer at the same time.
