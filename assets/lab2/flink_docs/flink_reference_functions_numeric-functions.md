---
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/numeric-functions.html
title: SQL numeric functions in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'functions', 'numeric-functions.html']
scraped_date: 2025-09-05T13:48:31.663650
---

# Numeric Functions in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides these built-in numeric functions to use in SQL queries:

Numeric | Trigonometry | Random number generators | Utility
---|---|---|---
ABS | ACOS | RAND | HEX
BIN | ASIN | RAND(INT) | UUID
CEILING | ATAN | RAND_INTEGER(INT) | UNHEX
E | ATAN2 | RAND_INTEGER(INT1, INT2) |
EXP | COS |  |
FLOOR | COSH |  |
LN | COT |  |
LOG | DEGREES |  |
LOG10 | RADIANS |  |
LOG2 | SIN |  |
PERCENTILE | SINH |  |
PI | TAN |  |
POWER | TANH |  |
ROUND |  |  |
SIGN |  |  |
SQRT |  |  |
TRUNCATE |  |  |

## ABS¶

Gets the absolute value of a number.

Syntax

    ABS(numeric)

Description
    The `ABS` function returns the absolute value of the specified NUMERIC.
Examples

    -- returns 23
    SELECT ABS(-23);

    -- returns 23
    SELECT ABS(23);

## ACOS¶

Computes the arccosine.

Syntax

    ACOS(numeric)

Description
    The `ACOS` function returns the arccosine of the specified NUMERIC.
Examples

    -- returns 1.5707963267948966
    -- (approximately PI/2)
    SELECT ACOS(0);

    -- returns 0.0
    SELECT ACOS(1);

## ASIN¶

Computes the arcsine.

Syntax

    ASIN(numeric)

Description
    The `ASIN` function returns the arcsine of the specified NUMERIC.
Examples

    -- returns 0.0
    SELECT ASIN(0);

    -- returns 1.5707963267948966
    -- (approximately PI/2)
    SELECT ASIN(1);

## ATAN¶

Computes the arctangent.

Syntax

    ATAN(numeric)

Description
    The `ATAN` function returns the arctangent of the specified NUMERIC.
Examples

    -- returns 0.0
    SELECT ATAN(0);

    -- returns 0.7853981633974483
    -- (approximately PI/4)
    SELECT ATAN2(1);

## ATAN2¶

Computes the arctangent of a 2D point.

Syntax

    ATAN2(numeric1, numeric2)

Description
    Returns the arctangent of the coordinate specified by `(numeric1, numeric2)`.
Examples

    -- returns 0.0
    SELECT ATAN2(0, 0);

    -- returns 0.7853981633974483
    -- (approximately PI/4)
    SELECT ATAN2(1, 1);

## BIN¶

Converts an INTEGER number to binary.

Syntax

    BIN(int)

Description
    The `BIN` function returns a string representation of the specified INTEGER in binary format. Returns NULL if `int` is NULL.
Examples

    -- returns "100"
    SELECT BIN(4);

    -- returns "1100"
    SELECT BIN(12);

## CEILING¶

Rounds a number up.

Syntax

    CEILING(numeric)

Description

The `CEILING` function rounds the specified NUMERIC up and returns the smallest integer that’s greater than or equal to the NUMERIC.

This function can be abbreviated to `CEIL(numeric)`.

Examples

    -- returns 24
    SELECT CEIL(23.55);

    -- returns -23
    SELECT CEIL(-23.55);

## COS¶

Computes the cosine of an angle.

Syntax

    COS(numeric)

Description
    Returns the cosine of the specified NUMERIC in radians.
Examples

    -- returns 1.0
    SELECT COS(0);

    -- returns 6.123233995736766E-17
    -- (approximately 0)
    SELECT COS(PI()/2);

## COSH¶

Computes the hyperbolic cosine.

Syntax

    COT(numeric)

Description
    The `COSH` function returns the hyperbolic cosine of the specified NUMERIC. The return value type is DOUBLE.
Example

    -- returns 1.0
    SELECT COSH(0);

## COT¶

Computes the cotangent of an angle.

Syntax

    COT(numeric)

Description
    The `COT` function returns the cotangent of the specified NUMERIC in radians.
Example

    -- returns 6.123233995736766E-17
    -- (approximately 0)
    SELECT COT(PI()/2);

## DEGREES¶

Converts an angle in radians to degrees.

Syntax

    DEGREES(numeric)

Description
    The `DEGREES` function converts the specified NUMERIC value in radians to degrees.
Examples

    -- returns 90.0
    SELECT DEGREES(PI()/2);

    -- returns 180.0
    SELECT DEGREES(PI());

    -- returns -45.0
    SELECT DEGREES(-PI()/4);

## E¶

Gets the approximate value of _e_.

Syntax

    E()

Description
    Returns a value that is closer than any other values to _e_ , the base of the natural logarithm.
Examples

    -- returns 2.718281828459045
    -- which is the approximate value of e
    SELECT E();

    -- returns 1.0
    SELECT LN(E());

## EXP¶

Computes _e_ raised to a power.

Syntax

    EXP(numeric)

Description
    The `EXP` function returns _e_ , the base of the natural logarithm, raised to the power of the specified NUMERIC.
Examples

    -- returns 2.718281828459045
    -- which is the approximate value of e
    SELECT EXP(1);

    -- returns 7.38905609893065
    SELECT EXP(2);

    -- returns 0.36787944117144233
    SELECT EXP(-1);

## FLOOR¶

Rounds a number down.

Syntax

    FLOOR(numeric)

Description
    The `FLOOR` function rounds the specified NUMERIC down and returns the largest integer that is less than or equal to the NUMERIC.
Examples

    -- returns 23
    SELECT FLOOR(23.55);

    -- returns -24
    SELECT FLOOR(-23.55);

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

## RAND_INTEGER(INT1, INT2)¶

Gets a random integer in a range.

Syntax

    RAND_INTEGER(seed INT, upper_bound INT)

Description

The `RAND_INTEGER(INT1, INT2)` function returns a pseudorandom integer value in the range _[0, upper_bound)_ with the initial seed value `seed`.

Two `RAND_INTEGER` functions return identical sequences of numbers if they have the same initial seed and bound.

Examples

    -- returns 227
    SELECT RAND_INTEGER(23, 1000);

    -- returns 1130
    SELECT RAND_INTEGER(42, 10000);

## ROUND¶

Rounds a number to the specified precision.

Syntax

    ROUND(numeric, int)

Description
    The `ROUND` function returns a number rounded to `int` decimal places for the specified NUMERIC.
Examples

    -- returns 23.6
    SELECT ROUND(23.58, 1);

    -- returns 3.1416
    SELECT ROUND(PI(), 4);

## SIGN¶

Gets the sign of a number.

Syntax

    SIGN(numeric)

Description
    The `SIGN` function returns the signum of the specified NUMERIC.
Examples

    -- returns -1.00
    SELECT SIGN(-23.55);

    -- returns 1.000
    SELECT SIGN(606.808);

## SIN¶

Compute the sine of an angle.

Syntax

    SIN(numeric)

Description
    The `SIN` function returns the sine of the specified NUMERIC in radians.
Examples

    -- returns 1.0
    SELECT SIN(PI()/2);

    -- returns -1.0
    SELECT SIN(-PI()/2);

## SINH¶

Computes the hyperbolic sine.

Syntax

    SINH(numeric)

Description
    The `SINH` function returns the hyperbolic sine of the specified NUMERIC. The return type is DOUBLE.
Example

    -- returns 0.0
    SELECT SINH(0);

## SQRT¶

Computes the square root of a number.

Syntax

    SQRT(numeric)

Description
    The `SQRT` function returns the square root of the specified NUMERIC, which must greater than or equal to _0_.
Examples

    -- returns 8.0
    SELECT SQRT(64);

    -- returns 10.0
    SELECT SQRT(100);

    -- returns 12.0
    SELECT SQRT(144);

## TAN¶

Computes the tangent of an angle.

Syntax

    TAN(numeric)

Description
    The `TAN` function returns the tangent of the specified NUMERIC in radians.
Examples

    -- returns 0.0
    SELECT TAN(0);

    -- returns 0.9999999999999999
    SELECT TAN(PI()/4);

## TANH¶

Computes the hyperbolic tangent.

Syntax

    TANH(numeric)

Description
    The `TANH` function returns the hyperbolic tangent of the specified NUMERIC. The return type is DOUBLE.
Examples

    -- returns 0.0
    SELECT TANH(0);

    -- returns 0.9999092042625951
    SELECT TANH(5);

## TRUNCATE¶

Truncates a number to the specified precision.

Syntax

    TRUNCATE(numeric, integer)

Description

The `TRUNCATE(numeric, integer)` function returns the specified NUMERIC truncated to the number of decimal places specified by `integer`. Returns NULL if `numeric` or `integer` is NULL.

If `integer` is _0_ , the result has no decimal point or fractional part.

The `integer` value can be negative, which causes `integer` digits to the left of the decimal point to become zero.

If `integer` is not set, the function truncates as if `integer` were _0_.

Examples

    --  returns 42.32
    SELECT TRUNCATE(42.324, 2);

    -- returns 42.0
    SELECT TRUNCATE(42.324);

    -- returns 40
    SELECT TRUNCATE(42.324, -1);

## UNHEX¶

Converts a hexadecimal expression to BINARY.

Syntax

    UNHEX(str)

Arguments
    `str`: a hexadecimal STRING. The characters in `str` must be legal hexadecimal digits: `0` \- `9`, `A` \- `F`, and `a` \- `f`.
Returns
    A BINARY string. If `str` contains any nonhexadecimal digits, or is NULL, the return value is NULL.
Description

The `UNHEX` function interprets each pair of characters in `str` as a hexadecimal number and converts it to the byte represented by the number.

If the length of `str` is odd, the first character is discarded, and the result is left-padded with a NULL byte.

Examples

    -- returns "Flink"
    SELECT DECODE(UNHEX('466C696E6B') , 'UTF-8');

    -- returns NULL
    SELECT UNHEX('ZZ');

Related functions

* [DECODE](string-functions.html#flink-sql-decode-function)
* HEX

## UUID¶

Generates a UUID.

Syntax

    UUID()

Description

The `UUID()` function returns a Universally Unique Identifier (UUID) string that conforms to the [RFC 4122 type 4 specification](https://www.rfc-editor.org/info/rfc4122).

The UUID is generated using a cryptographically strong pseudo-random number generator.

Examples

    -- an example return value is
    -- 3d3c68f7-f608-473f-b60c-b0c44ad4cc4e
    SELECT UUID();

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
* Numeric Functions
* [String Functions](string-functions.html#flink-sql-string-functions)
* [Table API Functions](table-api-functions.html#flink-table-api-functions)
