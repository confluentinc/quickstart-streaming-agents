---
document_id: flink_how-to-guides_convert-serialization-format_chunk_3
source_file: flink_how-to-guides_convert-serialization-format.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/convert-serialization-format.html
title: Convert the Serialization Format of a Topic with Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 5
---

in the Confluent Cloud cluster.

## Step 2: Inspect the source data¶

  1. In Cloud Console, navigate to your environment’s [Flink workspace](../get-started/quick-start-cloud-console.html#flink-sql-quick-start-create-workspace), or using the Confluent CLI, open a [SQL shell](../get-started/quick-start-shell.html#flink-sql-quick-start-shell) from the Confluent CLI.

If you use the workspace in Cloud Console, set the **Use catalog** and **Use database** controls to your environment and Kafka cluster.

If you use the Flink SQL shell, run the following statements to set the current environment and Kafka cluster.

         USE CATALOG <your-environment-name>;
         USE DATABASE <your-cluster-name>;

  2. Run the following statement to see the data flowing into the `gaming_player_activity_source` table.

         SELECT * FROM gaming_player_activity_source;

Your output should resemble:

         key         player_id game_room_id points coordinates
         x'31303833' 1083      4634         85     [30,39]
         x'31303731' 1071      3406         432    [91,61]
         x'31303239' 1029      3078         359    [63,04]
         x'31303736' 1076      4501         256    [73,12]
         x'31303437' 1047      3644         375    [24,55]
         ...

  3. If you add `$rowtime` to the `SELECT` statement, you can see the Kafka timestamp for each record.

         SELECT $rowtime, * FROM gaming_player_activity_source;

Your output should resemble:

         $rowtime                key         player_id game_room_id points coordinates
         2023-11-08 14:27:27.647 x'31303838' 1088      4198         22     [02,86]
         2023-11-08 14:27:27.695 x'31303638' 1068      1446         132    [80,86]
         2023-11-08 14:27:27.729 x'31303536' 1056      4839         125    [35,74]
         2023-11-08 14:27:27.732 x'31303530' 1050      4517         221    [11,69]
         2023-11-08 14:27:27.746 x'31303438' 1048      3337         339    [91,10]
         ...
