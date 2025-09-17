---
source_url: https://docs.confluent.io/cloud/current/flink/reference/sql-examples.html
title: Flink SQL Examples in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'sql-examples.html']
scraped_date: 2025-09-05T13:47:17.921047
---

# Flink SQL Examples in Confluent Cloud for Apache Flink¶

The following code examples show common Flink SQL use cases with Confluent Cloud for Apache Flink®.

  * CREATE TABLE
  * Inferred tables
  * ALTER TABLE
  * SELECT
  * Schema reference

## CREATE TABLE examples¶

The following examples show how to create Flink tables with various options.

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

The following examples show how to fill Kafka messages with an [instant](datatypes.html#flink-sql-timestamp-comparison-timestamp-ltz).

    INSERT INTO t (ts, name) SELECT NOW(), 'Alice';
    INSERT INTO t (ts, name) SELECT TO_TIMESTAMP_LTZ(0, 3), 'Bob';
    SELECT $rowtime, * FROM t;

The Schema Registry subject compatibility mode must be FULL or FULL_TRANSITIVE. For more information, see [Schema Evolution and Compatibility for Schema Registry on Confluent Cloud](../../sr/fundamentals/schema-evolution.html#schema-evolution-and-compatibility).

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

SHOW CREATE TABLE returns the following output:

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

### Record key and record value with overlap in Schema Registry¶

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

SHOW CREATE TABLE returns the following output:

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
  * `'value.fields-include' = 'all'` is set to exclude the key, because it is fully contained in the value.
  * Detecting that key is fully contained in the value requires that _both field name and data type match completely, including nullability_ , and _all fields of the key_ are included in the value.

### Union types in Schema Registry¶

For the following value schema in Schema Registry:

    ["int", "string"]

SHOW CREATE TABLE returns the following output:

    CREATE TABLE `t_union` (
      `key` VARBINARY(2147483647),
      `int` INT,
      `string` VARCHAR(2147483647)
    )
    ...

For the following value schema in Schema Registry:

    [
      "string",
      {
        "type": "record",
        "name": "User",
        "fields": [
          {
            "name": "uid",
            "type": "int"
          },{
            "name": "name",
            "type": "string"
          }
        ]
      },
      {
        "type": "record",
        "name": "Address",
        "fields": [
          {
            "name": "zip_code",
            "type": "string"
          }
        ]
      }
    ]

SHOW CREATE TABLE returns the following output:

    CREATE TABLE `t_union` (
      `key` VARBINARY(2147483647),
      `string` VARCHAR(2147483647),
      `User` ROW<`uid` INT NOT NULL, `name` VARCHAR(2147483647) NOT NULL>,
      `Address` ROW<`zip_code` VARCHAR(2147483647) NOT NULL>
    )
    ...

Properties

  * NULL and NOT NULL are inferred depending on whether a union contains NULL.
  * Elements of a union are always NULL, because they need to be set to NULL when a different element is set.
  * If a record defines a `namespace`, the field is prefixed with it, for example, `org.myorg.avro.User`.

### Multi-message protobuf schema in Schema Registry¶

For the following value schema in Schema Registry:

    syntax = "proto3";
    
    message Purchase {
       string item = 1;
       double amount = 2;
       string customer_id = 3;
    }
    
    message Pageview {
       string url = 1;
       bool is_special = 2;
       string customer_id = 3;
    }

SHOW CREATE TABLE returns the following output:

    CREATE TABLE `t` (
      `key` VARBINARY(2147483647),
      `Purchase` ROW<
          `item` VARCHAR(2147483647) NOT NULL,
          `amount` DOUBLE NOT NULL,
          `customer_id` VARCHAR(2147483647) NOT NULL
       >,
      `Pageview` ROW<
          `url` VARCHAR(2147483647) NOT NULL,
          `is_special` BOOLEAN NOT NULL,
          `customer_id` VARCHAR(2147483647) NOT NULL
       >
    )
    ...

For the following value schema in Schema Registry:

    syntax = "proto3";
    
    message Purchase {
       string item = 1;
       double amount = 2;
       string customer_id = 3;
       Pageview pageview = 4;
    }
    
    message Pageview {
       string url = 1;
       bool is_special = 2;
       string customer_id = 3;
    }

SHOW CREATE TABLE returns the following output:

    CREATE TABLE `t` (
      `key` VARBINARY(2147483647),
      `Purchase` ROW<
          `item` VARCHAR(2147483647) NOT NULL,
          `amount` DOUBLE NOT NULL,
          `customer_id` VARCHAR(2147483647) NOT NULL,
          `pageview` ROW<
             `url` VARCHAR(2147483647) NOT NULL,
             `is_special` BOOLEAN NOT NULL,
             `customer_id` VARCHAR(2147483647) NOT NULL
          >
       >,
      `Pageview` ROW<
          `url` VARCHAR(2147483647) NOT NULL,
          `is_special` BOOLEAN NOT NULL,
          `customer_id` VARCHAR(2147483647) NOT NULL
       >
    )
    ...

For the following value schema in Schema Registry:

    syntax = "proto3";
    
    message Purchase {
       string item = 1;
       double amount = 2;
       string customer_id = 3;
       Pageview pageview = 4;
       message Pageview {
          string url = 1;
          bool is_special = 2;
          string customer_id = 3;
       }
    }

SHOW CREATE TABLE returns the following output:

    CREATE TABLE `t` (
      `key` VARBINARY(2147483647),
      `item` VARCHAR(2147483647) NOT NULL,
      `amount` DOUBLE NOT NULL,
      `customer_id` VARCHAR(2147483647) NOT NULL,
      `pageview` ROW<
          `url` VARCHAR(2147483647) NOT NULL,
          `is_special` BOOLEAN NOT NULL,
          `customer_id` VARCHAR(2147483647) NOT NULL
       >
    )
    ...

### Debezium CDC format in Schema Registry¶

For a Debezium CDC format with the following value schema in Schema Registry:

    {
      "type": "record",
      "name": "Customer",
      "namespace": "io.debezium.data",
      "fields": [
        {
          "name": "before",
          "type": ["null", {
            "type": "record",
            "name": "Value",
            "fields": [
              {"name": "id", "type": "int"},
              {"name": "name", "type": "string"},
              {"name": "email", "type": "string"}
            ]
          }],
          "default": null
        },
        {
          "name": "after",
          "type": ["null", "Value"],
          "default": null
        },
        {
          "name": "source",
          "type": {
            "type": "record",
            "name": "Source",
            "fields": [
              {"name": "version", "type": "string"},
              {"name": "connector", "type": "string"},
              {"name": "name", "type": "string"},
              {"name": "ts_ms", "type": "long"},
              {"name": "db", "type": "string"},
              {"name": "schema", "type": "string"},
              {"name": "table", "type": "string"}
            ]
          }
        },
        {"name": "op", "type": "string"},
        {"name": "ts_ms", "type": ["null", "long"], "default": null},
        {"name": "transaction", "type": ["null", {
          "type": "record",
          "name": "Transaction",
          "fields": [
            {"name": "id", "type": "string"},
            {"name": "total_order", "type": "long"},
            {"name": "data_collection_order", "type": "long"}
          ]
        }], "default": null}
      ]
    }

SHOW CREATE TABLE returns the following output:

    CREATE TABLE `customer_changes` (
      `key` VARBINARY(2147483647),
       `id` INT NOT NULL,
       `name` VARCHAR(2147483647) NOT NULL,
       `email` VARCHAR(2147483647) NOT NULL
    )
    DISTRIBUTED BY HASH(`key`) INTO 6 BUCKETS
    WITH (
      'changelog.mode' = 'retract',
      'connector' = 'confluent',
      'key.format' = 'raw',
      'value.format' = 'avro-debezium-registry'
      ...
    )

Properties

  * Flink detects the Debezium format automatically, based on the schema structure with `after`, `before`, and `op` fields.

  * The table schema is inferred from the `after` schema, exposing only the actual data fields.

  * **Automatic Debezium Envelope Detection** : For schemas created after May 19, 2025 at 09:00 UTC, Flink automatically detects Debezium envelopes and sets appropriate defaults:

    * `value.format` defaults to `*-debezium-registry` (instead of `*-registry`)
    * `changelog.mode` defaults to `retract` (instead of `append`)
    * Exception: If Kafka `cleanup.policy` is `compact`, `changelog.mode` is set to `upsert`
  * The default `changelog.mode` is `retract`, which properly handles all CDC operations, including inserts, updates, and deletes.

  * You can manually override the changelog mode if necessary:
        
        -- Change to upsert mode for primary key-based operations
        ALTER TABLE customer_changes SET ('changelog.mode' = 'upsert');
        
        -- Change to append mode (processes only inserts and updates)
        ALTER TABLE customer_changes SET ('changelog.mode' = 'append');

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

You can use the ALTER TABLE statement to evolve schemas for inferred tables.

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

  * Because Confluent Cloud for Apache Flink advertises [FULL_TRANSITIVE mode](../../sr/fundamentals/schema-evolution.html#sr-compatibility-types), queries still work, and the physical column is set to NULL in the payload:
        
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

You can use ALTER TABLE with the [error-handling.mode](statements/create-table.html#flink-sql-create-table-with-error-handling-mode) and [error-handling.log.target](statements/create-table.html#flink-sql-create-table-with-error-handling-log-target) table properties to set custom error handling for deserialization errors.

The following code example shows how to log errors to the specified Dead Letter Queue (DLQ) table and enable processing to continue.

     ALTER TABLE my_table SET (
      'error-handling.mode' = 'log',
      'error-handling.log.target' = 'my_error_table'
    );

## Related content¶

  * Video: [How to Set Idle Timeouts](https://www.youtube.com/watch?v=YSIhM5-Sykw)

## SELECT examples¶

The following examples show frequently used scenarios for SELECT.

### Most minimal statement¶

Syntax

    SELECT 1;

Properties

  * Statement is bounded

### Check local time zone is configured correctly¶

Syntax

    SELECT NOW();

Properties

  * Statement is bounded
  * NOW() returns a TIMSTAMP_LTZ(3), so if the client is configured correctly, it should show a timestamp in your local time zone.

### Combine multiple tables into one¶

Syntax

    CREATE TABLE t_union_1 (i INT);
    CREATE TABLE t_union_2 (i INT);
    TABLE t_union_1 UNION ALL TABLE t_union_2;
    
    -- alternate syntax
    SELECT * FROM t_union_1
    UNION ALL
    SELECT * FROM t_union_2;

### Get insights into the current watermark¶

Syntax

    CREATE TABLE t_watermarked_insight (s STRING) DISTRIBUTED INTO 1 BUCKETS;
    
    INSERT INTO t_watermarked_insight VALUES ('Bob'), ('Alice'), ('Charly');
    
    SELECT $rowtime, CURRENT_WATERMARK($rowtime) FROM t_watermarked_insight;

The output resembles:

    $rowtime                EXPR$1
    2024-04-29 11:59:01.080 NULL
    2024-04-29 11:59:01.093 2024-04-04 15:27:37.433
    2024-04-29 11:59:01.094 2024-04-04 15:27:37.433

Properties

  * The CURRENT_WATERMARK function returns the watermark that arrived at the operator evaluating the SELECT statement.
  * The returned watermark is the minimum of all inputs, across all tables/topics and their partitions.
  * If a common watermark was not received from all inputs, the function returns NULL.
  * The CURRENT_WATERMARK function takes a [time attribute](../concepts/timely-stream-processing.html#flink-sql-time-attributes), which is a column that has WATERMARK FOR defined.

A watermark is always emitted after the row has been processed, so the first row always has a NULL watermark.

Because the default watermark algorithm requires at least 250 records, initially it assumes the maximum lag of 7 days plus a safety margin of 7 days.

The watermark quickly (exponentially) goes down as more data arrives.

Sources emit watermarks every 200 ms, but within the first 200 ms they emit per row for powering examples like this.

### Flatten fields into columns¶

Syntax

    CREATE TABLE t_flattening (i INT, r1 ROW<i INT, s STRING>, r2 ROW<other INT>);
    
    SELECT r1.*, r2.* FROM t_flattening;

Properties
    You can apply the `*` operator on nested data, which enables flattening fields into columns of the table.

## Schema reference examples¶

The following examples show how to use schema references in Flink SQL.

For the following schemas in Schema Registry:

AvroProtobufJSON

    {
       "type":"record",
       "namespace": "io.confluent.developer.avro",
       "name":"Purchase",
       "fields": [
          {"name": "item", "type":"string"},
          {"name": "amount", "type": "double"},
          {"name": "customer_id", "type": "string"}
       ]
    }

    syntax = "proto3";
    
    package io.confluent.developer.proto;
    
    message Purchase {
       string item = 1;
       double amount = 2;
       string customer_id = 3;
    }

    {
       "$schema": "http://json-schema.org/draft-07/schema#",
       "title": "Purchase",
       "type": "object",
       "properties": {
          "item": {
             "type": "string"
          },
          "amount": {
             "type": "number"
          },
          "customer_id": {
             "type": "string"
          }
       },
       "required": ["item", "amount", "customer_id"]
    }

AvroProtobufJSON

    {
       "type":"record",
       "namespace": "io.confluent.developer.avro",
       "name":"Pageview",
       "fields": [
          {"name": "url", "type":"string"},
          {"name": "is_special", "type": "boolean"},
          {"name": "customer_id", "type":  "string"}
       ]
    }

    syntax = "proto3";
    
    package io.confluent.developer.proto;
    
    message Pageview {
       string url = 1;
       bool is_special = 2;
       string customer_id = 3;
    }

    {
       "$schema": "http://json-schema.org/draft-07/schema#",
       "title": "Pageview",
       "type": "object",
       "properties": {
          "url": {
             "type": "string"
          },
          "is_special": {
             "type": "boolean"
          },
          "customer_id": {
             "type": "string"
          }
       },
       "required": ["url", "is_special", "customer_id"]
    }

AvroProtobufJSON

    [
       "io.confluent.developer.avro.Purchase",
       "io.confluent.developer.avro.Pageview"
    ]

    syntax = "proto3";
    
    package io.confluent.developer.proto;
    
    import "purchase.proto";
    import "pageview.proto";
    
    message CustomerEvent {
       oneof action {
          Purchase purchase = 1;
          Pageview pageview = 2;
       }
    }

    {
       "$schema": "http://json-schema.org/draft-07/schema#",
       "title": "CustomerEvent",
       "type": "object",
       "oneOf": [
          { "$ref": "io.confluent.developer.json.Purchase" },
          { "$ref": "io.confluent.developer.json.Pageview" }
       ]
    }

and references:

AvroProtobufJSON

    [
       {
          "name": "io.confluent.developer.avro.Purchase",
          "subject": "purchase",
          "version": 1
       },
       {
          "name": "io.confluent.developer.avro.Pageview",
          "subject": "pageview",
          "version": 1
       }
    ]

    [
       {
          "name": "purchase.proto",
          "subject": "purchase",
          "version": 1
       },
       {
          "name": "pageview.proto",
          "subject": "pageview",
          "version": 1
       }
    ]

    [
       {
          "name": "io.confluent.developer.json.Purchase",
          "subject": "purchase",
          "version": 1
       },
       {
          "name": "io.confluent.developer.json.Pageview",
          "subject": "pageview",
          "version": 1
       }
    ]

`SHOW CREATE TABLE customer-events;` returns the following output:

    CREATE TABLE `customer-events` (
      `key` VARBINARY(2147483647),
      `Purchase` ROW<`item` VARCHAR(2147483647) NOT NULL, `amount` DOUBLE NOT NULL, `customer_id` VARCHAR(2147483647) NOT NULL>,
      `Pageview` ROW<`url` VARCHAR(2147483647) NOT NULL, `is_special` BOOLEAN NOT NULL, `customer_id` VARCHAR(2147483647) NOT NULL>
    )
    DISTRIBUTED BY HASH(`key`) INTO 2 BUCKETS
    WITH (
      'changelog.mode' = 'append',
      'connector' = 'confluent',
      'kafka.cleanup-policy' = 'delete',
      'kafka.max-message-size' = '2097164 bytes',
      'kafka.retention.size' = '0 bytes',
      'kafka.retention.time' = '7 d',
      'key.format' = 'raw',
      'scan.bounded.mode' = 'unbounded',
      'scan.startup.mode' = 'earliest-offset',
      'value.format' = '[VALUE_FORMAT]'
    )

### Split into tables for each type¶

**Syntax**

    CREATE TABLE purchase AS
       SELECT Purchase.* FROM `customer-events`
       WHERE Purchase IS NOT NULL;
    
    SELECT * FROM purchase;

    CREATE TABLE pageview AS
       SELECT Pageview.* FROM `customer-events`
       WHERE Pageview IS NOT NULL;
    
    SELECT * FROM pageview;

Output:

item | amount | customer_id  
---|---|---  
apple | 9.99 | u-21  
jam | 4.29 | u-67  
mango | 13.99 | u-67  
socks | 7.99 | u-123  
url | is_special | customer_id  
---|---|---  
<https://www.confluent.io> | TRUE | u-67  
<http://www.cflt.io> | FALSE | u-12  
  
## Related content¶

  * [Flink SQL Queries](queries/overview.html#flink-sql-queries)
  * [Flink SQL Functions](functions/overview.html#flink-sql-functions-overview)
  * [DDL Statements in Confluent Cloud for Apache Flink](statements/overview.html#flink-sql-statements-overview)

Note

This website includes content developed at the [Apache Software Foundation](https://www.apache.org/) under the terms of the [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0.html).
