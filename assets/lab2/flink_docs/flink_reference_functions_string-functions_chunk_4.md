---
document_id: flink_reference_functions_string-functions_chunk_4
source_file: flink_reference_functions_string-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/string-functions.html
title: SQL string functions in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 5
---

brown fox', ' ', 3);

## STR_TO_MAP¶

Creates a map from a list of key-value strings.

Syntax

    STR_TO_MAP(string1[, string2, string3])

Description

The `STR_TO_MAP` function returns a map after splitting `string1` into key/value pairs using the pair delimiter specified in `string2`. The default is `','`. The `string3` argument specifies the key-value delimiter. The default is `'='`.

Both the pair delimiter and the key-value delimiter are treated as regular expressions, so special characters, like `<([{\^-=$!|]})?*+.>)`, must be properly escaped before using as a delimiter literal.

Example

    -- returns {a=1, b=2, c=3}
    SELECT STR_TO_MAP('a=1,b=2,c=3');

    -- returns {a=1, b=2, c=3}
    SELECT STR_TO_MAP('a:1;b:2;c:3', ';', ':');

## SUBSTRING¶

Finds a substring in a string.

Syntax

    SUBSTRING(string, integer1 [ FOR integer2 ])

Description

The `SUBSTRING` function returns a substring of the specified string, starting from position `integer1` with length `integer2`.

If `integer2` isn’t specified, the substring runs to the end of `string`.

This function can be abbreviated to `SUBSTR(string, integer1[, integer2])`, but `SUBSTR` doesn’t support the `FROM` and `FOR` keywords.

Examples

    -- returns "fox"
    SELECT SUBSTR('The quick brown fox', 17);

    -- returns "The"
    SELECT SUBSTR('The quick brown fox', 1, 3);

## TO_BASE64¶

Encodes a string to base64.

Syntax

    TO_BASE64(string)

Description
    The `TO_BASE64` function returns the base64-encoded representation of the specified string. Returns NULL if `string` is NULL.
Example

    -- returns "aGVsbG8gd29ybGQ="
    SELECT TO_BASE64('hello world');

Related function

* FROM_BASE64

## TRANSLATE¶

Substitutes characters in a string.

Syntax

    TRANSLATE(expr, from, to)

Arguments

* `expr`: A source STRING expression.
* `from`: A STRING expression that specifies a set of characters to be replaced.
* `to`: A STRING expression that specifies a corresponding set of replacement characters.

Returns
    A STRING that has the characters of `expr` replaced with the characters specified in the `to` string.
Description

The `TRANSLATE` function replaces the characters in the `expr` source string according to the replacement rules specified in the `from` and `to` strings.

The replacement is case-sensitive.

Examples:

    -- returns A1B2C3
    SELECT TRANSLATE('AaBbCc', 'abc', '123');

    -- returns A1BC
    SELECT TRANSLATE('AaBbCc', 'abc', '1');

    -- returns ABC
    SELECT TRANSLATE('AaBbCc', 'abc', '');

    -- returns    .APACHE.com
    SELECT TRANSLATE('www.apache.org', 'wapcheorg', ' APCHEcom');

Related functions

* OVERLAY
* REGEXP_REPLACE
* REPLACE

## TRIM¶

Removes leading and/or trailing characters from a string.

Syntax

    TRIM([ BOTH | LEADING | TRAILING ] string1 FROM string2)

Description
    The `TRIM` function returns a string that removes leading and/or trailing characters `string2` from `string1`.

Examples

    -- returns "The quick brown "
    SELECT TRIM(TRAILING 'fox' FROM 'The quick brown fox');

    -- returns " quick brown fox"
    SELECT TRIM(LEADING 'The' FROM 'The quick brown fox');

    -- returns " The quick brown fox "
    SELECT TRIM(BOTH 'yyy' FROM 'yyy The quick brown fox yyy');

Related functions

* BTRIM
* LTRIM
* RTRIM

## UPPER¶

Uppercases a string.

Syntax

    UPPER(string)

Description

The `UPPER` function returns the specified string in uppercase.

To lowercase a string, use the LOWER function.

Example

    -- returns "THE QUICK BROWN FOX"
    SELECT UPPER('The quick brown fox');

## URL_DECODE¶

Decodes a URL string.

Syntax

    URL_DECODE(string)

Description

The `URL_DECODE` function decodes the specified string in `application/x-www-form-urlencoded` format using the UTF-8 encoding scheme.

If the input string is NULL, or there is an issue with the decoding process, like encountering an illegal escape pattern, or the encoding scheme is not supported, the function returns NULL.

Example

    -- returns "http://confluent.io"
    SELECT URL_DECODE('http%3A%2F%2Fconfluent.io');

## URL_ENCODE¶

Encodes a URL string.

Syntax

    URL_ENCODE(string)

Description

The `URL_ENCODE` function translates the specified string into `application/x-www-form-urlencoded` format using the UTF-8 encoding scheme.

If the input string is NULL, or there is an issue with the decoding process, like encountering an illegal escape pattern, or the encoding scheme is not supported, the function returns NULL.

Example

    -- returns "http%3A%2F%2Fconfluent.io"
    SELECT URL_ENCODE('http://confluent.io');
