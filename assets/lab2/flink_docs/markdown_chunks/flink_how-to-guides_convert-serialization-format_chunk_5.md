---
document_id: flink_how-to-guides_convert-serialization-format_chunk_5
source_file: flink_how-to-guides_convert-serialization-format.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/convert-serialization-format.html
title: Convert the Serialization Format of a Topic with Confluent Cloud for Apache Flink
chunk_index: 5
total_chunks: 5
---

VARCHAR(2147483647) NOT NULL                                         |
         | ) DISTRIBUTED BY HASH(`key`) INTO 6 BUCKETS                                          |
         | WITH (                                                                               |
         |   'changelog.mode' = 'append',                                                       |
         |   'connector' = 'confluent',                                                         |
         |   'kafka.cleanup-policy' = 'delete',                                                 |
         |   'kafka.max-message-size' = '2097164 bytes',                                        |
         |   'kafka.partitions' = '6',                                                          |
         |   'kafka.retention.size' = '0 bytes',                                                |
         |   'kafka.retention.time' = '604800000 ms',                                           |
         |   'key.format' = 'raw',                                                              |
         |   'scan.bounded.mode' = 'unbounded',                                                 |
         |   'scan.startup.mode' = 'earliest-offset',                                           |
         |   'value.format' = 'json-registry'                                                   |
         | )                                                                                    |
         |                                                                                      |
         +--------------------------------------------------------------------------------------+

## Step 4: Delete the long-running statement¶

Your INSERT INTO statement is converting records in the Avro format to the JSON format continuously. When you’re done with this guide, free resources in your compute pool by deleting the long-running statement.

  1. In Cloud Console, navigate to the **Flink** page in your environment and click **Flink statements**.
  2. In the statements list, find the statement that has a status of **Running**.
  3. In the **Actions** column, click **…** and select **Delete statement**.
  4. In the **Confirm statement deletion** dialog, copy and paste the statement name and click **Confirm**.
