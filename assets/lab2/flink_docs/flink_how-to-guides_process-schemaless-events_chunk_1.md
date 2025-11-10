---
document_id: flink_how-to-guides_process-schemaless-events_chunk_1
source_file: flink_how-to-guides_process-schemaless-events.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/process-schemaless-events.html
title: Process schemaless events with Flink SQL in Confluent Cloud
chunk_index: 1
total_chunks: 1
---

# Process Schemaless Events with Confluent Cloud for Apache Flink¶

This guide explains how use Confluent Cloud for Apache Flink to handle and process events in Apache Kafka® topics that don’t use serializers that are compatible with Schema Registry, while still leveraging Schema Registry for data processing with Flink SQL.

## Overview¶

When working with Kafka topics containing events that aren’t serialized with Schema Registry-compatible serializers, you can still use Flink SQL to process your data. This approach enables you to handle “schemaless” events by defining a schema separately in Schema Registry.

## Prerequisites¶

* Access to Confluent Cloud
* A Kafka topic containing events you want to process
* Appropriate permissions to access Schema Registry in Confluent Cloud

## Step 1: Submit your schema to Schema Registry¶

  1. Log in to the Confluent Cloud Console.

  2. Navigate to the **Topics Overview** page.

  3. Locate your topic and click it to open the topic details page.

  4. Click **Set a schema**.

  5. Submit your schema in Avro, Protobuf, or JSON format.

Note: With JSON you can define a partial schema, which means that not all fields that can exist in the payload need to be defined in the schema at first. Flink ignores fields that aren’t defined. Also, the order of these fields doesn’t matter for JSON.

This differs from Avro and Protobuf, where you must define all fields in the right order. In case some fields don’t appear in every event, you can mark these fields as optional.

The following example schemas show how sensor data might be represented in full JSON, partial JSON, Avro, and Protobuf formats.

Full JSONPartial JSONAvroProtobuf

         {
           "$schema": "http://json-schema.org/draft-07/schema#",
           "additionalProperties": false,
           "properties": {
             "humidity": {
               "description": "The humidity reading as a percentage",
               "type": "number"
             },
               "id": {
               "description": "The unique identifier for the event",
               "type": "string"
             },
               "temperature": {
               "description": "The temperature reading in Celsius",
               "type": "number"
             },
               "timestamp": {
               "description": "The timestamp of the event in milliseconds since the epoch",
               "type": "integer"
             }
           },
           "required": [
             "id"
           ],
           "title": "DynamicEvent",
           "type": "object"
         }

         {
           "$schema": "http://json-schema.org/draft-07/schema#",
           "additionalProperties": false,
           "properties": {
             "id": {
               "description": "The unique identifier for the event",
               "type": "string"
             }
           },
           "required": [
             "id"
           ],
           "title": "DynamicEvent",
           "type": "object"
         }

         {
           "fields": [
             {
               "name": "id",
               "type": "string"
             },
             {
               "default": null,
               "name": "timestamp",
               "type": [
                 "null",
                 "long"
               ]
             },
             {
               "default": null,
               "name": "temperature",
               "type": [
                 "null",
                 "float"
               ]
             },
             {
               "default": null,
               "name": "humidity",
               "type": [
                 "null",
                 "float"
               ]
             }
           ],
           "name": "DynamicEvent",
           "type": "record"
         }

         syntax = "proto3";
         package example;

         message DynamicEvent {
           string id = 1;
           optional int64 timestamp = 2;
           optional float temperature = 3;
           optional float humidity = 4;
         }

## Step 2: Query your table¶

Once you’ve submitted the schema, you can start querying your topic immediately by using Flink SQL. The defined schema is used to interpret the data, even if the events themselves don’t contain schema information. Flink first tries to deserialize as if the data was serialized with Schema Registry serializers, and otherwise treats the incoming bytes as Avro, Protobuf, or JSON.

as Avro, Protobuf, or JSON.

## Important considerations¶

When possible, you should always use the Schema Registry serializers, to gain the benefits of properly governing your data streams.

This method works even if your events don’t include schema version information in their byte stream.

You can submit a partial schema only for JSON. Flink will process the defined fields and ignore the rest.

With this approach, automatic schema evolution within the stream is not supported. If you want to evolve the schema, you must manually evolve the it and consider the impact as described in [Schema Evolution and Compatibility for Schema Registry on Confluent Cloud](../../sr/fundamentals/schema-evolution.html#schema-evolution-and-compatibility).
