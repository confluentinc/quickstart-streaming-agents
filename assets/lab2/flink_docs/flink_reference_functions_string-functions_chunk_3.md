---
document_id: flink_reference_functions_string-functions_chunk_3
source_file: flink_reference_functions_string-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/string-functions.html
title: SQL string functions in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 5
---

'v1' SELECT PARSE_URL('<http://confluent.io/path1/p.php?k1=v1&k2=v2#Ref1>', 'QUERY', 'k1');

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
