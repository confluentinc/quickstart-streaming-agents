---
document_id: flink_reference_statements_create-table_chunk_4
source_file: flink_reference_statements_create-table.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-table.html
title: SQL CREATE TABLE Statement in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 14
---

example_value STRING) PARTITIONED BY (partition_key);

## Watermark clause¶

The `WATERMARK` clause defines the [event-time attributes](../../concepts/timely-stream-processing.html#flink-sql-event-time-and-watermarks) of a table.

A [watermark](../../../_glossary.html#term-watermark) in Flink is used to track the progress of event time and provide a way to trigger time-based operations.

### Default watermark strategy¶

Confluent Cloud for Apache Flink provides a default watermark strategy for all tables, whether created automatically from a Kafka topic or from a CREATE TABLE statement.

The default watermark strategy is applied on the `$rowtime` system column.

Watermarks are calculated per Kafka partition, and at least 250 events are required per partition.

If a delay of longer than 7 days can occur, choose a custom watermark strategy.

Because the concrete implementation is provided by Confluent, you see only `WATERMARK FOR $rowtime AS SOURCE_WATERMARK()` in the declaration.

### Custom watermark strategies¶

You can replace the default strategy with a custom strategy at any time by using [ALTER TABLE](alter-table.html#flink-sql-alter-table).

### Watermark strategy reference¶

    WATERMARK FOR rowtime_column_name AS watermark_strategy_expression

The `rowtime_column_name` defines an existing column that is marked as the event-time attribute of the table. The column must be of type `TIMESTAMP(3)`, and it must be a top-level column in the schema.

The `watermark_strategy_expression` defines the watermark generation strategy. It allows arbitrary non-query expressions, including computed columns, to calculate the watermark. The expression return type must be `TIMESTAMP(3)`, which represents the timestamp since the Unix Epoch.

The returned watermark is emitted only if it’s non-null and its value is larger than the previously emitted local watermark, to respect the contract of ascending watermarks.

The watermark generation expression is evaluated by Flink SQL for every record. The framework emits the largest generated watermark periodically.

No new watermark is emitted if any of the following conditions apply.

* The current watermark is null.
* The current watermark is identical to the previous watermark.
* The value of the returned watermark is smaller than the value of the last emitted watermark.

When you use event-time semantics, your tables must contain an event-time attribute and watermarking strategy.

Flink SQL provides these watermark strategies.

* **Strictly ascending timestamps:** Emit a watermark of the maximum observed timestamp so far. Rows that have a timestamp larger than the max timestamp are not late.

        WATERMARK FOR rowtime_column AS rowtime_column

* **Ascending timestamps:** Emit a watermark of the maximum observed timestamp so far, minus _1_. Rows that have a timestamp larger than or equal to the max timestamp are not late.

        WATERMARK FOR rowtime_column AS rowtime_column - INTERVAL '0.001' SECOND

* **Bounded out-of-orderness timestamps:** Emit watermarks which are the maximum observed timestamp minus the specified delay.

        WATERMARK FOR rowtime_column AS rowtime_column - INTERVAL 'string' timeUnit

The following example shows a “5-seconds delayed” watermark strategy.

        WATERMARK FOR rowtime_column AS rowtime_column - INTERVAL '5' SECOND

Example

The following CREATE TABLE statement defines an `orders` table that has a rowtime column named `order_time` and a watermark strategy with a 5-second delay.

    CREATE TABLE orders (
        `user` BIGINT,
        `product` STRING,
        `order_time` TIMESTAMP(3),
        WATERMARK FOR `order_time` AS `order_time` - INTERVAL '5' SECOND
    );

### Progressive idleness detection¶

When a source does not receive any elements for a timeout time, which is specified by the `sql.tables.scan.idle-timeout` property, the source is marked as temporarily idle. This enables each downstream task to advance its watermark without the need to wait for watermarks from this source while it’s idle.

By default, Confluent Cloud for Apache Flink has progressive idleness detection that starts with an idle-timeout of 15 seconds, and increases to a maximum of 5 minutes over time.

You can disable idleness detection by setting the `sql.tables.scan.idle-timeout` property to `0`, or you can set a fixed idleness timeout with your desired value. When idleness detection is disabled, a single idle partition on any of the sources causes the watermarks to stop advancing. In turn, this causes operations that rely on watermarks to stop producing results. On the other hand, with idleness detection enabled, with either progressive idleness or a fixed value, the watermark advances unless all partitions of all sources are idle.

For more information, see the video, [How to Set Idle Timeouts](https://www.youtube.com/watch?v=YSIhM5-Sykw).
