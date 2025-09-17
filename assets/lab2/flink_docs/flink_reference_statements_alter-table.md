---
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/alter-table.html
title: SQL ALTER TABLE Statement in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'statements', 'alter-table.html']
scraped_date: 2025-09-05T13:48:38.187029
---

# ALTER TABLE Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables changing properties of an existing table.

## Syntax¶

    ALTER TABLE [catalog_name.][db_name.]table_name {
       ADD (metadata_column_name metadata_column_type METADATA [FROM metadata_key] VIRTUAL [COMMENT column_comment])
     | ADD (computed_column_name AS computed_column_expression [COMMENT column_comment])
     | MODIFY WATERMARK FOR rowtime_column_name AS watermark_strategy_expression
     | DROP WATERMARK
     | SET (key1='value1' [, key2='value2', ...])
     | RESET (key1 [, key2, ...])
    }

## Description¶

ALTER TABLE allows you to add metadata columns, computed columns, change or remove the [watermark](../../../_glossary.html#term-watermark), and modify [table properties](create-table.html#flink-sql-with-options). Physical columns cannot be added, modified, or dropped within Confluent Cloud for Apache Flink directly, but schemas can be [evolved in Schema Registry](../../../sr/fundamentals/schema-evolution.html#schema-evolution-and-compatibility).

## Examples¶

The following examples show frequently encountered scenarios with ALTER TABLE.

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

Remove the custom watermark strategy to restore the [default watermark strategy](create-table.html#flink-sql-watermark-clause).

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
    -- * append:  Treats each record as an INSERT operation with no relationship between records
    -- * retract: Handles paired operations (INSERT/UPDATE/DELETE) where changes to the same row
    --            are represented as a retraction of the old value followed by an addition of the new value
    -- * upsert: Groups all operations for the primary key (derived from the Kafka message key),
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

The following statements may be helpful for debugging issues related to watermarks.

    -- example table
    CREATE TABLE t_watermark_debugging (k INT, s STRING)
      DISTRIBUTED BY (k) INTO 4 BUCKETS;
    
    -- Each value lands in a separate Kafka partition (out of 4).
    -- Leave out values to see missing watermarks.
    INSERT INTO t_watermark_debugging
      VALUES (1, 'Bob'), (2, 'Alice'), (8, 'John'), (15, 'David');
    
    -- If ROW_NUMBER doesn't show results, it's clearly a watermark issue.
    SELECT ROW_NUMBER() OVER (ORDER BY $rowtime ASC) AS `number`, *
      FROM t_watermark_debugging;
    
    -- Add partition information as metadata column
    ALTER TABLE t_watermark_debugging ADD part INT METADATA FROM 'partition' VIRTUAL;
    
    -- Use the CURRENT_WATERMARK() function to check which watermark is calculated
    SELECT
      *,
      part AS `Row Partition`,
      $rowtime AS `Row Timestamp`,
      CURRENT_WATERMARK($rowtime) AS `Operator Watermark`
    FROM t_watermark_debugging;
    
    -- Visualize the highest timestamp per Kafka partition
    -- Due to the table declaration (with 4 buckets), this query should show 4 rows.
    -- If not, the missing partitions might be the cause for watermark issues.
    SELECT part AS `Partition`, MAX($rowtime) AS `Max Timestamp in Partition`
      FROM t_watermark_debugging
      GROUP BY part;
    
    -- A workaround could be to not use the system watermark:
    ALTER TABLE t_watermark_debugging
      MODIFY WATERMARK FOR $rowtime AS $rowtime - INTERVAL '2' SECOND;
    -- Or for perfect input data:
    ALTER TABLE t_watermark_debugging
      MODIFY WATERMARK FOR $rowtime AS $rowtime - INTERVAL '0.001' SECOND;
    
    -- Add "fresh" data while the above statements with
    -- ROW_NUMBER() or CURRENT_WATERMARK() are running.
    INSERT INTO t_watermark_debugging VALUES
      (1, 'Fresh Bob'),
      (2, 'Fresh Alice'),
      (8, 'Fresh John'),
      (15, 'Fresh David');

The debugging examples above won’t solve everything but may help in finding the root cause.

The system watermark strategy is smart and excludes idle Kafka partitions from the watermark calculation after some time, but at least one partition must produce new data for the “logical clock” with watermarks.

Typically, root causes are:

  * Idle Kafka partitions
  * No data in Kafka partitions
  * Not enough data in Kafka partitions
  * Watermark strategy is too conservative
  * No fresh data after warm up with historical data for progressing the logical clock

### Handle idle partitions for missing watermarks¶

Idle partitions often cause missing watermarks. Also, no data in a partition or infrequent data can be a root cause.

    -- Create a topic with 4 partitions.
    CREATE TABLE t_watermark_idle (k INT, s STRING)
      DISTRIBUTED BY (k) INTO 4 BUCKETS;
    
    -- Avoid the "not enough data" problem by using a custom watermark.
    -- The watermark strategy is still coarse-grained enough for this example.
    ALTER TABLE t_watermark_idle
      MODIFY WATERMARK FOR $rowtime AS $rowtime - INTERVAL '2' SECONDS;
    
    -- Each value lands in a separate Kafka partition, and partition 1 is empty.
    INSERT INTO t_watermark_idle
      VALUES
        (1, 'Bob in partition 0'),
        (2, 'Alice in partition 3'),
        (8, 'John in partition 2');
    
    -- Thread 1: Start a streaming job.
    SELECT ROW_NUMBER() OVER (ORDER BY $rowtime ASC) AS `number`, *
      FROM t_watermark_idle;
    
    -- Thread 2: Insert some data immediately -> Thread 1 still without results.
    INSERT INTO t_watermark_idle
      VALUES (1, 'Another Bob in partition 0 shortly after');
    
    -- Thread 2: Insert some data after 15s -> Thread 1 should show results.
    INSERT INTO t_watermark_idle
      VALUES (1, 'Another Bob in partition 0 after 15s')

Within the first 15 seconds, all partitions contribute to the watermark calculation, so the first INSERT INTO has no effect because partition 1 is still empty.

After 15 seconds, all partitions are marked as idle. No partition contributes to the watermark calculation. But when the second INSERT INTO is executed, it becomes the main driving partition for the logical clock.

The global watermark jumps to “second INSERT INTO - 2 seconds”.

In the following code, the `sql.tables.scan.idle-timeout` configuration overrides the default idle-detection algorithm, so even an immediate INSERT INTO can be the main driving partition for the logical clock, because all other partitions are marked as idle after 1 second.

    -- Thread 1: Start a streaming job.
    -- Lower the idle timeout further.
    SET 'sql.tables.scan.idle-timeout' = '1s';
    SELECT ROW_NUMBER() OVER (ORDER BY $rowtime ASC) AS `number`, *
      FROM t_watermark_idle;
    
    -- Thread 2: Insert some data immediately -> Thread 1 should show results.
    INSERT INTO t_watermark_idle
      VALUES (1, 'Another Bob in partition 0 shortly after');

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

## Inferred tables schema evolution¶

You can use the ALTER TABLE statement to evolve schemas for [inferred tables](../sql-examples.html#flink-sql-examples-inferred-tables).

The following examples show output from the SHOW CREATE TABLE statement called on the resulting table.

### Schema Registry columns overlap with computed/metadata columns¶

For the following value schema in Schema Registry:

    {
      "type": "record",
      "name": "TestRecord",
      "fields": [
        {
          "name": "uid",
          "type": "int"
        }
      ]
    }

Evolve a table by adding metadata:

    ALTER TABLE t_metadata_overlap ADD `timestamp` TIMESTAMP_LTZ(3) NOT NULL METADATA;

SHOW CREATE TABLE returns the following output:

    CREATE TABLE t_metadata_overlap` (
      `key` VARBINARY(2147483647),
      `uid` INT NOT NULL,
      `timestamp` TIMESTAMP(3) WITH LOCAL TIME ZONE NOT NULL METADATA
    ) DISTRIBUTED BY HASH(`key`) INTO 6 BUCKETS
    WITH (
      ...
    )

Properties

  * Schema Registry says there is a timestamp physical column, but Flink says there is timestamp metadata column.

  * In this case, metadata columns and computed columns have precedence, and Confluent Cloud for Apache Flink removes the physical column from the schema.

  * Because Confluent Cloud for Apache Flink advertises [FULL_TRANSITIVE mode](../../../sr/fundamentals/schema-evolution.html#sr-compatibility-types), queries still work, and the physical column is set to NULL in the payload:
        
        INSERT INTO t_metadata_overlap
          SELECT CAST(NULL AS BYTES), 42, TO_TIMESTAMP_LTZ(0, 3);

Evolve the table by renaming metadata:

    ALTER TABLE t_metadata_overlap DROP `timestamp`;
    
    ALTER TABLE t_metadata_overlap
      ADD message_timestamp TIMESTAMP_LTZ(3) METADATA FROM 'timestamp';
    
    SELECT * FROM t_metadata_overlap;

SHOW CREATE TABLE returns the following output:

    CREATE TABLE `t_metadata_overlap` (
      `key` VARBINARY(2147483647),
      `uid` INT NOT NULL,
      `timestamp` VARCHAR(2147483647),
      `message_timestamp` TIMESTAMP(3) WITH LOCAL TIME ZONE METADATA FROM 'timestamp'
    ) DISTRIBUTED BY HASH(`key`) INTO 6 BUCKETS
    WITH (
      ...
    )

Properties

  * Now, both physical and metadata columns appear and can be accessed for reading and writing.

### Enrich a column that has no Schema Registry information¶

For the following value schema in Schema Registry:

    {
      "type": "record",
      "name": "TestRecord",
      "fields": [
        {
          "name": "uid",
          "type": "int"
        }
      ]
    }

SHOW CREATE TABLE returns the following output:

    CREATE TABLE `t_enrich_raw_key` (
      `key` VARBINARY(2147483647),
      `uid` INT NOT NULL
      ) DISTRIBUTED BY HASH(`key`) INTO 6 BUCKETS
    WITH (
      'changelog.mode' = 'append',
      'connector' = 'confluent',
      'key.format' = 'raw',
      'value.format' = 'avro-registry'
      ...
    )

Properties

  * Schema Registry provides only information for the value part.
  * Because the `key` part is not backed by Schema Registry, the `key.format` is `raw`.
  * The default data type of `raw` is BYTES, but you can change this by using the ALTER TABLE statement.

Evolve the table by giving a raw format column a specific type:

    ALTER TABLE t_enrich_raw_key MODIFY key STRING;

SHOW CREATE TABLE returns the following output:

    CREATE TABLE `t_enrich_raw_key` (
      `key` STRING,
      `uid` INT NOT NULL
    ) DISTRIBUTED BY HASH(`key`) INTO 6 BUCKETS
    WITH (
      'changelog.mode' = 'append',
      'connector' = 'confluent',
      'key.format' = 'raw',
      'value.format' = 'avro-registry'
      ...
    )

Properties

  * Only changes to simple, atomic types, like INT, BYTES, and STRING are supported, where the binary representation is clear.
  * For more complex modifications, use Schema Registry.
  * In multi-cluster scenarios, the ALTER TABLE statement must be executed for every cluster, because the data type for `key` is stored in the Flink regional metastore.

### Configure Schema Registry subject names¶

When working with topics that use RecordNameStrategy or TopicRecordNameStrategy, you can configure the subject names for the schema resolution in Schema Registry. This is particularly useful when handling multiple event types in a single topic.

For topics using these strategies, Flink initially infers a raw binary table:

    SHOW CREATE TABLE events;

Your output will show a raw binary structure:

    CREATE TABLE `events` (
      `key` VARBINARY(2147483647),
      `value` VARBINARY(2147483647)
    ) DISTRIBUTED BY HASH(`key`) INTO 6 BUCKETS
    WITH (
      'changelog.mode' = 'append',
      'connector' = 'confluent',
      'key.format' = 'raw',
      'value.format' = 'raw'
    )

Configure value schema subject names for each format:

AvroJSON SchemaProtobuf

    ALTER TABLE events SET (
      'value.format' = 'avro-registry',
      'value.avro-registry.subject-names' = 'com.example.Order;com.example.Shipment'
    );

    ALTER TABLE events SET (
      'value.format' = 'json-registry',
      'value.json-registry.subject-names' = 'com.example.Order;com.example.Shipment'
    );

    ALTER TABLE events SET (
      'value.format' = 'proto-registry',
      'value.proto-registry.subject-names' = 'com.example.Order;com.example.Shipment'
    );

If your topic uses keyed messages, you can also configure the key format:

    ALTER TABLE events SET (
      'key.format' = 'avro-registry',
      'key.avro-registry.subject-names' = 'com.example.OrderKey'
    );

You can configure both key and value schema subject names in a single statement:

    ALTER TABLE events SET (
      'key.format' = 'avro-registry',
      'key.avro-registry.subject-names' = 'com.example.OrderKey',
      'value.format' = 'avro-registry',
      'value.avro-registry.subject-names' = 'com.example.Order;com.example.Shipment'
    );

Properties:

  * Use semicolons (`;`) to separate multiple subject names
  * Subject names must match exactly with the names registered in Schema Registry
  * The format prefix (`avro-registry`, `json-registry`, or `proto-registry`) must match the schema format in Schema Registry

### Reset a key value¶

You can use the RESET option to set any key to its default value.

The following example shows how to reset a table that has a JSON Schema back to raw format.

    ALTER TABLE json_table RESET (
      'value.json-registry.wire-encoding',
      'value.json-registry.subject-names'
    );

## Custom error handling¶

You can use ALTER TABLE with the [error-handling.mode](create-table.html#flink-sql-create-table-with-error-handling-mode) and [error-handling.log.target](create-table.html#flink-sql-create-table-with-error-handling-log-target) table properties to set custom error handling for deserialization errors.

The following code example shows how to log errors to the specified Dead Letter Queue (DLQ) table and enable processing to continue.

     ALTER TABLE my_table SET (
      'error-handling.mode' = 'log',
      'error-handling.log.target' = 'my_error_table'
    );

## Related content¶

  * Video: [How to Set Idle Timeouts](https://www.youtube.com/watch?v=YSIhM5-Sykw)
