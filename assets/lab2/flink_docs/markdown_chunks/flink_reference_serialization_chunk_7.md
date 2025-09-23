---
document_id: flink_reference_serialization_chunk_7
source_file: flink_reference_serialization.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/serialization.html
title: Data Type Mappings with Flink SQL Statements in Confluent Cloud for Apache Flink
chunk_index: 7
total_chunks: 8
---

= {
          params: [
            {
              key: "flink.type",
              value: "multiset"
            },
            {
              key: "flink.version",
              value: "1"
            }
          ]
        }];

        message MultisetEntry {
          optional string key = 1;
          int32 value = 2;
        }

#### ROW¶

* Protobuf type: `MESSAGE`

* Message type: `fieldName`

* Additional properties: –

* Example:

        meta_Row meta = 1;

        message meta_Row {
          float a = 1;
          float b = 2;
        }

#### SMALLINT¶

* Protobuf type: `INT32`

* Message type: –

* Additional properties: MetaProto extension: `connect.type = int16`

* Example:

        optional int32 smallInt = 6 [(confluent.field_meta) = {
          doc: "smallInt comment",
          params: [
            {
              key: "flink.version",
              value: "1"
            },
            {
              key: "connect.type",
              value: "int16"
            }
          ]
        }];

#### TIMESTAMP¶

* Protobuf type: `MESSAGE`

* Message type: `google.protobuf.Timestamp`

* Additional properties:

  * `flink.precision`
  * `flink.type=timestamp`
* Example:

        optional .google.protobuf.Timestamp timestamp_ltz_3 = 16 [(confluent.field_meta) = {
          params: [
            {
              key: "flink.type",
              value: "timestamp"
            },
            {
              key: "flink.precision",
              value: "3"
            },
            {
              key: "flink.version",
              value: "1"
            }
          ]
        }];

#### TIMESTAMP_LTZ¶

* Protobuf type: `MESSAGE`

* Message type: `google.protobuf.Timestamp`

* Additional properties: `flink.precision`

* Example:

        optional .google.protobuf.Timestamp timestamp_ltz_3 = 15 [(confluent.field_meta) = {
          params: [
            {
              key: "flink.precision",
              value: "3"
            },
            {
              key: "flink.version",
              value: "1"
            }
          ]
        }];

#### TIME_WITHOUT_TIME_ZONE¶

* Protobuf type: `MESSAGE`

* Message type: `google.type.TimeOfDay`

* Additional properties: –

* Example:

        optional .google.type.TimeOfDay time = 18 [(confluent.field_meta) = {
          params: [
            {
              key: "flink.precision",
              value: "3"
            },
            {
              key: "flink.version",
              value: "1"
            }
          ]
        }];

#### TINYINT¶

* Protobuf type: `INT32`

* Message type: –

* Additional properties: MetaProto extension: `connect.type = int8`

* Example:

        optional int32 tinyInt = 4 [(confluent.field_meta) = {
          doc: "tinyInt comment",
          params: [
            {
              key: "flink.version",
              value: "1"
            },
            {
              key: "connect.type",
              value: "int8"
            }
          ]
        }];

#### VARBINARY¶

* Protobuf type: `BYTES`

* Message type: –

* Additional properties: `flink.maxLength` (default = MAX_LENGTH)

* Example:

        optional bytes varbinary = 14 [(confluent.field_meta) = {
          params: [
            {
              key: "flink.maxLength",
              value: "123"
            },
            {
              key: "flink.version",
              value: "1"
            }
          ]
        }];

#### VARCHAR¶

* Protobuf type: `STRING`

* Message type: –

* Additional properties: `flink.maxLength` (default = MAX_LENGTH)

* Example:

        optional string varchar = 12 [(confluent.field_meta) = {
          params: [
            {
              key: "flink.maxLength",
              value: "123"
            },
            {
              key: "flink.version",
              value: "1"
            }
          ]
        }];

### Protobuf types to Flink SQL types¶

The following table shows the mapping of Protobuf types to Flink SQL and Connect types. It shows only mappings that are not covered by the previous table. These types can’t originate from Flink SQL.

This mapping is important when consuming/reading records with a schema that was created outside of Flink. The mapping defines the Flink table’s schema [inferred](statements/show.html#flink-sql-show-inferred-tables) from a Protobuf schema.

Protobuf type | Flink SQL type | Message type | Connect type annotation
---|---|---|---
FIXED32 | FIXED64 | SFIXED64 | BIGINT | – | –
INT32 | SINT32 | SFIXED32 | INT | – | –
INT32 | SINT32 | SFIXED32 | SMALLINT | – | int16
INT32 | SINT32 | SFIXED32 | TINYINT | – | int8
INT64 | SINT64 | BIGINT | – | –
UINT32 | UINT64 | BIGINT | – | –
MESSAGE | BIGINT | google.protobuf.Int64Value | –
MESSAGE | BIGINT | google.protobuf.UInt64Value | –
MESSAGE
