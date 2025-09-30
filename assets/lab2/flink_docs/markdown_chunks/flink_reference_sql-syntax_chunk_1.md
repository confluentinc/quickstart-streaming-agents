---
document_id: flink_reference_sql-syntax_chunk_1
source_file: flink_reference_sql-syntax.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/sql-syntax.html
title: Flink SQL Syntax in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 2
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
