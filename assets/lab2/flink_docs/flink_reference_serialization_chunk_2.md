---
document_id: flink_reference_serialization_chunk_2
source_file: flink_reference_serialization.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/serialization.html
title: Data Type Mappings with Flink SQL Statements in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 8
---

JSON Schema * Protobuf schema

## Avro schemas¶

### Known limitations¶

* Avro enums have limited support. Flink supports reading and writing enums but treats them as a STRING type. From Flink’s perspective, enums are not distinguishable from the STRING type. You can’t create an Avro schema from Flink that has an enum field.
* Flink doesn’t support reading Avro `time-micros` as a TIME type. Flink supports TIME with precision up to `3`. `time-micros` is read and written as BIGINT.
* Field names must match Avro criteria. Avro expects field names to start with `[A-Za-z_]` and subsequently contain only `[A-Za-z0-9_]`.
* These Flink types are not supported:
  * INTERVAL_DAY_TIME
  * INTERVAL_YEAR_MONTH
  * TIMESTAMP_WITH_TIMEZONE

### Flink SQL types to Avro types¶

The following table shows the mapping of Flink SQL types to Avro physical types.

This mapping is important for creating tables, because it defines the Avro schema that’s produced by a CREATE TABLE statement.

#### ARRAY¶

* Avro type: `array`

* Avro logical type: –

* Additional properties: –

* Example:

        {
          "type" : "array",
          "items" : "long"
        }

#### BIGINT¶

* Avro type: `long`
* Avro logical type: –
* Additional properties: –
* Example: `long`

#### BINARY¶

* Avro type: `fixed`

* Avro logical type: –

* Additional properties: `flink.maxLength` (MAX_LENGTH if not set)

* Example:

        {
            "type" : "fixed",
            "name" : "row",
            "namespace" : "io.confluent",
            "size" : 123
          }

#### BOOLEAN¶

* Avro type: `boolean`
* Avro logical type: –
* Additional properties: –
* Example: `boolean`

#### CHAR¶

* Avro type: `string`

* Avro logical type: –

* Additional properties: `flink.maxLength` (MAX_LENGTH if not set)

* Example:

        {
          "type" : "string",
          "flink.maxLength" : 123,
          "flink.minLength" : 123,
          "flink.version" : "1"
        }

#### DATE¶

* Avro type: `int`

* Avro logical type: `date`

* Additional properties: –

* Example:

        {
          "type" : "int",
          "logicalType" : "date"
        }

#### DECIMAL¶

* Avro type: `bytes`

* Avro logical type: `decimal`

* Additional properties: –

* Example:

        {
          "type" : "bytes",
          "logicalType" : "decimal",
          "precision" : 6,
          "scale" : 3
        }

#### DOUBLE¶

* Avro type: `double`
* Avro logical type: –
* Additional properties: –
* Example: `double`

#### FLOAT¶

* Avro type: `float`
* Avro logical type: –
* Additional properties: –
* Example: `float`

#### INT¶

* Avro type: `int`
* Avro logical type: –
* Additional properties: –
* Example: `int`

#### MAP (character key)¶

* Avro type: `map`

* Avro logical type: –

* Additional properties: –

* Example:

        {
          "type" : "map",
          "values" : "boolean"
        }

#### MAP (non-character key)¶

* Avro type: `array`

* Avro logical type: –

* Additional properties: array of `io.confluent.connect.avro.MapEntry(key, value)`

* Example:

        {
          "type" : "array",
          "items" : {
            "type" : "record",
            "name" : "MapEntry",
            "namespace" : "io.confluent.connect.avro",
            "fields" : [ {
              "name" : "key",
              "type" : "int"
            }, {
              "name" : "value",
              "type" : "bytes"
            } ]
          }
        }

#### MULTISET (character element)¶

* Avro type: `map`

* Avro logical type: –

* Additional properties: `flink.type : multiset`

* Example:

        {
          "type" : "map",
          "values" : "int",
          "flink.type" : "multiset",
          "flink.version" : "1"
        }

#### MULTISET (non-character key)¶

* Avro type: `array`

* Avro logical type: –

* Additional properties: array of `io.confluent.connect.avro.MapEntry(key, value)`, `flink.type : multiset`

* Example:

        {
          "type" : "array",
          "items" : {
            "type" : "record",
            "name" : "MapEntry",
            "namespace" : "io.confluent.connect.avro",
            "fields" : [ {
              "name" : "key",
              "type" : "long"
            }, {
              "name" : "value",
              "type" : "int"
            } ]
          },
          "flink.type" : "multiset",
          "flink.version" : "1"
        }

#### ROW¶

* Avro type: `record`

* Avro logical type: –

* Additional properties: `connect.type=int16`

* Name: `org.apache.flink.avro.generated.record`

* Nested records name: `org.apache.flink.avro.generated.record_$fieldName`
