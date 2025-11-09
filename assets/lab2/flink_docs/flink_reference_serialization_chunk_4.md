---
document_id: flink_reference_serialization_chunk_4
source_file: flink_reference_serialization.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/serialization.html
title: Data Type Mappings with Flink SQL Statements in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 8
---

– | BINARY(size) | –

## JSON Schema¶

### Flink SQL types to JSON Schema types¶

The following table shows the mapping of Flink SQL types to JSON Schema types.

This mapping is important for creating tables, because it defines the JSON Schema that’s produced by a CREATE TABLE statement.

* Nullable types are expressed as oneOf(Null, T).
* Object for a MAP and MULTISET must have two fields [key, value].
* MULTISET is equivalent to MAP[K, INT] and is serialized accordingly.

#### ARRAY¶

* JSON Schema type: `Array`

* Additional properties: –

* JSON type title: –

* Example:

        {
          "type": "array",
          "items": {
            "type": "number",
            "title": "org.apache.kafka.connect.data.Time",
            "flink.precision": 2,
            "connect.type": "int32",
            "flink.version": "1"
          }
        }

#### BIGINT¶

* JSON Schema type: `Number`

* Additional properties: `connect.type=int64`

* JSON type title: –

* Example:

        {
          "type": "number",
          "connect.type": "int64"
        }

#### BINARY¶

* JSON Schema type: `String`

* Additional properties:

  * `connect.type=bytes`
  * `flink.minLength=flink.maxLength`: Different from JSON’s `minLength/maxLength`, because this property describes bytes length, not string length.
* JSON type title: –

* Example:

        {
          "type": "string",
          "flink.maxLength": 123,
          "flink.minLength": 123,
          "flink.version": "1",
          "connect.type": "bytes"
        }

#### BOOLEAN¶

* JSON Schema type: `Boolean`

* Additional properties: –

* JSON type title: –

* Example:

        {
          "type": "array",
          "items": {
            "type": "number",
            "title": "org.apache.kafka.connect.data.Time",
            "flink.precision": 2,
            "connect.type": "int32",
            "flink.version": "1"
          }
        }

#### CHAR¶

* JSON Schema type: `String`

* Additional properties: `minLength=maxLength`

* JSON type title: –

* Example:

        {
          "type": "string",
          "minLength": 123,
          "maxLength": 123
        }

#### DATE¶

* JSON Schema type: `Number`
* Additional properties: `connect.type=int32`
* JSON type title: `org.apache.kafka.connect.data.Date`
* Example: –

#### DECIMAL¶

* JSON Schema type: `Number`
* Additional properties: `connect.type=bytes`
* JSON type title: `org.apache.kafka.connect.data.Decimal`
* Example: –

#### DOUBLE¶

* JSON Schema type: `Number`

* Additional properties: `connect.type=float64`

* JSON type title: –

* Example:

        {
          "type": "number",
          "connect.type": "float64"
        }

#### FLOAT¶

* JSON Schema type: `Number`

* Additional properties: `connect.type=float32`

* JSON type title: –

* Example:

        {
          "type": "number",
          "connect.type": "float32"
        }

#### INT¶

* JSON Schema type: `Number`

* Additional properties: `connect.type=int32`

* JSON type title: –

* Example:

        {
          "type": "number",
          "connect.type": "int32"
        }

#### MAP[K, V]¶

* JSON Schema type: `Array[Object]`

* Additional properties: `connect.type=map`

* JSON type title: –

* Example:

        {
          "type": "array",
          "connect.type": "map",
          "items": {
            "type": "object",
            "properties": {
              "value": {
                "type": "number",
                "connect.type": "int64"
              },
              "key": {
                "type": "number",
                "connect.type": "int32"
              }
            }
          }
        }

#### MAP[VARCHAR, V]¶

* JSON Schema type: `Object`

* Additional properties: `connect.type=map`

* JSON type title: –

* Example:

        {
          "type":"object",
          "connect.type":"map",
          "additionalProperties":
           {
             "type":"number",
             "connect.type":"int64"
           }
        }

#### MULTISET[K]¶

* JSON Schema type: `Array[Object]`

* Additional properties:

  * `connect.type=map`
  * `flink.type=multiset`
* JSON type title: The count (value) in the JSON schema must map to a Flink INT type. For MULTISET types, the count (value) in the JSON schema must map to a Flink INT type, which corresponds to `connect.type: int32` in the JSON Schema. Using `connect.type: int64` causes a validation error.

* Example:

        {
          "type": "array",
          "connect.type": "map",
          "flink.type": "multiset",
          "items": {
            "type": "object",
            "properties": {
              "value": {
                "type": "number",
                "connect.type": "int32"
              },
              "key": {
                "type": "number",
                "connect.type": "int32"
              }
            }
          }
        }
