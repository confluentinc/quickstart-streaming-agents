---
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/window-join.html
title: SQL Window Join Queries in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'queries', 'window-join.html']
scraped_date: 2025-09-05T13:49:27.757617
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

## Examples¶

The following examples show Window joins over mock data produced by the [Datagen Source Connector](../../../connectors/cc-datagen-source.html#cc-datagen-source) configured with the [Gaming Player Activity](https://github.com/confluentinc/kafka-connect-datagen/blob/master/src/main/resources/gaming_player_activity.avro) quickstart.

Note

To show the behavior of windowing more clearly in the following examples, `TIMESTAMP(3)` values may be simplified so that trailing zeroes aren’t shown. For example, `2020-04-15 08:05:00.000` may be shown as `2020-04-15 08:05`. Columns may be hidden intentionally to enhance the readability of the content.

### FULL OUTER JOIN¶

The following example shows a FULL OUTER JOIN, with a Window Join that works on a Tumble Window TVF.

When performing a window join, all elements with a common key and a common tumbling window are joined together. By scoping the region of time for the oin into fixed five-minute intervals, the datasets are chopped into two distinct windows of time: `[12:00, 12:05)` and `[12:05, 12:10)`. The L2 and R2 rows don’t join together because they fall into separate windows.

    describe LeftTable;

    +-------------+--------------+----------+--------+
    | Column Name |  Data Type   | Nullable | Extras |
    +-------------+--------------+----------+--------+
    | row_time    | TIMESTAMP(3) | NULL     |        |
    | num         | INT          | NULL     |        |
    | id          | STRING       | NULL     |        |
    +-------------+--------------+----------+--------+

    SELECT * FROM LeftTable;

    row_time                num id
    2023-11-03 12:22:47.268 1   L1
    2023-11-03 12:22:43.189 2   L2
    2023-11-03 12:22:47.486 3   L3

    describe RightTable;

    +-------------+--------------+----------+--------+
    | Column Name |  Data Type   | Nullable | Extras |
    +-------------+--------------+----------+--------+
    | row_time    | TIMESTAMP(3) | NULL     |        |
    | num         | INT          | NULL     |        |
    | id          | STRING       | NULL     |        |
    +-------------+--------------+----------+--------+

    SELECT * FROM RightTable;

    row_time                num id
    2023-11-03 12:23:22.045 2   R2
    2023-11-03 12:23:16.437 3   R3
    2023-11-03 12:23:18.349 4   R4

    SELECT L.num as L_Num, L.id as L_Id, R.num as R_Num, R.id as R_Id,
      COALESCE(L.window_start, R.window_start) as window_start,
      COALESCE(L.window_end, R.window_end) as window_end
      FROM (
        SELECT * FROM TABLE(TUMBLE(TABLE LeftTable, DESCRIPTOR($rowtime), INTERVAL '5' MINUTES))
      ) L
      FULL JOIN (
        SELECT * FROM TABLE(TUMBLE(TABLE RightTable, DESCRIPTOR($rowtime), INTERVAL '5' MINUTES))
      ) R
      ON L.num = R.num AND L.window_start = R.window_start AND L.window_end = R.window_end;

The output resembles:

    L_Num L_Id R_Num R_Id window_start     window_end
    1     L1   NULL  NULL 2023-11-03 13:20 2023-11-03 13:25
    NULL  NULL 2     R2   2023-11-03 13:20 2023-11-03 13:25
    3     L3   3     R3   2023-11-03 13:20 2023-11-03 13:25
    2     L2   NULL  NULL 2023-11-03 13:25 2023-11-03 13:30
    NULL  NULL 4     R4   2023-11-03 13:25 2023-11-03 13:30

### SEMI¶

Semi Window Joins return a row from one left record if there is at least one matching row on the right side within the common window.

    SELECT *
      FROM (
         SELECT * FROM TABLE(TUMBLE(TABLE LeftTable, DESCRIPTOR($rowtime), INTERVAL '5' MINUTES))
      ) L WHERE L.num IN (
        SELECT num FROM (
          SELECT * FROM TABLE(TUMBLE(TABLE RightTable, DESCRIPTOR($rowtime), INTERVAL '5' MINUTES))
        ) R WHERE L.window_start = R.window_start AND L.window_end = R.window_end);

    row_time                num id window_start     window_end       window_time
    2023-11-03 12:43:57.095 1   L3 2023-11-03 13:40 2023-11-03 13:45 2023-11-03 13:44:59.999
    2023-11-03 12:43:54.914 1   L2 2023-11-03 13:40 2023-11-03 13:45 2023-11-03 13:44:59.999
    2023-11-03 12:43:56.898 1   L1 2023-11-03 13:40 2023-11-03 13:45 2023-11-03 13:44:59.999
    2023-11-03 12:43:59.112 1   L1 2023-11-03 13:40 2023-11-03 13:45 2023-11-03 13:44:59.999
    2023-11-03 12:43:59.626 1   L5 2023-11-03 13:40 2023-11-03 13:45 2023-11-03 13:44:59.999

    SELECT *
      FROM (
         SELECT * FROM TABLE(TUMBLE(TABLE LeftTable, DESCRIPTOR($rowtime), INTERVAL '5' MINUTES))
      ) L WHERE EXISTS (
        SELECT * FROM (
          SELECT * FROM TABLE(TUMBLE(TABLE RightTable, DESCRIPTOR($rowtime), INTERVAL '5' MINUTES))
        ) R WHERE L.num = R.num AND L.window_start = R.window_start AND L.window_end = R.window_end);

    row_time                num id  window_start     window_end       window_time
    2023-11-03 12:45:08.329 2   L4  2023-11-03 13:45 2023-11-03 13:50 2023-11-03 13:49:59.999
    2023-11-03 12:45:06.702 2   L3  2023-11-03 13:45 2023-11-03 13:50 2023-11-03 13:49:59.999
    2023-11-03 12:45:07.024 2   L4  2023-11-03 13:45 2023-11-03 13:50 2023-11-03 13:49:59.999
    2023-11-03 12:45:05.581 2   L3  2023-11-03 13:45 2023-11-03 13:50 2023-11-03 13:49:59.999

### ANTI¶

Anti Window Joins are the obverse of the Inner Window Join: they contain all of the unjoined rows within each common window.

    SELECT *
      FROM (
        SELECT * FROM TABLE(TUMBLE(TABLE LeftTable, DESCRIPTOR($rowtime), INTERVAL '5' MINUTES))
      ) L WHERE L.num NOT IN (
         SELECT num FROM (
           SELECT * FROM TABLE(TUMBLE(TABLE RightTable, DESCRIPTOR($rowtime), INTERVAL '5' MINUTES))
         ) R WHERE L.window_start = R.window_start AND L.window_end = R.window_end);

    row_time                num id window_start     window_end       window_time
    2023-11-03 12:23:42.865 1   L1 2023-11-03 13:20 2023-11-03 13:25 2023-11-03 13:24:59.999
    2023-11-03 12:23:42.956 1   L5 2023-11-03 13:20 2023-11-03 13:25 2023-11-03 13:24:59.999
    2023-11-03 12:23:41.029 2   L1 2023-11-03 13:20 2023-11-03 13:25 2023-11-03 13:24:59.999
    2023-11-03 12:23:36.826 1   L1 2023-11-03 13:20 2023-11-03 13:25 2023-11-03 13:24:59.999
    2023-11-03 12:23:36.435 1   L4 2023-11-03 13:20 2023-11-03 13:25 2023-11-03 13:24:59.999

    SELECT *
      FROM (
        SELECT * FROM TABLE(TUMBLE(TABLE LeftTable, DESCRIPTOR($rowtime), INTERVAL '5' MINUTES))
      ) L WHERE NOT EXISTS (
        SELECT * FROM (
          SELECT * FROM TABLE(TUMBLE(TABLE RightTable, DESCRIPTOR($rowtime), INTERVAL '5' MINUTES))
        ) R WHERE L.num = R.num AND L.window_start = R.window_start AND L.window_end = R.window_end);

    row_time                num id window_start     window_end       window_time
    2023-11-03 12:23:14.693 2   L1 2023-11-03 13:20 2023-11-03 13:25 2023-11-03 13:24:59.999
    2023-11-03 12:23:19.174 2   L1 2023-11-03 13:20 2023-11-03 13:25 2023-11-03 13:24:59.999
    2023-11-03 12:23:11.035 2   L1 2023-11-03 13:20 2023-11-03 13:25 2023-11-03 13:24:59.999
    2023-11-03 12:23:11.764 2   L3 2023-11-03 13:20 2023-11-03 13:25 2023-11-03 13:24:59.999
    2023-11-03 12:23:16.240 2   L5 2023-11-03 13:20 2023-11-03 13:25 2023-11-03 13:24:59.999

## Limitations¶

### Limitation on Join clause¶

Currently, the window join requires that the join-on condition contains window-starts equality of input tables and window-ends equality of input tables. In the future, the join on clause could be simplified to include only the window-start equality if the windowing TVF is TUMBLE or HOP.

### Limitation on Windowing TVFs of inputs¶

Currently, the windowing TVFs must be the same for left and right inputs. This could be extended in the future, for example, tumbling windows join sliding windows with the same window size.

## Related content¶

  * [Top-N Queries](topn.html#flink-sql-top-n)
  * [Window Top-N Queries](window-topn.html#flink-sql-window-top-n)
  * [Windowing Table-Valued Functions (Windowing TVFs)](window-tvf.html#flink-sql-window-tvfs)

Note

This website includes content developed at the [Apache Software Foundation](https://www.apache.org/) under the terms of the [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0.html).
