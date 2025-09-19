---
document_id: flink_reference_functions_hash-functions_chunk_1
source_file: flink_reference_functions_hash-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/hash-functions.html
title: SQL hash functions in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Hash Functions in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides these built-in functions to generate hash codes in SQL queries:

  * MD5
  * SHA1
  * SHA2
  * SHA224
  * SHA256
  * SHA384
  * SHA512

## MD5¶

Gets the MD5 hash of a string.

Syntax

    MD5(string)

Description

The `MD5` function returns the MD5 hash of the specified string as a string of _32_ hexadecimal digits.

Returns NULL if `string` is NULL.

Example

    -- returns 99dc0ea422440e5b3f675cffe6d...
    SELECT MD5('string-to-hash');

## SHA1¶

Gets the SHA-1 hash of a string.

Syntax

    SHA1(string)

Description

The `SHA1` function returns the SHA-1 hash of the specified string as a string of _40_ hexadecimal digits.

Returns NULL if `string` is NULL.

Example

    -- returns 771a2b04044f8c51e3383a2675a...
    SELECT SHA1('string-to-hash');

## SHA2¶

Hashes a string with one of the SHA-2 functions.

Syntax

    SHA2(string, hashLength)

Description

The `SHA2` function returns the hash using the SHA-2 family of hash functions (SHA-224, SHA-256, SHA-384, and SHA-512).

  * The first argument, `string`, is the string to be hashed.
  * The second argument, `hashLength`, is the bit length of the result.

These are the valid bit lengths for `hashLength`:

  * _224_
  * _256_
  * _384_
  * _512_

Returns NULL if `string` or `hashLength` is NULL.

Example

    -- returns 222145560dbaa2abc1617e2c7ce...
    SELECT SHA2('string-to-hash', 512);

## SHA224¶

Gets the SHA-224 hash of a string.

Syntax

    SHA224(string)

Description

The `SHA224` function returns the SHA-224 hash of the specified string as a string of _56_ hexadecimal digits.

Returns NULL if `string` is NULL.

Example

    -- returns af1f1c988d9154f2ddb6201f60f...
    SELECT SHA224('string-to-hash');

## SHA256¶

Gets the SHA-256 hash of a string.

Syntax

    SHA256(string)

Description

The `SHA256` function returns the SHA-256 hash of the specified string as a string of _64_ hexadecimal digits.

Returns NULL if `string` is NULL.

Example

    -- returns 2267d414e45335fd02e64057d55...
    SELECT SHA256('string-to-hash');

## SHA384¶

Gets the SHA-384 hash of a string.

Syntax

    SHA384(string)

Description

The `SHA5384` function returns the SHA-384 hash of the specified string as a string of _96_ hexadecimal digits.

Returns NULL if `string` is NULL.

Example

    -- returns 02ba979b23f1b4a098732463ea8...
    SELECT SHA384('string-to-hash');

## SHA512¶

Gets the SHA-512 hash of a string.

Syntax

    SHA512(string)

Description

The `SHA512` function returns the SHA-512 hash of the specified string as a string of _128_ hexadecimal digits.

Returns NULL if `string` is NULL.

Example

    -- returns 222145560dbaa2abc1617e2c7ce...
    SELECT SHA512('string-to-hash');

## Other built-in functions¶

  * [Aggregate Functions](aggregate-functions.html#flink-sql-aggregate-functions)
  * [Collection Functions](collection-functions.html#flink-sql-collection-functions)
  * [Comparison Functions](comparison-functions.html#flink-sql-comparison-functions)
  * [Conditional Functions](conditional-functions.html#flink-sql-conditional-functions)
  * [Datetime Functions](datetime-functions.html#flink-sql-datetime-functions)
  * Hash Functions
  * [JSON Functions](json-functions.html#flink-sql-json-functions)
  * [ML Preprocessing Functions](ml-preprocessing-functions.html#flink-sql-ml-preprocessing-functions)
  * [Model Inference Functions](model-inference-functions.html#flink-sql-model-inference-functions)
  * [Numeric Functions](numeric-functions.html#flink-sql-numeric-functions)
  * [String Functions](string-functions.html#flink-sql-string-functions)
  * [Table API Functions](table-api-functions.html#flink-table-api-functions)
