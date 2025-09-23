---
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/json-functions.html
title: SQL JSON functions in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'functions', 'json-functions.html']
scraped_date: 2025-09-05T13:50:27.725852
---

# JSON Functions in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides these built-in functions to help with JSON in SQL queries:

IS JSON | JSON_ARRAY | JSON_ARRAYAGG
---|---|---
JSON_EXISTS | JSON_OBJECT | JSON_OBJECTAGG
JSON_QUERY | JSON_QUOTE | JSON_STRING
JSON_UNQUOTE | JSON_VALUE |

JSON functions make use of JSON path expressions as described in [ISO/IEC TR 19075-6](https://www.iso.org/standard/78937.html) of the SQL standard. Their syntax is inspired by and adopts many features of ECMAScript, but is neither a subset nor superset of the standard.

Path expressions come in two flavors, lax and strict. When omitted, it defaults to the strict mode. Strict mode is intended to examine data from a schema perspective and will throw errors whenever data does not adhere to the path expression. However, functions like `JSON_VALUE` allow defining fallback behavior if an error is encountered. Lax mode, on the other hand, is more forgiving and converts errors to empty sequences.

The special character `$` denotes the root node in a JSON path. Paths can access properties (`$.a`), array elements (`$.a[0].b`), or branch over all elements in an array (`$.a[*].b`).

Known Limitations:

* Not all features of Lax mode are currently supported. This is an upstream bug ([CALCITE-4717](https://issues.apache.org/jira/browse/CALCITE-4717)).
* Non-standard behavior is not guaranteed.

## IS JSON¶

Checks whether a string is valid JSON.

Syntax

    IS JSON [ { VALUE | SCALAR | ARRAY | OBJECT } ]

Description

The `IS JSON` function determines whether the specified string is valid JSON.

Providing the optional type argument constrains the type of JSON object to check for validity. The default is `VALUE`. If the string is valid JSON but not the provided type, `IS JSON` returns FALSE.

Examples

The following SELECT statements return TRUE.

    -- The following statements return TRUE.
    SELECT '1' IS JSON;
    SELECT '[]' IS JSON;
    SELECT '{}' IS JSON;
    SELECT '"abc"' IS JSON;
    SELECT '1' IS JSON SCALAR;
    SELECT '{}' IS JSON OBJECT;

The following SELECT statements return FALSE.

    -- The following statements return FALSE.
    SELECT 'abc' IS JSON;
    SELECT '1' IS JSON ARRAY;
    SELECT '1' IS JSON OBJECT;
    SELECT '{}' IS JSON SCALAR;
    SELECT '{}' IS JSON ARRAY;

## JSON_ARRAY¶

Creates a JSON array string from a list of values.

Syntax

    JSON_ARRAY([value]* [ { NULL | ABSENT } ON NULL ])

Description

The `JSON_ARRAY` function returns a JSON string from the specified list of values. The values can be arbitrary expressions.

The `ON NULL` behavior defines how to handle NULL values. If omitted, `ABSENT ON NULL` is the default.

Elements that are created from other JSON construction function calls are inserted directly, rather than as a string. This enables building nested JSON structures by using the `JSON_OBJECT` and `JSON_ARRAY` construction functions.

Examples

The following SELECT statements return the values indicated in the comment lines.

    -- returns '[]'
    SELECT JSON_ARRAY();

    -- returns '[1,"2"]'
    SELECT JSON_ARRAY(1, '2');

    -- Use an expression as a value.
    SELECT JSON_ARRAY(orders.orderId);

    -- ON NULL
    -- returns '[null]'
    SELECT JSON_ARRAY(CAST(NULL AS STRING) NULL ON NULL);

    -- ON NULL
    -- returns '[]'
    SELECT JSON_ARRAY(CAST(NULL AS STRING) ABSENT ON NULL);

    -- returns '[[1]]'
    SELECT JSON_ARRAY(JSON_ARRAY(1));

    -- returns '[{"nested_json":{"value":42}}]'
    SELECT JSON_ARRAY(JSON('{"nested_json": {"value": 42}}'));

## JSON_ARRAYAGG¶

Aggregates items into a JSON array string.

Syntax

    JSON_ARRAYAGG(items [ { NULL | ABSENT } ON NULL ])

Description

The `JSON_ARRAYAGG` function creates a JSON object string by aggregating the specified items into an array.

The item expressions can be arbitrary, including other JSON functions.

If a value is NULL, the `ON NULL` behavior defines what to do. If omitted, `ABSENT ON NULL` is the default.

The `JSON_ARRAYAGG` function isn’t supported in `OVER` windows, unbounded session windows, or `HOP` windows.

Example

    -- '["Apple","Banana","Orange"]'
    SELECT
    JSON_ARRAYAGG(product)
    FROM orders;

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

## JSON_QUERY¶

Gets values from a JSON string.

Syntax

    JSON_QUERY(jsonValue, path
      [ RETURNING ]
      [ { WITHOUT | WITH CONDITIONAL | WITH UNCONDITIONAL } [ ARRAY ] WRAPPER ]
      [ { NULL | EMPTY ARRAY | EMPTY OBJECT | ERROR } ON EMPTY ]
      [ { NULL | EMPTY ARRAY | EMPTY OBJECT | ERROR } ON ERROR ])

Description

The `JSON_QUERY` function extracts JSON values from the specified JSON string.

The result is returned as a `STRING` or an `ARRAY<STRING>`. Use the `RETURNING` clause to control the return type.

The `WRAPPER` clause specifies whether the extracted value should be wrapped into an array and whether to do so unconditionally or only if the value itself isn’t an array already.

The `ON EMPTY` and `ON ERROR` clauses specify the behavior if the path expression is empty, or in case an error was raised, respectively. By default, in both cases NULL is returned. Other choices are to use an empty array, an empty object, or to raise an error.

Examples

The following SELECT statements return the values indicated in the comment lines.

    -- returns '{ "b": 1 }'
    SELECT JSON_QUERY('{ "a": { "b": 1 } }', '$.a');

    -- returns '[1, 2]'
    SELECT JSON_QUERY('[1, 2]', '$');

    -- returns NULL
    SELECT JSON_QUERY(CAST(NULL AS STRING), '$');

    -- returns array ['c1','c2']
    SELECT JSON_QUERY('{"a":[{"c":"c1"},{"c":"c2"}]}', 'lax $.a[*].c' RETURNING ARRAY<STRING>);

    -- Wrap the result into an array.
    -- returns '[{}]'
    SELECT JSON_QUERY('{}', '$' WITH CONDITIONAL ARRAY WRAPPER);

    -- returns '[1, 2]'
    SELECT JSON_QUERY('[1, 2]', '$' WITH CONDITIONAL ARRAY WRAPPER);

    -- returns '[[1, 2]]'
    SELECT JSON_QUERY('[1, 2]', '$' WITH UNCONDITIONAL ARRAY WRAPPER);

    -- Scalars must be wrapped to be returned.
    -- returns NULL
    SELECT JSON_QUERY(1, '$');

    -- returns '[1]'
    SELECT JSON_QUERY(1, '$' WITH CONDITIONAL ARRAY WRAPPER);

    -- Behavior if the path expression is empty.
    -- returns '{}'
    SELECT JSON_QUERY('{}', 'lax $.invalid' EMPTY OBJECT ON EMPTY);

    -- Behavior if the path expression has an error.
    -- returns '[]'
    SELECT JSON_QUERY('{}', 'strict $.invalid' EMPTY ARRAY ON ERROR);

## JSON_QUOTE¶

Quotes a string as a JSON value by wrapping it with double-quote characters.

Syntax

    JSON_QUOTE(string)

Description

The `JSON_QUOTE` function quotes a string as a JSON value by wrapping it with double-quote characters, escaping interior quote and special characters (’”’, ‘’, ‘/’, ‘b’, ‘f’, ’n’, ‘r’, ’t’), and returning the result as a string.

If `string` is NULL, the function returns NULL.

Example

>
>     -- returns { "SQL string" }
>     SELECT JSON_QUOTE('SQL string');
>

## JSON_STRING¶

Serializes a string to JSON.

Syntax

    JSON_STRING(value)

Description
    The `JSON_STRING` function returns a JSON string containing the serialized value. If the value is NULL, the function returns NULL.
Examples

The following SELECT statements return the values indicated in the comment lines.

    -- returns NULL
    SELECT JSON_STRING(CAST(NULL AS INT));

    -- returns '1'
    SELECT JSON_STRING(1);

    -- returns 'true'
    SELECT JSON_STRING(TRUE);

    -- returns '"Hello, World!"'
    JSON_STRING('Hello, World!');

    -- returns '[1,2]'
    JSON_STRING(ARRAY[1, 2])

## JSON_UNQUOTE¶

Unquotes a JSON value.

Syntax

    JSON_UNQUOTE(string)

Description

The `JSON_UNQUOTE` function unquotes a JSON value, unescapes escaped special characters (’”’, ‘’, ‘/’, ‘b’, ‘f’, ’n’, ‘r’, ’t’, ‘u’), and returns the result as a string.

If `string` is NULL, the function returns NULL.

If `string` doesn’t start and end with double quotes, or if it starts and ends with double quotes but is not a valid JSON string literal, the value is passed through unmodified.

Example

>
>     -- returns { "SQL string" }
>     SELECT JSON_UNQUOTE('SQL string');
>

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
