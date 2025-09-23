---
source_url: https://docs.confluent.io/cloud/current/flink/reference/serialization.html
title: Data Type Mappings with Flink SQL Statements in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'serialization.html']
scraped_date: 2025-09-05T13:47:06.810611
---

# Data Type Mappings in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® supports records in the Avro Schema Registry, JSON_SR, and Protobuf Schema Registry formats.

* Avro schemas
* JSON Schema
* Protobuf schema

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

        repeated MultisetEntry multiset = 1 [(confluent.field_meta) = {
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
MESSAGE | BIGINT | google.protobuf.UInt32Value | –
MESSAGE | BOOLEAN | google.protobuf.BoolValue | –
MESSAGE | DOUBLE | google.protobuf.DoubleValue | –
MESSAGE | FLOAT | google.protobuf.FloatValue | –
MESSAGE | INT | google.protobuf.Int32Value | –
MESSAGE | VARBINARY | google.protobuf.BytesValue | –
MESSAGE | VARCHAR | google.protobuf.StringValue | –
oneOf | ROW | – | –

### Protobuf 3 nullable field behavior¶

When working with Protobuf 3 schemas in Confluent Cloud for Apache Flink, it’s important to understand how nullable fields are handled.

When converting to a Protobuf schema, Flink marks all NULLABLE fields as `optional`.

In Protobuf, expressing something as NULLABLE or NOT NULL is not straightforward.

* All non-MESSAGE types are NOT NULL. If not set explicitly, the default value is assigned.

* Non-MESSAGE types marked with `optional` can be checked if they were set. If not set, Flink assumes NULL.

* MESSAGE types are all NULLABLE, which means that all fields of MESSAGE type are optional, and there is no way to ensure on a format level they are NOT NULL. To store this information, Flink uses the `flink.notNull` property, for example:

        message Row {
          .google.type.Date date = 1 [(confluent.field_meta) = {
            params: [
              {
                key: "flink.version",
                value: "1"
              },
              {
                key: "flink.notNull",
                value: "true"
              }
            ]
          }];
        }

Fields without the `optional` keyword
    In Protobuf 3, fields without the `optional` keyword are treated as NOT NULL by Flink. This is because Protobuf 3 doesn’t support nullable getters/setters by default. If a field is omitted in the data, Protobuf 3 assigns the default value, which is 0 for numbers, the empty string for strings, and `false` for booleans.
Fields with the `optional` keyword
    Fields marked with `optional` in Protobuf 3 are treated as nullable by Flink. When such a field is not set in the data, Flink interprets it as NULL.
Fields with the `repeated` keyword
    Fields marked with `repeated` in Protobuf 3 are treated as arrays by Flink. The array itself is NOT NULL, but individual elements within the array can be nullable depending on their type. For MESSAGE types, elements are nullable by default. For primitive types, elements are NOT NULL.

This behavior is consistent across all streaming platforms that work with Protobuf 3, including Kafka Streams and other Confluent products, and is not specific to Flink. It’s a fundamental characteristic of the Protobuf 3 specification itself.

In a Protobuf 3 schema, if you want a field to be nullable in Flink, you must explicitly mark it as `optional`, for example:

    message Example {
      string required_field = 1;        // NOT NULL in Flink
      optional string nullable_field = 2;  // NULLABLE in Flink
      repeated string array_field = 3;     // NOT NULL array in Flink
      repeated optional string nullable_array_field = 4;  // NOT NULL array with nullable elements
    }
