---
document_id: flink_reference_functions_comparison-functions_chunk_4
source_file: flink_reference_functions_comparison-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/comparison-functions.html
title: SQL comparison functions in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 4
---

'<bob.dobbs@company.com>' NOT SIMILAR TO '%@example.com';

## Conversion functions¶

* CAST
* TRY_CAST
* TYPEOF

### CAST¶

Casts a value to a different type.

Syntax

    CAST(value AS type)

Description

The `CAST` function returns the specified value cast to the type specified by `type`.

A cast error throws an exception and fails the job.

When performing a cast operation that may fail, like STRING to INT, prefer TRY_CAST, to enable handling errors.

If `table.exec.legacy-cast-behaviour` is enabled, the `CAST` function behaves like `TRY_CAST`.

Examples

    --  returns 42
    SELECT CAST('42' AS INT);

    -- returns NULL of type STRING
    SELECT CAST(NULL AS STRING);

    --  throws an exception and fails the job
    SELECT CAST('not-a-number' AS INT);

### TRY_CAST¶

Casts a value to a different type and returns NULL on error.

Syntax

    TRY_CAST(value AS type)

Description
    Similar to the CAST function, but in case of error, returns NULL rather than failing the job.
Examples

    --  returns 42
    SELECT TRY_CAST('42' AS INT);

    --  returns NULL of type STRING
    SELECT TRY_CAST(NULL AS STRING);

    --  returns NULL of type INT
    SELECT TRY_CAST('not-a-number' AS INT);

    --  returns 0 of type INT
    SELECT COALESCE(TRY_CAST('not-a-number' AS INT), 0);

### TYPEOF¶

Gets the string representation of a data type.

Syntax

    TYPEOF(input)
    TYPEOF(input, force_serializable)

Description

The `TYPEOF` function returns the string representation of the input expression’s data type.

By default, the returned string is a summary string that might omit certain details for readability.

If `force_serializable` is set to TRUE, the string represents a full data type that can be persisted in a catalog.

Anonymous, inline data types have no serializable string representation. In these cases, NULL is returned.

Examples

    -- returns "CHAR(13) NOT NULL"
    SELECT TYPEOF('a string type');

    -- returns "INT NOT NULL"
    SELECT TYPEOF(23);

    -- returns "DATE NOT NULL"
    SELECT TYPEOF(DATE '2023-05-04');

    -- returns "NULL"
    SELECT TYPEOF(NULL);

## Other built-in functions¶

* [Aggregate Functions](aggregate-functions.html#flink-sql-aggregate-functions)
* [Collection Functions](collection-functions.html#flink-sql-collection-functions)
* Comparison Functions
* [Conditional Functions](conditional-functions.html#flink-sql-conditional-functions)
* [Datetime Functions](datetime-functions.html#flink-sql-datetime-functions)
* [Hash Functions](hash-functions.html#flink-sql-hash-functions)
* [JSON Functions](json-functions.html#flink-sql-json-functions)
* [ML Preprocessing Functions](ml-preprocessing-functions.html#flink-sql-ml-preprocessing-functions)
* [Model Inference Functions](model-inference-functions.html#flink-sql-model-inference-functions)
* [Numeric Functions](numeric-functions.html#flink-sql-numeric-functions)
* [String Functions](string-functions.html#flink-sql-string-functions)
* [Table API Functions](table-api-functions.html#flink-table-api-functions)
