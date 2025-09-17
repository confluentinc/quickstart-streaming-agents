---
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/comparison-functions.html
title: SQL comparison functions in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'functions', 'comparison-functions.html']
scraped_date: 2025-09-05T13:49:10.535546
---

# Comparison Functions in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides these built-in comparison functions to use in SQL queries:

  * Equality operations
  * Logical operations
  * Comparison Functions
  * Conversion functions

## Equality operations¶

SQL function | Description  
---|---  
`value1 = value2` | Returns TRUE if value1 is equal to value2. Returns UNKNOWN if value1 or value2 is NULL.  
`value1 <> value2` | Returns TRUE if value1 is not equal to value2. Returns UNKNOWN if value1 or value2 is NULL.  
`value1 > value2` | Returns TRUE if value1 is greater than value2. Returns UNKNOWN if value1 or value2 is NULL.  
`value1 >= value2` | Returns TRUE if value1 is greater than or equal to value2. Returns UNKNOWN if value1 or value2 is NULL.  
`value1 < value2` | Returns TRUE if value1 is less than value2. Returns UNKNOWN if value1 or value2 is NULL.  
`value1 <= value2` | Returns TRUE if value1 is less than or equal to value2. Returns UNKNOWN if value1 or value2 is NULL.  
  
## Logical operations¶

Logical operation | Description  
---|---  
`boolean1 OR boolean2` | Returns TRUE if `boolean1` is TRUE or `boolean2` is TRUE. Supports three-valued logic. For example, `TRUE || NULL(BOOLEAN)` returns TRUE.  
`boolean1 AND boolean2` | Returns TRUE if `boolean1` and `boolean2` are both TRUE. Supports three-valued logic. For example, `TRUE && NULL(BOOLEAN)` returns UNKNOWN.  
`NOT boolean` | Returns TRUE if `boolean` is FALSE; returns FALSE if `boolean` is TRUE; returns UNKNOWN if boolean is UNKNOWN.  
`boolean IS FALSE` | Returns TRUE if `boolean` is FALSE; returns FALSE if `boolean` is TRUE or UNKNOWN.  
`boolean IS NOT FALSE` | Returns TRUE if `boolean` is TRUE or UNKNOWN; returns FALSE if `boolean` is FALSE.  
`boolean IS TRUE` | Returns TRUE if `boolean` is TRUE; returns FALSE if `boolean` is FALSE or UNKNOWN.  
`boolean IS NOT TRUE` | Returns TRUE if `boolean` is FALSE or UNKNOWN; returns FALSE if `boolean` is TRUE.  
`boolean IS UNKNOWN` | Returns TRUE if `boolean` is UNKNOWN; returns FALSE if `boolean` is TRUE or FALSE.  
`boolean IS NOT UNKNOWN` | Returns TRUE if `boolean` is TRUE or FALSE; returns FALSE if `boolean` is UNKNOWN.  
  
## Comparison functions¶

BETWEEN | NOT BETWEEN  
---|---  
IN | NOT IN  
IS DISTINCT FROM | IS NOT DISTINCT FROM  
IS NULL | IS NOT NULL  
LIKE | NOT LIKE  
SIMILAR TO | NOT SIMILAR TO  
EXISTS |   
  
### BETWEEN¶

Checks whether a value is between two other values.

Syntax

    value1 BETWEEN [ ASYMMETRIC | SYMMETRIC ] value2 AND value3

Description

The `BETWEEN` function returns TRUE if `value1` is greater than or equal to `value2` and less than or equal to `value3`, if ASYMMETRIC is specified. The default is ASYMMETRIC.

If SYMMETRIC is specified, the `BETWEEN` function returns TRUE if `value1` is _inclusively_ between `value2` and `value3`.

When either `value2` or `value3` is NULL, returns FALSE or UNKNOWN.

Examples

    - returns FALSE
    SELECT 12 BETWEEN 15 AND 12;
    
    - returns TRUE
    SELECT 12 BETWEEN SYMMETRIC 15 AND 12;
    
    - returns UNKNOWN
    SELECT 12 BETWEEN 10 AND NULL;
    
    - returns FALSE
    SELECT 12 BETWEEN NULL AND 10;
    
    - returns UNKNOWN
    SELECT 12 BETWEEN SYMMETRIC NULL AND 12;

### NOT BETWEEN¶

Checks whether a value is not between two other values.

Syntax

    value1 NOT BETWEEN [ ASYMMETRIC | SYMMETRIC ] value2 AND value3

Description

By default (or with the ASYMMETRIC keyword),

The `NOT BETWEEN` function returns TRUE if `value1` is less than `value2` or greater than `value3`, if ASYMMETRIC is specified.

If SYMMETRIC is specified, The `NOT BETWEEN` function returns TRUE if `value1` is not inclusively between `value2` and `value3`.

When either `value2` or `value3` is NULL, returns TRUE or UNKNOWN.

Examples

    -- returns TRUE
    SELECT 12 NOT BETWEEN 15 AND 12;
    
    -- returns FALSE
    SELECT 12 NOT BETWEEN SYMMETRIC 15 AND 12;
    
    -- returns UNKNOWN
    SELECT 12 NOT BETWEEN NULL AND 15;
    
    -- returns TRUE
    SELECT 12 NOT BETWEEN 15 AND NULL;
    
    --  returns UNKNOWN
    SELECT 12 NOT BETWEEN SYMMETRIC 12 AND NULL;

### EXISTS¶

Check whether a query returns a row.

Syntax

    EXISTS (sub-query)

Description

The `EXISTS` function returns TRUE if `sub-query` returns at least one row.

The `EXISTS` function is supported only if the operation can be rewritten in a join and group operation.

For streaming queries, the operation is rewritten in a join and group operation.

The required state to compute the query result might grow indefinitely, depending on the number of distinct input rows. Provide a query configuration with valid retention interval to prevent excessive state size.

Examples

    SELECT user_id, item_id
    FROM user_behavior
    WHERE EXISTS (
      SELECT * FROM category
      WHERE category.item_id = user_behavior.item_id
      AND category.name = 'book'
    );

### IN¶

Checks whether a value exists in a list.

Syntax

    value1 IN (value2 [, value3]* )
    value IN (sub-query)

Description

The `IN` function returns TRUE if `value1` exists in the specified list `(value2, value3, ...)`.

If a subquery is specified, The `IN` function returns TRUE if `value` is equal to a row returned by `sub-query`.

When `(value2, value3, ...)` contains NULL, The `IN` function returns TRUE if the element can be found and UNKNOWN otherwise.

Always returns UNKNOWN if `value1` is NULL.

Examples

    -- returns FALSE
    SELECT 4 IN (1, 2, 3);
    
    -- returns TRUE
    SELECT 1 IN (1, 2, NULL);
    
    -- returns UNKNOWN
    SELECT 4 IN (1, 2, NULL);

### NOT IN¶

Checks whether a value doesn’t exist in a list.

Syntax

    value1 NOT IN (value2 [, value3]* )
    value NOT IN (sub-query)

Description

The `NOT IN` function returns TRUE if `value1` does not exist in the specified list `(value2, value3, ...)`.

If a subquery is specified, The `NOT IN` function returns TRUE if `value` isn’t equal to a row returned by `sub-query`.

When `(value2, value3, ...)` contains NULL, the `NOT IN` function returns FALSE if `value1` can be found and UNKNOWN otherwise.

Always returns UNKNOWN if value1 is NULL.

Examples

    -- returns TRUE
    SELECT 4 NOT IN (1, 2, 3);
    
    -- returns FALSE
    SELECT 1 NOT IN (1, 2, NULL);
    
    -- returns UNKNOWN
    SELECT 4 NOT IN (1, 2, NULL);

### IS DISTINCT FROM¶

Checks whether two values are different.

Syntax

    value1 IS DISTINCT FROM value2

Description

The `IS DISTINCT FROM` function returns TRUE if two values are different.

NULL values are treated as identical.

Examples

    --  returns TRUE
    SELECT 1 IS DISTINCT FROM 2;
    
    --  returns TRUE
    SELECT 1 IS DISTINCT FROM NULL;
    
    --  returns FALSE
    SELECT NULL IS DISTINCT FROM NULL;

### IS NOT DISTINCT FROM¶

Checks whether two values are equal.

Syntax

    value1 IS NOT DISTINCT FROM value2

Description

The `IS NOT DISTINCT FROM` function returns TRUE if two values are equal.

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

## Conversion functions¶

  * CAST
  * TRY_CAST
  * TYPEOF

### CAST¶

Casts a value to a different type.

Syntax

    CAST(value AS type)

Description

The `CAST` function returns the specified value cast to the type specified by `type`.

A cast error throws an exception and fails the job.

When performing a cast operation that may fail, like STRING to INT, prefer TRY_CAST, to enable handling errors.

If `table.exec.legacy-cast-behaviour` is enabled, the `CAST` function behaves like `TRY_CAST`.

Examples

    --  returns 42
    SELECT CAST('42' AS INT);
    
    -- returns NULL of type STRING
    SELECT CAST(NULL AS STRING);
    
    --  throws an exception and fails the job
    SELECT CAST('not-a-number' AS INT);

### TRY_CAST¶

Casts a value to a different type and returns NULL on error.

Syntax

    TRY_CAST(value AS type)

Description
    Similar to the CAST function, but in case of error, returns NULL rather than failing the job.
Examples

    --  returns 42
    SELECT TRY_CAST('42' AS INT);
    
    --  returns NULL of type STRING
    SELECT TRY_CAST(NULL AS STRING);
    
    --  returns NULL of type INT
    SELECT TRY_CAST('not-a-number' AS INT);
    
    --  returns 0 of type INT
    SELECT COALESCE(TRY_CAST('not-a-number' AS INT), 0);

### TYPEOF¶

Gets the string representation of a data type.

Syntax

    TYPEOF(input)
    TYPEOF(input, force_serializable)

Description

The `TYPEOF` function returns the string representation of the input expression’s data type.

By default, the returned string is a summary string that might omit certain details for readability.

If `force_serializable` is set to TRUE, the string represents a full data type that can be persisted in a catalog.

Anonymous, inline data types have no serializable string representation. In these cases, NULL is returned.

Examples

    -- returns "CHAR(13) NOT NULL"
    SELECT TYPEOF('a string type');
    
    -- returns "INT NOT NULL"
    SELECT TYPEOF(23);
    
    -- returns "DATE NOT NULL"
    SELECT TYPEOF(DATE '2023-05-04');
    
    -- returns "NULL"
    SELECT TYPEOF(NULL);

## Other built-in functions¶

  * [Aggregate Functions](aggregate-functions.html#flink-sql-aggregate-functions)
  * [Collection Functions](collection-functions.html#flink-sql-collection-functions)
  * Comparison Functions
  * [Conditional Functions](conditional-functions.html#flink-sql-conditional-functions)
  * [Datetime Functions](datetime-functions.html#flink-sql-datetime-functions)
  * [Hash Functions](hash-functions.html#flink-sql-hash-functions)
  * [JSON Functions](json-functions.html#flink-sql-json-functions)
  * [ML Preprocessing Functions](ml-preprocessing-functions.html#flink-sql-ml-preprocessing-functions)
  * [Model Inference Functions](model-inference-functions.html#flink-sql-model-inference-functions)
  * [Numeric Functions](numeric-functions.html#flink-sql-numeric-functions)
  * [String Functions](string-functions.html#flink-sql-string-functions)
  * [Table API Functions](table-api-functions.html#flink-table-api-functions)

## Related content¶

  * [User-defined Functions](../../concepts/user-defined-functions.html#flink-sql-udfs)
  * [Create a User Defined Function](../../how-to-guides/create-udf.html#flink-sql-create-udf)

Note

This website includes content developed at the [Apache Software Foundation](https://www.apache.org/) under the terms of the [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0.html).
