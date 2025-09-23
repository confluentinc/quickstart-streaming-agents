---
document_id: flink_reference_functions_json-functions_chunk_2
source_file: flink_reference_functions_json-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/json-functions.html
title: SQL JSON functions in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 4
---

'["Apple","Banana","Orange"]' SELECT JSON_ARRAYAGG(product) FROM orders;

## JSON_EXISTS¶

Checks a JSON path.

Syntax

    JSON_EXISTS(jsonValue, path [ { TRUE | FALSE | UNKNOWN | ERROR } ON ERROR ])

Description

The `JSON_EXISTS` function determines whether a JSON string satisfies a specified path search criterion.

If the `ON ERROR` behavior is omitted, the default is `FALSE ON ERROR`.

Examples

The following SELECT statements return TRUE.

    -- The following statements return TRUE.
    SELECT JSON_EXISTS('{"a": true}', '$.a');
    SELECT JSON_EXISTS('{"a": [{ "b": 1 }]}', '$.a[0].b');
    SELECT JSON_EXISTS('{"a": true}', 'strict $.b' TRUE ON ERROR);

The following SELECT statements return FALSE.

    -- The following statements return FALSE.
    SELECT JSON_EXISTS('{"a": true}', '$.b');
    SELECT JSON_EXISTS('{"a": true}', 'strict $.b' FALSE ON ERROR);

## JSON_OBJECT¶

Syntax

    JSON_OBJECT([[KEY] key VALUE value]* [ { NULL | ABSENT } ON NULL ])

Description

The `JSON_OBJECT` function creates a JSON object string from the specified list of key-value pairs.

Keys must be non-NULL string literals, and values may be arbitrary expressions.

The `JSON_OBJECT` function returns a JSON string. The `ON NULL` behavior defines how to treat NULL values. If omitted, `NULL ON NULL` is the default.

Values that are created from another JSON construction function calls are inserted directly, rather than as a string. This enables building nested JSON structures by using the `JSON_OBJECT` and `JSON_ARRAY` construction functions.

Examples

The following SELECT statements return the values indicated in the comment lines.

    -- returns '{}'
    SELECT JSON_OBJECT();

    -- returns '{"K1":"V1","K2":"V2"}'
    SELECT JSON_OBJECT('K1' VALUE 'V1', 'K2' VALUE 'V2');

    -- Use an expression as a value.
    SELECT JSON_OBJECT('orderNo' VALUE orders.orderId);

    -- ON NULL
    -- '{"K1":null}'
    SELECT JSON_OBJECT(KEY 'K1' VALUE CAST(NULL AS STRING) NULL ON NULL);

    -- ON NULL
    -- '{}'
    SELECT JSON_OBJECT(KEY 'K1' VALUE CAST(NULL AS STRING) ABSENT ON NULL);

    -- returns '{"K1":{"nested_json":{"value":42}}}'
    SELECT JSON_OBJECT('K1' VALUE JSON('{"nested_json": {"value": 42}}'));

    -- returns '{"K1":{"K2":"V"}}'
    SELECT JSON_OBJECT(
      KEY 'K1'
      VALUE JSON_OBJECT(
        KEY 'K2'
        VALUE 'V'
      )
    );

## JSON_OBJECTAGG¶

Aggregates key-value expressions into a JSON string.

Syntax

    JSON_OBJECTAGG([KEY] key VALUE value [ { NULL | ABSENT } ON NULL ])

Description

The `JSON_OBJECTAGG` function creates a JSON object string by aggregating key-value expressions into a single JSON object.

The `key` expression must return a non-nullable character string. Value expressions can be arbitrary, including other JSON functions.

Keys must be unique. If a key occurs multiple times, an error is thrown.

If a value is NULL, the `ON NULL` behavior defines what to do. If omitted, `NULL ON NULL` is the default.

The `JSON_OBJECTAGG` function isn’t supported in `OVER` windows.

Example
