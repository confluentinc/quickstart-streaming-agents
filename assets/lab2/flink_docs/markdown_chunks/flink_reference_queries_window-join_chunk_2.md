---
document_id: flink_reference_queries_window-join_chunk_2
source_file: flink_reference_queries_window-join.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/window-join.html
title: SQL Window Join Queries in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 3
---

all of the different joins.

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
