---
document_id: flink_reference_functions_string-functions_chunk_1
source_file: flink_reference_functions_string-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/string-functions.html
title: SQL string functions in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 5
---

# String Functions in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides these built-in string functions to use in SQL queries:

ASCII | BTRIM | string1 || string2 | CHARACTER_LENGTH
---|---|---|---
CHR | CONCAT | CONCAT_WS | DECODE
ELT | ENCODE | FROM_BASE64 | INITCAP
INSTR | LEFT | LOCATE | LOWER
LPAD | LTRIM | OVERLAY | PARSE_URL
POSITION | REGEXP | REGEXP_EXTRACT | REGEXP_REPLACE
REPEAT | REPLACE | REVERSE | RIGHT
RPAD | RTRIM | SPLIT_INDEX | STR_TO_MAP
SUBSTRING | TO_BASE64 | TRANSLATE | TRIM
UPPER | URL_DECODE | URL_ENCODE |

## ASCII¶

Gets the ASCII value of the first character of a string.

Syntax

    ASCII(string)

Description
    The `ASCII` function returns the numeric value of the first character of the specified string. Returns NULL if `string` is NULL.
Examples

    -- returns 97
    SELECT ASCII('abc');

    -- returns NULL
    SELECT ASCII(CAST(NULL AS VARCHAR));

## string1 || string2¶

Concatenates two strings.

Syntax

    string1 || string2

Description
    The `||` function returns the concatenation of `string1` and `string2`.
Examples

    -- returns "FlinkSQL"
    SELECT 'Flink' || 'SQL';

Related functions

* CONCAT
* CONCAT_WS

## BTRIM¶

Trim both sides of a string.

Syntax

    BTRIM(str[, trimStr])

Arguments

* `str`: A source STRING expression.
* `trimStr`: An optional STRING expression that has characters to be trimmed. The default is the space character.

Returns
    A trimmed STRING.
Description
    The `BTRIM` function trims the leading and trailing characters from `str`.
Examples

    -- returns 'www.apache.org'
    SELECT BTRIM("  www.apache.org  ");

    -- returns 'www.apache.org'
    SELECT BTRIM('/www.apache.org/', '/');

    -- returns 'www.apache.org'
    SELECT BTRIM('/*www.apache.org*/', '/*');

Related functions

* LTRIM
* RTRIM
* TRIM

## CHARACTER_LENGTH¶

Gets the length of a string.

Syntax

    CHARACTER_LENGTH(string)

Description

The `CHARACTER_LENGTH` function returns the number of characters in the specified string.

This function can be abbreviated to `CHAR_LENGTH(string)`.

Examples

    -- returns 18
    SELECT CHAR_LENGTH('Thomas A. Anderson');

## CHR¶

Gets the character for an ASCII code.

Syntax

    CHR(integer)

Description

The `CHR` function returns the ASCII character that has the binary equivalent to the specified integer. Returns NULL if `integer` is NULL.

If `integer` is larger than _255_ , the function computes the modulus of `integer` divided by _255_ first and returns `CHR` of the modulus.

Examples

    -- returns 'a'
    SELECT CHR(97);

    -- returns 'a'
    SELECT CHR(353);

## CONCAT¶

Concatenates a list of strings.

Syntax

    CONCAT(string1, string2, ...)

Description
    The `CONCAT` function returns the concatenation of the specified strings. Returns NULL if any argument is NULL.
Example

    --  returns "AABBCC"
    SELECT CONCAT('AA', 'BB', 'CC');

Related functions

* string1 || string2
* CONCAT_WS

## CONCAT_WS¶

Concatenates a list of strings with a separator.

Syntax

    CONCAT_WS(string1, string2, string3, ...)

Description

The `CONCAT_WS` function returns a string that concatenates `string2, string3, ...` with the separator specified by `string1`.

The separator is added between the strings to be concatenated.

Returns NULL If `string1` is NULL.

Example

    -- returns "AA~BB~~CC"
    SELECT CONCAT_WS('~', 'AA', 'BB', '', 'CC');

Related functions

* string1 || string2
* CONCAT

## DECODE¶

Decodes a binary into a string.

Syntax

    DECODE(binary, string)

Description

The `DECODE` function decodes the binary argument into a string using the specified character set. Returns NULL if either argument is null.

These are the supported character set strings:

* ‘ISO-8859-1’
* ‘US-ASCII’
* ‘UTF-8’
* ‘UTF-16BE’
* ‘UTF-16LE’
* ‘UTF-16’

Related function

* ENCODE

## ELT¶

Gets the expression at the specified index.

Syntax

    ELT(index, expr[, exprs]*)

Arguments

* `index`: The 1-based index of the expression to get. `index` must be an integer between 1 and the number of expressions.
* `expr`: An expression that resolves to CHAR, VARCHAR, BINARY, or VARBINARY.

Returns

The expression at the location in the argument list specified by `index`. The result has the type of the least common type of all expressions.

Returns `NULL` if index is `NULL` or out of range.

Description
    Returns the index-th expression.
Example

    -- returns java-2
    SELECT ELT(2, 'scala-1', 'java-2', 'go-3');

## ENCODE¶

Encodes a string to a BINARY.

Syntax

    ENCODE(string1, string2)

Description

The `ENCODE` function encodes `string1` into a BINARY using the specified `string2` character set. Returns NULL if either argument is null.

These are the supported character set strings:

* ‘ISO-8859-1’
* ‘US-ASCII’
* ‘UTF-8’
* ‘UTF-16BE’
* ‘UTF-16LE’
* ‘UTF-16’

Related function

* DECODE
