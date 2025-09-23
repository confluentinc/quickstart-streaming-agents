---
document_id: flink_reference_sql-examples_chunk_7
source_file: flink_reference_sql-examples.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/sql-examples.html
title: Flink SQL Examples in Confluent Cloud for Apache Flink
chunk_index: 7
total_chunks: 12
---

customer_changes SET ('changelog.mode' = 'append');

## ALTER TABLE examples¶

The following examples show frequently used scenarios for ALTER TABLE.

### Define a watermark for perfectly ordered data¶

Flink guarantees that rows are always emitted before the watermark is generated. The following statements ensure that for perfectly ordered events, meaning events without time-skew, a watermark can be equal to the timestamp or 1 ms less than the timestamp.

    CREATE TABLE t_perfect_watermark (i INT);

    -- If multiple events can have the same timestamp.
    ALTER TABLE t_perfect_watermark
      MODIFY WATERMARK FOR $rowtime AS $rowtime - INTERVAL '0.001' SECOND;

    -- If a single event can have the timestamp.
    ALTER TABLE t_perfect_watermark
      MODIFY WATERMARK FOR $rowtime AS $rowtime;

### Drop your custom watermark strategy¶

Remove the custom watermark strategy to restore the [default watermark strategy](statements/create-table.html#flink-sql-watermark-clause).

  1. View the current table schema and metadata.

         DESCRIBE `orders`;

Your output should resemble:

         +-------------+------------------------+----------+-------------------+
         | Column Name |       Data Type        | Nullable |      Extras       |
         +-------------+------------------------+----------+-------------------+
         | user        | BIGINT                 | NOT NULL | PRIMARY KEY       |
         | product     | STRING                 | NULL     |                   |
         | amount      | INT                    | NULL     |                   |
         | ts          | TIMESTAMP(3) *ROWTIME* | NULL     | WATERMARK AS `ts` |
         +-------------+------------------------+----------+-------------------+

  2. Remove the watermark strategy of the table.

         ALTER TABLE `orders` DROP WATERMARK;

Your output should resemble:

         Statement phase is COMPLETED.

  3. Check the new table schema and metadata.

         DESCRIBE `orders`;

Your output should resemble:

         +-------------+--------------+----------+-------------+
         | Column Name |  Data Type   | Nullable |   Extras    |
         +-------------+--------------+----------+-------------+
         | user        | BIGINT       | NOT NULL | PRIMARY KEY |
         | product     | STRING       | NULL     |             |
         | amount      | INT          | NULL     |             |
         | ts          | TIMESTAMP(3) | NULL     |             |
         +-------------+--------------+----------+-------------+

### Configure Debezium format for CDC data¶

#### Change regular format to Debezium format¶

Note

For schemas created after May 19, 2025 at 09:00 UTC, Flink automatically detects Debezium envelopes and configures the appropriate format and changelog mode. Manual conversion is necessary only for older schemas or when you want to override the default behavior.

For tables that have been inferred with regular formats but contain Debezium CDC (Change Data Capture) data:

AvroJSON SchemaProtobuf

    -- Convert from regular Avro format to Debezium CDC format
    -- and configure the appropriate Flink changelog interpretation mode:
    -- * append:  Treats each record as an INSERT operation with no relationship between records
    -- * retract: Handles paired operations (INSERT/UPDATE/DELETE) where changes to the same row
    --            are represented as a retraction of the old value followed by an addition of the new value
    -- * upsert: Groups all operations for the primary key (derived from the Kafka message key),
    --           with each operation effectively merging with or replacing previous state
    --           (INSERT creates, UPDATE modifies, DELETE removes)
    ALTER TABLE customer_data SET (
      'value.format' = 'avro-debezium-registry',
      'changelog.mode' = 'retract'
    );

    -- Convert from regular JSON format to Debezium CDC format
    -- and configure the appropriate Flink changelog interpretation mode:
    -- * append:  Treats each record as an INSERT operation with no relationship between records
    -- * retract: Handles paired operations (INSERT/UPDATE/DELETE) where changes to the same row
    --            are represented as a retraction of the old value followed by an addition of the new value
    -- * upsert: Groups all operations for the primary key (derived from the Kafka message key),
    --           with each operation effectively merging with or replacing previous state
    --           (INSERT creates, UPDATE modifies, DELETE removes)
    ALTER TABLE customer_data_json SET (
      'value.format' = 'json-debezium-registry',
      'changelog.mode' = 'retract'
    );

    -- Convert from regular Protobuf format to Debezium CDC format
    -- and configure the appropriate Flink changelog interpretation mode:
    -- * append:  Treats each record as an INSERT operation
