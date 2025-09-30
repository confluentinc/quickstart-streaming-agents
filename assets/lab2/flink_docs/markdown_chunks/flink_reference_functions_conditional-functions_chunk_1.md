---
document_id: flink_reference_functions_conditional-functions_chunk_1
source_file: flink_reference_functions_conditional-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/conditional-functions.html
title: SQL conditional functions in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Conditional Functions in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides these built-in functions for controlling execution flow in SQL queries:

CASE | CASE WHEN CONDITION | COALESCE
---|---|---
GREATEST | IF | IFNULL
IS_ALPHA | IS_DECIMAL | IS_DIGIT
LEAST | NULLIF |

## CASE¶

Syntax

    CASE value
      WHEN value1_1 [, value1_2]* THEN result1
      (WHEN value2_1 [, value2_2 ]* THEN result2)*
      (ELSE result_z)
    END

Description
    Returns `resultX` when the specified value is contained in `(valueX_1, valueX_2, ...)`. If no value matches, `CASE` returns `result_z`, if it’s provided, otherwise NULL.

## CASE WHEN CONDITION¶

Syntax

    CASE
      WHEN condition1 THEN result1
      (WHEN condition2 THEN result2)*
      (ELSE result_z)
    END

Returns `resultX` when the first `conditionX` is met. When no condition is met, returns `result_z`, if it’s provided, otherwise NULL.

## COALESCE¶

Syntax

    COALESCE(value1 [, value2]*)

Returns the first argument that is not NULL.

If all arguments are NULL, the `COALESCE` function returns NULL.

The return type is the least-restrictive, common type of all the arguments.

The return type is nullable if all arguments are nullable as well.

Example

The following SELECT statements return the values indicated in the comment lines.

    -- Returns 'default'
    SELECT COALESCE(NULL, 'default');

    -- Returns the first non-null value among column0 and column1,
    -- or 'default' if column0 and column1 are both NULL.
    SELECT COALESCE(column0, column1, 'default');

## GREATEST¶

Syntax

    GREATEST(value1[, value2]*)

Returns the greatest value in the specified list of arguments. Returns NULL if any argument is NULL.

Example

    -- returns 4
    SELECT GREATEST(1, 2, 3, 4);

    -- returns d
    SELECT GREATEST('a', 'b', 'c', 'd');

## IF¶

Syntax

    IF(condition, true_value, false_value)

Returns the `true_value` if `condition` is met, otherwise `false_value`.

Example

The following SELECT statements return the values indicated in the comment lines.

    -- returns 5
    SELECT IF(5 > 3, 5, 3);

## IFNULL¶

Syntax

    IFNULL(input, null_replacement)

Returns `null_replacement` if `input` is NULL; otherwise returns `input`.

The `IFNULL` function enables passing nullable columns into a function or table that is declared with a NOT NULL constraint.

Compared with COALESCE or CASE, the `IFNULL` function returns a data type that’s specific with respect to nullability. The returned type is the common type of both arguments but only nullable if the `null_replacement` is nullable.

For example, `IFNULL(nullable_column, 5)` never returns NULL.

## IS_ALPHA¶

Syntax

    IS_ALPHA(string)

Returns TRUE if all characters in the specified string are alphabetic, otherwise FALSE.

Example

    -- returns FALSE
    SELECT IS_ALPHA('42');

    -- returns TRUE
    SELECT IS_ALPHA('string');

## IS_DECIMAL¶

Syntax

    IS_DECIMAL(string)

Returns TRUE if the specified string can be parsed to a valid NUMERIC, otherwise FALSE.

Example

    -- returns TRUE
    SELECT IS_DECIMAL('23');

    -- returns FALSE
    SELECT IS_DECIMAL('not a number');

## IS_DIGIT¶

Syntax

    IS_DIGIT(string)

Returns TRUE if all characters in the specified string are digits, otherwise FALSE.

Example

    -- returns TRUE
    SELECT IS_DIGIT('23');

    -- returns FALSE
    SELECT IS_DIGIT('2 not a digit 3');

## LEAST¶

Syntax

    LEAST(value1[, value2]*)

Returns the lowest value in the specified list of arguments. Returns NULL if any argument is NULL.

Example

    -- returns 1
    SELECT LEAST(1, 2, 3, 4);

    -- returns a
    SELECT LEAST('a', 'b', 'c', 'd');

## NULLIF¶

Syntax

    NULLIF(value1, value2)

Description
    Returns NULL if `value1` is equal to `value2`, otherwise returns `value1`.
Example

    -- returns NULL
    SELECT NULLIF(5, 5);

    -- returns 5
    SELECT NULLIF(5, 0);

## Other built-in functions¶

* [Aggregate Functions](aggregate-functions.html#flink-sql-aggregate-functions)
* [Collection Functions](collection-functions.html#flink-sql-collection-functions)
* [Comparison Functions](comparison-functions.html#flink-sql-comparison-functions)
* Conditional Functions
* [Datetime Functions](datetime-functions.html#flink-sql-datetime-functions)
* [Hash Functions](hash-functions.html#flink-sql-hash-functions)
* [JSON Functions](json-functions.html#flink-sql-json-functions)
* [ML Preprocessing Functions](ml-preprocessing-functions.html#flink-sql-ml-preprocessing-functions)
* [Model Inference Functions](model-inference-functions.html#flink-sql-model-inference-functions)
* [Numeric Functions](numeric-functions.html#flink-sql-numeric-functions)
* [String Functions](string-functions.html#flink-sql-string-functions)
* [Table API Functions](table-api-functions.html#flink-table-api-functions)
