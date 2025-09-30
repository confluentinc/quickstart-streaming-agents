---
document_id: flink_how-to-guides_convert-serialization-format_chunk_4
source_file: flink_how-to-guides_convert-serialization-format.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/convert-serialization-format.html
title: Convert the Serialization Format of a Topic with Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 5
---

1048 3337 339 [91,10] ...

## Step 3: Convert the serialization format to JSON¶

  1. Run the following statement to confirm that the current format of this table is Avro Schema Registry.

         SHOW CREATE TABLE gaming_player_activity_source;

Your output should resemble:

         +-------------------------------------------------------------+
         |                      SHOW CREATE TABLE                      |
         +-------------------------------------------------------------+
         | CREATE TABLE `env`.`clus`.`gaming_player_activity_source` ( |
         |   `key` VARBINARY(2147483647),                              |
         |   `player_id` INT NOT NULL,                                 |
         |   `game_room_id` INT NOT NULL,                              |
         |   `points` INT NOT NULL,                                    |
         |   `coordinates` VARCHAR(2147483647) NOT NULL,               |
         | ) DISTRIBUTED BY HASH(`key`) INTO 6 BUCKETS                 |
         | WITH (                                                      |
         |   'changelog.mode' = 'append',                              |
         |   'connector' = 'confluent',                                |
         |   'kafka.cleanup-policy' = 'delete',                        |
         |   'kafka.max-message-size' = '2097164 bytes',               |
         |   'kafka.partitions' = '6',                                 |
         |   'kafka.retention.size' = '0 bytes',                       |
         |   'kafka.retention.time' = '604800000 ms',                  |
         |   'key.format' = 'raw',                                     |
         |   'scan.bounded.mode' = 'unbounded',                        |
         |   'scan.startup.mode' = 'earliest-offset',                  |
         |   'value.format' = 'avro-registry'                          |
         | )                                                           |
         |                                                             |
         +-------------------------------------------------------------+

  2. Run the following statement to create a second table that has the same schema but is configured with the value format set to JSON with Schema Registry. The key format is unchanged.

         CREATE TABLE gaming_player_activity_source_json (
           `key` VARBINARY(2147483647),
           `player_id` INT NOT NULL,
           `game_room_id` INT NOT NULL,
           `points` INT NOT NULL,
           `coordinates` VARCHAR(2147483647) NOT NULL
         ) DISTRIBUTED BY HASH(`key`) INTO 6 BUCKETS
         WITH (
           'value.format' = 'json-registry',
           'key.format' = 'raw'
         );

This statement creates a corresponding Kafka topic and Schema Registry subject named `gaming_player_activity_source_json-value` for the value.

  3. Run the following SQL to create a long-running statement that continuously transforms `gaming_player_activity_source` records into `gaming_player_activity_source_json` records.

         INSERT INTO gaming_player_activity_source_json
         SELECT
           *
         FROM gaming_player_activity_source;

  4. Run the following statement to confirm that records are continuously appended to the target table:

         SELECT * FROM gaming_player_activity_source_json;

Your output should resemble:

         key         player_id game_room_id points coordinates
         x'31303834' 1084      3583         211    [51,93]
         x'31303037' 1007      2268         55     [98,72]
         x'31303230' 1020      1625         431    [01,08]
         x'31303934' 1094      4760         43     [80,71]
         x'31303539' 1059      2822         390    [33,74]
         ...

Tip

Run the `SHOW JOBS;` statement to see the phase of statements that you’ve started in your workspace or Flink SQL shell.

  5. Run the following statement to confirm that the format of the `gaming_player_activity_source_json` table is JSON.

         SHOW CREATE TABLE gaming_player_activity_source_json;

Your output should resemble:

         +--------------------------------------------------------------------------------------+
         |                                  SHOW CREATE TABLE                                   |
         +--------------------------------------------------------------------------------------+
         | CREATE TABLE `jim-flink-test-env`.`cluster_0`.`gaming_player_activity_source_json` ( |
         |   `key` VARBINARY(2147483647),                                                       |
         |   `player_id` INT NOT NULL,                                                          |
         |   `game_room_id` INT NOT NULL,                                                       |
         |   `points` INT NOT NULL,                                                             |
         |   `coordinates`
