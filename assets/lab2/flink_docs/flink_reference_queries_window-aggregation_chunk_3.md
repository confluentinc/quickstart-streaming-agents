---
document_id: flink_reference_queries_window-aggregation_chunk_3
source_file: flink_reference_queries_window-aggregation.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/window-aggregation.html
title: SQL Window Aggregation Queries in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 3
---

2023-11-02 12:50:00 2023-11-02 13:00:00 2636795.56

## GROUPING SETS¶

Window aggregations also support `GROUPING SETS` syntax. Grouping sets allow for more complex grouping operations than those describable by a standard `GROUP BY`. Rows are grouped separately by each specified grouping set and aggregates are computed for each group just as for simple `GROUP BY` clauses.

Window aggregations with `GROUPING SETS` require both the `window_start` and `window_end` columns have to be in the `GROUP BY` clause, but not in the `GROUPING SETS` clause.

    SELECT window_start, window_end, player_id, SUM(points) as `sum`
      FROM TABLE(
        TUMBLE(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '10' MINUTES))
      GROUP BY window_start, window_end, GROUPING SETS ((player_id), ());

    window_start     window_end       player_id sum
    2023-11-03 11:20 2023-11-03 11:30 (NULL)    6596
    2023-11-03 11:20 2023-11-03 11:30 1025      6232
    2023-11-03 11:20 2023-11-03 11:30 1007      4486
    2023-11-03 11:30 2023-11-03 11:40 (NULL)    6073
    2023-11-03 11:30 2023-11-03 11:40 1025      6953
    2023-11-03 11:30 2023-11-03 11:40 1007      3723

Each sublist of `GROUPING SETS` may specify zero or more columns or expressions and is interpreted the same way as though used directly in the `GROUP BY` clause. An empty grouping set means that all rows are aggregated down to a single group, which is output even if no input rows were present.

References to the grouping columns or expressions are replaced by null values in result rows for grouping sets in which those columns do not appear.

### ROLLUP¶

`ROLLUP` is a shorthand notation for specifying a common type of grouping set. It represents the given list of expressions and all prefixes of the list, including the empty list.

Window aggregations with `ROLLUP` requires both the `window_start` and `window_end` columns have to be in the `GROUP BY` clause, but not in the `ROLLUP` clause.

For example, the following query is equivalent to the one above.

    SELECT window_start, window_end, player_id, SUM(points) as `sum`
        FROM TABLE(
          TUMBLE(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '10' MINUTES))
        GROUP BY window_start, window_end, ROLLUP (player_id);

### CUBE¶

`CUBE` is a shorthand notation for specifying a common type of grouping set. It represents the given list and all of its possible subsets - the power set.

Window aggregations with `CUBE` requires both the `window_start` and `window_end` columns have to be in the `GROUP BY` clause, but not in the `CUBE` clause.

For example, the following two queries are equivalent.

    SELECT window_start, window_end, game_room_id, player_id, SUM(points) as `sum`
       FROM TABLE(
         TUMBLE(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '10' MINUTES))
       GROUP BY window_start, window_end, CUBE (player_id, game_room_id);

    SELECT window_start, window_end, game_room_id, player_id, SUM(points) as `sum`
       FROM TABLE(
         TUMBLE(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '10' MINUTES))
       GROUP BY window_start, window_end, GROUPING SETS (
                (player_id, game_room_id),
                (player_id              ),
                (           game_room_id),
                (                 )
          );

### Selecting Group Window Start and End Timestamps¶

The start and end timestamps of group windows can be selected with the grouped `window_start` and `window_end` columns.

### Cascading Window Aggregation¶

The `window_start` and `window_end` columns are regular timestamp columns, not time attributes, so they can’t be used as time attributes in subsequent time-based operations. To propagate time attributes, you also need to add `window_time` column into `GROUP BY` clause. The `window_time` is the third column produced by [Windowing TVFs](window-tvf.html#flink-sql-window-tvfs-window-functions), which is a time attribute of the assigned window.

Adding `window_time` into a `GROUP BY` clause makes `window_time` also to be a group key that can be selected. Following queries can use this column for subsequent time-based operations, like cascading window aggregations and [Window TopN](window-topn.html#flink-sql-window-top-n).

The following code shows a cascading window aggregation in which the first window aggregation propagates the time attribute for the second window aggregation.

    -- tumbling 5 minutes for each player_id
    WITH fiveminutewindow AS (
    -- Note: The window start and window end fields of inner Window TVF
    -- are optional in the SELECT clause. But if they appear in the clause,
    -- they must be aliased to prevent name conflicts with the window start
    -- and window end of the outer Window TVF.
    SELECT window_start AS window_5mintumble_start, window_end as window_5mintumble_end, window_time AS rowtime, SUM(points) as `partial_sum`
      FROM TABLE(
        TUMBLE(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '5' MINUTES))
      GROUP BY player_id, window_start, window_end, window_time
    )
    -- tumbling 10 minutes on the first window
    SELECT window_start, window_end, SUM(partial_price) as total_price
      FROM TABLE(
          TUMBLE(TABLE fiveminutewindow, DESCRIPTOR($rowtime), INTERVAL '10' MINUTES))
      GROUP BY window_start, window_end;
