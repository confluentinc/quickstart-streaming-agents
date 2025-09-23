---
document_id: flink_reference_statements_create-table_chunk_11
source_file: flink_reference_statements_create-table.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-table.html
title: SQL CREATE TABLE Statement in Confluent Cloud for Apache Flink
chunk_index: 11
total_chunks: 14
---

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
             `url` VARCHAR(2147483647) NOT
