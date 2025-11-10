---
document_id: flink_reference_statements_create-table_chunk_13
source_file: flink_reference_statements_create-table.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-table.html
title: SQL CREATE TABLE Statement in Confluent Cloud for Apache Flink
chunk_index: 13
total_chunks: 14
---

customer_changes SET ('changelog.mode' = 'append');

## Examples¶

The following examples show how to create Flink tables for frequently encountered scenarios.

### Minimal table¶

    CREATE TABLE t_minimal (s STRING);

Properties

  * Append changelog mode.
  * No Schema Registry key.
  * Round robin distribution.
  * 6 Kafka partitions.
  * The `$rowtime` column and system watermark are added implicitly.

### Table with a primary key¶

Syntax

    CREATE TABLE t_pk (k INT PRIMARY KEY NOT ENFORCED, s STRING);

Properties

  * Upsert changelog mode.
  * The primary key defines an implicit DISTRIBUTED BY(k).
  * `k` is the Schema Registry key.
  * Hash distribution on `k`.
  * The table has 6 Kafka partitions.
  * `k` is declared as being unique, meaning no duplicate rows.
  * `k` must not contain NULLs, so an implicit NOT NULL is added.
  * The `$rowtime` column and system watermark are added implicitly.

### Table with a primary key in append mode¶

Syntax

    CREATE TABLE t_pk_append (k INT PRIMARY KEY NOT ENFORCED, s STRING)
      DISTRIBUTED INTO 4 BUCKETS
      WITH ('changelog.mode' = 'append');

Properties

  * Append changelog mode.
  * `k` is the Schema Registry key.
  * Hash distribution on `k`.
  * The table has 4 Kafka partitions.
  * `k` is declared as being unique, meaning no duplicate rows.
  * `k` must not contain NULLs, meaning implicit NOT NULL.
  * The `$rowtime` column and system watermark are added implicitly.

### Table with hash distribution¶

Syntax

    CREATE TABLE t_dist (k INT, s STRING) DISTRIBUTED BY (k) INTO 4 BUCKETS;

Properties

  * Append changelog mode.
  * `k` is the Schema Registry key.
  * Hash distribution on `k`.
  * The table has 4 Kafka partitions.
  * The `$rowtime` column and system watermark are added implicitly.

### Complex table with all concepts combined¶

Syntax

    CREATE TABLE t_complex (k1 INT, k2 INT, PRIMARY KEY (k1, k2) NOT ENFORCED, s STRING)
      COMMENT 'My complex table'
      DISTRIBUTED BY HASH(k1) INTO 4 BUCKETS
      WITH ('changelog.mode' = 'append');

Properties

  * Append changelog mode.
  * `k1` is the Schema Registry key.
  * Hash distribution on `k1`.
  * `k2` is treated as a value column and is stored in the value part of Schema Registry.
  * The table has 4 Kafka partitions.
  * `k1` and `k2` are declared as being unique, meaning no duplicates.
  * `k` and `k2` must not contain NULLs, meaning implicit NOT NULL.
  * The `$rowtime` column and system watermark are added implicitly.
  * An additional comment is added.

### Table with overlapping names in key/value of Schema Registry but disjoint data¶

Syntax

    CREATE TABLE t_disjoint (from_key_k INT, k STRING)
      DISTRIBUTED BY (from_key_k)
      WITH ('key.fields-prefix' = 'from_key_');

Properties

  * Append changelog mode.
  * Hash distribution on `from_key_k`.
  * The key prefix `from_key_` is defined and is stripped before storing the schema in Schema Registry.
    * Therefore, `k` is the Schema Registry key of type INT.
    * Also, `k` is the Schema Registry value of type STRING.
  * Both key and value store disjoint data, so they can have different data types

### Create with overlapping names in key/value of Schema Registry but joint data¶

Syntax

    CREATE TABLE t_joint (k INT, v STRING)
      DISTRIBUTED BY (k)
      WITH ('value.fields-include' = 'all');

Properties

  * Append changelog mode.
  * Hash distribution on `k`.
  * By default, the key is never included in the value in Schema Registry.
  * By setting `'value.fields-include' = 'all'`, the value contains the full table schema
    * Therefore, `k` is the Schema Registry key.
    * Also, `k, v` is the Schema Registry value.
  * The payload of `k` is stored twice in the Kafka message, because key and value store joint data and they have the same data type for `k`.

### Table with metadata columns for writing a Kafka message timestamp¶

Syntax

    CREATE TABLE t_metadata_write (name STRING, ts TIMESTAMP_LTZ(3) NOT NULL METADATA FROM 'timestamp')
      DISTRIBUTED INTO 1 BUCKETS;

Properties

  * Adds the `ts` metadata column, which isn’t part of Schema Registry but instead is a pure Flink concept.
  * In contrast with `$rowtime`, which is declared as a METADATA VIRTUAL column, `ts` is selected in a SELECT * statement and is writable.

The following examples show how to fill Kafka messages with an [instant](../datatypes.html#flink-sql-timestamp-comparison-timestamp-ltz).

    INSERT INTO t (ts, name) SELECT NOW(), 'Alice';
    INSERT INTO t (ts, name) SELECT TO_TIMESTAMP_LTZ(0, 3), 'Bob';
    SELECT $rowtime, * FROM t;

The Schema Registry subject compatibility mode must be FULL or FULL_TRANSITIVE. For more information, see [Schema Evolution and Compatibility for Schema Registry on Confluent Cloud](../../../sr/fundamentals/schema-evolution.html#schema-evolution-and-compatibility).
