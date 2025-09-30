---
document_id: flink_reference_statements_create-table_chunk_14
source_file: flink_reference_statements_create-table.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-table.html
title: SQL CREATE TABLE Statement in Confluent Cloud for Apache Flink
chunk_index: 14
total_chunks: 14
---

### Table with string key and value in Schema Registry¶

Syntax

    CREATE TABLE t_raw_string_key (key STRING, i INT)
      DISTRIBUTED BY (key)
      WITH ('key.format' = 'raw');

Properties

* Schema Registry is filled with a value subject containing `i`.
* The key columns are determined by the DISTRIBUTED BY clause.
* By default, Avro in Schema Registry would be used for the key, but the WITH clause overrides this to the `raw` format.

### Tables with cross-region schema sharing¶

  1. Create two Kafka clusters in different regions, for example, `eu-west-1` and `us-west-2`.

  2. Create two Flink compute pools in different regions, for example, `eu-west-1` and `us-west-2`.

  3. In the first region, run the following statement.

         CREATE TABLE t_shared_schema (key STRING, s STRING) DISTRIBUTED BY (key);

  4. In the second region, run the same statement.

         CREATE TABLE t_shared_schema (key STRING, s STRING) DISTRIBUTED BY (key);

Properties

* Schema Registry is shared across regions.
* The SQL metastore, Flink compute pools, and Kafka clusters are regional.
* Both tables in either region share the Schema Registry subjects `t_shared_schema-key` and `t_shared_schema-value`.

### Create with different changelog modes¶

There are three ways of storing events in a table’s log, this is, in the underlying Kafka topic.

append

* Every insertion event is an **immutable fact**.
* Every event is **insert-only**.
* Events can be distributed in a round-robin fashion across workers/shards because they are **unrelated**.

upsert

* Events are **related** using a primary key.
* Every event is either an **upsert or delete** event for a primary key.
* Events for the same primary key should land at the same worker/shard.

retract

* Every upsert event is a **fact that can be “undone”**.

* This means that every event is either an insertion or its retraction.

* So, **two events are related by all columns**. In other words, the entire row is the key.

For example, `+I['Bob', 42]` is related to `-D['Bob', 42]` and `+U['Alice', 13]` is related to `-U['Alice', 13]`.

* The **retract** mode is intermediate between the **append** and **upsert** modes.
* The **append** and **upsert** modes are natural to existing Kafka consumers and producers.
* Kafka compaction is a kind of **upsert**.

Start with a table created by the following statement.

    CREATE TABLE t_changelog_modes (i BIGINT);

Properties

* Confluent Cloud for Apache Flink always derives an appropriate changelog mode for the preceding declaration.
* If there is no primary key, **append** is the safest option, because it prevents users from pushing updates into a topic accidentally, and it has the best support of downstream consumers.

    -- works because the query is non-updating
    INSERT INTO t_changelog_modes SELECT 1;

    -- does not work because the query is updating, causing an error
    INSERT INTO t_changelog_modes SELECT COUNT(*) FROM (VALUES (1), (2), (3));

If you need updates, and if downstream consumers support it, for example, when the consumer is another Flink job, you can set the changelog mode to **retract**.

    ALTER TABLE t_changelog_modes SET ('changelog.mode' = 'retract');

Properties

* The table starts accepting retractions during INSERT INTO.
* Already existing records in the Kafka topic are treated as insertions.
* Newly added records receive a changeflag (+I, +U, -U, -D) in the Kafka message header.

Going back to **append** mode is possible, but retractions (-U, -D) appear as insertions, and the Kafka header metadata column reveals the changeflag.

    ALTER TABLE t_changelog_modes SET ('changelog.mode' = 'append');
    ALTER TABLE t_changelog_modes ADD headers MAP<BYTES, BYTES> METADATA VIRTUAL;

    -- Shows what is serialized internally
    SELECT i, headers FROM t_changelog_modes;

### Table with infinite retention time¶

    CREATE TABLE t_infinite_retention (i INT) WITH ('kafka.retention.time' = '0');

Properties

* By default, the retention time is 7 days, as in all other APIs.
* Flink doesn’t support `-1` for durations, so `0` means infinite retention time.
* Durations in Flink support `2 day` or `2 d` syntax, so it doesn’t need to be in milliseconds.
* If no unit is specified, the unit is milliseconds.
* The following units are supported:

    "d", "day", "h", "hour", "m", "min", "minute", "ms", "milli", "millisecond",
    "µs", "micro", "microsecond", "ns", "nano", "nanosecond"
