---
document_id: flink_reference_queries_select_chunk_1
source_file: flink_reference_queries_select.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/select.html
title: SQL SELECT statement in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 3
---

# SELECT Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables querying the content of your tables by using familiar SELECT syntax.

## Syntax¶

    SELECT [DISTINCT] select_list FROM table_expression [ WHERE boolean_expression ] [ LIMIT row_limit ]

## Description¶

The SELECT statement in Flink does what the SQL standard says it must do. You needn’t look further than standard SQL itself to understand the behavior.

For example, UNION without ALL means that duplicate rows must be removed.

Flink maintains the relation, called a [dynamic table](../../concepts/dynamic-tables.html#flink-sql-dynamic-tables), specified by the SQL query. Its behavior is always the same as if you ran the SQL query again, over the current snapshot of the data, each time a new row arrives for any table in the relation.

This formalism is what enables you to reason about exactly what Flink will do just by understanding what any SQL system, like MySQL, Snowflake, or Oracle, would do.

Another way to understand what Flink SQL does is to consider the following statement:

    SELECT * FROM clicks ORDER BY clickTime LIMIT 10;

This statement doesn’t only look at 10 rows, sort them, and terminate. It maintains this relation, and as new orders arrive, the relation changes, always showing the top 10 most recent orders. This is exactly as if you re-ran the query each time a new row was written to the `clicks` table. You’ll get the same result.

## Select list¶

The `select_list` specification `*` means the query resolves all columns. But in production, using `*` is not recommended, because it makes queries less robust to catalog changes. Instead, use a `select_list` to specify a subset of available columns or make calculations using the columns. For example, if an `orders` table has columns named `order_id`, `price`, and `tax` you could write the following query:

    SELECT order_id, price + tax FROM orders

## Table expression¶

The `table_expression` can be any source of data, including a table, view, or `VALUES` clause, the joined results of multiple existing tables, or a subquery.

Assuming that an `orders` table is available in the catalog, the following would read all rows from .

    SELECT * FROM orders;

## VALUES clause¶

Queries can consume from inline data by using the `VALUES` clause. Each tuple corresponds to one row. You can provide an alias to assign a name to each column.

     SELECT order_id, price
       FROM (VALUES (1, 2.0), (2, 3.1))
       AS t (order_id, price);

Your output should resemble:

    order_id price
    1        2.0
    2        3.1

## WHERE clause¶

Filter rows by using the `WHERE` clause.

     SELECT price + tax
       FROM orders
       WHERE id = 10;

## Functions¶

You can invoke built-in scalar functions on the columns of a single row.

    SELECT PRETTY_PRINT(order_id) FROM orders;

## DISTINCT¶

If `SELECT DISTINCT` is specified, all duplicate rows are removed from the result set, which means that one row is kept from each group of duplicates.

For streaming queries, the required state for computing the query result might grow infinitely. State size depends on the number of distinct rows.

    SELECT DISTINCT id FROM orders;
