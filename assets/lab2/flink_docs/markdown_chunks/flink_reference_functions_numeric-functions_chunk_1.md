---
document_id: flink_reference_functions_numeric-functions_chunk_1
source_file: flink_reference_functions_numeric-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/numeric-functions.html
title: SQL numeric functions in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 4
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
