---
document_id: flink_reference_functions_comparison-functions_chunk_1
source_file: flink_reference_functions_comparison-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/comparison-functions.html
title: SQL comparison functions in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 4
---

# Comparison Functions in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides these built-in comparison functions to use in SQL queries:

* Equality operations
* Logical operations
* Comparison Functions
* Conversion functions

## Equality operations¶

SQL function | Description
---|---
`value1 = value2` | Returns TRUE if value1 is equal to value2. Returns UNKNOWN if value1 or value2 is NULL.
`value1 <> value2` | Returns TRUE if value1 is not equal to value2. Returns UNKNOWN if value1 or value2 is NULL.
`value1 > value2` | Returns TRUE if value1 is greater than value2. Returns UNKNOWN if value1 or value2 is NULL.
`value1 >= value2` | Returns TRUE if value1 is greater than or equal to value2. Returns UNKNOWN if value1 or value2 is NULL.
`value1 < value2` | Returns TRUE if value1 is less than value2. Returns UNKNOWN if value1 or value2 is NULL.
`value1 <= value2` | Returns TRUE if value1 is less than or equal to value2. Returns UNKNOWN if value1 or value2 is NULL.

## Logical operations¶

Logical operation | Description
---|---
`boolean1 OR boolean2` | Returns TRUE if `boolean1` is TRUE or `boolean2` is TRUE. Supports three-valued logic. For example, `TRUE || NULL(BOOLEAN)` returns TRUE.
`boolean1 AND boolean2` | Returns TRUE if `boolean1` and `boolean2` are both TRUE. Supports three-valued logic. For example, `TRUE && NULL(BOOLEAN)` returns UNKNOWN.
`NOT boolean` | Returns TRUE if `boolean` is FALSE; returns FALSE if `boolean` is TRUE; returns UNKNOWN if boolean is UNKNOWN.
`boolean IS FALSE` | Returns TRUE if `boolean` is FALSE; returns FALSE if `boolean` is TRUE or UNKNOWN.
`boolean IS NOT FALSE` | Returns TRUE if `boolean` is TRUE or UNKNOWN; returns FALSE if `boolean` is FALSE.
`boolean IS TRUE` | Returns TRUE if `boolean` is TRUE; returns FALSE if `boolean` is FALSE or UNKNOWN.
`boolean IS NOT TRUE` | Returns TRUE if `boolean` is FALSE or UNKNOWN; returns FALSE if `boolean` is TRUE.
`boolean IS UNKNOWN` | Returns TRUE if `boolean` is UNKNOWN; returns FALSE if `boolean` is TRUE or FALSE.
`boolean IS NOT UNKNOWN` | Returns TRUE if `boolean` is TRUE or FALSE; returns FALSE if `boolean` is UNKNOWN.
