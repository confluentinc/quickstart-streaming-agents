---
document_id: flink_reference_queries_with_chunk_1
source_file: flink_reference_queries_with.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/with.html
title: SQL WITH Clause in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# WITH Clause in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables writing auxiliary statements to use in larger SQL queries.

## Syntax¶

    WITH <with_item_definition> [ , ... ]
    SELECT ... FROM ...;

    <with_item_defintion>:
       with_item_name (column_name[, ...n]) AS ( <select_query> )

## Description¶

The `WITH` clause provides a way to write auxiliary statements for use in a larger query. These statements, which are often referred to as Common Table Expressions (CTE), can be thought of as defining temporary views that exist just for one query.

## Example¶

The following example defines a common table expression `orders_with_total` and uses it in a `GROUP BY` query.

    WITH orders_with_total AS (
        SELECT order_id, price + tax AS total
        FROM orders
    )
    SELECT order_id, SUM(total)
    FROM orders_with_total
    GROUP BY order_id;
