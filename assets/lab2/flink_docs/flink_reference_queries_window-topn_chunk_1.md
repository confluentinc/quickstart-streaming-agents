---
document_id: flink_reference_queries_window-topn_chunk_1
source_file: flink_reference_queries_window-topn.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/window-topn.html
title: SQL Window Top-N Queries in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 2
---

# Window Top-N Queries in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables Window Top-N queries in dynamic tables.

## Syntax¶

    SELECT [column_list]
    FROM (
       SELECT [column_list],
         ROW_NUMBER() OVER (PARTITION BY window_start, window_end [, col_key1...]
           ORDER BY col1 [asc|desc][, col2 [asc|desc]...]) AS rownum
       FROM table_name) -- relation applied windowing TVF
    WHERE rownum <= N [AND conditions]

## Description¶

Window Top-N is a special [Top-N](topn.html#flink-sql-top-n) that returns the _N_ smallest or largest values for each window and other partitioned keys.

For streaming queries, unlike regular Top-N on continuous tables, Window Top-N doesn’t emit intermediate results, but only a final result, the total Top N records at the end of the window. Moreover, Window Top-N purges all intermediate state when no longer needed, so Window Top-N queries have better performance if you don’t need results updated per record.

Usually, Window Top-N is used with [Windowing TVF](window-tvf.html#flink-sql-window-tvfs) directly, but Window Top-N can be used with other operations based on Windowing TVF, like [Window Aggregation](window-aggregation.html#flink-sql-window-aggregation), and [Window Join](window-join.html#flink-sql-window-join).

You can define Window Top-N with the same syntax as regular Top-N. For more information, see [Top-N](topn.html#flink-sql-top-n).

In addition, Window Top-N requires that the `PARTITION BY` clause contains `window_start` and `window_end` columns of the relation applied by [Windowing TVF](window-tvf.html#flink-sql-window-tvfs) or [Window Aggregation](window-aggregation.html#flink-sql-window-aggregation). Otherwise, the optimizer can’t translate the query.
