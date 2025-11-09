---
document_id: flink_reference_statements_create-table_chunk_9
source_file: flink_reference_statements_create-table.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-table.html
title: SQL CREATE TABLE Statement in Confluent Cloud for Apache Flink
chunk_index: 9
total_chunks: 14
---

### scan.bounded.mode¶

  * Type: Enum
  * Default: `unbounded`

Specify the bounded mode for the Kafka consumer.

    scan.bounded.mode = [latest-offset | timestamp | unbounded]

The following list shows the valid bounded mode values.

  * `latest-offset`: bounded by latest offsets. This is evaluated at the start of consumption from a given partition.
  * `timestamp`: bounded by a user-supplied timestamp.
  * `unbounded`: table is unbounded.

If `scan.bounded.mode` isn’t set, the default is an unbounded table. For more information, see [Bounded and unbounded tables](../../concepts/overview.html#flink-sql-stream-processing-concepts-bounded-and-unbounded-tables).

If `timestamp` is specified, the scan.bounded.timestamp-millis config option is required to specify a specific bounded timestamp in milliseconds since the Unix epoch, `January 1, 1970 00:00:00.000 GMT`.

### scan.bounded.timestamp-millis¶

  * Type: Long
  * Default: (none)

End at the specified epoch timestamp (milliseconds) when the `timestamp` bounded mode is set in the scan.bounded.mode property.

    'scan.bounded.mode' = 'timestamp',
    'scan.bounded.timestamp-millis' = '<long-value>'

### scan.startup.mode¶

  * Type: Enum
  * Default: `earliest-offset`

The startup mode for Kafka consumers.

    'scan.startup.mode' = '<startup-mode>'

The following list shows the valid startup mode values.

  * `earliest-offset`: start from the earliest offset possible.
  * `latest-offset`: start from the latest offset.
  * `timestamp`: start from the user-supplied timestamp for each partition.

The default is `earliest-offset`. This differs from the default in Apache Flink, which is `group-offsets`.

If `timestamp` is specified, the scan.startup.timestamp-millis config option is required, to define a specific startup timestamp in milliseconds since the Unix epoch, January 1, 1970 00:00:00.000 GMT.

### scan.startup.timestamp-millis¶

  * Type: Long
  * Default: (none)

Start from the specified Unix epoch timestamp (milliseconds) when the `timestamp` mode is set in the scan.startup.mode property.

    'scan.startup.mode' = 'timestamp',
    'scan.startup.timestamp-millis' = '<long-value>'

### value.fields-include¶

  * Type: Enum
  * Default: `except-key`

Specify a strategy for handling key columns in the data type of the value format.

    'value.fields-include' = [all, except-key]

If `all` is specified, all physical columns of the table schema are included in the value format, which means that key columns appear in the data type for both the key and value format.

### value.format¶

  * Type: String
  * Default: “avro-registry”

Specify the format for serializing and deserializing the value part of Kafka messages.

    'value.format' = '<format>'

These are the value formats for an inferred table:

  * `raw` (if no Schema Registry entry)
  * `avro-registry` (for Avro Schema Registry entry)
  * `json-registry` (for JSON Schema Registry entry)
  * `proto-registry` (for Protobuf Schema Registry entry)
  * `avro-debezium-registry` (for Avro Debezium Schema Registry entry)
  * `json-debezium-registry` (for JSON Debezium Schema Registry entry)
  * `proto-debezium-registry` (for Protobuf Debezium Schema Registry entry)

These are the value formats for a manually created table:

  * `avro-registry` (for Avro Schema Registry entry)
  * `json-registry` (for JSON Schema Registry entry)
  * `proto-registry` (for Protobuf Schema Registry entry)

If no format is specified, Avro Schema Registry is used by default.

### value.format.schema-context¶

  * Type: String
  * Default: (none)

Specify the Confluent Schema Registry Schema Context for the value format.

    'value.<format>.schema-context' = '<schema-context>'

A schema context represents an independent scope in Schema Registry and can be used to create separate “sub-registries” within one Schema Registry. Each schema context is an independent grouping of schema IDs and subject names, enabling the same schema ID in different contexts to represent completely different schemas.
