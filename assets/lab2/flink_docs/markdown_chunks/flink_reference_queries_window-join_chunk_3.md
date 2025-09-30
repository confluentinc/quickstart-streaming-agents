---
document_id: flink_reference_queries_window-join_chunk_3
source_file: flink_reference_queries_window-join.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/window-join.html
title: SQL Window Join Queries in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 3
---

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
