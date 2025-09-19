---
document_id: flink_reference_functions_aggregate-functions_chunk_3
source_file: flink_reference_functions_aggregate-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/aggregate-functions.html
title: SQL aggregate functions in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 3
---

my_values; Related function * STDDEV_POP

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
