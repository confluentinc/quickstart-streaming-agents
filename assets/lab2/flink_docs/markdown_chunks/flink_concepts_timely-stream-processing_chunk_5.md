---
document_id: flink_concepts_timely-stream-processing_chunk_5
source_file: flink_concepts_timely-stream-processing.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/timely-stream-processing.html
title: Time and Watermarks in Confluent Cloud for Apache Flink
chunk_index: 5
total_chunks: 5
---

is lower than 5 minutes.

## Time attributes¶

Confluent Cloud for Apache Flink can process data based on different notions of time.

* **Event time** refers to stream processing based on timestamps that are attached to each row. The timestamps can encode when an event happened.
* **Processing time** refers to the machine’s system time that’s executing the operation. Processing time is also known as “epoch time”, for example, Java’s `System.currentTimeMillis()`. Processing time is not supported in Confluent Cloud for Apache Flink.

Time attributes can be part of every table schema. They are defined when creating a table from a `CREATE TABLE` DDL statement.

Once a time attribute is defined, it can be referenced as a field and used in time-based operations. As long as a time attribute is not modified and is simply forwarded from one part of a query to another, it remains a valid time attribute.

Time attributes behave like regular timestamps, and are accessible for calculations. When used in calculations, time attributes are materialized and act as standard timestamps, but ordinary timestamps can’t be used in place of, or converted to, time attributes.

### Event time¶

Event time enables a table program to produce results based on timestamps in every record, which allows for consistent results despite out-of-order or late events. Event time also ensures the replayability of the results of the table program when reading records from persistent storage.

Also, event time enables unified syntax for table programs in both batch and streaming environments. A time attribute in a streaming environment can be a regular column of a row in a batch environment.

To handle out-of-order events and to distinguish between on-time and late events in streaming, Flink must know the timestamp for each row, and it also needs regular indications of how far along in event time the processing has progressed so far, by using watermarks.

You can define event-time attributes in [CREATE TABLE](../reference/statements/create-table.html#flink-sql-create-table) statements.

#### Defining in DDL¶

The event-time attribute is defined by using a WATERMARK clause in a `CREATE TABLE` DDL statement. A watermark statement defines a watermark generation expression on an existing event-time field, which marks the event-time field as the event-time attribute. For more information about watermark strategies, see [Watermark clause](../reference/statements/create-table.html#flink-sql-watermark-clause).

Flink SQL supports defining an event-time attribute on TIMESTAMP and TIMESTAMP_LTZ columns. If the timestamp data in the source is represented as year-month-day-hour-minute-second, usually a string value without time-zone information, for example, `2020-04-15 20:13:40.564`, it’s recommended to define the event-time attribute as a `TIMESTAMP` column.

    CREATE TABLE user_actions (
      user_name STRING,
      data STRING,
      user_action_time TIMESTAMP(3),
      -- Declare the user_action_time column as an event-time attribute
      -- and use a 5-seconds-delayed watermark strategy.
      WATERMARK FOR user_action_time AS user_action_time - INTERVAL '5' SECOND
    ) WITH (
      ...
    );

    SELECT TUMBLE_START(user_action_time, INTERVAL '10' MINUTE), COUNT(DISTINCT user_name)
    FROM user_actions
    GROUP BY TUMBLE(user_action_time, INTERVAL '10' MINUTE);

If the timestamp data in the source is represented as epoch time, which is usually a LONG value like `1618989564564`, consider defining the event-time attribute as a `TIMESTAMP_LTZ` column.

    CREATE TABLE user_actions (
      user_name STRING,
      data STRING,
      ts BIGINT,
      time_ltz AS TO_TIMESTAMP_LTZ(ts, 3),
      -- Declare the time_ltz column as an event-time attribute
      -- and use a 5-seconds-delayed watermark strategy.
      WATERMARK FOR time_ltz AS time_ltz - INTERVAL '5' SECOND
    ) WITH (
      ...
    );

    SELECT TUMBLE_START(time_ltz, INTERVAL '10' MINUTE), COUNT(DISTINCT user_name)
    FROM user_actions
    GROUP BY TUMBLE(time_ltz, INTERVAL '10' MINUTE);

### Processing time¶

Processing time enables a table program to produce results based on the time of the local machine. It’s the simplest notion of time, but it generates non-deterministic results. Processing time doesn’t require timestamp extraction or watermark generation.

Processing time is not supported in Confluent Cloud for Apache Flink.
