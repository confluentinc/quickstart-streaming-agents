---
document_id: flink_reference_statements_create-table_chunk_2
source_file: flink_reference_statements_create-table.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-table.html
title: SQL CREATE TABLE Statement in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 14
---

`active` BOOLEAN, `created_at` TIMESTAMP_LTZ(3) );

## Metadata columns¶

You can access the following table metadata as metadata columns in a table definition.

  * Available metadata
  * leader-epoch
  * offset
  * partition
  * raw-key
  * raw-value
  * timestamp
  * timestamp-type
  * topic

Use the METADATA keyword to declare a metadata column.

Metadata fields are readable or readable/writable. Read-only columns must be declared VIRTUAL to exclude them during INSERT INTO operations.

Metadata columns are not registered in Schema Registry.

Example

The following CREATE TABLE statement shows the syntax for exposing metadata fields.

    CREATE TABLE t (
      `user_id` BIGINT,
      `item_id` BIGINT,
      `behavior` STRING,
      `event_time` TIMESTAMP_LTZ(3) METADATA FROM 'timestamp',
      `partition` BIGINT METADATA VIRTUAL,
      `offset` BIGINT METADATA VIRTUAL
    );

### Available metadata¶

#### headers¶

  * Type: MAP NOT NULL
  * Access: readable/writable

Headers of the Kafka record as a map of raw bytes.

#### leader-epoch¶

  * Type: INT NULL
  * Access: readable

Leader epoch of the Kafka record, if available.

#### offset¶

  * Type: BIGINT NOT NULL
  * Access: readable

Offset of the Kafka record in the partition.

#### partition¶

  * Type: INT NOT NULL
  * Access: readable

Partition ID of the Kafka record.

#### raw-key¶

  * Type: BYTES NOT NULL
  * Access: readable

The unique identifier or key of the Kafka record as raw bytes. The type may vary based on the serializer used, for example, STRING for `StringSerializer`.

#### raw-value¶

  * Type: BYTES NOT NULL
  * Access: readable

The actual message content or payload of the Kafka record as raw bytes. Contains the main data being transmitted. The type may vary based on the serializer used, for example, STRING for `StringSerializer`.

#### timestamp¶

  * Type: TIMESTAMP_LTZ(3) NOT NULL
  * Access: readable/writable

Timestamp of the Kafka record.

With `timestamp`, you can pass [event time](../../concepts/timely-stream-processing.html#flink-sql-event-time-and-watermarks) end-to-end. Otherwise, the sink uses the ingestion time by default.

#### timestamp-type¶

  * Type: STRING NOT NULL
  * Access: readable

Timestamp type of the Kafka record.

Valid values are:

  * “NoTimestampType”
  * “CreateTime” (also set when writing metadata)
  * “LogAppendTime”

#### topic¶

  * Type: STRING NOT NULL
  * Access: readable

Topic name of the Kafka record.

## Computed columns¶

Computed columns are virtual columns that are not stored in the table but are computed on the fly based on the values of other columns. These virtual columns are not registered in Schema Registry.

A computed column is defined by using an expression that references one or more physical or metadata columns in the table. The expression can use arithmetic [operators](../functions/comparison-functions.html#flink-sql-comparison-and-equality-functions), [functions](../functions/overview.html#flink-sql-functions-overview), and other SQL constructs to manipulate the values of the physical and metadata columns and compute the value of the computed column.

Example

The following CREATE TABLE statement shows the syntax for declaring a `full_name` computed column by concatenating a `first_name` column and a `last_name` column.

    CREATE TABLE t (
      `id` BIGINT,
      `first_name` STRING,
      `last_name` STRING,
      `full_name` AS CONCAT(first_name, ' ', last_name)
    );

## Vector database columns¶

Confluent Cloud for Apache Flink supports read-only external tables to enable search with federated query execution on external vector databases, like MongoDB, Pinecone, and ElasticSearch.

Note

Vector Search is an Open Preview feature in Confluent Cloud.

A Preview feature is a Confluent Cloud component that is being introduced to gain early feedback from developers. Preview features can be used for evaluation and non-production testing purposes or to provide feedback to Confluent. The warranty, SLA, and Support Services provisions of your agreement with Confluent do not apply to Preview features. Confluent may discontinue providing preview releases of the Preview features at any time in Confluent’s’ sole discretion.

For more information, see [Vector Search](../../../ai/external-tables/vector-search.html#flink-sql-vector-search).
