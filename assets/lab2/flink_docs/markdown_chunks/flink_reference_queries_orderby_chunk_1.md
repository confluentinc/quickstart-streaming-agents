---
document_id: flink_reference_queries_orderby_chunk_1
source_file: flink_reference_queries_orderby.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/orderby.html
title: SQL ORDER BY Clause in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# ORDER BY Clause in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables sorting rows from a SELECT statement.

## Description¶

The `ORDER BY` clause causes the result rows to be sorted according to the specified expression(s). If two rows are equal according to the leftmost expression, they are compared according to the next expression, and so on. If they are equal according to all specified expressions, they are returned in an implementation-dependent order.

When running in streaming mode, the primary sort order of a table must be ascending on a [time attribute](../../concepts/timely-stream-processing.html#flink-sql-time-attributes). All subsequent sort orders can be freely chosen.

When running in batch mode, there is no sort-order limitation.

## Example¶

    SELECT *
    FROM orders
    ORDER BY order_time, order_id
