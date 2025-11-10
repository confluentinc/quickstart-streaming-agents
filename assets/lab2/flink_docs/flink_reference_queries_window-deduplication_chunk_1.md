---
document_id: flink_reference_queries_window-deduplication_chunk_1
source_file: flink_reference_queries_window-deduplication.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/window-deduplication.html
title: SQL Window Deduplication Queries in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 2
---

# Window Deduplication Queries in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables removing duplicate rows over a set of columns in a windowed table.

## Syntax¶

    SELECT [column_list]
    FROM (
       SELECT [column_list],
         ROW_NUMBER() OVER (PARTITION BY window_start, window_end [, column_key1...]
           ORDER BY time_attr [asc|desc]) AS rownum
       FROM table_name) -- relation applied windowing TVF
    WHERE (rownum = 1 | rownum <=1 | rownum < 2) [AND conditions]

**Parameter Specification**

Note

This query pattern must be followed exactly, otherwise, the optimizer won’t translate the query to Window Deduplication.

  * `ROW_NUMBER()`: Assigns an unique, sequential number to each row, starting with one.
  * `PARTITION BY window_start, window_end [, column_key1...]`: Specifies the partition columns which contain `window_start`, `window_end` and other partition keys.
  * `ORDER BY time_attr [asc|desc]`: Specifies the ordering column, which must be a [time attribute](../../concepts/timely-stream-processing.html#flink-sql-time-attributes). Flink SQL supports the [event time attribute](../../concepts/timely-stream-processing.html#flink-sql-time-attributes-event-time). Processing time is not supported in Confluent Cloud for Apache Flink. Ordering by ASC means keeping the first row, ordering by DESC means keeping the last row.
  * `WHERE (rownum = 1 | rownum <=1 | rownum < 2)`: The `rownum = 1 | rownum <=1 | rownum < 2` is required for the optimizer to recognize the query should be translated to Window Deduplication.

## Description¶

Window Deduplication is a special [deduplication](deduplication.html#flink-sql-deduplication) that removes duplicate rows over a set of columns, keeping the first row or the last row for each window and partitioned keys.

For streaming queries, unlike regular deduplicate on continuous tables, Window Deduplication doesn’t emit intermediate results, instead emitting only a final result at the end of the window. Also, window Deduplication purges all intermediate state when it’s no longer needed. As a result, Window Deduplication queries have better performance, if you don’t need results updated per row.

Usually, Window Deduplication is used with [Windowing TVF](window-tvf.html#flink-sql-window-tvfs) directly. Window Deduplication can be used with other operations based on Windowing TVF, like [Window Aggregation](window-aggregation.html#flink-sql-window-aggregation), [Window TopN](window-topn.html#flink-sql-window-top-n), and [Window Join](window-join.html#flink-sql-window-join).

Window Deduplication can be defined in the same syntax as regular Deduplication. For more information, see [Deduplication Queries in Confluent Cloud for Apache Flink](deduplication.html#flink-sql-deduplication). Window Deduplication requires that the `PARTITION BY` clause contains `window_start` and `window_end` columns of the relation, otherwise, the optimizer can’t translate the query.

Flink uses `ROW_NUMBER()` to remove duplicates, similar to its usage in [Top-N Queries in Confluent Cloud for Apache Flink](topn.html#flink-sql-top-n). Deduplication is a special case of the Top-N query, in which `N` is one and order is by event time.
