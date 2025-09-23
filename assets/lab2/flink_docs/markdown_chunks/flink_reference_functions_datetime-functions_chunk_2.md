---
document_id: flink_reference_functions_datetime-functions_chunk_2
source_file: flink_reference_functions_datetime-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/datetime-functions.html
title: SQL Datetime Functions in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 6
---

| YEAR | | |

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
