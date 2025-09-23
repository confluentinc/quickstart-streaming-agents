---
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/select.html
title: SQL SELECT statement in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'queries', 'select.html']
scraped_date: 2025-09-05T13:50:06.235026
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

## Usage¶

In the Flink SQL shell or in a Cloud Console workspace, run the following commands to see examples of the SELECT statement.

  1. Create a table for web page click events.

         -- Create a table for web page click events.
         CREATE TABLE clicks (
           ip_address VARCHAR,
           url VARCHAR,
           click_ts_raw BIGINT
         );

  2. Populate the table with mock clickstream data.

         -- Populate the table with mock clickstream data.
         INSERT INTO clicks
         VALUES( '10.0.0.1',  'https://acme.com/index.html',     1692812175),
               ( '10.0.0.12', 'https://apache.org/index.html',   1692826575),
               ( '10.0.0.13', 'https://confluent.io/index.html', 1692826575),
               ( '10.0.0.1',  'https://acme.com/index.html',     1692812175),
               ( '10.0.0.12', 'https://apache.org/index.html',   1692819375),
               ( '10.0.0.13', 'https://confluent.io/index.html', 1692826575);

Press ENTER to return to the SQL shell. Because INSERT INTO VALUES is a point-in-time statement, it exits after it completes inserting records.

  3. View all rows in the `clicks` table by using a SELECT statement.

         SELECT * FROM clicks;

Your output should resemble:

         ip_address url                             click_ts_raw
         10.0.0.1   https://acme.com/index.html     1692812175
         10.0.0.12  https://apache.org/index.html   1692826575
         10.0.0.13  https://confluent.io/index.html 1692826575
         10.0.0.1   https://acme.com/index.html     1692812175
         10.0.0.12  https://apache.org/index.html   1692819375
         10.0.0.13  https://confluent.io/index.html 1692826575

  4. View only unique rows in the `clicks` table by using a SELECT DISTINCT statement.

         SELECT DISTINCT * FROM clicks;

Your output should resemble:

         ip_address url                             click_ts_raw
         10.0.0.1   https://acme.com/index.html     1692812175
         10.0.0.12  https://apache.org/index.html   1692826575
         10.0.0.13  https://confluent.io/index.html 1692826575
         10.0.0.12  https://apache.org/index.html   1692819375

  5. View only records that have the ip_address of `10.0.0.1` by using a SELECT WHERE statement.

         SELECT * FROM clicks WHERE ip_address='10.0.0.1';

Your output should resemble:

         ip_address url                         click_ts_raw
         10.0.0.1   https://acme.com/index.html 1692812175
         10.0.0.1   https://acme.com/index.html 1692812175

## Examples¶

The following examples show frequently encountered scenarios with SELECT.

### Most minimal statement¶

Syntax

    SELECT 1;

Properties

* Statement is bounded

### Check local time zone is configured correctly¶

Syntax

    SELECT NOW();

Properties

* Statement is bounded
* NOW() returns a TIMSTAMP_LTZ(3), so if the client is configured correctly, it should show a timestamp in your local time zone.

### Combine multiple tables into one¶

Syntax

    CREATE TABLE t_union_1 (i INT);
    CREATE TABLE t_union_2 (i INT);
    TABLE t_union_1 UNION ALL TABLE t_union_2;

    -- alternate syntax
    SELECT * FROM t_union_1
    UNION ALL
    SELECT * FROM t_union_2;

### Get insights into the current watermark¶

Syntax

    CREATE TABLE t_watermarked_insight (s STRING) DISTRIBUTED INTO 1 BUCKETS;

    INSERT INTO t_watermarked_insight VALUES ('Bob'), ('Alice'), ('Charly');

    SELECT $rowtime, CURRENT_WATERMARK($rowtime) FROM t_watermarked_insight;

The output resembles:

    $rowtime                EXPR$1
    2024-04-29 11:59:01.080 NULL
    2024-04-29 11:59:01.093 2024-04-04 15:27:37.433
    2024-04-29 11:59:01.094 2024-04-04 15:27:37.433

Properties

* The CURRENT_WATERMARK function returns the watermark that arrived at the operator evaluating the SELECT statement.
* The returned watermark is the minimum of all inputs, across all tables/topics and their partitions.
* If a common watermark was not received from all inputs, the function returns NULL.
* The CURRENT_WATERMARK function takes a [time attribute](../../concepts/timely-stream-processing.html#flink-sql-time-attributes), which is a column that has WATERMARK FOR defined.

A watermark is always emitted after the row has been processed, so the first row always has a NULL watermark.

Because the default watermark algorithm requires at least 250 records, initially it assumes the maximum lag of 7 days plus a safety margin of 7 days.

The watermark quickly (exponentially) goes down as more data arrives.

Sources emit watermarks every 200 ms, but within the first 200 ms they emit per row for powering examples like this.

### Flatten fields into columns¶

Syntax

    CREATE TABLE t_flattening (i INT, r1 ROW<i INT, s STRING>, r2 ROW<other INT>);

    SELECT r1.*, r2.* FROM t_flattening;

Properties
    You can apply the `*` operator on nested data, which enables flattening fields into columns of the table.
