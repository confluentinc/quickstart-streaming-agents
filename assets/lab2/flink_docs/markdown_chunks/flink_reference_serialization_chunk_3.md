---
document_id: flink_reference_serialization_chunk_3
source_file: flink_reference_serialization.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/serialization.html
title: Data Type Mappings with Flink SQL Statements in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 8
---

* Example:

        {
          "type" : "record",
          "name" : "row",
          "namespace" : "io.confluent",
          "fields" : [ {
            "name" : "f0",
            "type" : "long",
            "doc" : "field comment"
          } ]
        }

#### SMALLINT¶

* Avro type: `int`

* Avro logical type: –

* Additional properties: `connect.type=int16`

* Example:

        {
          "type" : "int",
          "connect.type" : "int16"
        }

#### STRING / VARCHAR¶

* Avro type: `string`

* Avro logical type: –

* Additional properties: `flink.maxLength = flink.minLength` (MAX_LENGTH if not set)

* Example:

        {
          "type" : "string",
          "flink.maxLength" : 123,
          "flink.version" : "1"
        }

#### TIME¶

* Avro type: `int`

* Avro logical type: `time-millis`

* Additional properties: `flink.precision` (default: 3, max supported: 3)

* Example:

        {
          "type" : "int",
          "flink.precision" : 2,
          "flink.version" : "1",
          "logicalType" : "time-millis"
        }

#### TIMESTAMP¶

* Avro type: `long`

* Avro logical type: `local-timestamp-millis` / `local-timestamp-micros`

* Additional properties: `flink.precision` (default: 3/6, max supported: 3/9)

* Example:

        {
          "type" : "long",
          "flink.precision" : 2,
          "flink.version" : "1",
          "logicalType" : "local-timestamp-millis"
        }

#### TIMESTAMP_LTZ¶

* Avro type: `long`

* Avro logical type: `timestamp-millis` / `timestamp-micros`

* Additional properties: `flink.precision` (default: 3/6, max supported: 3/9)

* Example:

        {
          "type" : "long",
          "flink.precision" : 2,
          "flink.version" : "1",
          "logicalType" : "timestamp-millis"
        }

#### TINYINT¶

* Avro type: `int`

* Avro logical type: –

* Additional properties: `connect.type=int8`

* Example:

        {
          "type" : "int",
          "connect.type" : "int8"
        }

#### VARBINARY¶

* Avro type: `bytes`

* Avro logical type: –

* Additional properties: `flink.maxLength` (MAX_LENGTH if not set)

* Example:

        {
            "type" : "bytes",
            "flink.maxLength" : 123,
            "flink.version" : "1"
          }

### Avro types to Flink SQL types¶

The following table shows the mapping of Avro types to Flink SQL and types. It shows only mappings that are not covered by the previous table. These types can’t originate from Flink SQL.

This mapping is important when consuming/reading records with a schema that was created outside of Flink. The mapping defines the Flink table’s schema [inferred](statements/show.html#flink-sql-show-inferred-tables) from an Avro schema.

Flink SQL supports reading and writing nullable types. A nullable type is mapped to an Avro `union(avro_type, null)`, with the `avro_type` converted from the corresponding Flink type.

Avro type | Avro logical type | Flink SQL type | Example
---|---|---|---
long | time-micros | BIGINT | –
enum | – | STRING | –
union with null type (null + one other type) | – | NULLABLE(type) | –
union (other unions) | – | ROW(type_name Type0, …) |

    [
      "long",
      "string",
      {
        "type": "record",
        "name": "User",
        "namespace": "io.test1",
        "fields": [
          {
            "name": "f0",
            "type": "long"
          }
        ]
      }
    ]

string (uuid) | – | STRING | –
fixed (duration) | – | BINARY(size) | –
