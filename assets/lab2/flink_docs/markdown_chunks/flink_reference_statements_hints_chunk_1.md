---
document_id: flink_reference_statements_hints_chunk_1
source_file: flink_reference_statements_hints.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/hints.html
title: SQL HINTS in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Dynamic Table Options in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® supports dynamic table options, or SQL _hints_ , which enable you to specify or override [table options](create-table.html#flink-sql-with-options) dynamically.

## Syntax¶

To use dynamic table options, employ the following Oracle-style SQL hint syntax:

    table_path /*+ OPTIONS(key=val [, key=val]*) */

    key:
        stringLiteral
    val:
        stringLiteral

The dynamic options must be placed next to the table and not by any aliases, for example:

    SELECT * FROM t /*+ OPTIONS(...) */ AS alias;

## Description¶

Dynamic Table Options in Confluent Cloud for Apache Flink offer the following benefits:

* **Flexible configuration:** Specify table options on a per-statement basis, providing more flexibility than static options as stored in the table definition.
* **Query-specific adjustments:** Customize table behavior for individual queries without altering the permanent table definition.

## Examples¶

Here are some examples of using dynamic table options in Confluent Cloud for Apache Flink:

* Override [scan startup mode](create-table.html#flink-sql-create-table-with-scan-startup-mode) for a table:

        SELECT id, name
        FROM table /*+ OPTIONS('scan.startup.mode'='earliest-offset') */;

* Set options for multiple tables in a [join](../queries/joins.html#flink-sql-joins):

        SELECT *
        FROM table1 /*+ OPTIONS('scan.startup.mode'='earliest-offset') */ t1
        JOIN table2 /*+ OPTIONS('scan.startup.mode'='earliest-offset') */ t2
        ON t1.id = t2.id;

* Set the scan startup mode to use the latest offset:

        SELECT *
        FROM orders /*+ OPTIONS('scan.startup.mode'='latest-offset') */;

* Set the scan startup mode to use the specific offsets, for example, using the latest_offsets attribute from a previous statement:

        INSERT INTO customers_sink (customer_id, name, address, postcode, city, email)
            SELECT customer_id, name, address, postcode, city, email
            FROM customers_source
            /*+ OPTIONS(
                'scan.startup.mode' = 'specific-offsets',
                'scan.startup.specific-offsets'  = 'partition:0,offset:10;partition:1,offset:123'
            ) */;

        // Note: for a statement with multiple topics, use OPTIONS for each table
        SELECT *
        FROM table1 /*+ OPTIONS('scan.startup.mode'='specific-offsets', 'scan.startup.specific-offsets' = '...') */ t1
        JOIN table2 /*+ OPTIONS('scan.startup.mode'='specific-offsets', 'scan.startup.specific-offsets' = '...') */ t2
        ON t1.id = t2.id;

## State TTL Hints¶

For stateful computations such as Regular Joins and Group Aggregations, Confluent Cloud for Apache Flink supports the STATE_TTL hint. This hint allows you to specify operator-level Idle State Retention Time, enabling these operators to have a different TTL from the pipeline-level configuration set by sql.state-ttl.

### Syntax¶

The syntax for using State TTL hints is as follows:

    table_path /*+ STATE_TTL('table_name_or_alias'='ttl_value') */

    ttl_value:
        stringLiteral (e.g., '6h', '2d', '10800s')

### Examples¶

Here are some examples of using State TTL hints in Confluent Cloud for Apache Flink for social media analytics:

* Set State TTL for a Regular Join of posts and users:

        SELECT /*+ STATE_TTL('posts'='6h', 'users'='2d') */ *
        FROM posts
        JOIN users ON posts.user_id = users.id;

* Use table aliases with State TTL hints for analyzing engagement:

        SELECT /*+ STATE_TTL('p'='4h', 'e'='12h') */ *
        FROM posts p
        JOIN engagement e ON p.post_id = e.post_id;

* Apply State TTL hints in a Group Aggregation for trending hashtags:

        SELECT /*+ STATE_TTL('hashtags' = '1h') */
               hashtag, COUNT(*) AS usage_count
        FROM hashtags
        GROUP BY hashtag;

### Important Considerations¶

When using State TTL hints, keep the following in mind:

* You can use either the table name or table alias as the hint key.
* If you specify an alias for a table, you must use that alias in the STATE_TTL hint.
* For queries with multiple joins, the specified TTLs are applied in a bottom-up order.
* The STATE_TTL hint only affects the query block where it’s applied.
* If a hint key is duplicated, the last occurrence takes precedence.
* When multiple STATE_TTL hints are used with the same hint key, the first occurrence is applied.
