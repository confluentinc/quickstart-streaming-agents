---
document_id: flink_reference_datatypes_chunk_9
source_file: flink_reference_datatypes.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/datatypes.html
title: Flink SQL Data Types in Confluent Cloud for Apache Flink
chunk_index: 9
total_chunks: 10
---

described here only for completeness.

## Casting¶

Flink SQL can perform casting between a defined input type and target type. While some casting operations can always succeed regardless of the input value, others can fail at runtime when there’s no way to create a value for the target type. For example, it’s always possible to convert `INT` to `STRING`, but you can’t always convert a `STRING` to `INT`.

During the planning stage, the query validator rejects queries for invalid type pairs with a `ValidationException`, for example, when trying to cast a `TIMESTAMP` to an `INTERVAL`. Valid type pairs that can fail at runtime are accepted by the query validator, but this requires you to handle cast failures correctly.

In Flink SQL, casting can be performed by using one of these two built-in functions:

* [CAST](functions/comparison-functions.html#flink-sql-cast-function): The regular cast function defined by the SQL standard. It can fail the job if the cast operation is fallible and the provided input is not valid. Type inference preserves the nullability of the input type.
* [TRY_CAST](functions/comparison-functions.html#flink-sql-try-cast-function): An extension to the regular cast function that returns `NULL` if the cast operation fails. Its return type is always nullable.

For example:

    -- returns 42 of type INT NOT NULL
    SELECT CAST('42' AS INT);

    -- returns NULL of type VARCHAR
    SELECT CAST(NULL AS VARCHAR);

    -- throws an exception and fails the job
    SELECT CAST('non-number' AS INT);

    -- returns 42 of type INT
    SELECT TRY_CAST('42' AS INT);

    -- returns NULL of type VARCHAR
    SELECT TRY_CAST(NULL AS VARCHAR);

    -- returns NULL of type INT
    SELECT TRY_CAST('non-number' AS INT);

    -- returns 0 of type INT NOT NULL
    SELECT COALESCE(TRY_CAST('non-number' AS INT), 0);

The following matrix shows the supported cast pairs, where “Y” means supported, “!” means fallible, and “N” means unsupported:

Input / Target | CHAR¹ / VARCHAR¹ / STRING | BINARY¹ / VARBINARY¹ / BYTES | BOOLEAN | DECIMAL | TINYINT | SMALLINT | INTEGER | BIGINT | FLOAT | DOUBLE | DATE | TIME | TIMESTAMP | TIMESTAMP_LTZ | INTERVAL | ARRAY | MULTISET | MAP | ROW
---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---
CHAR / VARCHAR / STRING | Y | ! | ! | ! | ! | ! | ! | ! | ! | ! | ! | ! | ! | ! | N | N | N | N | N
BINARY / VARBINARY / BYTES | Y | Y | N | N | N | N | N | N | N | N | N | N | N | N | N | N | N | N | N
BOOLEAN | Y | N | Y | Y | Y | Y | Y | Y | Y | Y | N | N | N | N | N | N | N | N | N
DECIMAL | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | N | N | N | N | N | N | N | N
TINYINT | Y | N | Y | Y | Y | Y | Y | Y | Y | Y | N | N | N² | N² | N | N | N | N | N
SMALLINT | Y | N | Y | Y | Y | Y | Y | Y | Y | Y | N | N | N² | N² | N | N | N | N | N
INTEGER | Y | N | Y | Y | Y | Y | Y | Y | Y | Y | N | N | N² | N² | Y⁵ | N | N | N | N
BIGINT | Y | N | Y | Y | Y | Y | Y | Y | Y | Y | N | N | N² | N² | Y⁶ | N | N | N | N
FLOAT | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | N | N | N | N | N | N | N | N
DOUBLE | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | N | N | N | N | N | N | N | N
DATE | Y | N | N | N | N | N | N | N | N | N | Y | N | Y | Y | N | N | N | N | N
TIME | Y | N | N | N | N | N | N | N | N | N | N | Y | Y | Y | N | N | N | N | N
TIMESTAMP | Y | N | N | N | N | N | N | N | N | N | Y | Y | Y | Y | N | N | N | N | N
TIMESTAMP_LTZ | Y | N | N | N | N | N | N | N | N | N | Y | Y | Y | Y | N | N | N | N | N
INTERVAL | Y | N | N | N | N | N | Y⁵ | Y⁶ | N | N | N | N | N | N | Y | N | N | N | N
ARRAY | Y | N | N | N | N | N | N | N | N | N | N | N | N | N | N | !³ | N | N | N
MULTISET | Y | N | N | N | N | N | N | N | N | N | N | N | N | N | N | N | !³ | N | N
MAP | Y | N | N | N | N | N | N | N | N | N | N | N | N | N | N | N | N | !³ | N
ROW | Y | N | N | N | N | N | N | N | N | N | N | N | N | N | N | N | N | N | !³

Notes:

  1. All the casting to constant length or variable length also trims and pads, according to the type definition.
  2. `TO_TIMESTAMP` and `TO_TIMESTAMP_LTZ` must be used instead of `CAST`/ `TRY_CAST`.
  3. Supported iff the children type pairs are supported. Fallible iff the children type pairs are fallible.
  4. Supported iff the `RAW` class and serializer are equals.
  5. Supported iff `INTERVAL` is a `MONTH TO YEAR` range.
  6. Supported iff `INTERVAL` is a `DAY TO TIME` range.

Note

A cast of a `NULL` value always returns `NULL`, regardless of whether the function used is [CAST](functions/comparison-functions.html#flink-sql-cast-function) or [TRY_CAST](functions/comparison-functions.html#flink-sql-try-cast-function).
