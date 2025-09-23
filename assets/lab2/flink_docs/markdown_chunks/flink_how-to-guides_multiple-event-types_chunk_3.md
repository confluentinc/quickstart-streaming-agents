---
document_id: flink_how-to-guides_multiple-event-types_chunk_3
source_file: flink_how-to-guides_multiple-event-types.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/multiple-event-types.html
title: Handle Multiple Event Types In Tables in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 4
---

WHERE action.pageview IS NOT NULL;

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
