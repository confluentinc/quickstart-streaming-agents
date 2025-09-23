---
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/aggregate-functions.html
title: SQL aggregate functions in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'functions', 'aggregate-functions.html']
scraped_date: 2025-09-05T13:50:19.104898
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

## MAX¶

Syntax

    MAX([ ALL | DISTINCT ] expression)

Description

By default or with the `ALL` keyword, returns the maximum value of `expression` over all input rows.

Use `DISTINCT` to return one unique instance of each value.

Examples

    -- returns 3
    SELECT MAX(my_values)
    FROM (VALUES (0), (1), (2), (3)) AS my_values;

The following example shows how to use the MAX function to find the highest player score in a tumbling window.

    SELECT
      window_start,
      window_end,
      SUM(points) AS total,
      MIN(points) as min_points,
      MAX(points) as max_points
    FROM TABLE(TUMBLE(TABLE gaming_player_activity_source, DESCRIPTOR($rowtime), INTERVAL '10' SECOND))
    GROUP BY window_start, window_end;

For the full code example, see [Aggregate a Stream in a Tumbling Window](../../how-to-guides/aggregate-tumbling-window.html#flink-sql-aggregate-tumbling-window-declare-table).

Related function

* MIN

## MIN¶

Syntax

    MIN([ ALL | DISTINCT ] expression )

Description

By default or with the `ALL` keyword, returns the minimum value of `expression` across all input rows.

Use `DISTINCT` to return one unique instance of each value.

Examples

    -- returns 0
    SELECT MIN(my_values)
    FROM (VALUES (0), (1), (2), (3)) AS my_values;

The following example shows how to use the MIN function to find the lowest player score in a tumbling window.

    SELECT
      window_start,
      window_end,
      SUM(points) AS total,
      MIN(points) as min_points,
      MAX(points) as max_points
    FROM TABLE(TUMBLE(TABLE gaming_player_activity_source, DESCRIPTOR($rowtime), INTERVAL '10' SECOND))
    GROUP BY window_start, window_end;

For the full code example, see [Aggregate a Stream in a Tumbling Window](../../how-to-guides/aggregate-tumbling-window.html#flink-sql-aggregate-tumbling-window-declare-table).

Related function

* MAX

## NTILE¶

Syntax

    NTILE(n)

Description

Divides the rows for each window partition into `n` buckets ranging from _1_ to at most `n`.

If the number of rows in the window partition doesn’t divide evenly into the number of buckets, the remainder values are distributed one per bucket, starting with the first bucket.

For example, with _6_ rows and _4_ buckets, the bucket values would be:

    1 1 2 2 3 4

## PERCENT_RANK¶

Syntax

    PERCENT_RANK()

Description

Returns the percentage ranking of a value in a group of values.

The result is the rank value minus one, divided by the number of rows in the partition minus one.

If the partition only contains one row, the `PERCENT_RANK` function returns _0_.

## RANK¶

Syntax

    RANK()

Description

Returns the rank of a value in a group of values.

The result is one plus the number of rows preceding or equal to the current row in the partition ordering.

The values produce gaps in the sequence.

Related functions

* DENSE_RANK
* ROW_NUMBER

## ROW_NUMBER¶

Syntax

    ROW_NUMBER()

Description

Assigns a unique, sequential number to each row, starting with one, according to the ordering of rows within the window partition.

The `ROW_NUMBER` and `RANK` functions are similar. `ROW_NUMBER` numbers all rows sequentially, for example, `1, 2, 3, 4, 5`. `RANK` provides the same numeric value for ties, for example `1, 2, 2, 4, 5`.

Related functions

* RANK
* DENSE_RANK

## STDDEV_POP¶

Syntax

    STDDEV_POP([ ALL | DISTINCT ] expression)

Description

By default or with the `ALL` keyword, returns the population standard deviation of `expression` over all input rows.

Use `DISTINCT` to return one unique instance of each value.

Example

    -- returns 0.986154
    SELECT STDDEV_POP(my_values)
    FROM (VALUES (0.5), (1.5), (2.2), (3.2)) AS my_values;

Related function

* STDDEV_SAMP

## STDDEV_SAMP¶

Syntax

    STDDEV_SAMP([ ALL | DISTINCT ] expression)

Description

By default or with the `ALL` keyword, returns the sample standard deviation of `expression` over all input rows.

Use `DISTINCT` to return one unique instance of each value.

Example

    -- returns 1.138713
    SELECT STDDEV_SAMP(my_values)
    FROM (VALUES (0.5), (1.5), (2.2), (3.2)) AS my_values;

Related function

* STDDEV_POP

## SUM¶

Syntax

    SUM([ ALL | DISTINCT ] expression)

By default or with the `ALL` keyword, returns the sum of `expression` across all input rows.

Use `DISTINCT` to return one unique instance of each value.

Examples

    -- returns 6
    SELECT SUM(my_values)
    FROM (VALUES (0), (1), (2), (3)) AS my_values;

The following example shows how to use the SUM function to find the total of player scores in a tumbling window.

    SELECT
      window_start,
      window_end,
      SUM(points) AS total,
      MIN(points) as min_points,
      MAX(points) as max_points
    FROM TABLE(TUMBLE(TABLE gaming_player_activity_source, DESCRIPTOR($rowtime), INTERVAL '10' SECOND))
    GROUP BY window_start, window_end;

For the full code example, see [Aggregate a Stream in a Tumbling Window](../../how-to-guides/aggregate-tumbling-window.html#flink-sql-aggregate-tumbling-window-declare-table).

## VAR_POP¶

Syntax

    VAR_POP([ ALL | DISTINCT ] expression)

Description

By default or with the `ALL` keyword, returns the population variance, which is the square of the population standard deviation, of `expression` over all input rows.

Use `DISTINCT` to return one unique instance of each value.

Example

    -- returns 0.972500
    SELECT VAR_POP(my_values)
    FROM (VALUES (0.5), (1.5), (2.2), (3.2)) AS my_values;

Related function

* VAR_SAMP

## VAR_SAMP¶

Syntax

    VAR_SAMP([ ALL | DISTINCT ] expression)

Description

By default or with the `ALL` keyword, returns the sample variance, which is the square of the sample standard deviation, of `expression` over all input rows.

Use `DISTINCT` to return one unique instance of each value.

The `VARIANCE` function is equivalent to `VAR_SAMP`.

Example

    -- returns 1.296667
    SELECT VAR_SAMP(my_values)
    FROM (VALUES (0.5), (1.5), (2.2), (3.2)) AS my_values;

Related functions

* STDDEV_POP
* VARIANCE

## VARIANCE¶

Syntax

    VARIANCE([ ALL | DISTINCT ] expression)

Description
    Equivalent to VAR_SAMP.

## Other built-in functions¶

* Aggregate Functions
* [Collection Functions](collection-functions.html#flink-sql-collection-functions)
* [Comparison Functions](comparison-functions.html#flink-sql-comparison-functions)
* [Conditional Functions](conditional-functions.html#flink-sql-conditional-functions)
* [Datetime Functions](datetime-functions.html#flink-sql-datetime-functions)
* [Hash Functions](hash-functions.html#flink-sql-hash-functions)
* [JSON Functions](json-functions.html#flink-sql-json-functions)
* [ML Preprocessing Functions](ml-preprocessing-functions.html#flink-sql-ml-preprocessing-functions)
* [Model Inference Functions](model-inference-functions.html#flink-sql-model-inference-functions)
* [Numeric Functions](numeric-functions.html#flink-sql-numeric-functions)
* [String Functions](string-functions.html#flink-sql-string-functions)
* [Table API Functions](table-api-functions.html#flink-table-api-functions)
