---
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/collection-functions.html
title: SQL Collection Functions in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'functions', 'collection-functions.html']
scraped_date: 2025-09-05T13:50:21.279836
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

## ARRAY_JOIN¶

Syntax

    ARRAY_JOIN(array, delimiter [, nullReplacement])

Description

Returns a string that represents the concatenation of the elements in `array`. Elements are cast to their string representation.

The `delimiter` is a string that separates each pair of consecutive elements of the array.

The optional `nullReplacement` is a string that replaces null elements in the array. If `nullReplacement` is not specified, null elements in the array are omitted from the resulting string.

Returns NULL if any of the inputs is NULL.

Example

    -- returns "Java, SQL, Python, not specified"
    SELECT ARRAY_JOIN(ARRAY['Java', 'SQL', 'Python', NULL], ', ', 'not specified');

## ARRAY_MAX¶

Syntax

    ARRAY_MAX(array)

Description
    Returns the maximum value from `array`, or NULL if `array` is NULL.
Example

    -- returns 4
    SELECT ARRAY_MAX(ARRAY[1, 2, 3, 4]);

## ARRAY_MIN¶

Syntax

    ARRAY_MIN(array)

Description
    Returns the minimum value from `array`, or NULL if `array` is NULL.
Example

    -- returns 1
    SELECT ARRAY_MIN(ARRAY[1, 2, 3, 4]);

## ARRAY_POSITION¶

Syntax

    ARRAY_POSITION(array, element)

Description

Returns the position of the first occurrence of `element` in `array` as an integer. The index is 1-based, so the first element in the array has index 1.

Returns 0 if `element` is not found in `array`.

Returns NULL if either of the arguments is NULL.

Example

    -- returns 2
    SELECT ARRAY_POSITION(ARRAY['Java', 'SQL', 'Python'], 'SQL');

## ARRAY_PREPEND¶

Syntax

    ARRAY_PREPEND(array, element)

Description

Prepends an element to the beginning of the array and returns the result.

If `array` is NULL, the function returns NULL.

If `element` is NULL, the NULL element is prepended to the beginning of the array.

Example

    -- returns [SQL,Java,Python]
    SELECT ARRAY_PREPEND(ARRAY['Java', 'Python'], 'SQL');

## ARRAY_REMOVE¶

Syntax

    ARRAY_REMOVE(array, element)

Description

Removes from `array` all elements that are equal to `element`. Order of elements is retained.

If `array` is NULL, the function returns NULL.

Example

    -- returns [Java,Python]
    SELECT ARRAY_REMOVE(ARRAY['Java', 'SQL', 'Python'], 'SQL');

## ARRAY_REVERSE¶

Syntax

    ARRAY_REVERSE(array)

Description

Returns an array that has elements in the reverse order of the elements in `array`.

If `array` is NULL, the function returns NULL.

Example

    -- returns [Python,SQL,Java]
    SELECT ARRAY_REVERSE(ARRAY['Java', 'SQL', 'Python']);

## ARRAY_SLICE¶

Syntax

    ARRAY_SLICE(array, start_offset [, end_offset])

Description

Returns a subarray of the input array between `start_offset` and `end_offset`, inclusive. The offsets are 1-based, but 0 is also treated as the beginning of the array.

Elements of the subarray are returned in the order they appear in `array`.

Positive values are counted from the beginning of the array. Negative values are counted from the end.

If `end_offset` is omitted, this offset is treated as the length of the array.

If `start_offset` is after `end_offset`, or both are out of array bounds, an empty array is returned.

Returns NULL if any input value is NULL.

Example

    -- returns [SQL,Python,C#,JavaScript]
    SELECT ARRAY_SLICE(ARRAY['Java', 'SQL', 'Python', 'C#', 'JavaScript', 'Go'], 2, 5);

## ARRAY_SORT¶

Syntax

    ARRAY_SORT(array [, ascending_order [, null_first]])

Description

Returns an array that has the elements of `array` in sorted order.

When only `array` is specified, the function defaults to ascending order with NULLs at the start.

Specifying `ascending_order` as `TRUE` orders the array in ascending order, with NULLs first. Setting `ascending_order` to `FALSE` orders the array in descending order, with NULLs last.

Independently, specifying `null_first` as TRUE moves NULLs to the beginning. specifying `null_first` as FALSE moves NULLs to the end, irrespective of the sorting order.

The function returns NULL if any input is NULL.

Example

    -- returns [1,2,3,4,5]
    SELECT ARRAY_SORT(ARRAY[5,4,3,2,1]);
    
    -- returns [NULL,SQL,Python,Java,Go,C#]
    SELECT ARRAY_SORT(ARRAY['Java', 'SQL', 'Python', NULL, 'Go', 'C#'], FALSE, TRUE);

## ARRAY_UNION¶

Syntax

    ARRAY_UNION(array1, array2)

Description

Returns an array that has the elements from the union of `array1` and `array2`. Duplicate elements are removed.

If `array1` or `array2` is NULL, the function returns NULL.

Example

    -- returns [Java,SQL,Python,C#,Go]
    SELECT ARRAY_UNION(ARRAY['Java', 'SQL', 'Python'], ARRAY['C#', 'SQL', 'Go']);

## CARDINALITY(array)¶

Syntax

    CARDINALITY(array)

Description
    Returns the number of elements in the specified array.
Example

    -- returns 5
    SELECT CARDINALITY(ARRAY['Java', 'SQL', 'Python', 'Rust', 'C++']);

## CARDINALITY(map)¶

Syntax

    CARDINALITY(map)

Description
    Returns the number of entries in the specified map.
Example

    -- returns 3
    SELECT CARDINALITY(MAP['Java', 5, 'SQL', 4, 'Python', 3]);

## ELEMENT¶

Syntax

    ELEMENT(array)

Description

Returns the sole element of the specified array. The cardinality of `array` must be _1_.

Returns NULL if `array` is empty.

Throws an exception if `array` has more than one element.

Example

    -- returns Java
    SELECT ELEMENT(ARRAY['Java']);

## GROUP_ID¶

Syntax

    GROUP_ID()

Description
    Returns an integer that uniquely identifies the combination of grouping keys.

## GROUPING¶

Syntax

    GROUPING(expression1 [, expression2]* )
    GROUPING_ID(expression1 [, expression2]* )

Description
    Returns a bit vector of the specified grouping expressions.

## Implicit row constructor¶

Syntax

    (value1 [, value2]*)

Description

Returns a row created from a list of values, `(value1, value2,...)`.

The implicit row constructor supports arbitrary expressions as fields and requires at least two fields.

The explicit row constructor can deal with an arbitrary number of fields but doesn’t support all kinds of field expressions.

Example

    -- returns (1, SQL)
    SELECT (1, 'SQL');

## MAP¶

Syntax

    MAP [ key1, value1 [, key2, value2 ], ... ]

Description

Returns a map created from the specified list of key-value pairs, `((key1, value1), (key2, value2), ...)`.

Use the bracket syntax, `map_name[key]`, to return the value that corresponds with the specified key.

Example

    -- returns 4
    SELECT MAP['Java', 5, 'SQL', 4, 'Python', 3]['SQL'];

## MAP_ENTRIES¶

Syntax

    MAP_ENTRIES(map)

Description
    Returns an array with all elements in `map`. Order of elements in the returned array is not guaranteed.
Example

    -- returns [Java,5,SQL,4,Python,3]
    SELECT MAP_ENTRIES(MAP['Java', 5, 'SQL', 4, 'Python', 3]);

## MAP_FROM_ARRAYS¶

Syntax

    MAP_FROM_ARRAYS(array_of_keys, array_of_values)

Description
    Returns a map created from an array of keys and an array of and values. The lengths of `array_of_keys` and `array_of_values` must be the same.
Example

    -- returns {key1=Python, key2=SQL, key3=Java}
    SELECT MAP_FROM_ARRAYS(ARRAY['key1', 'key2', 'key3'], ARRAY['Python', 'SQL', 'Java']);

## MAP_KEYS¶

Syntax

    MAP_KEYS(map)

Description
    Returns the keys of `map` as an array. Order of elements in the returned array is not guaranteed.
Example

    -- returns [Java,Python,SQL]
    SELECT MAP_KEYS(MAP['Java', 5, 'SQL', 4, 'Python', 3]);

## MAP_UNION¶

Syntax

    MAP_UNION(map1, …)

Description

Returns a map created by merging at least one map. The maps must have a common map type.

If there are overlapping keys, the value from `map2` overwrites the value from `map1`, the value from `map3` overwrites the value from `map2`, the value from `mapn` overwrites the value from `map(n-1)`.

If any of the maps is NULL, the function returns NULL.

Example

    -- returns ['Java', 5, 'SQL', 4, 'Python', 3, 'C#', 2, 'Rust', 1]
    SELECT MAP_UNION(MAP['Java', 5, 'SQL', 4, 'Python', 3], MAP['C#', 2, 'Rust', 1]);

## MAP_VALUES¶

Syntax

    MAP_VALUES(map)

Description
    Returns the values of `map` as an array. Order of elements in the returned array is not guaranteed.
Example

    -- returns [3,5,4]
    SELECT MAP_VALUES(MAP['Java', 5, 'SQL', 4, 'Python', 3]);

## Other built-in functions¶

  * [Aggregate Functions](aggregate-functions.html#flink-sql-aggregate-functions)
  * Collection Functions
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

## Related content¶

  * [User-defined Functions](../../concepts/user-defined-functions.html#flink-sql-udfs)
  * [Create a User Defined Function](../../how-to-guides/create-udf.html#flink-sql-create-udf)

Note

This website includes content developed at the [Apache Software Foundation](https://www.apache.org/) under the terms of the [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0.html).
