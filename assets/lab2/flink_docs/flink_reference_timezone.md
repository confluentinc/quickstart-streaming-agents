---
source_url: https://docs.confluent.io/cloud/current/flink/reference/timezone.html
title: SQL Timezone Types in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'timezone.html']
scraped_date: 2025-09-05T13:47:08.968679
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

## Set the timezone¶

The local timezone defines the current session timezone id. You can configure the timezone in the Flink SQL shell or in your applications.

    -- set to UTC timezone
    SET 'sql.local-time-zone' = 'UTC';

    -- set to Shanghai timezone
    SET 'sql.local-time-zone' = 'Asia/Shanghai';

    -- set to Los_Angeles timezone
    SET 'sql.local-time-zone' = 'America/Los_Angeles';

### Datetime functions and timezones¶

The return values of the following datetime functions depend on the configured timezone.

* [LOCALTIME](functions/datetime-functions.html#flink-sql-localtime-function)
* [LOCALTIMESTAMP](functions/datetime-functions.html#flink-sql-localtimestamp-function)
* [CURRENT_DATE](functions/datetime-functions.html#flink-sql-current-date-function)
* [CURRENT_TIME](functions/datetime-functions.html#flink-sql-current-time-function)
* [CURRENT_TIMESTAMP](functions/datetime-functions.html#flink-sql-current-timestamp-function)
* [CURRENT_ROW_TIMESTAMP](functions/datetime-functions.html#flink-sql-current-row-timestamp-function)
* [NOW](functions/datetime-functions.html#flink-sql-now-function)

The following example code shows the return types of these datetime functions.

    CREATE TABLE timeview AS SELECT
      LOCALTIME,
      LOCALTIMESTAMP,
      CURRENT_DATE,
      CURRENT_TIME,
      CURRENT_TIMESTAMP,
      CURRENT_ROW_TIMESTAMP() as current_row_ts,
      NOW() as now;

    DESC timeview;

Your output should resemble:

    +-------------------+------------------+----------+--------+
    |    Column Name    |    Data Type     | Nullable | Extras |
    +-------------------+------------------+----------+--------+
    | LOCALTIME         | TIME(0)          | NOT NULL |        |
    | LOCALTIMESTAMP    | TIMESTAMP(3)     | NOT NULL |        |
    | CURRENT_DATE      | DATE             | NOT NULL |        |
    | CURRENT_TIME      | TIME(0)          | NOT NULL |        |
    | CURRENT_TIMESTAMP | TIMESTAMP_LTZ(3) | NOT NULL |        |
    | current_row_ts    | TIMESTAMP_LTZ(3) | NOT NULL |        |
    | now               | TIMESTAMP_LTZ(3) | NOT NULL |        |
    +-------------------+------------------+----------+--------+

Set the timezone to UTC and and query the table.

    SET 'sql.local-time-zone' = 'UTC';
    SELECT * FROM timeview;

Your output should resemble:

    LOCALTIME LOCALTIMESTAMP          CURRENT_DATE CURRENT_TIME CURRENT_TIMESTAMP       current_row_ts          now
    04:33:01  2024-09-26 04:33:01.822 2024-09-26   04:33:01     2024-09-25 20:33:01.822 2024-09-25 20:33:01.822 2024-09-25 20:33:01.822

Change the timezone and query the table again.

    SET 'sql.local-time-zone' = 'Asia/Shanghai';
    SELECT * FROM timeview;

Your output should resemble:

    LOCALTIME LOCALTIMESTAMP          CURRENT_DATE CURRENT_TIME CURRENT_TIMESTAMP       current_row_ts          now
    04:33:01  2024-09-26 04:33:01.822 2024-09-26   04:33:01     2024-09-26 04:33:01.822 2024-09-26 04:33:01.822 2024-09-26 04:33:01.822

### TIMESTAMP_LTZ string representation¶

The session timezone is used when represents a `TIMESTAMP_LTZ` value to string format, i.e print the value, cast the value to `STRING` type, cast the value to `TIMESTAMP`, cast a `TIMESTAMP` value to `TIMESTAMP_LTZ`:

    CREATE TABLE timeview2 AS SELECT
      TO_TIMESTAMP_LTZ(4001, 3) AS ltz,
      TIMESTAMP '1970-01-01 00:00:01.001' AS ntz;

    DESC timeview2;

Your output should resemble:

    +-------------+------------------+----------+--------+
    | Column Name |    Data Type     | Nullable | Extras |
    +-------------+------------------+----------+--------+
    | ltz         | TIMESTAMP_LTZ(3) | NULL     |        |
    | ntz         | TIMESTAMP(3)     | NOT NULL |        |
    +-------------+------------------+----------+--------+

Set the timezone to UTC and and query the table.

    SET 'sql.local-time-zone' = 'UTC';
    SELECT * FROM timeview2;

Your output should resemble:

    ltz                     ntz
    1970-01-01 00:00:04.001 1970-01-01 00:00:01.001

Change the timezone and query the table again.

    SET 'sql.local-time-zone' = 'Asia/Shanghai';
    SELECT * FROM timeview2;

Your output should resemble:

    ltz                     ntz
    1970-01-01 08:00:04.001 1970-01-01 00:00:01.001

The following table shows that columns with data types that result from casting.

    CREATE TABLE timeview3 AS SELECT ltz,
      CAST(ltz AS TIMESTAMP(3)),
      CAST(ltz AS STRING),
      ntz,
      CAST(ntz AS TIMESTAMP_LTZ(3)) FROM timeview2;

    DESC timeview3;

Your output should resemble:

    +-------------+------------------+----------+--------+
    | Column Name |    Data Type     | Nullable | Extras |
    +-------------+------------------+----------+--------+
    | ltz         | TIMESTAMP_LTZ(3) | NULL     |        |
    | ts3         | TIMESTAMP(3)     | NULL     |        |
    | string_rep  | STRING           | NULL     |        |
    | ntz         | TIMESTAMP(3)     | NOT NULL |        |
    | ts_ltz3     | TIMESTAMP_LTZ(3) | NOT NULL |        |
    +-------------+------------------+----------+--------+

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
