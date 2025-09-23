---
document_id: flink_reference_functions_json-functions_chunk_4
source_file: flink_reference_functions_json-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/json-functions.html
title: SQL JSON functions in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 4
---

> SELECT JSON_UNQUOTE('SQL string'); >

## JSON_VALUE¶

Gets a value from a JSON string.

Syntax

    JSON_VALUE(jsonValue, path
      [RETURNING <dataType>]
      [ { NULL | ERROR | DEFAULT <defaultExpr> } ON EMPTY ]
      [ { NULL | ERROR | DEFAULT <defaultExpr> } ON ERROR ])

Description

The `JSON_VALUE` function extracts a scalar value from a JSON string. It searches a JSON string with the specified path expression and returns the value if the value at that path is scalar.

Non-scalar values can’t be returned.

By default, the value is returned as `STRING`. Use `RETURNING` to specify a different return type. The following return types are supported:

* `BOOLEAN`
* `DOUBLE`
* `INTEGER`
* `VARCHAR` / `STRING`

For empty path expressions or errors, you can define a behavior to return NULL, raise an error, or return a defined default value instead. The default is `NULL ON EMPTY` or `NULL ON ERROR`, respectively. The default value may be a literal or an expression. If the default value itself raises an error, it falls through to the error behavior for `ON EMPTY` and raises an error for `ON ERROR`.

For paths that contain special characters, like spaces, you can use `['property']` or `["property"]` to select the specified property in a parent object. Be sure to put single or double quotes around the property name.

When using JSON_VALUE in SQL, the path is a character parameter that’s already single-quoted, so you must escape the single quotes around the property name, for example, `JSON_VALUE('{"a b": "true"}', '$.[''a b'']')`.

Examples

The following SELECT statements return the values indicated in the comment lines.

    -- returns "true"
    SELECT JSON_VALUE('{"a": true}', '$.a');

    -- returns TRUE
    SELECT JSON_VALUE('{"a": true}', '$.a' RETURNING BOOLEAN);

    -- returns "false"
    SELECT JSON_VALUE('{"a": true}', 'lax $.b' DEFAULT FALSE ON EMPTY);

    -- returns "false"
    SELECT JSON_VALUE('{"a": true}', 'strict $.b' DEFAULT FALSE ON ERROR);

    -- returns 0.998D
    SELECT JSON_VALUE('{"a.b": [0.998,0.996]}','$.["a.b"][0]' RETURNING DOUBLE);

    -- returns "right"
    SELECT JSON_VALUE('{"contains blank": "right"}', 'strict $.[''contains blank'']' NULL ON EMPTY DEFAULT 'wrong' ON ERROR);

## Other built-in functions¶

* [Aggregate Functions](aggregate-functions.html#flink-sql-aggregate-functions)
* [Collection Functions](collection-functions.html#flink-sql-collection-functions)
* [Comparison Functions](comparison-functions.html#flink-sql-comparison-functions)
* [Conditional Functions](conditional-functions.html#flink-sql-conditional-functions)
* [Datetime Functions](datetime-functions.html#flink-sql-datetime-functions)
* [Hash Functions](hash-functions.html#flink-sql-hash-functions)
* JSON Functions
* [ML Preprocessing Functions](ml-preprocessing-functions.html#flink-sql-ml-preprocessing-functions)
* [Model Inference Functions](model-inference-functions.html#flink-sql-model-inference-functions)
* [Numeric Functions](numeric-functions.html#flink-sql-numeric-functions)
* [String Functions](string-functions.html#flink-sql-string-functions)
* [Table API Functions](table-api-functions.html#flink-table-api-functions)
