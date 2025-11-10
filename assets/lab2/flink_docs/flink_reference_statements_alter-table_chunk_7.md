---
document_id: flink_reference_statements_alter-table_chunk_7
source_file: flink_reference_statements_alter-table.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/alter-table.html
title: SQL ALTER TABLE Statement in Confluent Cloud for Apache Flink
chunk_index: 7
total_chunks: 7
---

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

You can use ALTER TABLE with the [error-handling.mode](create-table.html#flink-sql-create-table-with-error-handling-mode) and [error-handling.log.target](create-table.html#flink-sql-create-table-with-error-handling-log-target) table properties to set custom error handling for deserialization errors.

The following code example shows how to log errors to the specified Dead Letter Queue (DLQ) table and enable processing to continue.

     ALTER TABLE my_table SET (
      'error-handling.mode' = 'log',
      'error-handling.log.target' = 'my_error_table'
    );
