---
document_id: flink_reference_functions_numeric-functions_chunk_3
source_file: flink_reference_functions_numeric-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/numeric-functions.html
title: SQL numeric functions in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 4
---

-- returns 28 SELECT RAND_INTEGER(42);

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
