---
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/string-functions.html
title: SQL string functions in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'functions', 'string-functions.html']
scraped_date: 2025-09-05T13:50:32.168345
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

## POSITION¶

Finds a substring in a string.

Syntax

    POSITION(string1 IN string2)

Description

The `POSITION` function returns the position of the first occurrence of `string1` in `string2`. Returns _0_ if `string1` isn’t found in `string2`.

The position is 1-based, so the index of the first character is _1_.

Examples

    -- returns 1
    SELECT POSITION('the' IN 'the quick brown fox');
    
    -- returns 17
    SELECT POSITION('fox' IN 'the quick brown fox');

## REGEXP¶

Matches a string against a regular expression.

Syntax

    REGEXP(string1, string2)

Description
    The `REGEXP` function returns TRUE if any (possibly empty) substring of `string1` matches the regular expression in `string2`; otherwise, FALSE. Returns NULL if either of the arguments is NULL.
Examples

    -- returns TRUE
    SELECT REGEXP('800 439 3207', '.?(\d{3}).*(\d{3}).*(\d{4})');
    
    -- returns TRUE
    SELECT REGEXP('2023-05-04', '((\d{4}.\d{2}).(\d{2}))');

## REGEXP_EXTRACT¶

Gets a string from a regular expression matching group.

Syntax

    REGEXP_EXTRACT(string1, string2[, integer])

Description

The `REGEXP_EXTRACT` function returns a string from `string1` that’s extracted with the regular expression specified in `string2` and a regex match group index integer.

The regex match group index starts from _1_ , and _0_ specifies matching the whole regex.

The regex match group index must not exceed the number of the defined groups.

Example

    -- returns "bar"
    SELECT REGEXP_EXTRACT('foothebar', 'foo(.*?)(bar)', 2);

## REGEXP_REPLACE¶

Replaces substrings in a string that match a regular expression.

Syntax

    REGEXP_REPLACE(string1, string2, string3)

Description
    The `REGEXP_REPLACE` function returns a string from `string1` with all of the substrings that match the regular expression in `string2` consecutively replaced with `string3`.
Example

    --  returns "fb"
    SELECT REGEXP_REPLACE('foobar', 'oo|ar', '');

Related functions

  * OVERLAY
  * REPLACE
  * TRANSLATE

## REPEAT¶

Concatenates copies of a string.

Syntax

    REPEAT(string, integer)

Description
    The `REPEAT` function returns a string that repeats the base string `integer` times.
Example

    -- returns "TestingTesting"
    SELECT REPEAT('Testing', 2);

## REPLACE¶

Replace substrings in a string.

Syntax

    REPLACE(string1, string2, string3)

Description
    The `REPLACE` function returns a new string that replaces all occurrences of `string2` with `string3` (non-overlapping) from `string1`.
Examples

    -- returns "hello flink"
    SELECT REPLACE('hello world', 'world', 'flink');
    
    -- returns "zab"
    SELECT REPLACE('ababab', 'abab', 'z');

Related functions

  * OVERLAY
  * REGEXP_REPLACE
  * TRANSLATE

## REVERSE¶

Reverses a string.

Syntax

    REVERSE(string)

Description
    The `REVERSE` function returns the reversed string. Returns NULL if `string` is NULL.
Example

    -- returns "xof nworb kciuq eht"
    SELECT REVERSE('the quick brown fox');

## RIGHT¶

Gets the rightmost characters in a string.

Syntax

    RIGHT(string, integer)

Description
    The `RIGHT` function returns the rightmost `integer` characters from the specified string. Returns an empty string if `integer` is negative. Returns NULL if either argument is NULL.
Example

    -- returns "Anderson"
    SELECT RIGHT('Thomas A. Anderson', 8);

Related function

  * LEFT

## RPAD¶

Right-pad a string.

Syntax

    RPAD(string1, integer, string2)

Description

The `RPAD` function returns a new string from `string1` that’s right-padded with `string2` to a length of `integer` characters.

If the length of `string1` is shorter than `integer`, returns `string1` shortened to `integer` characters.

To left-pad a string, use the LPAD function.

Examples

    -- returns "hi??"
    SELECT RPAD('hi', 4, '??');
    
    -- returns "h"
    SELECT RPAD('hi', 1, '??');

Related function

  * LPAD

## RTRIM¶

Removes right whitespaces from a string.

Syntax

    RTRIM(string)

Description

The `RTRIM` function removes the right whitespaces from the specified string.

To remove the left whitespaces from a string, use the LTRIM function.

Example

    -- returns "This is a test string."
    SELECT RTRIM('This is a test string. ');

Related functions

  * BTRIM
  * LTRIM
  * TRIM

## SPLIT_INDEX¶

Splits a string by a delimiter.

Syntax

    SPLIT_INDEX(string1, string2, integer1)

Description
    The `SPLIT_INDEX` function splits `string1` by the delimiter in `string2` and returns the `integer1` zero-based string of the split strings. Returns NULL if `integer` is negative. Returns NULL if any of the arguments is NULL.
Example

    -- returns "fox"
    SELECT SPLIT_INDEX('The quick brown fox', ' ', 3);

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

## Other built-in functions¶

  * [Aggregate Functions](aggregate-functions.html#flink-sql-aggregate-functions)
  * [Collection Functions](collection-functions.html#flink-sql-collection-functions)
  * [Comparison Functions](comparison-functions.html#flink-sql-comparison-functions)
  * [Conditional Functions](conditional-functions.html#flink-sql-conditional-functions)
  * [Datetime Functions](datetime-functions.html#flink-sql-datetime-functions)
  * [Hash Functions](hash-functions.html#flink-sql-hash-functions)
  * [JSON Functions](json-functions.html#flink-sql-json-functions)
  * [ML Preprocessing Functions](ml-preprocessing-functions.html#flink-sql-ml-preprocessing-functions)
  * [Model Inference Functions](model-inference-functions.html#flink-sql-model-inference-functions)
  * [Numeric Functions](numeric-functions.html#flink-sql-numeric-functions)
  * String Functions
  * [Table API Functions](table-api-functions.html#flink-table-api-functions)

