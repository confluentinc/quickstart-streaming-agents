---
document_id: flink_reference_functions_collection-functions_chunk_3
source_file: flink_reference_functions_collection-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/collection-functions.html
title: SQL Collection Functions in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 3
---

CARDINALITY(ARRAY['Java', 'SQL', 'Python', 'Rust', 'C++']);

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
