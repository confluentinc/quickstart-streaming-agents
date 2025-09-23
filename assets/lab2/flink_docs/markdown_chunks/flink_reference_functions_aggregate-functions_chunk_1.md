---
document_id: flink_reference_functions_aggregate-functions_chunk_1
source_file: flink_reference_functions_aggregate-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/aggregate-functions.html
title: SQL aggregate functions in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 3
---

# Aggregate Functions in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides these built-in functions to aggregate rows in Flink SQL queries:

AVG | COLLECT | COUNT | CUME_DIST
---|---|---|---
DENSE_RANK | FIRST_VALUE | LAG | LAST_VALUE
LEAD | LISTAGG | MAX | MIN
NTILE | PERCENT_RANK | RANK | ROW_NUMBER
STDDEV_POP | STDDEV_SAMP | SUM | VAR_POP
VAR_SAMP | VARIANCE |  |

The aggregate functions take an expression across all the rows as the input and return a single aggregated value as the result.

## AVG¶

Syntax

    AVG([ ALL | DISTINCT ] expression)

Description

By default or with keyword `ALL`, returns the average (arithmetic mean) of `expression` over all input rows.

Use `DISTINCT` to return one unique instance of each value.

Example

    -- returns 1.500000
    SELECT AVG(my_values)
    FROM (VALUES (0.0), (1.0), (2.0), (3.0)) AS my_values;

## COLLECT¶

Syntax

    COLLECT([ ALL | DISTINCT ] expression)

Description

By default or with the `ALL` keyword, returns a multiset of `expression` over all input rows.

NULL values are ignored.

Use `DISTINCT` to return one unique instance of each value.

## COUNT¶

Syntax

    COUNT([ ALL ] expression | DISTINCT expression1 [, expression2]*)

Description

By default or with `ALL`, returns the number of input rows for which expression isn’t NULL.

Use `DISTINCT` to return one unique instance of each value.

Use `COUNT(*)` or `COUNT(1)` to return the number of input rows.

Example

    -- returns 4
    SELECT COUNT(my_values)
    FROM (VALUES (0), (1), (2), (3)) AS my_values;

## CUME_DIST¶

Syntax

    CUME_DIST()

Description
    Returns the cumulative distribution of a value in a group of values. The result is the number of rows preceding or equal to the current row in the partition ordering divided by the number of rows in the window partition.

## DENSE_RANK¶

Syntax

    DENSE_RANK()

Description

Returns the rank of a value in a group of values.

The result is one plus the previously assigned rank value.

Unlike the RANK function, `DENSE_RANK` doesn’t produce gaps in the ranking sequence.

Related function

* RANK

## FIRST_VALUE¶

Syntax

    FIRST_VALUE(expression)

Description
    Returns the first value in an ordered set of values.
Example

    -- returns first
    SELECT FIRST_VALUE(my_values)
    FROM (VALUES ('first'), ('second'), ('third')) AS my_values;

Related function

* LAST_VALUE

## LAG¶

Syntax

    LAG(expression [, offset] [, default])

Description

Returns the value of expression at the offsetth row _before_ the current row in the window.

The default value of `offset` is _1_ , and the default value of the `default` argument is NULL.

Example

The following example shows how to use the LAG function to see player scores changing over time.

    SELECT $rowtime AS row_time
      , player_id
      , game_room_id
      , points
      , LAG(points, 1) OVER (PARTITION BY player_id ORDER BY $rowtime) previous_points_value
     FROM gaming_player_activity;

For the full code example, see [Compare Current and Previous Values in a Data Stream](../../how-to-guides/compare-current-and-previous-values.html#flink-sql-compare-values-query).

Related function

* LEAD

## LAST_VALUE¶

Syntax

    LAST_VALUE(expression)

Description
    Returns the last value in an ordered set of values.
Example

    -- returns third
    SELECT LAST_VALUE(my_values)
    FROM (VALUES ('first'), ('second'), ('third')) AS my_values;

Related function

* FIRST_VALUE

## LEAD¶

Syntax

    LEAD(expression [, offset] [, default])

Description

Returns the value of the expression at the offsetth row _after_ the current row in the window.

The default value of `offset` is _1_ , and the default value of the `default` argument is NULL.

Related function

* LAG

## LISTAGG¶

Syntax

    LISTAGG(expression [, separator])

Description

Concatenates the values of string expressions and inserts separator values between them.

The separator isn’t added at the end of string.

The default value of separator is `','`.

Example

    -- returns first,second,third
    SELECT LISTAGG(my_values)
    FROM (VALUES ('first'), ('second'), ('third')) AS my_values;
