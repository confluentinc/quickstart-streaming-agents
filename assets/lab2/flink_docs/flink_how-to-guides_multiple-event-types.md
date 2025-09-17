---
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/multiple-event-types.html
title: Handle Multiple Event Types In Tables in Confluent Cloud for Apache Flink
hierarchy: ['how-to-guides', 'multiple-event-types.html']
scraped_date: 2025-09-05T13:47:39.616083
---

# Handle Multiple Event Types with Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides several ways to work with Kafka topics containing multiple event types. This guide explains how Flink automatically infers and handles different event type patterns, allowing you to query and process mixed event streams effectively.

## Overview¶

When working with Kafka topics containing multiple event types, Flink [automatically](../reference/serialization.html#flink-sql-serialization) infers table schemas based on the Schema Registry configuration and schema format. The following sections describe the supported approaches in order of recommendation.

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

## Using Union Types¶

Flink automatically handles union types across different schema formats. With this approach, all event types are defined within a single schema using the format’s native union type mechanism:

  * Avro unions
  * JSON Schema oneOf
  * Protocol Buffer oneOf

For example, consider a schema combining order and shipment events:

AvroJSON SchemaProtobuf

    {
       "type": "record",
       "namespace": "io.confluent.examples.avro",
       "name": "AllTypes",
       "fields": [
          {
             "name": "event_type",
             "type": [
                {
                   "type": "record",
                   "name": "Order",
                   "fields": [
                      {"name": "order_id", "type": "string"},
                      {"name": "amount", "type": "double"}
                   ]
                },
                {
                   "type": "record",
                   "name": "Shipment",
                   "fields": [
                      {"name": "tracking_id", "type": "string"},
                      {"name": "status", "type": "string"}
                   ]
                }
             ]
          }
       ]
    }

    {
       "$schema": "http://json-schema.org/draft-07/schema#",
       "title": "AllTypes",
       "type": "object",
       "oneOf": [
          {
             "type": "object",
             "title": "Order",
             "properties": {
                "order_id": { "type": "string" },
                "amount": { "type": "number" }
             },
             "required": ["order_id", "amount"]
          },
          {
             "type": "object",
             "title": "Shipment",
             "properties": {
                "tracking_id": { "type": "string" },
                "status": { "type": "string" }
             },
             "required": ["tracking_id", "status"]
          }
       ]
    }

    syntax = "proto3";
    
    package io.confluent.examples.proto;
    
    message Order {
       string order_id = 1;
       double amount = 2;
    }
    
    message Shipment {
       string tracking_id = 1;
       string status = 2;
    }
    
    message AllTypes {
       oneof event_type {
          Order order = 1;
          Shipment shipment = 2;
       }
    }

When using these union types with TopicNameStrategy, Flink automatically creates a table structure based on your schema format. You can see this structure using:

    SHOW CREATE TABLE `events`;

The output shows a table structure that reflects how each format handles unions:

AvroJSON SchemaProtobuf

    CREATE TABLE `events` (
      `key` VARBINARY(2147483647),
      `event_type` ROW
        `Order` ROW<`order_id` VARCHAR(2147483647) NOT NULL, `amount` DOUBLE NOT NULL>,
        `Shipment` ROW<`tracking_id` VARCHAR(2147483647) NOT NULL, `status` VARCHAR(2147483647) NOT NULL>
      > NOT NULL
    )

You can query specific event types:

    -- Query orders
    SELECT event_type.Order.* FROM `events` WHERE event_type.Order IS NOT NULL;
    
    -- Query shipments
    SELECT event_type.Shipment.* FROM `events` WHERE event_type.Shipment IS NOT NULL;

    CREATE TABLE `events` (
      `key` VARBINARY(2147483647),
      `connect_union_field_0` ROW<`amount` DOUBLE NOT NULL, `order_id` VARCHAR(2147483647) NOT NULL>,
      `connect_union_field_1` ROW<`status` VARCHAR(2147483647) NOT NULL, `tracking_id` VARCHAR(2147483647) NOT NULL>
    )

You can query specific event types:

    -- Query orders
    SELECT connect_union_field_0.* FROM `events` WHERE connect_union_field_0 IS NOT NULL;
    
    -- Query shipments
    SELECT connect_union_field_1.* FROM `events` WHERE connect_union_field_1 IS NOT NULL;

    CREATE TABLE `events` (
      `key` VARBINARY(2147483647),
      `AllTypes` ROW
        `event_type` ROW
          `order` ROW<`order_id` VARCHAR(2147483647) NOT NULL, `amount` DOUBLE NOT NULL>,
          `shipment` ROW<`tracking_id` VARCHAR(2147483647) NOT NULL, `status` VARCHAR(2147483647) NOT NULL>
        >
      >
    )

You can query specific event types:

    -- Query orders
    SELECT AllTypes.event_type.order.* FROM `events` WHERE AllTypes.event_type.order IS NOT NULL;
    
    -- Query shipments
    SELECT AllTypes.event_type.shipment.* FROM `events` WHERE AllTypes.event_type.shipment IS NOT NULL;

## Using RecordNameStrategy Or TopicRecordNameStrategy Strategies¶

For topics using RecordNameStrategy or TopicRecordNameStrategy, Flink initially infers a raw binary table:

    CREATE TABLE `events` (
      `key` VARBINARY(2147483647),
      `value` VARBINARY(2147483647)
    )

To work with these events, you need to manually configure the table with the appropriate subject names:

    ALTER TABLE events SET (
      'value.format' = 'avro-registry',
      'value.avro-registry.subject-names' = 'com.example.events.OrderEvent;com.example.events.ShipmentEvent'
    );

If your topic uses keyed messages, you may also need to configure the key format:

    ALTER TABLE events SET (
      'key.format' = 'avro-registry',
      'key.avro-registry.subject-names' = 'com.example.events.OrderKey'
    );

Replace `avro-registry` with `json-registry` or `proto-registry` based on your schema format.

## Best Practices¶

  1. Use schema references with TopicNameStrategy when possible, as this provides the best balance of flexibility and manageability.
  2. If schema references aren’t suitable, use union types for a simpler schema management approach.
  3. Configure alternative subject name strategies only when working with existing systems that require them.

## Related Content¶

  * [Schema References](../../sr/fundamentals/serdes-develop/index.html#referenced-schemas)
  * [Flink SQL Data Type Mappings](../reference/serialization.html#flink-sql-serialization)
  * [Subject Name Strategy](../../sr/fundamentals/serdes-develop/index.html#sr-schemas-subject-name-strategy)

Note

This website includes content developed at the [Apache Software Foundation](https://www.apache.org/) under the terms of the [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0.html).
