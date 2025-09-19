---
document_id: flink_reference_queries_window-join_chunk_1
source_file: flink_reference_queries_window-join.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/window-join.html
title: SQL Window Join Queries in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 3
---

# Window Join Queries in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables joining data over time windows in dynamic tables.

## Syntax¶

The following shows the syntax of the INNER/LEFT/RIGHT/FULL OUTER Window Join statement.

    SELECT ...
    FROM L [LEFT|RIGHT|FULL OUTER] JOIN R -- L and R are relations applied windowing TVF
    ON L.window_start = R.window_start AND L.window_end = R.window_end AND ...

## Description¶

A window join adds the dimension of time into the join criteria themselves. In doing so, the window join joins the elements of two streams that share a common key and are in the same window.

For streaming queries, unlike other joins on continuous tables, window join does not emit intermediate results but only emits final results at the end of the window. Moreover, window join purge all intermediate state when no longer needed.

Usually, Window Join is used with [Windowing TVF](window-tvf.html#flink-sql-window-tvfs). Also, Window Join can follow after other operations based on Windowing TVF, like [Window Aggregation](window-aggregation.html#flink-sql-window-aggregation) and [Window TopN](window-topn.html#flink-sql-window-top-n).

Window Join requires that the join on condition contains `window_starts` equality of input tables and `window_ends` equality of input tables.

Window Join supports INNER/LEFT/RIGHT/FULL OUTER/ANTI/SEMI JOIN. The syntax is very similar for all of the different joins.
