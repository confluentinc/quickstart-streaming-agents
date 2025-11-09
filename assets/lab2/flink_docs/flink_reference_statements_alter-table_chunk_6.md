---
document_id: flink_reference_statements_alter-table_chunk_6
source_file: flink_reference_statements_alter-table.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/alter-table.html
title: SQL ALTER TABLE Statement in Confluent Cloud for Apache Flink
chunk_index: 6
total_chunks: 7
---

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
