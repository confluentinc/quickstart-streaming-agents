---
document_id: flink_reference_functions_datetime-functions_chunk_6
source_file: flink_reference_functions_datetime-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/datetime-functions.html
title: SQL Datetime Functions in Confluent Cloud for Apache Flink
chunk_index: 6
total_chunks: 6
---

Examples

    -- returns 1683201600
    SELECT UNIX_TIMESTAMP('2023-05-04 12:00:00');

    -- Returns 25201
    SELECT UNIX_TIMESTAMP('1970-01-01 08:00:01.001', 'yyyy-MM-dd HH:mm:ss.SSS');

    -- Returns 1
    SELECT UNIX_TIMESTAMP('1970-01-01 08:00:01.001 +0800', 'yyyy-MM-dd HH:mm:ss.SSS X');

    -- Returns 25201
    SELECT UNIX_TIMESTAMP('1970-01-01 08:00:01.001 +0800', 'yyyy-MM-dd HH:mm:ss.SSS');

    -- Returns -9223372036854775808
    SELECT UNIX_TIMESTAMP('1970-01-01 08:00:01.001', 'yyyy-MM-dd HH:mm:ss.SSS X');

### WEEK¶

Gets the week of year from a DATE.

Syntax

    WEEK(date)

Description

The `WEEK` function returns the week of a year from the specified SQL DATE as an integer between _1_ and _53_.

The `WEEK` function is equivalent to `EXTRACT(WEEK FROM date)`.

Example

    --  returns 39
    SELECT WEEK(DATE '1994-09-27');

Related functions

* DAYOFMONTH
* DAYOFYEAR
* QUARTER
* YEAR

### YEAR¶

Gets the year from a DATE.

Syntax

    YEAR(date)

The `YEAR` function returns the year from the specified SQL DATE.

The `YEAR` function is equivalent to `EXTRACT(YEAR FROM date)`.

Example

    --  returns 1994
    SELECT YEAR(DATE '1994-09-27');

Related functions

* DAYOFMONTH
* DAYOFYEAR
* QUARTER
* MONTH

### Other built-in functions¶

* [Aggregate Functions](aggregate-functions.html#flink-sql-aggregate-functions)
* [Collection Functions](collection-functions.html#flink-sql-collection-functions)
* [Comparison Functions](comparison-functions.html#flink-sql-comparison-functions)
* [Conditional Functions](conditional-functions.html#flink-sql-conditional-functions)
* Datetime Functions
* [Hash Functions](hash-functions.html#flink-sql-hash-functions)
* [JSON Functions](json-functions.html#flink-sql-json-functions)
* [ML Preprocessing Functions](ml-preprocessing-functions.html#flink-sql-ml-preprocessing-functions)
* [Model Inference Functions](model-inference-functions.html#flink-sql-model-inference-functions)
* [Numeric Functions](numeric-functions.html#flink-sql-numeric-functions)
* [String Functions](string-functions.html#flink-sql-string-functions)
* [Table API Functions](table-api-functions.html#flink-table-api-functions)

### Related content¶

* [User-defined Functions](../../concepts/user-defined-functions.html#flink-sql-udfs)
* [Create a User Defined Function](../../how-to-guides/create-udf.html#flink-sql-create-udf)

Note

This website includes content developed at the [Apache Software Foundation](https://www.apache.org/) under the terms of the [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0.html).
