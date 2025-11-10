---
document_id: flink_reference_datatypes_chunk_10
source_file: flink_reference_datatypes.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/datatypes.html
title: Flink SQL Data Types in Confluent Cloud for Apache Flink
chunk_index: 10
total_chunks: 10
---

used is [CAST](functions/comparison-functions.html#flink-sql-cast-function) or [TRY_CAST](functions/comparison-functions.html#flink-sql-try-cast-function).

## Data type extraction¶

In many locations in the API, Flink tries to extract data types automatically from class information by using reflection to avoid repetitive manual schema work. But extracting a data type using reflection is not always successful, because logical information might be missing. In these cases, it may be necessary to add additional information close to a class or field declaration for supporting the extraction logic.

The following table lists classes that map implicitly to a data type without requiring further information. Other JVM bridging classes require the [@DataTypeHint](../concepts/user-defined-functions.html#flink-sql-udfs-type-inference-data-type-hints) annotation.

Class | Data Type
---|---
boolean | BOOLEAN NOT NULL
byte | TINYINT NOT NULL
byte[] | BYTES
double | DOUBLE NOT NULL
float | FLOAT NOT NULL
int | INT NOT NULL
java.lang.Boolean | BOOLEAN
java.lang.Byte | TINYINT
java.lang.Double | DOUBLE
java.lang.Float | FLOAT
java.lang.Integer | INT
java.lang.Long | BIGINT
java.lang.Short | SMALLINT
java.lang.String | STRING
java.sql.Date | DATE
java.sql.Time | TIME(0)
java.sql.Timestamp | TIMESTAMP(9)
java.time.Duration | INTERVAL SECOND(9)
java.time.Instant | TIMESTAMP_LTZ(9)
java.time.LocalDate | DATE
java.time.LocalTime | TIME(9)
java.time.LocalDateTime | TIMESTAMP(9)
java.time.OffsetDateTime | TIMESTAMP(9) WITH TIME ZONE
java.time.Period | INTERVAL YEAR(4) TO MONTH
java.util.Map<K, V> | MAP<K, V>
short | SMALLINT NOT NULL
structured type T | anonymous structured type T
long | BIGINT NOT NULL
T[] | ARRAY<T>
