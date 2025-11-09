---
document_id: flink_reference_statements_create-table_chunk_8
source_file: flink_reference_statements_create-table.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-table.html
title: SQL CREATE TABLE Statement in Confluent Cloud for Apache Flink
chunk_index: 8
total_chunks: 14
---

* `fail`: Flink fails the statement.
  * `ignore`: Flink ignores the error and continues processing with the next row.
  * `log`: Flink sends the poison pill to the DLQ table and continues processing with the next row.

All Flink tables receive the `error-handling.mode` setting. If you don’t specify a value, the default is `fail`. You can override the setting for an existing table by using the [ALTER TABLE](alter-table.html#flink-sql-alter-table) statement. Only table-level overrides are supported. Per-statement overrides are not supported.

The following limitations apply:

  * Only deserialization errors at the source are supported.
  * Errors outside the source, for example, in windowed aggregations, are not handled.

### kafka.cleanup-policy¶

  * Type: enum
  * Default: `delete`

    'kafka.cleanup-policy' = [delete | compact | delete-compact]

Set the default cleanup policy for Kafka topic log segments beyond the retention window. Translates to the Kafka `log.cleanup.policy` property. For more information, see [Log Compaction](/kafka/design/log_compaction.html).

  * `compact`: topic log is compacted periodically in the background by the log cleaner.
  * `delete`: old log segments are discarded when their retention time or size limit is reached.
  * `delete-compact`: compact the log and follow the retention time or size limit settings.

### kafka.consumer.isolation-level¶

  * Type: enum
  * Default: `read-committed`

    'kafka.consumer.isolation-level' = [read-committed | read-uncommitted]

Controls which transactional messages to read:

  * `read-committed`: Only return messages from committed transactions. Any transactional messages from aborted or in-progress transactions are filtered out.
  * `read-uncommitted`: Return all messages, including those from transactional messages that were aborted or are still in progress.

For more information, see [delivery guarantees and latency](../../concepts/delivery-guarantees.html#flink-sql-delivery-guarantees-latency).

### kafka.max-message-size¶

    'kafka.max-message-size' = MemorySize

Translates to the Kafka `max.message.bytes` property.

The default is _2097164_ bytes.

### kafka.producer.compression.type¶

  * Type: enum
  * Default: `none`

    'kafka.producer.compression.type' = [none | gzip | snappy | lz4 | zstd]

Translates to the Kafka `compression.type` property.

### kafka.retention.size¶

  * Type: Integer
  * Default: _0_

    'kafka.retention.size' = MemorySize

Translates to the Kafka `log.retention.bytes` property.

### kafka.retention.time¶

  * Type: Duration
  * Default: `7 days`

    'kafka.retention.time' = '<duration>'

Translates to the Kafka `log.retention.ms` property.

### key.fields-prefix¶

  * Type: String
  * Default: “”

Specify a custom prefix for all fields of the key format.

    'key.fields-prefix' = '<prefix-string>'

The `key.fields-prefix` property defines a custom prefix for all fields of the key format, which avoids name clashes with fields of the value format.

By default, the prefix is empty. If a custom prefix is defined, the table schema property works with prefixed names.

When constructing the data type of the key format, the prefix is removed, and the non-prefixed names are used within the key format.

This option requires that the value.fields-include property is set to `EXCEPT_KEY`.

The prefix for an inferred table is `key_`, for non-atomic Schema Registry types and fields that have a name.

### key.format¶

  * Type: String
  * Default: “avro-registry”

Specify the serialization format of the table’s key fields.

    'key.format' = '<key-format>'

These are the key formats for an inferred table:

  * `raw` (if no Schema Registry entry)
  * `avro-registry` (for AVRO Schema Registry entry)
  * `json-registry` (for JSON Schema Registry entry)
  * `proto-registry` (for Protobuf Schema Registry entry)

These are the key formats for a manually created table:

  * `avro-registry` (for Avro Schema Registry entry)
  * `json-registry` (for JSON Schema Registry entry)
  * `proto-registry` (for Protobuf Schema Registry entry)

If no format is specified, Avro Schema Registry is used by default. This applies only if a primary or distribution key is defined.

The Schema Registry subject compatibility mode must be FULL or FULL_TRANSITIVE. For more information, see [Schema Evolution and Compatibility for Schema Registry on Confluent Cloud](../../../sr/fundamentals/schema-evolution.html#schema-evolution-and-compatibility).

### key.format.schema-context¶

  * Type: String
  * Default: (none)

Specify the Confluent Schema Registry Schema Context for the key format.

    'key.<format>.schema-context' = '<schema-context>'

Similar to value.format.schema-context, this option enables you to specify a schema context for the key format. It provides an independent scope in Schema Registry for key schemas.
