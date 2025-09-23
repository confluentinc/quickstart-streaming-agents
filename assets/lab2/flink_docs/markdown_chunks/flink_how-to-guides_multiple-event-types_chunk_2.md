---
document_id: flink_how-to-guides_multiple-event-types_chunk_2
source_file: flink_how-to-guides_multiple-event-types.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/multiple-event-types.html
title: Handle Multiple Event Types In Tables in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 4
---

approaches in order of recommendation.

## Using Schema References¶

Schema references provide the most robust way to handle multiple event types in a single topic. With this approach, you define a main schema that references other schemas, allowing for modular schema management and independent evolution of event types.

For example, consider a topic that combines purchase and pageview events.

  1. Schema for **purchase** events.

AvroJSON SchemaProtobuf

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

         syntax = "proto3";

         package io.confluent.developer.proto;

         message Purchase {
            string item = 1;
            double amount = 2;
            string customer_id = 3;
         }

  2. Schema for **pageview** events.

AvroJSON SchemaProtobuf

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

         syntax = "proto3";

         package io.confluent.developer.proto;

         message Pageview {
            string url = 1;
            bool is_special = 2;
            string customer_id = 3;
         }

  3. Combined schema that references both event types:

AvroJSON SchemaProtobuf

         [
            "io.confluent.developer.avro.Purchase",
            "io.confluent.developer.avro.Pageview"
         ]

         {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "CustomerEvent",
            "type": "object",
            "oneOf": [
               { "$ref": "io.confluent.developer.json.Purchase" },
               { "$ref": "io.confluent.developer.json.Pageview" }
            ]
         }

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

When these schemas are registered in Schema Registry and used with the default TopicNameStrategy, Flink automatically infers the table structure. You can see this structure using:

    SHOW CREATE TABLE `customer-events`;

Your output will show a table structure that includes columns for both event types:

AvroJSON SchemaProtobuf

    CREATE TABLE `customer-events` (
      `key` VARBINARY(2147483647),
      `Purchase` ROW<`item` VARCHAR(2147483647), `amount` DOUBLE, `customer_id` VARCHAR(2147483647)>,
      `Pageview` ROW<`url` VARCHAR(2147483647), `is_special` BOOLEAN, `customer_id` VARCHAR(2147483647)>
    )

    CREATE TABLE `customer-events` (
      `key` VARBINARY(2147483647),
      `connect_union_field_0` ROW<`amount` DOUBLE NOT NULL, `customer_id` VARCHAR(2147483647) NOT NULL, `item` VARCHAR(2147483647) NOT NULL>,
      `connect_union_field_1` ROW<`customer_id` VARCHAR(2147483647) NOT NULL, `is_special` BOOLEAN NOT NULL, `url` VARCHAR(2147483647) NOT NULL>
    )

    CREATE TABLE `customer-events` (
      `key` VARBINARY(2147483647),
      `action` ROW
        `purchase` ROW<`item` VARCHAR(2147483647) NOT NULL, `amount` DOUBLE NOT NULL, `customer_id` VARCHAR(2147483647) NOT NULL>,
        `pageview` ROW<`url` VARCHAR(2147483647) NOT NULL, `is_special` BOOLEAN NOT NULL, `customer_id` VARCHAR(2147483647) NOT NULL>
      >
    )

You can query specific event types using standard SQL. The exact syntax depends on your schema format:

AvroJSON SchemaProtobuf

    -- Query purchase events
    SELECT Purchase.* FROM `customer-events` WHERE Purchase IS NOT NULL;

    -- Query pageview events
    SELECT Pageview.* FROM `customer-events` WHERE Pageview IS NOT NULL;

    -- Query purchase events
    SELECT connect_union_field_0.* FROM `customer-events` WHERE connect_union_field_0 IS NOT NULL;

    -- Query pageview events
    SELECT connect_union_field_1.* FROM `customer-events` WHERE connect_union_field_1 IS NOT NULL;

    -- Query purchase events
    SELECT action.purchase.* FROM `customer-events` WHERE action.purchase IS NOT NULL;

    -- Query pageview events
    SELECT action.pageview.* FROM `customer-events` WHERE action.pageview IS NOT NULL;
