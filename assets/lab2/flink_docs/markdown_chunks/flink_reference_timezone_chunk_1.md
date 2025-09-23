---
document_id: flink_reference_timezone_chunk_1
source_file: flink_reference_timezone.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/timezone.html
title: SQL Timezone Types in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 3
---

# Timezone Types in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides rich data types for date and time, including these:

* [DATE](datatypes.html#flink-sql-date)
* [TIME](datatypes.html#flink-sql-time)
* [TIMESTAMP](datatypes.html#flink-sql-timestamp)
* [TIMESTAMP_LTZ](datatypes.html#flink-sql-timestamp-ltz)
* [INTERVAL YEAR TO MONTH](datatypes.html#flink-sql-interval-y-to-m)
* [INTERVAL DAY TO SECOND](datatypes.html#flink-sql-interval-d-to-s)

These datetime types and the related [datetime functions](functions/datetime-functions.html#flink-sql-datetime-functions) enable processing business data across timezones.

## TIMESTAMP vs TIMESTAMP_LTZ¶

### TIMESTAMP type¶

* `TIMESTAMP(p)` is an abbreviation for `TIMESTAMP(p) WITHOUT TIME ZONE`. The precision `p` supports a range from _0_ to _9_. The default is _6_.

* `TIMESTAMP` describes a timestamp that represents year, month, day, hour, minute, second, and fractional seconds.

* `TIMESTAMP` can be specified from a string literal. The following code example shows a SELECT statement that creates a timestamp from a string.

        SELECT TIMESTAMP '1970-01-01 00:00:04.001';

Your output should resemble:

        EXPR$0
        1970-01-01 00:00:04.001

### TIMESTAMP_LTZ type¶

* `TIMESTAMP_LTZ(p)` is an abbreviation for `TIMESTAMP(p) WITH LOCAL TIME ZONE`. The precision `p` supports a range from 0* to _9_. The default is _6_.

* `TIMESTAMP_LTZ` describes an absolute time point on the time-line. It stores a LONG value representing epoch-milliseconds and an INT representing nanosecond-of-millisecond. The epoch time is measured from the standard Java epoch of `1970-01-01T00:00:00Z`. Every datum of `TIMESTAMP_LTZ` type is interpreted in the local timezone configured in the current session. Typically, the local timezone is used for computation and visualization.

* `TIMESTAMP_LTZ` can be used in cross timezones business because the absolute time point. for example, _4001_ milliseconds describes a same instantaneous point in different timezones. If the local system time of all machines in the world returns same value, for example, _4001_ milliseconds, this is the meaning of “absolute time point”.

* `TIMESTAMP_LTZ` has no literal representation, so you can’t create it from a literal. It can be derived from a LONG epoch time, as shown in the following code example.

        SET 'sql.local-time-zone' = 'UTC';

Your output should resemble:

        +---------------------+-------+
        |         Key         | Value |
        +---------------------+-------+
        | sql.local-time-zone | UTC   |
        +---------------------+-------+

Query the [TO_TIMESTAMP_LTZ](functions/datetime-functions.html#flink-sql-to-timestamp-ltz-function) function to convert a Unix time to a `TIMESTAMP_LTZ`.

        SELECT TO_TIMESTAMP_LTZ(4001, 3);

Your output should resemble:

        EXPR$0
        1970-01-01 00:00:04.001

Change the timezone:

        SET 'sql.local-time-zone' = 'Asia/Shanghai';

Your output should resemble:

        +---------------------+---------------+
        |         Key         |     Value     |
        +---------------------+---------------+
        | sql.local-time-zone | Asia/Shanghai |
        +---------------------+---------------+

Query the time again:

        SELECT TO_TIMESTAMP_LTZ(4001, 3);

Your output should resemble:

        EXPR$0
        1970-01-01 08:00:04.001
