---
document_id: flink_reference_functions_datetime-functions_chunk_4
source_file: flink_reference_functions_datetime-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/datetime-functions.html
title: SQL Datetime Functions in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 6
---

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
