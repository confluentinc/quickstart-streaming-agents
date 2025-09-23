---
document_id: flink_reference_serialization_chunk_5
source_file: flink_reference_serialization.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/serialization.html
title: Data Type Mappings with Flink SQL Statements in Confluent Cloud for Apache Flink
chunk_index: 5
total_chunks: 8
---

#### MULTISET[VARCHAR]¶

* JSON Schema type: `Object`

* Additional properties:

  * `connect.type=map`
  * `flink.type=multiset`
* JSON type title: The count (value) in the JSON schema must map to a Flink INT type. For MULTISET types, the count (value) in the JSON schema must map to a Flink INT type, which corresponds to `connect.type: int32` in the JSON Schema. Using `connect.type: int64` causes a validation error.

* Example:

        {
          "type": "object",
          "connect.type": "map",
          "flink.type": "multiset",
          "additionalProperties": {
            "type": "number",
            "connect.type": "int32"
          }
        }

#### ROW¶

* JSON Schema type: `Object`
* Additional properties: –
* JSON type title: –
* Example: –

#### SMALLINT¶

* JSON Schema type: `Number`

* Additional properties: `connect.type=int16`

* JSON type title: –

* Example:

        {
          "type": "number",
          "connect.type": "int16"
        }

#### TIME¶

* JSON Schema type: `Number`

* Additional properties:

  * `connect.type=int32`
  * `flink.precision`
* JSON type title: `org.apache.kafka.connect.data.Time`

* Example:

        {
          "type":"number",
          "title":"org.apache.kafka.connect.data.Time",
          "flink.precision":2,
          "connect.type":"int32",
          "flink.version":"1"
        }

#### TIMESTAMP¶

* JSON Schema type: `Number`

* Additional properties:

  * `connect.type=int64`
  * `flink.precision`
  * `flink.type=timestamp`
* JSON type title: `org.apache.kafka.connect.data.Timestamp`

* Example:

        {
          "type":"number",
          "title":"org.apache.kafka.connect.data.Timestamp",
          "flink.precision":2,
          "flink.type":"timestamp",
          "connect.type":"int64",
          "flink.version":"1"
        }

#### TIMESTAMP_LTZ¶

* JSON Schema type: `Number`

* Additional properties:

  * `connect.type=int64`
  * `flink.precision`
* JSON type title: `org.apache.kafka.connect.data.Timestamp`

* Example:

        {
          "type":"number",
          "title":"org.apache.kafka.connect.data.Timestamp",
          "flink.precision":2,
          "connect.type":"int64",
          "flink.version":"1"
        }

#### TINYINT¶

* JSON Schema type: `Number`

* Additional properties: `connect.type=int8`

* JSON type title: –

* Example:

        {
          "type": "number",
          "connect.type": "int8"
        }

#### VARBINARY¶

* JSON Schema type: `String`

* Additional properties:

  * `connect.type=bytes`
  * `flink.maxLength`: Different from JSON’s `maxLength`, because this property describes bytes length, not string length.
* JSON type title: –

* Example:

        {
          "type": "string",
          "flink.maxLength": 123,
          "flink.version": "1",
          "connect.type": "bytes"
        }

#### VARCHAR¶

* JSON Schema type: `String`

* Additional properties: `maxLength`

* JSON type title: –

* Example:

        {
          "type": "string",
          "maxLength": 123
        }

### JSON types to Flink SQL types¶

The following table shows the mapping of JSON types to Flink SQL types. It shows only mappings that are not covered by the previous table. These types can’t originate from Flink SQL.

This mapping is important when consuming/reading records with a schema that was created outside of Flink. The mapping defines the Flink table’s schema [inferred](statements/show.html#flink-sql-show-inferred-tables) from JSON Schema.

JSON type | Flink SQL type
---|---
Combined | ROW
Enum | VARCHAR
Number(requiresInteger=true) | BIGINT
Number(requiresInteger=false) | DOUBLE
