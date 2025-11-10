---
document_id: flink_reference_functions_aggregate-functions_chunk_2
source_file: flink_reference_functions_aggregate-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/aggregate-functions.html
title: SQL aggregate functions in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 3
---

('first'), ('second'), ('third')) AS my_values;

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
