---
document_id: flink_reference_queries_group-aggregation_chunk_3
source_file: flink_reference_queries_group-aggregation.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/group-aggregation.html
title: SQL Group Aggregation Queries in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 3
---

AS Products(supplier_id, product_id, rating)
    GROUP BY GROUPING SET (
        ( supplier_id, product_id, rating ),
        ( supplier_id, product_id         ),
        ( supplier_id,             rating ),
        ( supplier_id                     ),
        (              product_id, rating ),
        (              product_id         ),
        (                          rating ),
        (                                 )
    )

### HAVING¶

The `HAVING` clause eliminates group rows that don’t satisfy the specified condition.

`HAVING` is distinct from the `WHERE` clause, because `WHERE` filters individual rows _before_ the `GROUP BY`, while `HAVING` filters group rows _created by_ `GROUP BY`. Each column referenced in the condition must unambiguously reference a grouping column, unless it appears within an aggregate function.

    SELECT SUM(amount)
    FROM orders
    GROUP BY users
    HAVING SUM(amount) > 50

The presence of a `HAVING` clause turns a query into a grouped query, even if there is no `GROUP BY` clause. It’s the same as what happens when the query contains aggregate functions but no `GROUP BY` clause. The query considers all selected rows to form a single group, and the `SELECT` list and `HAVING` clause can reference only table columns from within aggregate functions. Such a query emits a single row if the `HAVING` condition is true, and zero rows if it’s not true.
