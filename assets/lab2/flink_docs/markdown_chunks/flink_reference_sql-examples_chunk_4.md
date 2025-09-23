---
document_id: flink_reference_sql-examples_chunk_4
source_file: flink_reference_sql-examples.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/sql-examples.html
title: Flink SQL Examples in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 12
---

"micro", "microsecond", "ns", "nano", "nanosecond"

## Inferred table examples¶

Inferred tables are tables that have not been created by using a CREATE TABLE statement, but instead are automatically detected from information about existing Kafka topics and Schema Registry entries.

You can use the ALTER TABLE statement to [evolve schemas](statements/alter-table.html#flink-sql-alter-table-examples) for inferred tables.

The following examples show output from the SHOW CREATE TABLE statement called on the resulting table.

### No key or value in Schema Registry¶

For an inferred table with no registered key or value schemas, SHOW CREATE TABLE returns the following output:

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
    )

Properties

* Key and value formats are raw (binary format) with BYTES.

* Following Kafka message semantics, both key and value support NULL as well, so the following code is valid:

        INSERT INTO t_raw (key, val) SELECT CAST(NULL AS BYTES), CAST(NULL AS BYTES);

### No key and but record value in Schema Registry¶

For the following value schema in Schema Registry:

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

SHOW CREATE TABLE returns the following output:

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

* The key format is raw (binary format) with BYTES.

* Following Kafka message semantics, the key supports NULL as well, so the following code is valid:

        INSERT INTO t_raw_key SELECT CAST(NULL AS BYTES), 12, 'Bob';

### Atomic key and record value in Schema Registry¶

For the following key schema in Schema Registry:

    "int"

And for the following value schema in Schema Registry:

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

SHOW CREATE TABLE returns the following output:

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

* Schema Registry defines the column data type as INT NOT NULL.
* The column name, `key`, is used as the default, because Schema Registry doesn’t provide a column name.

### Overlapping names in key/value, no key in Schema Registry¶

For the following value schema in Schema Registry:

    {
      "type": "record",
      "name": "TestRecord",
      "fields": [
        {
          "name": "i",
          "type": "int"
        },
        {
          "name": "key",
          "type": "string"
        }
      ]
    }

SHOW CREATE TABLE returns the following output:

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

* The Schema Registry value schema defines columns `i INT NOT NULL` and `key STRING`.
* The column name `key BYTES` is used as the default if no key is in Schema Registry.
* Because `key` would collide with value schema column, the `key_` prefix is added.

### Record key and record value in Schema Registry¶

For the following key schema in Schema Registry:

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

And for the following value schema in Schema Registry:

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
