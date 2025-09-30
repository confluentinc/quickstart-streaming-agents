---
document_id: flink_reference_datatypes_chunk_1
source_file: flink_reference_datatypes.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/datatypes.html
title: Flink SQL Data Types in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 10
---

# Data Types in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® has a rich set of native data types that you can use in SQL statements and queries.

The query planner supports the following SQL types.

Flink SQL type | Java type | JSON Schema type | Protobuf type | Avro type | Avro logical type
---|---|---|---|---|---
ARRAY | t[] | Array | repeated T | array | –
BIGINT | long | Number | INT64 | long | –
BINARY | byte[] | String | BYTES | fixed | –
BOOLEAN | boolean | Boolean | BOOL | boolean | –
BYTES / VARBINARY | byte[] | String | BYTES | bytes | –
CHAR | String | String | STRING | string | –
DATE | java.time.LocalDate | Number | MESSAGE | int | date
DECIMAL | java.math.BigDecimal | Number | MESSAGE | bytes | decimal
DOUBLE | double | Number | DOUBLE | double | –
FLOAT | float | Number | FLOAT | float | –
INT | long | Number | INT32 | int | –
INTERVAL DAY TO SECOND | java.time.Duration | Not supported | Not supported | Not supported | –
INTERVAL YEAR TO MONTH | java.time.Period | Not supported | Not supported | Not supported | –
MAP | java.util.Map<kt, vt> | Array[Object] / Object | repeated MESSAGE | map / array | –
MULTISET | java.util.Map<t, Integer> | Array[Object] / Object | repeated MESSAGE | map / array | –
NULL | java.lang.Object | oneOf(Null, T) | [1] | union(avro_type, null) | –
ROW | org.apache.flink.types.Row | Object | MESSAGE | record [2] | –
SMALLINT | short | Number | INT32 | int | –
TIME | java.time.LocalTime | Number | – | int | time-millis
TIMESTAMP | java.time.LocalDateTime | Number | MESSAGE | long | local-timestamp-millis/local-timestamp-micros
TIMESTAMP_LTZ | java.time.Instant | Number | MESSAGE | long | timestamp-millis / timestamp-micros
TINYINT | byte | Number | INT32 | int | –
VARCHAR / STRING | String | String | STRING | string | –
[1]| See discussion at [Flink SQL types to Protobuf types](serialization.html#flink-sql-serialization-sql-to-protobuf)
---|---
[2]| See discussion at [Flink SQL types to Avro types](serialization.html#flink-sql-serialization-sql-to-avro)
---|---

## Data type definition¶

A _data type_ describes the logical type of a value in a SQL table. You use data types to declare the input and output types of an operation.

The Flink data types are similar to the SQL standard data type terminology, but for efficient handling of scalar expressions, they also contain information about the nullability of a value.

These are examples of SQL data types:

    INT
    INT NOT NULL
    INTERVAL DAY TO SECOND(3)
    ROW<fieldOne ARRAY<BOOLEAN>, fieldTwo TIMESTAMP(3)>

The following sections list all pre-defined data types in Flink SQL.

## Character strings¶

### CHAR¶

Represents a fixed-length character string.

**Declaration**

    CHAR
    CHAR(n)

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
java.lang.String | ✓ | ✓ | Default
byte[] | ✓ | ✓ | Assumes UTF-8 encoding
org.apache.flink.table.data.StringData | ✓ | ✓ | Internal data structure

**Formats**

The following table shows examples of the CHAR type in different formats.

JSON for data type |

    {"type":"CHAR","nullable":true,"length":8}

---|---
CLI/UI format |

    CHAR(8)

JSON for payload |

    "Example string"

CLI/UI format for payload |

    Example string

Declare this type by using `CHAR(n)`, where `n` is the number of code points. `n` must have a value between _1_ and _2,147,483,647_ (both inclusive). If no length is specified, `n` is equal to _1_.

`CHAR(0)` is not supported for CAST or persistence in catalogs, but it exists in protocols.

### VARCHAR / STRING¶

Represents a variable-length character string.

**Declaration**

    VARCHAR
    VARCHAR(n)

    STRING

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
java.lang.String | ✓ | ✓ | Default
byte[] | ✓ | ✓ | Assumes UTF-8 encoding
org.apache.flink.table.data.StringData | ✓ | ✓ | Internal data structure

**Formats**

The following table shows examples of the VARCHAR type in different formats.

JSON for data type |

    {"type":"VARCHAR","nullable":true,"length":8}

---|---
CLI/UI format |

    VARCHAR(800)

JSON for payload |

    "Example string"

CLI/UI format for payload |

    Example string

Declare this type by using `VARCHAR(n)`, where `n` is the maximum number of code points. `n` must have a value between _1_ and _2,147,483,647_ (both inclusive). If no length is specified, `n` is equal to _1_.

`STRING` is equivalent to `VARCHAR(2147483647)`.

`VARCHAR(0)` is not supported for CAST or persistence in catalogs, but it exists in protocols.
