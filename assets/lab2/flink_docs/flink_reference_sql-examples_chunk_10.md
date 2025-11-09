---
document_id: flink_reference_sql-examples_chunk_10
source_file: flink_reference_sql-examples.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/sql-examples.html
title: Flink SQL Examples in Confluent Cloud for Apache Flink
chunk_index: 10
total_chunks: 12
---

### Change the schema context property¶

You can set the schema context for key and value formats to control the namespace for your schema resolution in Schema Registry.

  1. Set the schema context for the value format

         ALTER TABLE `orders` SET ('value.format.schema-context' = '.lsrc-newcontext');

Your output should resemble:

         Statement phase is COMPLETED.

  2. Check the new table properties.

         SHOW CREATE TABLE `orders`;

Your output should resemble:

         +----------------------------------------------------------------------+
         |                          SHOW CREATE TABLE                           |
         +----------------------------------------------------------------------+
         | CREATE TABLE `catalog`.`database`.`orders` (                         |
         |   `user` BIGINT NOT NULL,                                            |
         |   `product` VARCHAR(2147483647),                                     |
         |   `amount` INT,                                                      |
         |   `ts` TIMESTAMP(3)                                                  |
         | )                                                                    |
         |   DISTRIBUTED BY HASH(`user`) INTO 6 BUCKETS                         |
         | WITH (                                                               |
         |   'changelog.mode' = 'upsert',                                       |
         |   'connector' = 'confluent',                                         |
         |   'kafka.cleanup-policy' = 'delete',                                 |
         |   'kafka.max-message-size' = '2097164 bytes',                        |
         |   'kafka.retention.size' = '0 bytes',                                |
         |   'kafka.retention.time' = '604800000 ms',                           |
         |   'key.format' = 'avro-registry',                                    |
         |   'scan.bounded.mode' = 'unbounded',                                 |
         |   'scan.startup.mode' = 'latest-offset',                             |
         |   'value.format' = 'avro-registry',                                  |
         |   'value.format.schema-context' = '.lsrc-newcontext'                 |
         | )                                                                    |
         |                                                                      |
         +----------------------------------------------------------------------+
