---
document_id: flink_reference_functions_comparison-functions_chunk_3
source_file: flink_reference_functions_comparison-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/comparison-functions.html
title: SQL comparison functions in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 4
---

NULL values are treated as identical.

Examples

    --  returns FALSE
    SELECT 1 IS NOT DISTINCT FROM 2;

    --  returns FALSE
    SELECT 1 IS NOT DISTINCT FROM NULL;

    --  returns TRUE
    SELECT NULL IS NOT DISTINCT FROM NULL;

### IS NULL¶

Checks whether a value is NULL.

Syntax

    value IS NULL

Description
    The `IS NULL` function returns TRUE if `value` is NULL.
Examples

    --  returns FALSE
    SELECT 1 IS NULL;

    --  returns TRUE
    SELECT NULL IS NULL;

### IS NOT NULL¶

Checks whether a value is assigned.

Syntax

    value IS NOT NULL

Description
    The `IS NOT NULL` function returns TRUE if `value` is not NULL.
Examples

    --  returns TRUE
    SELECT 1 IS NOT NULL;

    --  returns FALSE
    SELECT NULL IS NOT NULL;

### LIKE¶

Checks whether a string matches a pattern.

Syntax

    string1 LIKE string2

Description

The `LIKE` function returns TRUE if `string1` matches the pattern specified by `string2`.

The pattern can contain these special characters:

* **%** – matches any number of characters
* **_** – matches a single character

Returns UNKNOWN if either `string1` or `string2` is NULL.

Examples

    -- returns TRUE
    SELECT 'book-23' LIKE 'book-%';

    -- returns FALSE
    SELECT 'book23' LIKE 'book_';

    -- returns TRUE
    SELECT 'book2' LIKE 'book_';

### NOT LIKE¶

Checks whether a string matches a pattern.

Syntax

    string1 NOT LIKE string2 [ ESCAPE char ]

Description

The `NOT LIKE` function returns TRUE if `string1` does not match the pattern specified by `string2`.

The pattern can contain these special characters:

* **%** – matches any number of characters
* **_** – matches a single character

Returns UNKNOWN if `string1` or `string2` is NULL.

Examples

    -- returns FALSE
    SELECT 'book-23' NOT LIKE 'book-%';

    -- returns TRUE
    SELECT 'book23' NOT LIKE 'book_';

    -- returns FALSE
    SELECT 'book2' NOT LIKE 'book_';

### SIMILAR TO¶

Checks whether a string matches a regular expression.

Syntax

    string1 SIMILAR TO string2

Description

The `SIMILAR TO` function returns TRUE if `string1` matches the SQL regular expression in `string2`.

The pattern can contain any characters that are valid in regular expressions, like `.`, which matches any character, `*`, which matches zero or more occurrences, and `+` which matches one or more occurrences.

Returns UNKNOWN if `string1` or `string2` is NULL.

Examples

    -- returns TRUE
    SELECT 'book-523' SIMILAR TO 'book-[0-9]+';

    -- returns TRUE
    SELECT 'bob.dobbs@example.com' SIMILAR TO '%@example.com';

### NOT SIMILAR TO¶

Checks whether a string doesn’t match a regular expression.

Syntax

    string1 NOT SIMILAR TO string2 [ ESCAPE char ]

Description

The `NOT SIMILAR TO` function returns TRUE if `string1` does not match the SQL regular expression specified by `string2`.

Returns UNKNOWN if `string1` or `string2` is NULL.

Examples

    -- returns TRUE
    SELECT 'book-nan' NOT SIMILAR TO 'book-[0-9]+';

    -- returns TRUE
    SELECT 'bob.dobbs@company.com' NOT SIMILAR TO '%@example.com';
