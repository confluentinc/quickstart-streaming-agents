---
document_id: flink_reference_functions_collection-functions_chunk_1
source_file: flink_reference_functions_collection-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/collection-functions.html
title: SQL Collection Functions in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 3
---

# Collection Functions in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides these built-in collection functions to use in Flink SQL queries:

ARRAY | ARRAY_AGG | ARRAY_APPEND
---|---|---
ARRAY_CONCAT | ARRAY_CONTAINS | ARRAY_DISTINCT
ARRAY_EXCEPT | ARRAY_INTERSECT | ARRAY_JOIN
ARRAY_MAX | ARRAY_MIN | ARRAY_POSITION
ARRAY_PREPEND | ARRAY_REMOVE | ARRAY_REVERSE
ARRAY_SLICE | ARRAY_SORT | ARRAY_UNION
CARDINALITY(array) | CARDINALITY(map) | ELEMENT
GROUP_ID | GROUPING | Implicit row constructor
MAP | MAP_ENTRIES | MAP_FROM_ARRAYS
MAP_KEYS | MAP_UNION | MAP_VALUES

## ARRAY¶

Syntax

    ARRAY ‘[’ value1 [, value2 ]* ‘]’

Description

Creates an array from the specified list of values, `(value1, value2, ...)`.

Use the bracket syntax, `array_name[INT]`, to return the element at position INT in the array.

The index starts at _1_.

Example

    -- returns Java
    SELECT ARRAY['Java', 'SQL'][1];

## ARRAY_AGG¶

Syntax

    ARRAY_AGG([ ALL | DISTINCT ] expression [ RESPECT NULLS | IGNORE NULLS ])

Description

Concatenates the input rows and returns an array, or NULL if there are no input rows.

Use the DISTINCT keyword to specify one unique instance of each value. The ALL keyword concatenates all rows. The default is ALL.

By default, NULL values are respected. You can use IGNORE NULLS to skip NULL values.

Currently, the ORDER BY clause is not supported.

Example

    -- returns:
    -- product_name quantities
    -- Apple        [3, 7]
    -- Orange       [2]
    -- Banana       [5, 4]
    WITH sales_data (id, product_name, quantity_sold) AS (
      VALUES
        (1, 'Apple', 3),
        (2, 'Banana', 5),
        (3, 'Apple', 7),
        (4, 'Orange', 2),
        (5, 'Banana', 4)
    )
    SELECT
      product_name,
      ARRAY_AGG(quantity_sold) AS quantities
    FROM sales_data
    GROUP BY product_name;

## ARRAY_APPEND¶

Syntax

    ARRAY_APPEND(array, element)

Description

Appends an element to the end of the array and returns the result.

If `array` is NULL, the function returns NULL.

If `element` is NULL, the NULL element is added to the end of the array.

Example

    -- returns [SQL,Java,C#]
    SELECT ARRAY_APPEND(ARRAY['SQL', 'Java'], 'C#');

## ARRAY_CONCAT¶

Syntax

    ARRAY_CONCAT(array1, array2, …)

Description

Returns an array that is the result of concatenating at least one array.

The returned array contains all of the elements in the first array, followed by all of the elements in the second array, and so forth, up to the Nth array.

If any input array is NULL, the function returns NULL.

Example

    -- returns [SQL,Java,Python,Python,Rust,Haskell,C#]
    SELECT ARRAY_CONCAT(ARRAY['SQL', 'Java'], ARRAY['Python'], ARRAY['Python', 'Rust', 'Haskell', 'C#']);

## ARRAY_CONTAINS¶

Syntax

    ARRAY_CONTAINS(array, element)

Description

Returns a value indicating whether the `element` exists in `array`.

Checking for NULL elements in the array is supported.

If `array` is NULL, the `ARRAY_CONTAINS` function returns NULL.

The specified element is cast implicitly to the array’s element type, if necessary.

Example

    -- returns TRUE
    SELECT ARRAY_CONTAINS(ARRAY['Java', 'SQL'], 'SQL');

## ARRAY_DISTINCT¶

Syntax

    ARRAY_DISTINCT(array)

Description

Returns an array with unique elements.

If `array` is NULL, the `ARRAY_DISTINCT` function returns NULL.

The order of elements in the source array is preserved in the returned array.

Example

    -- returns [SQL,Java,Python]
    SELECT ARRAY_DISTINCT(ARRAY['SQL', 'Java', 'SQL', 'Python', 'SQL']);

## ARRAY_EXCEPT¶

Syntax

    ARRAY_EXCEPT(array1, array2)

Description

Returns an array that contains the elements from `array1` that are not in `array2`, without duplicates.

The order of the elements from `array1` is retained.

If no elements remain after excluding the elements in `array2` from `array1`, the function returns an empty array.

If one or both arguments are NULL, the function returns NULL.

Example

    -- returns [Java, SQL]
    SELECT ARRAY_EXCEPT(ARRAY['SQL', 'Java', 'Python', 'Rust',], ARRAY['Python', 'Rust', 'Haskell', 'C#']);

## ARRAY_INTERSECT¶

Syntax

    ARRAY_INTERSECT(array1, array2)

Description

Returns an array that contains the elements from `array1` that are also in `array2`, without duplicates.

The order of the elements from `array1` is retained.

If there are no common elements in `array1` and `array2`, the function returns an empty array.

If either array is NULL, the function returns NULL.

Example

    -- returns [Python, Rust]
    SELECT ARRAY_INTERSECT(ARRAY['SQL', 'Java', 'Python', 'Rust',], ARRAY['Python', 'Rust', 'Haskell', 'C#']);
