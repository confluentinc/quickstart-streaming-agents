---
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/datetime-functions.html
title: SQL Datetime Functions in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'functions', 'datetime-functions.html']
scraped_date: 2025-09-05T13:48:27.331329
---

# Datetime Functions in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides these built-in functions for handling date and time logic in SQL queries:

Date | Time | Timestamp | Utility
---|---|---|---
CURRENT_DATE | CONVERT_TZ | CURRENT_TIMESTAMP | CEIL
DATE_FORMAT | CURRENT_TIME | CURRENT_ROW_TIMESTAMP | CURRENT_WATERMARK
DATE | HOUR | LOCALTIMESTAMP | EXTRACT
DAYOFMONTH | LOCALTIME | TIMESTAMP | FLOOR
DAYOFWEEK | MINUTE | TO_TIMESTAMP | FROM_UNIXTIME
DAYOFYEAR | NOW | TO_TIMESTAMP_LTZ | INTERVAL
MONTH | SECOND | TIMESTAMPADD | SOURCE_WATERMARK
QUARTER | TIME | TIMESTAMPDIFF | OVERLAPS
TO_DATE |  | UNIX_TIMESTAMP |
WEEK |  | UNIX_TIMESTAMP |
YEAR |  |  |

## Time interval and point unit specifiers¶

The following table lists specifiers for time interval and time point units.

Time interval unit | Time point unit
---|---
`MILLENNIUM` |
`CENTURY` |
`DECADE` |
`YEAR` | `YEAR`
`YEAR TO MONTH` |
`QUARTER` | `QUARTER`
`MONTH` | `MONTH`
`WEEK` | `WEEK`
`DAY` | `DAY`
`DAY TO HOUR` |
`DAY TO MINUTE` |
`DAY TO SECOND` |
`HOUR` | `HOUR`
`HOUR TO MINUTE` |
`HOUR TO SECOND` |
`MINUTE` | `MINUTE`
`MINUTE TO SECOND` |
`SECOND` | `SECOND`
`MILLISECOND` | `MILLISECOND`
`MICROSECOND` | `MICROSECOND`
`NANOSECOND` |
`EPOCH` |
`DOY` |
`DOW` |
`EPOCH` |
`ISODOW` |
`ISOYEAR` | `SQL_TSI_YEAR` `SQL_TSI_QUARTER` `SQL_TSI_MONTH` `SQL_TSI_WEEK` `SQL_TSI_DAY` `SQL_TSI_HOUR` `SQL_TSI_MINUTE` `SQL_TSI_SECOND`

### CEIL¶

Rounds a time point up.

Syntax

    CEIL(timepoint TO timeintervalunit)

Description
    The `CEIL` function returns a value that rounds `timepoint` up to the time unit specified by `timeintervalunit`.
Example

    -- returns "12:45:00"
    SELECT CEIL(TIME '12:44:31' TO MINUTE);

Related function

  * FLOOR

### CONVERT_TZ¶

Converts a datetime from one time zone to another.

Syntax

    CONVERT_TZ(string1, string2, string3)

Description

The `CONVERT_TZ` function converts a datetime `string1` that has the default ISO timestamp format, “yyyy-MM-dd hh:mm:ss”, from the time zone specified by `string2` to the time zone specified by `string3`.

The format of the time zone arguments is either an abbreviation, like “PST”, a full name, like “America/Los_Angeles”, or a custom ID, like “GMT-08:00”.

Example

    -- returns "1969-12-31 16:00:00"
    SELECT CONVERT_TZ('1970-01-01 00:00:00', 'UTC', 'America/Los_Angeles');

### CURRENT_DATE¶

Returns the current date.

Syntax

    CURRENT_DATE

Description

The `CURRENT_DATE` function returns the current SQL date in the local time zone.

  * In streaming mode, the current date is evaluated for each record.
  * In batch mode, the current date is evaluated once when the query starts, and `CURRENT_DATE` returns the same result for every row.

Example

    -- returns the current date
    SELECT CURRENT_DATE;

### CURRENT_ROW_TIMESTAMP¶

Returns the current timestamp for each row.

Syntax

    CURRENT_ROW_TIMESTAMP()

Description

The `CURRENT_ROW_TIMESTAMP` function returns the current SQL timestamp in the local time zone. The return type is `TIMESTAMP_LTZ(3)`.

The timestamp is evaluated for each row, in both batch and streaming mode.

Example

    -- returns the timestamp of the current datetime
    SELECT CURRENT_ROW_TIMESTAMP();

### CURRENT_TIME¶

Syntax

    CURRENT_TIME

Description

The `CURRENT_TIME` function returns the current SQL time in the local time zone.

The `CURRENT_TIME` function is equivalent to LOCALTIME.

Example

    -- returns the current time, for example:
    -- 13:03:56
    SELECT CURRENT_TIME;

### CURRENT_TIMESTAMP¶

Syntax

    CURRENT_TIMESTAMP

Description

The `CURRENT_TIMESTAMP` function returns the current SQL timestamp in the local time zone. The return type is `TIMESTAMP_LTZ(3)`.

  * In streaming mode, the current timestamp is evaluated for each record.
  * In batch mode, the current timestamp is evaluated once when the query starts, and `CURRENT_TIMESTAMP` returns the same result for every row.

The `CURRENT_TIMESTAMP` function is equivalent to NOW.

Example

    -- returns the current timestamp, for example:
    -- 2023-10-16 13:04:58.081
    SELECT CURRENT_TIMESTAMP;

### CURRENT_WATERMARK¶

Gets the current [watermark](../../../_glossary.html#term-watermark) for a `rowtime` column.

Syntax

    CURRENT_WATERMARK(rowtime)

Description

The `CURRENT_WATERMARK` function returns the current watermark for the given `rowtime` attribute, or NULL if no common watermark of all upstream operations is available at the current operation in the pipeline.

The return type of the function is inferred to match that of the provided `rowtime` attribute, but with an adjusted precision of _3_.

For example, if the rowtime attribute is `TIMESTAMP_LTZ(9)`, the function returns `TIMESTAMP_LTZ(3)`.

This function can return NULL, and it may be necessary to consider this case.

For more information, see [watermarks](../../concepts/timely-stream-processing.html#flink-sql-event-time-and-watermarks).

Example

The following example shows how to filter out late data by using the `CURRENT_WATERMARK` function with a `rowtime` column named `ts`.

    WHERE
      CURRENT_WATERMARK(ts) IS NULL
      OR ts > CURRENT_WATERMARK(ts)

Related function

  * SOURCE_WATERMARK

### DATE_FORMAT¶

Converts a timestamp to a formatted string.

Syntax

    DATE_FORMAT(timestamp, date_format)

Description

The `DATE_FORMAT` function converts the specified timestamp to a string value in the format specified by the `date_format` string.

The format string is compatible with the Java [SimpleDateFormat](https://docs.oracle.com/en/java/javase/19/docs/api/java.base/java/text/SimpleDateFormat.html). class.

Example

    -- returns "5:32 PM, UTC"
    SELECT DATE_FORMAT('2023-03-15 17:32:01.009', 'K:mm a, z');

### DATE¶

Parses a DATE from a string.

Syntax

    DATE string

Description

The `DATE` function returns a SQL date parsed from the specified string.

The date format of the input string must be “yyyy-MM-dd”.

Example

    -- returns "2023-05-23"
    SELECT DATE '2023-05-23';

### DAYOFMONTH¶

Gets the day of month from a DATE.

Syntax

    DAYOFMONTH(date)

Description

The `DAYOFMONTH` function returns the day of a month from the specified SQL DATE as an integer between _1_ and _31_.

The `DAYOFMONTH` function is equivalent to `EXTRACT(DAY FROM date)`.

Example

    -- returns 27
    SELECT DAYOFMONTH(DATE '1994-09-27');

### DAYOFWEEK¶

Gets the day of week from a DATE.

Syntax

    DAYOFWEEK(date)

Description

The `DAYOFWEEK` function returns the day of a week from the specified SQL DATE as an integer between _1_ and _7_.

The `DAYOFWEEK` function is equivalent to `EXTRACT(DOW FROM date)`.

Example

    -- returns 3
    SELECT DAYOFWEEK(DATE '1994-09-27');

### DAYOFYEAR¶

Gets the day of year from a DATE.

Syntax

    DAYOFYEAR(date)

Description

The `DAYOFYEAR` function returns the day of a year from the specified SQL DATE as an integer between _1_ and _366_.

The `DAYOFYEAR` function is equivalent to `EXTRACT(DOY FROM date)`.

Example

    -- returns 270
    SELECT DAYOFYEAR(DATE '1994-09-27');

### EXTRACT¶

Gets a time interval unit from a datetime.

Syntax

    EXTRACT(timeintervalunit FROM temporal)

Description
    The `EXTRACT` function returns a LONG value extracted from the specified `timeintervalunit` part of `temporal`.
Example

    -- returns 5
    SELECT EXTRACT(DAY FROM DATE '2006-06-05');

Related functions

  * DAYOFMONTH
  * DAYOFWEEK
  * DAYOFYEAR

### FLOOR¶

Rounds a time point down.

Syntax

    FLOOR(timepoint TO timeintervalunit)

Description
    The `FLOOR` function returns a value that rounds `timepoint` down to the time unit specified by `timeintervalunit`.
Example

    -- returns 12:44:00
    SELECT FLOOR(TIME '12:44:31' TO MINUTE);

Related function

  * CEIL

### FROM_UNIXTIME¶

Gets a Unix time as a formatted string.

Syntax

    FROM_UNIXTIME(numeric[, string])

Description

The `FROM_UNIXTIME` function returns a representation of the NUMERIC argument as a value in string format. The default format is “yyyy-MM-dd hh:mm:ss”.

The specified NUMERIC is an internal timestamp value representing seconds since “1970-01-01 00:00:00” UTC, such as produced by the UNIX_TIMESTAMP function.

The return value is expressed in the session time zone (specified in TableConfig).

Example

    -- Returns "1970-01-01 00:00:44" if in the UTC time zone,
    -- but returns "1970-01-01 09:00:44" if in the 'Asia/Tokyo' time zone.
    SELECT FROM_UNIXTIME(44);

### HOUR¶

Gets the hour of day from a timestamp.

Syntax

    HOUR(timestamp)

Description

The `HOUR` function returns the hour of a day from the specified SQL timestamp as an integer between _0_ and _23_.

The `HOUR` function is equivalent to `EXTRACT(HOUR FROM timestamp)`.

Example

    -- returns 13
    SELECT HOUR(TIMESTAMP '1994-09-27 13:14:15');

Related functions

  * MINUTE
  * SECOND

### INTERVAL¶

Parses an interval string.

Syntax

    INTERVAL string range

Description

The `INTERVAL` function parses an interval string in the form “dd hh:mm:ss.fff” for SQL intervals of milliseconds, or “yyyy-mm” for SQL intervals of months.

For intervals of milliseconds, these interval ranges apply:

  * DAY
  * MINUTE
  * DAY TO HOUR
  * DAY TO SECOND

For intervals of months, these interval ranges apply:

  * YEAR
  * YEAR TO MONTH

Examples

The following SELECT statements return the values indicated in the comment lines.

    -- returns +10 00:00:00.004
    SELECT INTERVAL '10 00:00:00.004' DAY TO SECOND;

    -- returns +10 00:00:00.000
    SELECT INTERVAL '10' DAY;

    -- returns +2-10
    SELECT INTERVAL '2-10' YEAR TO MONTH;

### LOCALTIME¶

Gets the current local time.

Syntax

    LOCALTIME

Description

The `LOCALTIME` function returns the current SQL time in the local time zone. The return type is `TIME(0)`.

  * In streaming mode, the current local time is evaluated for each record.
  * In batch mode, the current local time is evaluated once when the query starts, and `LOCALTIME` returns the same result for every row.

Example

    -- returns the local machine time as "hh:mm:ss", for example:
    -- 13:16:03
    SELECT LOCALTIME;

### LOCALTIMESTAMP¶

Gets the current timestamp.

Syntax

    LOCALTIMESTAMP

Description

The `LOCALTIMESTAMP` function returns the current SQL timestamp in local time zone. The return type is `TIMESTAMP(3)`.

  * In streaming mode, the current timestamp is evaluated for each record.
  * In batch mode, the current timestamp is evaluated once when the query starts, and `LOCALTIMESTAMP` returns the same result for every row.

Example

    -- returns the local machine datetime as "yyyy-mm-dd hh:mm:ss.sss", for example:
    -- 2023-10-16 13:15:32.390
    SELECT LOCALTIMESTAMP;

### MINUTE¶

Gets the minute of hour from a timestamp.

Syntax

    MINUTE(timestamp)

Description

The `MINUTE` function returns the minute of an hour from the specified SQL timestamp as an integer between _0_ and _59_.

The `MINUTE` function is equivalent to `EXTRACT(MINUTE FROM timestamp)`.

Example

    - returns 14
    SELECT MINUTE(TIMESTAMP '1994-09-27 13:14:15');

Related functions

  * HOUR
  * SECOND

### MONTH¶

Gets the month of year from a DATE.

Syntax

    MONTH(date)

Description

The `MONTH` function returns the month of a year from the specified SQL date as an integer between _1_ and _12_.

The `MONTH` function is equivalent to `EXTRACT(MONTH FROM date)`.

Example

    -- returns 9
    SELECT MONTH(DATE '1994-09-27');

Related functions

  * DAYOFMONTH
  * DAYOFYEAR
  * WEEK
  * YEAR

### NOW¶

Gets the current timestamp.

Syntax

    NOW()

Description

The `NOW` function returns the current SQL timestamp in the local time zone.

The `NOW` function is equivalent to CURRENT_TIMESTAMP.

Example

    -- returns the local machine datetime as "yyyy-mm-dd hh:mm:ss.sss", for example:
    -- 2023-10-16 13:17:54.382
    SELECT NOW();

### OVERLAPS¶

Checks whether two time intervals overlap.

Syntax

    (timepoint1, temporal1) OVERLAPS (timepoint2, temporal2)

Description

The `OVERLAPS` function returns TRUE if two time intervals defined by `(timepoint1, temporal1)` and `(timepoint2, temporal2)` overlap.

The temporal values can be either a time point or a time interval.

Example

    -- returns TRUE
    SELECT (TIME '2:55:00', INTERVAL '1' HOUR) OVERLAPS (TIME '3:30:00', INTERVAL '2' HOUR);

    -- returns FALSE
    SELECT (TIME '9:00:00', TIME '10:00:00') OVERLAPS (TIME '10:15:00', INTERVAL '3' HOUR);

### QUARTER¶

Gets the quarter of year from a DATE.

Syntax

    QUARTER(date)

Description

The `QUARTER` function returns the quarter of a year from the specified SQL DATE as an integer between _1_ and _4_.

The `QUARTER` function is equivalent to `EXTRACT(QUARTER FROM date)`.

Example

    --  returns 3
    SELECT QUARTER(DATE '1994-09-27');

Related functions

  * DAYOFMONTH
  * DAYOFYEAR
  * WEEK
  * YEAR

### SECOND¶

Gets the second of minute from a TIMESTAMP.

Syntax

    SECOND(timestamp)

Description

The `SECOND` function returns the second of a minute from the specified SQL TIMESTAMP as an integer between _0_ and _59_.

The `SECOND` function is equivalent to `EXTRACT(SECOND FROM timestamp)`.

Example

    --  returns 15
    SELECT SECOND(TIMESTAMP '1994-09-27 13:14:15');

Related functions

  * HOUR
  * MINUTE

### SOURCE_WATERMARK¶

Provides a default [watermark](../../../_glossary.html#term-watermark) strategy.

Syntax

    WATERMARK FOR column AS SOURCE_WATERMARK()

Description

The `SOURCE_WATERMARK` function provides a default watermark strategy.

Watermarks are assigned per Kafka partition in the source operator. They are based on a moving histogram of observed out-of-orderness in the table, In other words, the difference between the current event time of an event and the maximum event time seen so far.

The watermark is then assigned as the maximum event time seen to this point, minus the 95% quantile of observed out-of-orderness. In other words, the default watermark strategy aims to assign watermarks so that at most 5% of messages are “late”, meaning they arrive after the watermark.

The minimum out-of-orderness is 50 milliseconds. The maximum out-of-orderness is 7 days.

The algorithm always considers the out-of-orderness of the last 5000 events per partition. During warmup, before the algorithm has seen 1000 messages (per partition) it applies an additional safety margin to the observed out-of-orderness. The safety margin depends on the number of messages seen so far.

Number of messages | Safety margin
---|---
1 - 250 | 7 days
251 - 500 | 30s
501 - 750 | 10s
751 - 1000 | 1s

In effect, the algorithm doesn’t provide a usable watermark before it has seen 250 records per partition.

Example

    -- Create a table that has the default watermark strategy
    -- on the ts column.
    CREATE TABLE t2 (
       i INT,
       ts TIMESTAMP_LTZ(3),
       WATERMARK FOR ts AS SOURCE_WATERMARK());

     -- The queryable schema for the table has the default watermark
     -- strategy on the ts column.
     (
       i INT,
       ts TIMESTAMP_LTZ(3),
       `$rowtime` TIMESTAMP_LTZ(3) NOT NULL METADATA VIRTUAL COMMENT 'SYSTEM',
       WATERMARK FOR ts AS SOURCE_WATERMARK()
    );

Related functions

  * CURRENT_WATERMARK
  * [Watermark clause](../statements/create-table.html#flink-sql-watermark-clause)

### TIME¶

Parses a string to a TIME.

Syntax

    TIME string

Description

The `TIME` function returns a SQL TIME parsed from the specified string.

The time format of the input string must be “hh:mm:ss”.

Example

    -- returns 23:42:55 as a TIME
    SELECT TIME '23:42:55';

### TIMESTAMP¶

Syntax

    TIMESTAMP string

Description

The `TIMESTAMP` function returns a SQL TIMESTAMP parsed from the specified string.

The timestamp format of the input string must be “yyyy-MM-dd hh:mm:ss[.SSS]”.

Example

    -- returns 2023-05-04 23:42:55 as a TIMESTAMP
    SELECT TIMESTAMP '2023-05-04 23:42:55';

### TO_DATE¶

Converts a date string to a DATE.

Syntax

    TO_DATE(string1[, string2])

Description

The `TO_DATE` function converts the date string `string1` with format `string2` to a DATE.

The default format is ‘yyyy-mm-dd’.

Example

    -- returns 2023-05-04 as a DATE
    SELECT TO_DATE('2023-05-04');

### TO_TIMESTAMP¶

Converts a date string to a TIMESTAMP.

Syntax

    TO_TIMESTAMP(string1[, string2])

Description

The `TO_TIMESTAMP` function converts datetime string `string1` with format `string2` under the ‘UTC+0’ time zone to a TIMESTAMP.

The default format is ‘yyyy-mm-dd hh:mm:ss’.

Example

    -- returns 2023-05-04 23:42:55.000 as a TIMESTAMP
    SELECT TO_TIMESTAMP('2023-05-04 23:42:55', 'yyyy-mm-dd hh:mm:ss');

### TO_TIMESTAMP_LTZ¶

Converts a Unix time to a `TIMESTAMP_LTZ`.

Syntax

    TO_TIMESTAMP_LTZ(numeric, precision)
    TO_TIMESTAMP_LTZ(string1[, string2[, string3]])

Description

The first version of the `TO_TIMESTAMP_LTZ` function converts Unix epoch seconds or epoch milliseconds to a `TIMESTAMP_LTZ`.

These are the valid precision values:

  * **0** , which represents `TO_TIMESTAMP_LTZ(epoch_seconds, 0)`
  * **3** , which represents `TO_TIMESTAMP_LTZ(epoch_milliseconds, 3)`

If no precision is provided, the default precision is 3.

The second version converts a timestamp string `string1` with format `string2` (by default ‘yyyy-MM-dd HH:mm:ss.SSS’) in time zone `string3` (by default ‘UTC’) to a TIMESTAMP_LTZ.

If any input is NULL, the function will return NULL.

Examples

    -- convert 1000 epoch seconds
    -- returns 1970-01-01 00:16:40.000 as a TIMESTAMP_LTZ
    SELECT TO_TIMESTAMP_LTZ(1000, 0);

    -- convert 1000 epoch milliseconds
    -- returns 1970-01-01 00:00:01.000 as a TIMESTAMP_LTZ
    SELECT TO_TIMESTAMP_LTZ(1000, 3);

    -- convert timestamp string with custom format and timezone
    -- returns appropriate TIMESTAMP_LTZ based on the timezone
    SELECT TO_TIMESTAMP_LTZ('2023-05-04 12:00:00', 'yyyy-MM-dd HH:mm:ss', 'America/Los_Angeles');

### TIMESTAMPADD¶

Adds a time interval to a datetime.

Syntax

    TIMESTAMPADD(timeintervalunit, interval, timepoint)

Description

Returns the sum of `timepoint` and the `interval` number of time units specified by `timeintervalunit`.

The unit for the interval is given by the first argument, which must be one of the following values:

  * DAY
  * HOUR
  * MINUTE
  * MONTH
  * SECOND
  * YEAR

Example

    -- returns 2000-01-01
    SELECT TIMESTAMPADD(DAY, 1, DATE '1999-12-31');

    -- returns 2000-01-01 01:00:00
    SELECT TIMESTAMPADD(HOUR, 2, TIMESTAMP '1999-12-31 23:00:00');

### TIMESTAMPDIFF¶

Computes the interval between two datetimes.

Syntax

    TIMESTAMPDIFF(timepointunit, timepoint1, timepoint2)

Description

The `TIMESTAMPDIFF` function returns the (signed) number of `timepointunit` between `timepoint1` and `timepoint2`.

The unit for the interval is given by the first argument, which must be one of the following values:

  * DAY
  * HOUR
  * MINUTE
  * MONTH
  * SECOND
  * YEAR

Example

    -- returns -1
    SELECT TIMESTAMPDIFF(DAY, DATE '2000-01-01', DATE '1999-12-31');

    -- returns -2
    SELECT TIMESTAMPDIFF(HOUR, TIMESTAMP '2000-01-01 01:00:00', TIMESTAMP '1999-12-31 23:00:00');

### UNIX_TIMESTAMP¶

Gets the current Unix timestamp in seconds.

Syntax

    UNIX_TIMESTAMP()

Description
    The `UNIX_TIMESTAMP` function is not deterministic, which means the value is recalculated for each row.
Example

    -- returns Epoch seconds, for example:
    -- 1697487923
    SELECT UNIX_TIMESTAMP();

### UNIX_TIMESTAMP¶

Converts a datetime string to a Unix timestamp.

Syntax

    UNIX_TIMESTAMP(string1[, string2])

Description

The `UNIX_TIMESTAMP(string)` function converts the specified datetime string `string1` in format `string2` to a Unix timestamp (in seconds), using the time zone specified in table config.

The default format is “yyyy-MM-dd HH:mm:ss”.

If a time zone is specified in the datetime string and parsed by the UTC+X format, like `yyyy-MM-dd HH:mm:ss.SSS X`, this function uses the specified timezone in the datetime string instead of the timezone in the table configuration. If the datetime string can’t be parsed, the default value of `Long.MIN_VALUE(-9223372036854775808)` is returned.

Examples

    -- returns 1683201600
    SELECT UNIX_TIMESTAMP('2023-05-04 12:00:00');

    -- Returns 25201
    SELECT UNIX_TIMESTAMP('1970-01-01 08:00:01.001', 'yyyy-MM-dd HH:mm:ss.SSS');

    -- Returns 1
    SELECT UNIX_TIMESTAMP('1970-01-01 08:00:01.001 +0800', 'yyyy-MM-dd HH:mm:ss.SSS X');

    -- Returns 25201
    SELECT UNIX_TIMESTAMP('1970-01-01 08:00:01.001 +0800', 'yyyy-MM-dd HH:mm:ss.SSS');

    -- Returns -9223372036854775808
    SELECT UNIX_TIMESTAMP('1970-01-01 08:00:01.001', 'yyyy-MM-dd HH:mm:ss.SSS X');

### WEEK¶

Gets the week of year from a DATE.

Syntax

    WEEK(date)

Description

The `WEEK` function returns the week of a year from the specified SQL DATE as an integer between _1_ and _53_.

The `WEEK` function is equivalent to `EXTRACT(WEEK FROM date)`.

Example

    --  returns 39
    SELECT WEEK(DATE '1994-09-27');

Related functions

  * DAYOFMONTH
  * DAYOFYEAR
  * QUARTER
  * YEAR

### YEAR¶

Gets the year from a DATE.

Syntax

    YEAR(date)

The `YEAR` function returns the year from the specified SQL DATE.

The `YEAR` function is equivalent to `EXTRACT(YEAR FROM date)`.

Example

    --  returns 1994
    SELECT YEAR(DATE '1994-09-27');

Related functions

  * DAYOFMONTH
  * DAYOFYEAR
  * QUARTER
  * MONTH

### Other built-in functions¶

  * [Aggregate Functions](aggregate-functions.html#flink-sql-aggregate-functions)
  * [Collection Functions](collection-functions.html#flink-sql-collection-functions)
  * [Comparison Functions](comparison-functions.html#flink-sql-comparison-functions)
  * [Conditional Functions](conditional-functions.html#flink-sql-conditional-functions)
  * Datetime Functions
  * [Hash Functions](hash-functions.html#flink-sql-hash-functions)
  * [JSON Functions](json-functions.html#flink-sql-json-functions)
  * [ML Preprocessing Functions](ml-preprocessing-functions.html#flink-sql-ml-preprocessing-functions)
  * [Model Inference Functions](model-inference-functions.html#flink-sql-model-inference-functions)
  * [Numeric Functions](numeric-functions.html#flink-sql-numeric-functions)
  * [String Functions](string-functions.html#flink-sql-string-functions)
  * [Table API Functions](table-api-functions.html#flink-table-api-functions)

### Related content¶

  * [User-defined Functions](../../concepts/user-defined-functions.html#flink-sql-udfs)
  * [Create a User Defined Function](../../how-to-guides/create-udf.html#flink-sql-create-udf)

Note

This website includes content developed at the [Apache Software Foundation](https://www.apache.org/) under the terms of the [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0.html).
