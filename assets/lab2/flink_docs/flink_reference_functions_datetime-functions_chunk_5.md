---
document_id: flink_reference_functions_datetime-functions_chunk_5
source_file: flink_reference_functions_datetime-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/datetime-functions.html
title: SQL Datetime Functions in Confluent Cloud for Apache Flink
chunk_index: 5
total_chunks: 6
---

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
