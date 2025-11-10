---
document_id: flink_reference_statements_create-table_chunk_3
source_file: flink_reference_statements_create-table.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-table.html
title: SQL CREATE TABLE Statement in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 14
---

more information, see [Vector Search](../../../ai/external-tables/vector-search.html#flink-sql-vector-search).

## System columns¶

Confluent Cloud for Apache Flink introduces system columns for Flink tables. System columns build on the metadata columns.

System columns can only be read and are not part of the query-to-sink schema.

System columns aren’t selected in a `SELECT *` statement, and they’re not shown in `DESCRIBE` or `SHOW CREATE TABLE` statements. The result from the `DESCRIBE EXTENDED` statement _does_ include system columns.

Both inferred and manual tables are provisioned with a set of default system columns.

### $rowtime¶

Currently, `$rowtime TIMESTAMP_LTZ(3) NOT NULL` is provided as a system column.

You can use the `$rowtime` system column to get the timestamp from a Kafka record, because `$rowtime` is exactly the Kafka record timestamp. If you want to write out `$rowtime`, you must use the timestamp metadata key.

## PRIMARY KEY constraint¶

A primary key constraint is a hint for Flink SQL to leverage for optimizations which specifies that a column or a set of columns in a table or a view are unique and they _do not_ contain null.

A primary key uniquely identifies a row in a table. No columns in a primary key can be nullable.

You can declare a primary key constraint together with a column definition (a column constraint) or as a single line (a table constraint). In both cases, it must be declared as a singleton. If you define more than one primary key constraint in the same statement, Flink SQL throws an exception.

The SQL standard specifies that a constraint can be `ENFORCED` or `NOT ENFORCED`, which controls whether the constraint checks are performed on the incoming/outgoing data. Flink SQL doesn’t own the data, so the only mode it supports is `NOT ENFORCED`. It’s your responsibility to ensure that the query enforces key integrity.

Flink SQL assumes correctness of the primary key by assuming that the column’s nullability is aligned with the columns in primary key. Connectors must ensure that these are aligned.

The `PRIMARY KEY` constraint distributes the table implicitly by the key column. A Kafka message key is defined either by an implicit DISTRIBUTED BY clause clause from a PRIMARY KEY constraint or an explicit `DISTRIBUTED BY`.

Note

In a CREATE TABLE statement, a primary key constraint alters the column’s nullability, which means that a column with a primary key constraint isn’t nullable.

Example

The following SQL statement creates a table named `latest_page_per_ip` with a primary key defined on `ip`. This statement creates a Kafka topic, a value-schema, and a key-schema. The value-schema contains the definitions for `page_url` and `ts`, while the key-schema contains the definition for `ip`.

    CREATE TABLE latest_page_per_ip (
        `ip` STRING,
        `page_url` STRING,
        `ts` TIMESTAMP_LTZ(3),
        PRIMARY KEY(`ip`) NOT ENFORCED
    );

## DISTRIBUTED BY clause¶

The `DISTRIBUTED BY` clause buckets the created table by the specified columns.

Bucketing enables a file-like structure with a small, human-enumerable key space. It groups rows that have “infinite” key space, like `user_id`, usually by using a hash function, for example:

    bucket = hash(user_id) % number_of_buckets

Kafka partitions map 1:1 to SQL buckets. The `n` BUCKETS are used for the number of partitions when creating a topic.

If `n` is not defined, the default is 6.

  * The number of buckets is fixed.
  * A bucket is identifiable regardless of partition.
  * Bucketing is good in long-term storage for reading across partitions based on a large key space, for example, `user_id`.
  * Also, bucketing is good for short-term storage for load balancing.

Every mode comes with a default distribution, so DISTRIBUTED BY is required only by power users. In most cases, a simple `CREATE TABLE t (schema);` is sufficient.

  * For upsert mode, the bucket key must be equal to primary key.
  * For append/retract mode, the bucket key can be a subset of the primary key.
  * The bucket key can be undefined, which corresponds to a “connector defined” distribution: round robin for append, and hash-by-row for retract.

Custom distributions are possible, but currently only custom hash distributions are supported.

Example

The following SQL declares a table named `t_dist` that has one key column named `k` and 4 Kafka partitions.

    CREATE TABLE t_dist (k INT, s STRING) DISTRIBUTED BY (k) INTO 4 BUCKETS;

BY (k) INTO 4 BUCKETS;

## PARTITIONED BY clause¶

**Deprecated** Use the DISTRIBUTED BY clause instead.

The `PARTITIONED BY` clause partitions the created table by the specified columns.

Use `PARTITIONED BY` to declare key columns in a table explicitly. A Kafka message key is defined either by an explicit `PARTITIONED BY` clause or an implicit `PARTITIONED BY` clause from a PRIMARY KEY constraint.

If compaction is enabled, the Kafka message key is overloaded with another semantic used for compaction, which influences constraints on the Kafka message key for partitioning.

Example

The following SQL declares a table named `t` that has one key column named `key` of type INT.

    CREATE TABLE t (partition_key INT, example_value STRING) PARTITIONED BY (partition_key);
