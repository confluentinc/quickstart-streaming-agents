---
document_id: flink_reference_functions_numeric-functions_chunk_2
source_file: flink_reference_functions_numeric-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/numeric-functions.html
title: SQL numeric functions in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 4
---

-- returns -24 SELECT FLOOR(-23.55);

## HEX¶

Converts an integer or string to hexadecimal.

Syntax

    HEX(numeric)
    HEX(string)

Description
    The `HEX` function returns a string representation of an integer NUMERIC value or a STRING in hexadecimal format. Returns NULL if the argument is NULL.
Examples

    -- returns "14"
    SELECT HEX(20);

    --  returns "64"
    SELECT HEX(100);

    -- returns "68656C6C6F2C776F726C64"
    SELECT HEX('hello,world');

Related function
    UNHEX

## LN¶

Computes the natural log.

Syntax

    LN(numeric)

Description
    The `LN` function returns the natural logarithm (base _e_) of the specified NUMERIC.
Examples

    -- returns 1.0
    SELECT LN(E());

    -- returns 0.0
    SELECT LN(1);

## LOG¶

Computes a logarithm.

Syntax

    LOG(numeric1, numeric2)

Description

The `LOG` function returns the logarithm of `numeric2` to the base of `numeric1`.

When called with one argument, returns the natural logarithm of `numeric2`.

`numeric2` must be greater than _0_ , and `numeric1` must be greater than _1_.

Examples

    -- returns 1.0
    SELECT LOG(10, 10);

    -- returns 8.0
    SELECT LOG(2, 256);

    -- returns 1.0
    SELECT LOG(E());

## LOG10¶

Computes the base-10 logarithm.

Syntax

    LOG10(numeric)

Description
    The `LOG10` function returns the base-10 logarithm of the specified NUMERIC.
Examples

    -- returns 1.0
    SELECT LOG10(10);

    -- returns 3.0
    SELECT LOG(1000);

## LOG2¶

Computes the base-2 logarithm.

Syntax

    LOG2(numeric)

Description The `LOG2` function returns the base-2 logarithm of the specified NUMERIC.

Examples

    -- returns 1.0
    SELECT LOG2(2);

    -- returns 10.0
    SELECT LOG2(1024);

## PERCENTILE¶

Gets a percentile value based on a continuous distribution.

Syntax

    PERCENTILE(expr, percentage[, frequency])

Arguments

* `expr`: A NUMERIC expression.
* `percentage`: A NUMERIC expression between 0 and 1, or an ARRAY of NUMERIC expressions, each between 0 and 1.
* `frequency`: An optional integral number greater than 0 that describes the number of times `expr` must be counted. The default is 1.

Returns
    DOUBLE if `percentage` is numeric, or an ARRAY of DOUBLE if `percentage` is an ARRAY.
Description

The `PERCENTILE` function returns a percentile value based on a continuous distribution of the input column.

If no input row lies exactly at the desired percentile, the result is calculated using linear interpolation of the two nearest input values. NULL values are ignored in the calculation.

Examples

    -- returns 6.0
    SELECT PERCENTILE(col, 0.3) FROM (VALUES (0), (10), (10)) AS col;

    -- returns 6.0
    SELECT PERCENTILE(col, 0.3, freq) FROM ( VALUES (0, 1), (10, 2)) AS tab(col, freq);

    -- returns [2.5,7.5]
    SELECT PERCENTILE(col, ARRAY(0.25, 0.75)) FROM (VALUES (0), (10)) AS col;

    -- returns 50.0
    SELECT PERCENTILE(age, 0.5) FROM (VALUES 0, 50, 100) AS age;

## PI¶

Gets the approximate value of _pi_.

Syntax

    PI()

Description
    The `PI` function returns a value that is closer than any other values to _pi_.
Examples

    -- returns 3.141592653589793
    -- (approximately PI)
    SELECT PI();

    -- returns -1.0
    SELECT COS(PI());

## POWER¶

Raises a number to a power.

Syntax

    POWER(numeric1, numeric2)

Description
    The `POWER` function returns `numeric1` raised to the power of `numeric2`.
Examples

    -- returns 1000.0
    SELECT POWER(10, 3);

    -- returns 256.0
    SELECT POWER(2, 8);

    -- returns 1.0
    SELECT POWER(500, 0);

## RADIANS¶

Converts an angle in degrees to radians.

Syntax

    RADIANS(numeric)

Description
    The `RADIANS` function converts the specified NUMERIC value in degrees to radians.
Examples

    -- returns 3.141592653589793
    -- (approximately PI)
    SELECT RADIANS(180);

    -- returns 0.7853981633974483
    -- (approximately PI/4)
    SELECT RADIANS(45);

## RAND¶

Gets a random number.

Syntax

    RAND()

Description
    The `RAND` function returns a pseudorandom DOUBLE value in the range _[0.0, 1.0)_.
Example

    -- an example return value is 0.9346105267662114
    SELECT RAND();

## RAND(INT)¶

Gets a random number from a seed.

Syntax

    RAND(seed INT)

Description

The `RAND(INT)` function returns a pseudorandom DOUBLE value in the range _[0.0, 1.0)_ with the initial `seed` integer.

Two RAND functions return identical sequences of numbers if they have the same initial seed value.

Examples

    -- returns 0.7321323355141605
    SELECT RAND(23);

    -- returns 0.7275636800328681
    SELECT RAND(42);

## RAND_INTEGER(INT)¶

Gets a pseudorandom integer.

Syntax

    RAND_INTEGER(upper_bound INT)

Description
    The `RAND_INTEGER(INT)` functions returns a pseudorandom integer value in the range _[0, upper_bound)_.
Examples

    -- returns 20
    SELECT RAND_INTEGER(23);

    -- returns 28
    SELECT RAND_INTEGER(42);
