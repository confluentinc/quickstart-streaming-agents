---
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/window-deduplication.html
title: SQL Window Deduplication Queries in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'queries', 'window-deduplication.html']
scraped_date: 2025-09-05T13:49:21.330849
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

## Example¶

The following example shows how to keep the last record for every 10-minute tumbling window.

The mock data is produced by the [Datagen Source Connector](../../../connectors/cc-datagen-source.html#cc-datagen-source) configured with the [Gaming Player Activity](https://github.com/confluentinc/kafka-connect-datagen/blob/master/src/main/resources/gaming_player_activity.avro) quickstart.

    DESCRIBE gaming_player_activity_source;

    +--------------+-----------+----------+---------------+
    | Column Name  | Data Type | Nullable |    Extras     |
    +--------------+-----------+----------+---------------+
    | key          | BYTES     | NULL     | PARTITION KEY |
    | player_id    | INT       | NOT NULL |               |
    | game_room_id | INT       | NOT NULL |               |
    | points       | INT       | NOT NULL |               |
    | coordinates  | STRING    | NOT NULL |               |
    +--------------+-----------+----------+---------------+

    SELECT * FROM gaming_player_activity_source;

    player_id game_room_id points coordinates
    1051      1144         371    [65,36]
    1079      3451         38     [20,71]
    1017      4177         419    [63,05]
    1092      1801         209    [31,67]
    1074      3013         401    [32,69]
    1003      1038         284    [18,32]
    1081      2265         196    [78,68]

    SELECT *
      FROM (
        SELECT $rowtime, points, game_room_id, player_id, window_start, window_end,
          ROW_NUMBER() OVER (PARTITION BY window_start, window_end ORDER BY $rowtime DESC) AS rownum
        FROM TABLE(
                   TUMBLE(TABLE gaming_player_activity_source, DESCRIPTOR($rowtime), INTERVAL '10' MINUTES))
      ) WHERE rownum <= 1;

    $rowtime                points game_room_id player_id window_start     window_end       rownum
    2023-11-03 19:59:59.407 371    2504         1094      2023-11-03 19:50 2023-11-03 20:00 1
    2023-11-03 20:09:59.921 188    4342         1036      2023-11-03 20:00 2023-11-03 20:10 1
    2023-11-03 20:19:59.741 128    3427         1046      2023-11-03 20:10 2023-11-03 20:20 1
    2023-11-03 20:29:59.992 311    1000         1049      2023-11-03 20:20 2023-11-03 20:30 1
    2023-11-03 20:39:59.569 429    1217         1062      2023-11-03 20:30 2023-11-03 20:40 1

## Related content¶

  * [Top-N Queries](topn.html#flink-sql-top-n)
  * [Window Top-N Queries](window-topn.html#flink-sql-window-top-n)
  * [Windowing Table-Valued Functions (Windowing TVFs)](window-tvf.html#flink-sql-window-tvfs)

Note

This website includes content developed at the [Apache Software Foundation](https://www.apache.org/) under the terms of the [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0.html).
