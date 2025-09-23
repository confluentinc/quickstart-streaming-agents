---
source_url: https://docs.confluent.io/cloud/current/flink/reference/sql-syntax.html
title: Flink SQL Syntax in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'sql-syntax.html']
scraped_date: 2025-09-05T13:45:56.989089
---

# Flink SQL Syntax in Confluent Cloud for Apache Flink¶

SQL is a domain-specific language for managing and manipulating data. It’s used primarily to work with structured data, where the types and relationships across entities are well-defined. Originally adopted for relational databases, SQL is rapidly becoming the language of choice for stream processing. It’s declarative, expressive, and ubiquitous.

The American National Standards Institute (ANSI) maintains a standard for the specification of SQL. Flink SQL is compliant with ANSI SQL 2011. Beyond the standard, there are many flavors and extensions to SQL so that it can express programs beyond what’s possible with the SQL 2011 grammar.

## Lexical structure¶

The grammar of Apache Flink® parses SQL using [Apache Calcite](https://calcite.apache.org/docs/reference.html), which supports standard ANSI SQL.

## Syntax¶

Flink SQL inputs are made up of a series of [statements](../concepts/statements.html#flink-sql-statements). Each statement is made up of a series of tokens and ends in a semicolon (`;`). The tokens that apply depend on the statement being invoked.

A token is any keyword, identifier, backticked identifier, literal, or special character. By convention, tokens are separated by whitespace, unless there is no ambiguity in the grammar. This happens when tokens flank a special character.

The following example statements are syntactically valid Flink SQL input:

    -- Create a users table.
    CREATE TABLE users (
      user_id STRING,
      registertime BIGINT,
      gender STRING,
      regionid STRING
    );

    -- Populate the table with mock users data.
    INSERT INTO users VALUES
      ('Thomas A. Anderson', 1677260724, 'male', 'Region_4'),
      ('Trinity', 1677260733, 'female', 'Region_4'),
      ('Morpheus', 1677260742, 'male', 'Region_8');

    SELECT * FROM users;

## Keywords¶

Some tokens, such as SELECT, INSERT, and CREATE, are _keywords_. Keywords are reserved tokens that have a specific meaning in Flink’s syntax. They control their surrounding allowable tokens and execution semantics. Keywords are case insensitive, meaning `SELECT` and `select` are equivalent. You can’t create an identifier that is already a reserved word, unless you use backticked identifiers, for example, ``table``.

For a complete list of keywords, see [Flink SQL Reserved Keywords](keywords.html#flink-sql-keywords).

## Identifiers¶

Identifiers are symbols that represent user-defined entities, like tables, columns, and other objects. For example, if you have a table named `t1`, `t1` is an identifier for that table.

By default, identifiers _are_ case-sensitive, meaning `t1` and `T1` refer to different tables.

Unless an identifier is backticked, it may be composed only of characters that are a letter, number, or underscore. There is no imposed limit on the number of characters.

To make it possible to use any character in an identifier, you can enclose it in backtick characters (```) when you declare and use it. A backticked identifier is useful when you don’t control the data, so it might have special characters, or even keywords.

If you want to use one of the keyword strings as an identifier, enclose them with backticks, for example:

* ``value``
* ``count``

When you use backticked identifiers, Flink SQL captures the case exactly, and any future references to the identifier are case-sensitive. For example, if you declare the following table:

    CREATE TABLE `t1` (
      id VARCHAR,
      `@MY-identifier-table-column!` INT);

You must select from it by backticking the table name and column name and using the original casing:

    SELECT `@MY-identifier-table-column!` FROM `t1`;

If you use an invalid identifier without enclosing it in backticks, you receive a `SQL parse failed` error. For example, the following SQL query tries to read records from a table named `table-with-dashes`, but the dash character (`-`) is not valid in an identifier.

    SELECT * FROM table-with-dashes;

The error output resembles:

    SQL parse failed. Encountered "-" at line 1, column 20.

You can fix the error by enclosing the identifier with backticks:

    SELECT * FROM `table-with-dashes`;

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
