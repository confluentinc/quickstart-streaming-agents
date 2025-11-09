---
document_id: flink_reference_serialization_chunk_6
source_file: flink_reference_serialization.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/serialization.html
title: Data Type Mappings with Flink SQL Statements in Confluent Cloud for Apache Flink
chunk_index: 6
total_chunks: 8
---

| BIGINT Number(requiresInteger=false) | DOUBLE

## Protobuf schema¶

### Flink SQL types to Protobuf types¶

The following table shows the mapping of Flink SQL types to Protobuf types.

This mapping is important for creating tables, because it defines the Protobuf schema that’s produced by a CREATE TABLE statement.

#### ARRAY[T]¶

* Protobuf type: `repeated T`

* Message type: –

* Additional properties: `flink.wrapped`, which indicates that Flink wrappers are used to represent nullability, because Protobuf doesn’t support nullable repeated natively.

* Example:

        repeated int64 value = 1;

Nullable array:

        arrayNullableRepeatedWrapper arrayNullable = 1 [(confluent.field_meta) = {
          params: [
            {
              key: "flink.wrapped",
              value: "true"
            },
            {
              key: "flink.version",
              value: "1"
            }
          ]
        }];

        message arrayNullableRepeatedWrapper {
          repeated int64 value = 1;
        }

Nullable elements:

        repeated elementNullableElementWrapper elementNullable = 2 [(confluent.field_meta) = {
          params: [
            {
              key: "flink.wrapped",
              value: "true"
            },
            {
              key: "flink.version",
              value: "1"
            }
          ]
        }];

        message elementNullableElementWrapper {
          optional int64 value = 1;
        }

#### BIGINT¶

* Protobuf type: `INT64`

* Message type: –

* Additional properties: –

* Example:

        optional int64 bigint = 8;

#### BINARY¶

* Protobuf type: `BYTES`

* Message type: –

* Additional properties: `flink.maxLength=flink.minLength`

* Example:

        optional bytes binary = 13 [(confluent.field_meta) = {
          params: [
            {
              key: "flink.maxLength",
              value: "123"
            },
            {
              key: "flink.minLength",
              value: "123"
            },
            {
              key: "flink.version",
              value: "1"
            }
          ]
        }];

#### BOOLEAN¶

* Protobuf type: `BOOL`

* Message type: –

* Additional properties: –

* Example:

        optional bool boolean = 2;

#### CHAR¶

* Protobuf type: `STRING`

* Message type: –

* Additional properties: `flink.maxLength=flink.minLength`

* Example:

        optional string char = 11 [(confluent.field_meta) = {
          params: [
            {
              key: "flink.maxLength",
              value: "123"
            },
            {
              key: "flink.minLength",
              value: "123"
            },
            {
              key: "flink.version",
              value: "1"
            }
          ]
        }];

#### DATE¶

* Protobuf type: `MESSAGE`

* Message type: `google.type.Date`

* Additional properties: –

* Example:

        optional .google.type.Date date = 17;

#### DECIMAL¶

* Protobuf type: `MESSAGE`

* Message type: `confluent.type.Decimal`

* Additional properties: –

* Example:

        optional .confluent.type.Decimal decimal = 19 [(confluent.field_meta) = {
          params: [
            {
              value: "5",
              key: "precision"
            },
            {
              value: "1",
              key: "scale"
            },
            {
              key: "flink.version",
              value: "1"
            }
          ]
        }];

#### DOUBLE¶

* Protobuf type: `DOUBLE`

* Message type: –

* Additional properties: –

* Example:

        optional double double = 10;

#### FLOAT¶

* Protobuf type: `FLOAT`

* Message type: –

* Additional properties: –

* Example:

        optional float float = 9;

#### INT¶

* Protobuf type: `INT32`

* Message type: –

* Additional properties: –

* Example:

        optional int32 int = 7;

#### MAP[K, V]¶

* Protobuf type: `repeated MESSAGE`

* Message type: `XXEntry(K key, V value)`

* Additional properties: `flink.wrapped`, which indicates that Flink wrappers are used to represent nullability, because Protobuf doesn’t support nullable repeated natively. For examples, see the ARRAY type.

* Example:

        repeated MapEntry map = 20;

        message MapEntry {
            optional string key = 1;
            optional int64 value = 2;
          }

#### MULTISET[V]¶

* Protobuf type: `repeated MESSAGE`

* Message type: `XXEntry(V key, int32 value)`

* Additional properties:

  * `flink.wrapped`, which indicates that Flink wrappers are used to represent nullability, because Protobuf doesn’t support nullable repeated natively. For examples, see the ARRAY type.
  * `flink.type=multiset`
* Example:

        repeated MultisetEntry multiset = 1 [(confluent.field_meta)
