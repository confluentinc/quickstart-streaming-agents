---
document_id: flink_reference_statements_show_chunk_2
source_file: flink_reference_statements_show.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/show.html
title: SQL SHOW Statements in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 5
---

+-----------------------+ | cluster_0 | +-----------------------+

## SHOW TABLES¶

Syntax

    SHOW TABLES [ [catalog_name.]database_name ] [ [NOT] LIKE <sql_like_pattern> ]

Description

Show all tables for the current database. You can filter the output of SHOW TABLES by using the LIKE clause with an optional matching pattern.

The optional LIKE clause shows all tables with names that match `<sql_like_pattern>`.

The syntax of the SQL pattern in a `LIKE` clause is the same as in the `MySQL` dialect.

  * `%` matches any number of characters, including zero characters. Use the backslash character to escape the `%` character: `\%` matches one `%` character.
  * `_` matches exactly one character. Use the backslash character to escape the `_` character: `\_` matches one `_` character.

Example

Create two tables in the current catalog: `flights` and `orders`.

    -- Create a flights table.
    CREATE TABLE flights (
      flight_id STRING,
      origin STRING,
      destination STRING
    );

    -- Create an orders table.
    CREATE TABLE orders (
      user_id BIGINT NOT NULL,
      product_id STRING,
      amount INT
    );

Show all tables in the current database that are similar to the specified SQL pattern.

    SHOW TABLES LIKE 'f%';

Your output should resemble:

    +------------+
    | table name |
    +------------+
    | flights    |
    +------------+

Show all tables in the given database that are not similar to the specified SQL pattern.

    SHOW TABLES NOT LIKE 'f%';

Your output should resemble:

    +------------+
    | table name |
    +------------+
    | orders     |
    +------------+

Show all tables in the current database.

    SHOW TABLES;

    +------------+
    | table name |
    +------------+
    | flights    |
    | orders     |
    +------------+
