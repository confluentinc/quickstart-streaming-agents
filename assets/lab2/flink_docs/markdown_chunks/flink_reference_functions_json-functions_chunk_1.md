---
document_id: flink_reference_functions_json-functions_chunk_1
source_file: flink_reference_functions_json-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/json-functions.html
title: SQL JSON functions in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 4
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
