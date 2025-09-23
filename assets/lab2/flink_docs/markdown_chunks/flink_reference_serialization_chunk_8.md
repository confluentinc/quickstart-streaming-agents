---
document_id: flink_reference_serialization_chunk_8
source_file: flink_reference_serialization.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/serialization.html
title: Data Type Mappings with Flink SQL Statements in Confluent Cloud for Apache Flink
chunk_index: 8
total_chunks: 8
---

| BIGINT | google.protobuf.UInt32Value | –
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
