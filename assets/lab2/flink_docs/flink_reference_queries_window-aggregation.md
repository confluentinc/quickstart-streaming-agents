---
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/window-aggregation.html
title: SQL Window Aggregation Queries in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'queries', 'window-aggregation.html']
scraped_date: 2025-09-05T13:49:19.185132
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

## Examples¶

The following examples show Window aggregations over [example data streams](../example-data.html#flink-sql-example-data) that you can experiment with.

Note

To show the behavior of windowing more clearly in the following examples, `TIMESTAMP(3)` values may be simplified so that trailing zeroes aren’t shown. For example, `2020-04-15 08:05:00.000` may be shown as `2020-04-15 08:05`. Columns may be hidden intentionally to enhance the readability of the content.

Here are some examples for `TUMBLE`, `HOP`, `CUMULATE` and `SESSION` window aggregations.

    DESCRIBE `examples`.`marketplace`.`orders`;

    +--------------+-----------+----------+---------------+
    | Column Name  | Data Type | Nullable |    Extras     |
    +--------------+-----------+----------+---------------+
    | order_id     | STRING    | NOT NULL |               |
    | customer_id  | INT       | NOT NULL |               |
    | product_id   | STRING    | NOT NULL |               |
    | price        | DOUBLE    | NOT NULL |               |
    +--------------+-----------+----------+---------------+

    SELECT * FROM `examples`.`marketplace`.`orders`;

    order_id                             customer_id  product_id price
    d770a538-a70c-4de6-9d06-e6c16c5bef5a 3075         1379       32.21
    787ee1f4-d0d0-4c39-bdb9-44dc2d203d55 3028         1335       34.74
    7ab7ce23-5f61-4398-afad-b1e3f548fee3 3148         1045       69.26
    6fea712c-9454-497e-8038-ebaf6dfc7a17 3247         1390       67.26
    dc9daf5e-98d5-4bcd-8839-251fed13b75e 3167         1309       12.04
    ab3151d0-2950-49cd-9783-016ccc6a3281 3105         1094       21.52
    d27ca945-3cff-48a4-afcc-7b17446aa95d 3168         1250       99.95

    -- apply aggregation on the tumbling windowed table
    SELECT window_start, window_end, SUM(price) as `sum`
      FROM TABLE(
        TUMBLE(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '10' MINUTES))
      GROUP BY window_start, window_end;

    window_start        window_end          sum
    2023-11-02 10:40:00 2023-11-02 10:50:00 258484.93
    2023-11-02 10:50:00 2023-11-02 11:00:00 287632.15
    2023-11-02 11:00:00 2023-11-02 11:10:00 271945.78
    2023-11-02 11:10:00 2023-11-02 11:20:00 315207.46
    2023-11-02 11:20:00 2023-11-02 11:30:00 342618.92
    2023-11-02 11:30:00 2023-11-02 11:40:00 329754.31

    -- apply aggregation on the hopping windowed table
    SELECT window_start, window_end, SUM(price) as `sum`
      FROM TABLE(
        HOP(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '5' MINUTES, INTERVAL '10' MINUTES))
      GROUP BY window_start, window_end;

    window_start        window_end          sum
    2023-11-02 11:10:00 2023-11-02 11:20:00 296049.38
    2023-11-02 11:15:00 2023-11-02 11:25:00 1122455.07
    2023-11-02 11:20:00 2023-11-02 11:30:00 1648270.20
    2023-11-02 11:25:00 2023-11-02 11:35:00 2143271.00
    2023-11-02 11:30:00 2023-11-02 11:40:00 2701592.45
    2023-11-02 11:35:00 2023-11-02 11:45:00 3214376.78

    -- apply aggregation on the cumulating windowed table
    SELECT window_start, window_end, SUM(price) as `sum`
      FROM TABLE(
        CUMULATE(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '2' MINUTES, INTERVAL '10' MINUTES))
      GROUP BY window_start, window_end;

    window_start            window_end              sum
    2023-11-02 12:40:00.000 2023-11-02 12:46:00.000 327376.23
    2023-11-02 12:40:00.000 2023-11-02 12:48:00.000 661272.70
    2023-11-02 12:40:00.000 2023-11-02 12:50:00.000 989294.13
    2023-11-02 12:50:00.000 2023-11-02 12:52:00.000 1316596.58
    2023-11-02 12:50:00.000 2023-11-02 12:54:00.000 1648097.20
    2023-11-02 12:50:00.000 2023-11-02 12:56:00.000 1977881.53
    2023-11-02 12:50:00.000 2023-11-02 12:58:00.000 2304080.32
    2023-11-02 12:50:00.000 2023-11-02 13:00:00.000 2636795.56

    -- apply aggregation on the session windowed table
    SELECT window_start, window_end, customer_id, SUM(price) as `sum`
      FROM TABLE(
        SESSION(TABLE `examples`.`marketplace`.`orders` PARTITION BY customer_id, DESCRIPTOR($rowtime), INTERVAL '1' MINUTES))
      GROUP BY window_start, window_end, customer_id;

    window_start        window_end          sum
    2023-11-02 12:40:00 2023-11-02 12:46:00 327376.23
    2023-11-02 12:40:00 2023-11-02 12:48:00 661272.70
    2023-11-02 12:40:00 2023-11-02 12:50:00 989294.13
    2023-11-02 12:50:00 2023-11-02 12:52:00 1316596.58
    2023-11-02 12:50:00 2023-11-02 12:54:00 1648097.20
    2023-11-02 12:50:00 2023-11-02 12:56:00 1977881.53
    2023-11-02 12:50:00 2023-11-02 12:58:00 2304080.32
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
