---
document_id: flink_reference_timezone_chunk_2
source_file: flink_reference_timezone.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/timezone.html
title: SQL Timezone Types in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 3
---

should resemble: EXPR$0 1970-01-01 08:00:04.001

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
