---
document_id: flink_reference_functions_json-functions_chunk_3
source_file: flink_reference_functions_json-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/json-functions.html
title: SQL JSON functions in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 4
---

supported in `OVER` windows. Example

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
