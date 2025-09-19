---
source_url: https://docs.confluent.io/cloud/current/flink/concepts/comparison-with-apache-flink.html
title: Comparing Apache Flink with Confluent Cloud for Apache Flink
hierarchy: ['concepts', 'comparison-with-apache-flink.html']
scraped_date: 2025-09-05T13:46:18.497253
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

## Behavioral differences¶

The following list shows differences in behavior between Confluent Cloud for Apache Flink and Apache Flink.

### Configuration options¶

Apache Flink supports various optimization configuration options on different levels, like Execution Options, Optimizer Options, Table Options, and SQL Client Options. Confluent Cloud for Apache Flink supports only the necessary [subset](../reference/statements/set.html#flink-sql-set-statement-config-options) of these options.

Some of these options have different names in Confluent Cloud for Apache Flink, as shown in the following table.

Confluent Cloud for Apache Flink | Apache Flink  
---|---  
client.results-timeout | table.exec.async-lookup.timeout  
client.statement-name | –  
sql.current-catalog | table.builtin-catalog-name  
sql.current-database | table.builtin-database-name  
sql.dry-run | –  
sql.inline-result | –  
sql.local-time-zone | table.local-time-zone  
sql.state-ttl | table.exec.state.ttl  
sql.tables.scan.bounded.timestamp-millis | scan.bounded.timestamp-millis  
sql.tables.scan.bounded.mode | scan.bounded.mode  
sql.tables.scan.idle-timeout | table.exec.source.idle-timeout  
sql.tables.scan.startup.timestamp-millis | scan.startup.timestamp-millis  
sql.tables.scan.startup.mode | scan.startup.mode  
sql.tables.scan.watermark-alignment.max-allowed-drift | scan.watermark.alignment.max-drift  
sql.tables.scan.source-operator-parallelism | –  
  
### CREATE statements provision underlying resources¶

When you run a CREATE TABLE statement in Confluent Cloud for Apache Flink, it creates the underlying Kafka topic and a Schema Registry schema in Confluent Cloud. In Apache Flink, a CREATE TABLE statement only registers the object in the Apache Flink catalog and doesn’t create an underlying resource.

This also means that temporary tables are not supported in Confluent Cloud for Apache Flink, while they are in Apache Flink.

### One Kafka connector and only Confluent Cloud support¶

Apache Flink contains a Kafka connector and an Upsert-Kafka connector, which, combined with the format, defines whether the source/sink is treated as an append-stream or update stream. Confluent Cloud for Apache Flink has only one Kafka connector and determines if the source/sink is an append-stream or update stream by examining the [changelog.mode](../reference/statements/create-table.html#flink-sql-create-table-with-changelog-mode) connector option.

Confluent Cloud for Apache Flink only supports reading from and writing to Kafka topics that are located on Confluent Cloud. Apache Flink supports other connectors, like Kinesis, Pulsar, JDBC, etc., and also other Kafka environments, like on-premises and different cloud service providers.

## Limitations¶

The following list shows limitations of Confluent Cloud for Apache Flink compared with Apache Flink.

### Windowing functions syntax¶

Confluent Cloud for Apache Flink supports the TUMBLE, HOP, SESSION, and CUMULATE windowing functions only by using so-called Table-Valued Functions syntax. Apache Flink supports these windowing functions also by using the outdated Group Window Aggregations functions.

### Unsupported statements and features¶

Confluent Cloud for Apache Flink does not support the following statements and features.

  * ANALYZE statements
  * CALL statements
  * CATALOG commands other than SHOW (No CREATE/DROP/ALTER)
  * DATABASE command other than SHOW (No CREATE/DROP/ALTER)
  * DELETE statements
  * DROP CATALOG and DROP DATABASE
  * JAR statements
  * LOAD / UNLOAD statements
  * TRUNCATE statements
  * UPDATE statements
  * Processing time operations, like `PROCTIME()`, `TUMBLE_PROCTIME`, `HOP_PROCTIME`, `SESSION_PROCTIME`, and `CUMULATE_PROCTIME`

### Limited support for ALTER¶

Confluent Cloud for Apache Flink has limited support for ALTER TABLE compared with Apache Flink. In Confluent Cloud for Apache Flink, you can use ALTER TABLE only to change the watermark strategy, add a metadata column, or change a parameter value.

