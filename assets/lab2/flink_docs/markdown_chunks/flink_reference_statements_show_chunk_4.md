---
document_id: flink_reference_statements_show_chunk_4
source_file: flink_reference_statements_show.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/show.html
title: SQL SHOW Statements in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 5
---

CREATE TABLE `t_raw_disjoint` (
      `key_key` VARBINARY(2147483647),
      `i` INT NOT NULL,
      `key` VARCHAR(2147483647) NOT NULL
    ) DISTRIBUTED BY HASH(`key_key`) INTO 1 BUCKETS
    WITH (
      'changelog.mode' = 'append',
      'connector' = 'confluent',
      'key.fields-prefix' = 'key_',
      'key.format' = 'raw',
      'value.format' = 'avro-registry'
      ...
    )

Properties

* Schema Registry value defines columns INT NOT NULL and `key STRING`
* The column name `key BYTES` is used as a default if no key is in Schema Registry
* Because `key` would collide with value column, `key_` prefix is added

#### Record key and record value in Schema Registry¶

Given the following key and value in Schema Registry:

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

    {
      "type": "record",
      "name": "TestRecord",
      "fields": [
         {
            "name": "name",
            "type": "string"
         },
         {
            "name": "zip_code",
            "type": "string"
         }
      ]
    }

SHOW CREATE TABLE returns:

    CREATE TABLE `t_sr_disjoint` (
      `uid` INT NOT NULL,
      `name` VARCHAR(2147483647) NOT NULL,
      `zip_code` VARCHAR(2147483647) NOT NULL
    ) DISTRIBUTED BY HASH(`uid`) INTO 1 BUCKETS
    WITH (
      'changelog.mode' = 'append',
      'connector' = 'confluent',
      'value.format' = 'avro-registry'
      ...
    )

Properties

* Schema Registry defines columns for both key and value.
* The column names of key and value are disjoint sets and don’t overlap.

#### Record key and record value with overlap in Schema Registry¶

Given the following key and value in Schema Registry:

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

    {
      "type": "record",
      "name": "TestRecord",
      "fields": [
         {
            "name": "uid",
            "type": "int"
         },{
            "name": "name",
            "type": "string"
         },
         {
            "name": "zip_code",
            "type": "string"
         }
      ]
    }

SHOW CREATE TABLE returns:

    CREATE TABLE `t_sr_joint` (
      `uid` INT NOT NULL,
      `name` VARCHAR(2147483647) NOT NULL,
      `zip_code` VARCHAR(2147483647) NOT NULL
    ) DISTRIBUTED BY HASH(`uid`) INTO 1 BUCKETS
    WITH (
      'changelog.mode' = 'append',
      'connector' = 'confluent',
      'value.fields-include' = 'all',
      'value.format' = 'avro-registry'
      ...
    )

Properties

* Schema Registry defines columns for both key and value.
* The column names of key and value overlap on `uid`.
* `'value.fields-include' = 'all'` is set to exclude the key because it is fully contained in the value.

### Inferred tables schema evolution¶

#### Schema Registry columns overlap with computed/metadata columns¶

Given the following value in Schema Registry:

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

Evolve the table by adding metadata:

    ALTER TABLE t_metadata_overlap ADD `timestamp` TIMESTAMP_LTZ(3) NOT NULL METADATA;

Evolve the table by adding an optional schema column:

    {
      "type": "record",
      "name": "TestRecord",
      "fields": [
         {
            "name": "uid",
            "type": "int"
         },
         {
            "name": "timestamp",
            "type": ["null", "string"],
            "default": null
         }
      ]
    }

SHOW CREATE TABLE shows:

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

* In this case, metadata columns and computed columns have precedence, so Flink removes the physical column from the schema.

* Given that Flink advertises FULL_TRANSITIVE mode, queries still work, and the physical column is set to NULL in the payload:

        INSERT INTO t_metadata_overlap
          SELECT CAST(NULL AS BYTES), 42, TO_TIMESTAMP_LTZ(0, 3);

        SELECT * FROM t_metadata_overlap;

Evolve the table by renaming metadata:

    ALTER TABLE t_metadata_overlap DROP `timestamp`;

    ALTER TABLE t_metadata_overlap
      ADD message_timestamp TIMESTAMP_LTZ(3) METADATA FROM 'timestamp';

SHOW CREATE TABLE shows:

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

* Now, both physical and metadata column show up and can be accessed both for reading and writing.
