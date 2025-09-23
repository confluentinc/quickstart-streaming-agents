---
document_id: flink_reference_statements_show_chunk_3
source_file: flink_reference_statements_show.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/show.html
title: SQL SHOW Statements in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 5
---

| | orders | +------------+

## SHOW CREATE TABLE¶

Syntax

    SHOW CREATE TABLE [catalog_name.][db_name.]table_name;

Description
    Show details about the specified table.
Example

    SHOW CREATE TABLE flights;

Your output should resemble:

    +-----------------------------------------------------------+
    |                     SHOW CREATE TABLE                     |
    +-----------------------------------------------------------+
    | CREATE TABLE `my_environment`.`cluster_0`.`flights` (     |
    |   `flight_id` VARCHAR(2147483647),                        |
    |   `origin` VARCHAR(2147483647),                           |
    |   `destination` VARCHAR(2147483647)                       |
    | ) WITH (                                                  |
    |   'changelog.mode' = 'append',                            |
    |   'connector' = 'confluent',                              |
    |   'kafka.cleanup-policy' = 'delete',                      |
    |   'kafka.max-message-size' = '2097164 bytes',             |
    |   'kafka.partitions' = '6',                               |
    |   'kafka.retention.size' = '0 bytes',                     |
    |   'kafka.retention.time' = '604800000 ms',                |
    |   'scan.bounded.mode' = 'unbounded',                      |
    |   'scan.startup.mode' = 'earliest-offset',                |
    |   'value.format' = 'avro-registry'                        |
    | )                                                         |
    |                                                           |
    +-----------------------------------------------------------+

### Inferred Tables¶

Inferred tables are tables that have not been created with CREATE TABLE but are detected automatically by using information about existing topics and Schema Registry entries.

The following examples show SHOW CREATE TABLE called on the resulting table.

#### No key and no value in Schema Registry¶

SHOW CREATE TABLE returns:

    CREATE TABLE `t_raw` (
      `key` VARBINARY(2147483647),
      `val` VARBINARY(2147483647)
    ) DISTRIBUTED BY HASH(`key`) INTO 2 BUCKETS
    WITH (
      'changelog.mode' = 'append',
      'connector' = 'confluent',
      'key.format' = 'raw',
      'value.format' = 'raw'
      ...
    );

Properties

* Key and value formats are raw (binary format) with BYTES

* Following Kafka message semantics, both key and value support NULL as well, so the following statement is supported:

        INSERT INTO t_raw (key, val) SELECT CAST(NULL AS BYTES), CAST(NULL AS BYTES);

#### No key and but record value in Schema Registry¶

Given the following value in Schema Registry:

    {
      "type": "record",
      "name": "TestRecord",
      "fields": [
        {
          "name": "i",
          "type": "int"
        },
        {
          "name": "s",
          "type": "string"
        }
      ]
    }

SHOW CREATE TABLE returns:

    CREATE TABLE `t_raw_key` (
      `key` VARBINARY(2147483647),
      `i` INT NOT NULL,
      `s` VARCHAR(2147483647) NOT NULL
    ) DISTRIBUTED BY HASH(`key`) INTO 6 BUCKETS
    WITH (
      'changelog.mode' = 'append',
      'connector' = 'confluent',
      'key.format' = 'raw',
      'value.format' = 'avro-registry'
      ...
    )

Properties

* Key format is raw (binary format) with BYTES

* Following Kafka message semantics, key supports NULL as well. So this is possible: so the following statement is supported:

        INSERT INTO t_raw_key SELECT CAST(NULL AS BYTES), 12, 'Bob';

#### Atomic key and record value in Schema Registry¶

Given the following key and value in Schema Registry:

    "int"

    {
      "type": "record",
      "name": "TestRecord",
      "fields": [
         {
            "name": "i",
            "type": "int"
         },
         {
            "name": "s",
            "type": "string"
         }
      ]
    }

SHOW CREATE TABLE returns:

    CREATE TABLE `t_atomic_key` (
      `key` INT NOT NULL,
      `i` INT NOT NULL,
      `s` VARCHAR(2147483647) NOT NULL
    ) DISTRIBUTED BY HASH(`key`) INTO 2 BUCKETS
    WITH (
      'changelog.mode' = 'append',
      'connector' = 'confluent',
      'key.format' = 'avro-registry',
      'value.format' = 'avro-registry'
      ...
    )

Properties

* Schema Registry defines column data type INT NOT NULL.
* The column name `key` is used as a default, because Schema Registry doesn’t provide a column name.

#### Overlapping names in key/value, no key in Schema Registry¶

Given the following value in Schema Registry:

    {
      "type": "record",
      "name": "TestRecord",
      "fields": [
         {
            "name": "i",
            "type": "int"
         },
         {
            "name": "s",
            "type": "string"
         }
      ]
    }

SHOW CREATE TABLE returns:
