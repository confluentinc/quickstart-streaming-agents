---
document_id: flink_how-to-guides_multiple-event-types_chunk_4
source_file: flink_how-to-guides_multiple-event-types.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/multiple-event-types.html
title: Handle Multiple Event Types In Tables in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 4
---

WHERE AllTypes.event_type.shipment IS NOT NULL;

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
