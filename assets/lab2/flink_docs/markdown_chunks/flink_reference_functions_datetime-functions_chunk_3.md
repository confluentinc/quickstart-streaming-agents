---
document_id: flink_reference_functions_datetime-functions_chunk_3
source_file: flink_reference_functions_datetime-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/datetime-functions.html
title: SQL Datetime Functions in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 6
---

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
