---
document_id: flink_reference_queries_window-aggregation_chunk_1
source_file: flink_reference_queries_window-aggregation.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/window-aggregation.html
title: SQL Window Aggregation Queries in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 3
---

# Window Aggregation Queries in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables aggregating data over windows in a table.

## Syntax¶

    SELECT ...
    FROM <windowed_table> -- relation applied windowing TVF
    GROUP BY window_start, window_end, ...

## Description¶

### Window TVF Aggregation¶

Window aggregations are defined in the `GROUP BY` clause containing “window_start” and “window_end” columns of the relation applied [Windowing TVF](window-tvf.html#flink-sql-window-tvfs).

Just like queries with regular `GROUP BY` clauses, queries with a group by window aggregation compute a single result row per group.

Unlike other aggregations on continuous tables, window aggregations do not emit intermediate results but only a final result: the total aggregation at the end of the window. Moreover, window aggregations purge all intermediate state when they’re no longer needed.

### Windowing TVFs¶

Flink supports `TUMBLE`, `HOP`, `CUMULATE` and `SESSION` types of window aggregations. The time attribute field of a window table-valued function must be [event time attributes](../../concepts/timely-stream-processing.html#flink-sql-time-attributes). For more information, see [Windowing TVF](window-tvf.html#flink-sql-window-tvfs).

In batch mode, the time attribute field of a window table-valued function must be an attribute of type `TIMESTAMP` or `TIMESTAMP_LTZ`.

`SESSION` window aggregation is not supported in batch mode.
