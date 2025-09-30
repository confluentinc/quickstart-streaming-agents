---
document_id: flink_reference_sql-examples_chunk_8
source_file: flink_reference_sql-examples.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/sql-examples.html
title: Flink SQL Examples in Confluent Cloud for Apache Flink
chunk_index: 8
total_chunks: 12
---

with no relationship between records
    -- *retract: Handles paired operations (INSERT/UPDATE/DELETE) where changes to the same row
    --            are represented as a retraction of the old value followed by an addition of the new value
    --* upsert: Groups all operations for the primary key (derived from the Kafka message key),
    --           with each operation effectively merging with or replacing previous state
    --           (INSERT creates, UPDATE modifies, DELETE removes)
    ALTER TABLE customer_data_proto SET (
      'value.format' = 'proto-debezium-registry',
      'changelog.mode' = 'retract'
    );

### Modify Changelog Processing Mode¶

For tables with any type of data that need a different processing mode for handling changes:

    -- Change to append mode (default)
    -- Best for event streams where each record is independent
    ALTER TABLE customer_changes SET (
      'changelog.mode' = 'append'
    );

    -- Change to retract mode
    -- Useful when changes to the same row are represented as paired operations
    ALTER TABLE customer_changes SET (
      'changelog.mode' = 'retract'
    );

    -- Change upsert mode when working with primary keys
    -- Best when tracking state changes using a primary key (derived from Kafka message key)
    ALTER TABLE customer_changes SET (
      'changelog.mode' = 'upsert'
    );

### Read and/or write Kafka headers¶

    -- Create example topic
    CREATE TABLE t_headers (i INT);

    -- For read-only (virtual)
    ALTER TABLE t_headers ADD headers MAP<BYTES, BYTES> METADATA VIRTUAL;

    -- For read and write (persisted). Column becomes mandatory in INSERT INTO.
    ALTER TABLE t_headers MODIFY headers MAP<BYTES, BYTES> METADATA;

    -- Use implicit casting (origin is always MAP<BYTES, BYTES>)
    ALTER TABLE t_headers MODIFY headers MAP<STRING, STRING> METADATA;

    -- Insert and read
    INSERT INTO t_headers SELECT 42, MAP['k1', 'v1', 'k2', 'v2'];
    SELECT * FROM t_headers;

Properties

* The metadata key is `headers`. If you don’t want to name the column this way, use: `other_name MAP<BYTES, BYTES> METADATA FROM 'headers' VIRTUAL`.
* Keys of headers must be unique. Multi-key headers are not supported.

### Add headers as a metadata column¶

You can get the headers of a Kafka record as a map of raw bytes by adding a `headers` virtual metadata column.

  1. Run the following statement to add the Kafka partition as a metadata column:

         ALTER TABLE `orders` ADD (
           `headers` MAP<BYTES,BYTES> METADATA VIRTUAL);

  2. View the new schema.

         DESCRIBE `orders`;

Your output should resemble:

         +-------------+-------------------+----------+-------------------------+
         | Column Name |     Data Type     | Nullable |         Extras          |
         +-------------+-------------------+----------+-------------------------+
         | user        | BIGINT            | NOT NULL | PRIMARY KEY, BUCKET KEY |
         | product     | STRING            | NULL     |                         |
         | amount      | INT               | NULL     |                         |
         | ts          | TIMESTAMP(3)      | NULL     |                         |
         | headers     | MAP<BYTES, BYTES> | NULL     | METADATA VIRTUAL        |
         +-------------+-------------------+----------+-------------------------+

### Read topic from specific offsets¶

    -- Create example topic with 1 partition filled with values
    CREATE TABLE t_specific_offsets (i INT) DISTRIBUTED INTO 1 BUCKETS;
    INSERT INTO t_specific_offsets VALUES (1), (2), (3), (4), (5);

    -- Returns 1, 2, 3, 4, 5
    SELECT * FROM t_specific_offsets;

    -- Changes the scan range
    ALTER TABLE t_specific_offsets SET (
      'scan.startup.mode' = 'specific-offsets',
      'scan.startup.specific-offsets' = 'partition:0,offset:3'
    );

    -- Returns 4, 5
    SELECT * FROM t_specific_offsets;

Properties

* `scan.startup.mode` and `scan.bounded.mode` control which range in the changelog (Kafka topic) to read.
* `scan.startup.specific-offsets` and `scan.bounded.specific-offsets` define offsets per partition.
* In the example, only 1 partition is used. For multiple partitions, use the following syntax:

    'scan.startup.specific-offsets' = 'partition:0,offset:3; partition:1,offset:42; partition:2,offset:0'

### Debug “no output” and no watermark cases¶

The root cause for most “no output” cases is that a time-based operation, for example, TUMBLE, MATCH_RECOGNIZE, and FOR SYSTEM_TIME AS OF, did not receive recent enough watermarks.

The current time of an operator is calculated by the minimum watermark of all inputs, meaning across all tables/topics and their partitions.

If one partition does not emit a watermark, it can affect the entire pipeline.
