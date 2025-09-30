---
document_id: flink_reference_functions_string-functions_chunk_2
source_file: flink_reference_functions_string-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/string-functions.html
title: SQL string functions in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 5
---

‘UTF-16’ Related function * DECODE

## FROM_BASE64¶

Decodes a base-64 encoded string.

Syntax

    FROM_BASE64(string)

Description
    The `FROM_BASE64` function returns the base64-decoded result from the specified string. Returns NULL if `string` is NULL.
Example

    -- returns "hello world"
    SELECT FROM_BASE64('aGVsbG8gd29ybGQ=');

Related function

* TO_BASE64

## INITCAP¶

Titlecase a string.

Syntax

    INITCAP(string)

Description

The `INITCAP` function returns a string that has the first character of each word converted to uppercase and the other characters converted to lowercase.

A “word” is assumed to be a sequence of alphanumeric characters.

Example

    -- returns "Title Case This String"
    SELECT INITCAP('title case this string');

Related functions

* LOWER
* UPPER

## INSTR¶

Find a substring in a string.

Syntax

    INSTR(string1, string2)

Description

The `INSTR` function returns the position of the first occurrence of `string2` in `string1`. Returns NULL if either argument is NULL.

The search is case-sensitive.

Example

    -- returns 33
    SELECT INSTR('The quick brown fox jumped over the lazy dog.', 'the');

Related function

* LOCATE

## LEFT¶

Gets the leftmost characters in a string.

Syntax

    LEFT(string, integer)

Description
    The `LEFT` function returns the leftmost `integer` characters from the specified string. Returns an empty string if `integer` is negative. Returns NULL if either argument is NULL.
Example

    -- returns "Morph"
    SELECT LEFT('Morpheus', 5);

Related function

* RIGHT

## LOCATE¶

Finds a substring in a string after a specified position.

Syntax

    LOCATE(string1, string2[, integer])

Description
    The `LOCATE` function returns the position of the first occurrence of `string1` in `string2` after position `integer`. Returns _0_ if `string1` isn’t found. Returns NULL if any of the arguments is NULL.
Example

    -- returns 12
    SELECT LOCATE('the', 'the play’s the thing', 10);

## LOWER¶

Lowercases a string.

Syntax

    LOWER(string)

Description

The `LOWER` function returns the specified string in lowercase.

To uppercase a string, use the UPPER function.

Example

    -- returns "the quick brown fox jumped over the lazy dog."
    SELECT LOWER('The Quick Brown Fox Jumped Over The Lazy Dog.');

Related functions

* INITCAP
* UPPER

## LPAD¶

Left-pad a string.

Syntax

    LPAD(string1, integer, string2)

Description

The `LPAD` function returns a new string from `string1` that’s left-padded with `string2` to a length of `integer` characters.

If the length of `string1` is shorter than `integer`, the `LPAD` function returns `string1` shortened to `integer` characters.

To right-pad a string, use the RPAD function.

Examples

    -- returns "??hi"
    SELECT LPAD('hi', 4, '??');

    -- returns "h"
    SELECT LPAD('hi', 1, '??');

Related function \- RPAD

## LTRIM¶

Removes left whitespaces from a string.

Syntax

    LTRIM(string)

Description

The `LTRIM` function removes the left whitespaces from the specified string.

To remove the right whitespaces from a string, use the RTRIM function.

Example

    -- returns "This is a test string."
    SELECT LTRIM(' This is a test string.');

Related functions

* BTRIM
* RTRIM
* TRIM

## OVERLAY¶

Replaces characters in a string with another string.

Syntax

    OVERLAY(string1 PLACING string2 FROM integer1 [ FOR integer2 ])

Description

The `OVERLAY` function returns a string that replaces `integer2` characters of `string1` with `string2`, starting from position `integer1`.

If `integer2` isn’t specified, the default is the length of `string2`.

Examples

    -- returns "xxxxxxxxx"
    SELECT OVERLAY('xxxxxtest' PLACING 'xxxx' FROM 6);

    -- returns "xxxxxxxxxst"
    SELECT OVERLAY('xxxxxtest' PLACING 'xxxx' FROM 6 FOR 2);

Related functions

* REGEXP_REPLACE
* REPLACE
* TRANSLATE

## PARSE_URL¶

Gets parts of a URL.

Syntax

    PARSE_URL(string1, string2[, string3])

Description

The `PARSE_URL` function returns the part specified by `string2` from the URL in `string1`.

For a URL that has a query, the optional `string3` argument specifies the key to extract from the query string.

Returns NULL if `string1` or `string2` is NULL.

These are the valid values for `string2`:

* ‘AUTHORITY’
* ‘FILE’
* ‘HOST’
* ‘PATH’
* ‘PROTOCOL’
* ‘QUERY’
* ‘REF’
* ‘USERINFO’

Example

    -- returns 'confluent.io'
    SELECT PARSE_URL('http://confluent.io/path1/p.php?k1=v1&k2=v2#Ref1', 'HOST');

    -- returns 'v1'
    SELECT PARSE_URL('http://confluent.io/path1/p.php?k1=v1&k2=v2#Ref1', 'QUERY', 'k1');
