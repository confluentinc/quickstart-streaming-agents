---
document_id: flink_reference_sql-syntax_chunk_2
source_file: flink_reference_sql-syntax.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/sql-syntax.html
title: Flink SQL Syntax in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 2
---

backticks: SELECT * FROM `table-with-dashes`;

## Constants¶

There are three implicitly typed constants, or literals, in Flink SQL: strings, numbers, and booleans.

### String constants¶

A string constant is an arbitrary series of characters surrounded by single quotes (`'`), like `'Hello world'`. To include a quote inside of a string literal, escape the quote by prefixing it with another quote, for example, `'You can call me ''Stuart'', or Stu.'`

### Numeric constants¶

Numeric constants are accepted in the following forms:

  * digits
  * digits.[digits][e[+-]digits]
  * [digits].digits[e[+-]digits]
  * digitse[+-]digits

where `digits` is one or more single-digit integers (_0_ through _9_).

  * At least one digit must be present before or after the decimal point, if there is one.
  * At least one digit must follow the exponent symbol `e`, if there is one.
  * No spaces, underscores, or any other characters are allowed in the constant.
  * Numeric constants may also have a `+` or `-` prefix, but this is considered to be a function applied to the constant, not the constant itself.

Here are some examples of valid numeric constants:

  * `5`
  * `7.2`
  * `0.0087`
  * `1.`
  * `.5`
  * `1e-3`
  * `1.332434e+2`
  * `+100`
  * `-250`

### Boolean constants¶

A boolean constant is represented as either the identifier `true` or `false`. Boolean constants are not case-sensitive, which means that `true` evaluates to the same value as `TRUE`.

## Operators¶

Operators are infix functions composed of special characters. Flink SQL doesn’t allow you to add user-space operators.

For a complete list of operators, see [Comparison Functions in Confluent Cloud for Apache Flink](functions/comparison-functions.html#flink-sql-comparison-and-equality-functions).

## Special characters¶

Some characters have a particular meaning that doesn’t correspond to an operator. The following list describes the special characters and their purposes.

  * Parentheses (`()`) retain their usual meaning in programming languages for grouping expressions and controlling the order of evaluation.
  * Brackets (`[]`) are used to work with arrays, both in their construction and subscript access. They also allow you to key into maps.
  * Commas (`,`) delineate a discrete list of entities.
  * The semi-colon (`;`) terminates a SQL statement.
  * The asterisk (`*`), when used in particular syntax, is used as an “all” qualifier. This is seen most commonly in a SELECT command to retrieve all columns.
  * The period (`.`) accesses a column in a table or a field in a struct data type.

## Comments¶

A comment is a string beginning with two dashes. It includes all of the content from the dashes to the end of the line:

    -- Here is a comment.

You can also span a comment over multiple lines by using C-style syntax:

    /* Here is
       another comment.
    */

## Lexical precedence¶

Operators are evaluated using the following order of precedence:

  1. `*`, `/`, `%`
  2. `+`, `-`
  3. `=`, `>`, `<`, `>=`, `<=`, `<>`, `!=`
  4. `NOT`
  5. `AND`
  6. `BETWEEN`, `LIKE`, `OR`

In an expression, when two operators have the same precedence level, they’re evaluated left-to-right, based on their position.

You can enclose an expression in parentheses to force precedence or clarify precedence, for example, `(5 + 2) * 3`.
