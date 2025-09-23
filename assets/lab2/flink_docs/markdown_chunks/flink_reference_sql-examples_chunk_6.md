---
document_id: flink_reference_sql-examples_chunk_6
source_file: flink_reference_sql-examples.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/sql-examples.html
title: Flink SQL Examples in Confluent Cloud for Apache Flink
chunk_index: 6
total_chunks: 12
---

NULL,
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
