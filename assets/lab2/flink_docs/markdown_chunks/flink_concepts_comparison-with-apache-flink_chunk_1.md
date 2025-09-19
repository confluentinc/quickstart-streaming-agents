---
document_id: flink_concepts_comparison-with-apache-flink_chunk_1
source_file: flink_concepts_comparison-with-apache-flink.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/comparison-with-apache-flink.html
title: Comparing Apache Flink with Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 2
---

# Comparing Apache Flink with Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® supports many of the capabilities of Apache Flink® and provides additional features. Also, Confluent Cloud for Apache Flink has some different behaviors and limitations relative to Apache Flink. This topic describes the key differences between Confluent Cloud for Apache Flink and Apache Flink.

## Additional features¶

The following list shows features provided by Confluent Cloud for Apache Flink that go beyond what Apache Flink offers.

### Auto-inference of environments, clusters, topics, and schemas¶

In Apache Flink, you must define and configure your tables and their schemas, including authentication and authorization to Apache Kafka®. Confluent Cloud for Apache Flink maps environments, clusters, topics, and schemas automatically from Confluent Cloud to the corresponding Apache Flink concepts of catalogs, databases, tables, and table schemas.

### Autoscaling¶

[Autopilot](autopilot.html#flink-sql-autopilot) scales up and scales down the compute resources that SQL statements use in Confluent Cloud. The autoscaling process is based on [parallelism](overview.html#flink-sql-stream-processing-concepts-parallel-dataflows), which is the number of parallel operations that occur when the SQL statement is running. A SQL statement performs at its best when it has the optimal resources for its required parallelism.

### Default system column implementation¶

Confluent Cloud for Apache Flink has a default implementation for a [system column](../reference/statements/create-table.html#flink-sql-system-columns) named [$rowtime](../reference/statements/create-table.html#flink-sql-system-columns-rowtime). This column is mapped to the Kafka record timestamp, which can be either `LogAppendTime` or `CreateTime`.

### Default watermark strategy¶

Flink requires a [watermark](../../_glossary.html#term-watermark) strategy for a variety of features, such as [windowing](timely-stream-processing.html#flink-sql-event-time-lateness) and [temporal joins](../reference/queries/joins.html#flink-sql-temporal-joins). Confluent Cloud for Apache Flink has a default watermark strategy applied on all tables/topics, which is based on the `$rowtime` system column. Apache Flink requires you to define a watermark strategy manually. For more information, see [Event Time and Watermarks](timely-stream-processing.html#flink-sql-event-time-and-watermarks).

Because the default strategy is defined for general usage, there are cases that require a custom strategy, for example, when delays in record arrival of longer than 7 days occur in your streams. You can override the default strategy with a custom strategy by using the [ALTER TABLE](../reference/statements/alter-table.html#flink-sql-alter-table) statement.

### Schema Registry support for JSON_SR and Protobuf¶

Confluent Cloud for Apache Flink has support for Schema Registry formats AVRO, JSON_SR, and Protobuf, while Apache Flink currently supports only Schema Registry AVRO.

### INFORMATION_SCHEMA support¶

Confluent Cloud for Apache Flink has an implementation for IMPLEMENTATION_SCHEMA, which is a system view that provides insights on catalogs, databases, tables, and schemas. This doesn’t exist in Apache Flink.
