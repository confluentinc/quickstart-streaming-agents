---
document_id: flink_reference_functions_comparison-functions_chunk_2
source_file: flink_reference_functions_comparison-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/comparison-functions.html
title: SQL comparison functions in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 4
---

FALSE if `boolean` is UNKNOWN.

## Comparison functions¶

BETWEEN | NOT BETWEEN
---|---
IN | NOT IN
IS DISTINCT FROM | IS NOT DISTINCT FROM
IS NULL | IS NOT NULL
LIKE | NOT LIKE
SIMILAR TO | NOT SIMILAR TO
EXISTS |

### BETWEEN¶

Checks whether a value is between two other values.

Syntax

    value1 BETWEEN [ ASYMMETRIC | SYMMETRIC ] value2 AND value3

Description

The `BETWEEN` function returns TRUE if `value1` is greater than or equal to `value2` and less than or equal to `value3`, if ASYMMETRIC is specified. The default is ASYMMETRIC.

If SYMMETRIC is specified, the `BETWEEN` function returns TRUE if `value1` is _inclusively_ between `value2` and `value3`.

When either `value2` or `value3` is NULL, returns FALSE or UNKNOWN.

Examples

    - returns FALSE
    SELECT 12 BETWEEN 15 AND 12;

    - returns TRUE
    SELECT 12 BETWEEN SYMMETRIC 15 AND 12;

    - returns UNKNOWN
    SELECT 12 BETWEEN 10 AND NULL;

    - returns FALSE
    SELECT 12 BETWEEN NULL AND 10;

    - returns UNKNOWN
    SELECT 12 BETWEEN SYMMETRIC NULL AND 12;

### NOT BETWEEN¶

Checks whether a value is not between two other values.

Syntax

    value1 NOT BETWEEN [ ASYMMETRIC | SYMMETRIC ] value2 AND value3

Description

By default (or with the ASYMMETRIC keyword),

The `NOT BETWEEN` function returns TRUE if `value1` is less than `value2` or greater than `value3`, if ASYMMETRIC is specified.

If SYMMETRIC is specified, The `NOT BETWEEN` function returns TRUE if `value1` is not inclusively between `value2` and `value3`.

When either `value2` or `value3` is NULL, returns TRUE or UNKNOWN.

Examples

    -- returns TRUE
    SELECT 12 NOT BETWEEN 15 AND 12;

    -- returns FALSE
    SELECT 12 NOT BETWEEN SYMMETRIC 15 AND 12;

    -- returns UNKNOWN
    SELECT 12 NOT BETWEEN NULL AND 15;

    -- returns TRUE
    SELECT 12 NOT BETWEEN 15 AND NULL;

    --  returns UNKNOWN
    SELECT 12 NOT BETWEEN SYMMETRIC 12 AND NULL;

### EXISTS¶

Check whether a query returns a row.

Syntax

    EXISTS (sub-query)

Description

The `EXISTS` function returns TRUE if `sub-query` returns at least one row.

The `EXISTS` function is supported only if the operation can be rewritten in a join and group operation.

For streaming queries, the operation is rewritten in a join and group operation.

The required state to compute the query result might grow indefinitely, depending on the number of distinct input rows. Provide a query configuration with valid retention interval to prevent excessive state size.

Examples

    SELECT user_id, item_id
    FROM user_behavior
    WHERE EXISTS (
      SELECT * FROM category
      WHERE category.item_id = user_behavior.item_id
      AND category.name = 'book'
    );

### IN¶

Checks whether a value exists in a list.

Syntax

    value1 IN (value2 [, value3]* )
    value IN (sub-query)

Description

The `IN` function returns TRUE if `value1` exists in the specified list `(value2, value3, ...)`.

If a subquery is specified, The `IN` function returns TRUE if `value` is equal to a row returned by `sub-query`.

When `(value2, value3, ...)` contains NULL, The `IN` function returns TRUE if the element can be found and UNKNOWN otherwise.

Always returns UNKNOWN if `value1` is NULL.

Examples

    -- returns FALSE
    SELECT 4 IN (1, 2, 3);

    -- returns TRUE
    SELECT 1 IN (1, 2, NULL);

    -- returns UNKNOWN
    SELECT 4 IN (1, 2, NULL);

### NOT IN¶

Checks whether a value doesn’t exist in a list.

Syntax

    value1 NOT IN (value2 [, value3]* )
    value NOT IN (sub-query)

Description

The `NOT IN` function returns TRUE if `value1` does not exist in the specified list `(value2, value3, ...)`.

If a subquery is specified, The `NOT IN` function returns TRUE if `value` isn’t equal to a row returned by `sub-query`.

When `(value2, value3, ...)` contains NULL, the `NOT IN` function returns FALSE if `value1` can be found and UNKNOWN otherwise.

Always returns UNKNOWN if value1 is NULL.

Examples

    -- returns TRUE
    SELECT 4 NOT IN (1, 2, 3);

    -- returns FALSE
    SELECT 1 NOT IN (1, 2, NULL);

    -- returns UNKNOWN
    SELECT 4 NOT IN (1, 2, NULL);

### IS DISTINCT FROM¶

Checks whether two values are different.

Syntax

    value1 IS DISTINCT FROM value2

Description

The `IS DISTINCT FROM` function returns TRUE if two values are different.

NULL values are treated as identical.

Examples

    --  returns TRUE
    SELECT 1 IS DISTINCT FROM 2;

    --  returns TRUE
    SELECT 1 IS DISTINCT FROM NULL;

    --  returns FALSE
    SELECT NULL IS DISTINCT FROM NULL;

### IS NOT DISTINCT FROM¶

Checks whether two values are equal.

Syntax

    value1 IS NOT DISTINCT FROM value2

Description

The `IS NOT DISTINCT FROM` function returns TRUE if two values are equal.
