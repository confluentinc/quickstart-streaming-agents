---
document_id: flink_reference_queries_window-deduplication_chunk_2
source_file: flink_reference_queries_window-deduplication.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/window-deduplication.html
title: SQL Window Deduplication Queries in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 2
---

order is by event time.

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
