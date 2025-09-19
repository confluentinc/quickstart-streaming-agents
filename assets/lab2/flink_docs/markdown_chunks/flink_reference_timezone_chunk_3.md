---
document_id: flink_reference_timezone_chunk_3
source_file: flink_reference_timezone.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/timezone.html
title: SQL Timezone Types in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 3
---

Query the table.

    SELECT * FROM timeview3;

Your output should resemble:

    ltz                     ts3                     string_rep              ntz                     ts_ltz3
    1970-01-01 08:00:04.001 1970-01-01 08:00:04.001 1970-01-01 08:00:04.001 1970-01-01 00:00:01.001 1970-01-01 00:00:01.001

### Time attribute and timezone¶

For more information about time attributes, see [Time attributes](../concepts/timely-stream-processing.html#flink-sql-time-attributes).

### Event time and timezone¶

Flink SQL supports defining an event-time attribute on TIMESTAMP and TIMESTAMP_LTZ columns.

#### Event-time attribute on TIMESTAMP¶

If the timestamp data in the source is represented as year-month-day-hour-minute-second, usually a string value without timezone information, for example, `2020-04-15 20:13:40.564`, you can define the event-time attribute as a `TIMESTAMP` column.

#### Event-time attribute on TIMESTAMP_LTZ¶

If the timestamp data in the source is represented as a epoch time, usually as a LONG value, for example, `1618989564564`, you can define an event-time attribute as a `TIMESTAMP_LTZ` column.

### Daylight Saving Time support¶

Flink SQL supports defining time attributes on a TIMESTAMP_LTZ column, and Flink SQL uses the TIMESTAMP and TIMESTAMP_LTZ types in window processing to support the Daylight Saving Time.

Flink SQL uses a timestamp literal to split the window and assigns window to data according to the epoch time of the each row. This means that Flink SQL uses the `TIMESTAMP` type for window start and window end, like `TUMBLE_START` and `TUMBLE_END`, and it uses `TIMESTAMP_LTZ` for window-time attributes, like `TUMBLE_ROWTIME`. Given an example tumble window, the Daylight Saving Time in the `America/Los_Angeles` timezone starts at time `2021-03-14 02:00:00`:

    long epoch1 = 1615708800000L; // 2021-03-14 00:00:00
    long epoch2 = 1615712400000L; // 2021-03-14 01:00:00
    long epoch3 = 1615716000000L; // 2021-03-14 03:00:00, skip one hour (2021-03-14 02:00:00)
    long epoch4 = 1615719600000L; // 2021-03-14 04:00:00

The tumble window [2021-03-14 00:00:00, 2021-03-14 00:04:00] collects 3 hours’ worth of data in the `America/Los_Angeles` timezone, but it collect 4 hours’ worth of data in other non-DST timezones. You only need to define time the attribute on a TIMESTAMP_LTZ column.

All windows in Flink SQL, like Hop window, Session window, Cumulative window follow this pattern, and all operations in Flink SQL support TIMESTAMP_LTZ, so Flink SQL provides complete support for Daylight Saving Time.

### Related content¶

  * [Datetime Functions](functions/datetime-functions.html#flink-sql-datetime-functions)
  * [Time attributes](../concepts/timely-stream-processing.html#flink-sql-time-attributes)
  * [Flink SQL Queries](queries/overview.html#flink-sql-queries)
  * [DDL Statements](../concepts/statements.html#flink-sql-statements)

Note

This website includes content developed at the [Apache Software Foundation](https://www.apache.org/) under the terms of the [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0.html).
