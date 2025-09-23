---
source_url: https://docs.confluent.io/cloud/current/flink/reference/datatypes.html
title: Flink SQL Data Types in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'datatypes.html']
scraped_date: 2025-09-05T13:47:04.577366
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

## Binary strings¶

### BINARY¶

Represents a fixed-length binary string (=a sequence of bytes).

**Declaration**

    BINARY
    BINARY(n)

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
byte[] | ✓ | ✓ | Default

**Formats**

The following table shows examples of the BINARY type in different formats.

JSON for data type |

    {"type":"BINARY","nullable":true,"length":1}

---|---
CLI/UI format |

    BINARY(3)

JSON for payload |

    "x'7f0203'"

CLI/UI format for payload |

    x'7f0203'

Declare this type by using `BINARY(n)`, where `n` is the number of bytes. `n` must have a value between _1_ and _2,147,483,647_ (both inclusive). If no length is specified, `n` is equal to _1_.

The string representation is hexadecimal format.

`BINARY(0)` is not supported for CAST or persistence in catalogs, but it exists in protocols.

### BYTES / VARBINARY¶

Represents a variable-length binary string (=a sequence of bytes).

**Declaration**

    BYTES

    VARBINARY
    VARBINARY(n)

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
byte[] | ✓ | ✓ | Default

**Formats**

The following table shows examples of the VARBINARY type in different formats.

JSON for data type |

    {"type":"VARBINARY","nullable":true,"length":1}

---|---
CLI/UI format |

    VARBINARY(800)

JSON for payload |

    "x'7f0203'"

CLI/UI format for payload |

    x'7f0203'

Declare this type by using `VARBINARY(n)` where `n` is the maximum number of bytes. `n` must have a value between _1_ and _2,147,483,647_ (both inclusive). If no length is specified, `n` is equal to _1_.

`BYTES` is equivalent to `VARBINARY(2147483647)`.

`VARCHAR(0)` is not supported for CAST or persistence in catalogs, but it exists in protocols.

## Exact numerics¶

### BIGINT¶

Represents an 8-byte signed integer with values from _-9,223,372,036,854,775,808_ to _9,223,372,036,854,775,807_.

**Declaration**

    BIGINT

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
java.lang.Long | ✓ | ✓ | Default
long | ✓ | (✓) | Output only if type is not nullable

**Formats**

The following table shows examples of the BIGINT type in different formats.

JSON for data type |

    {"type":"BIGINT","nullable":true}

---|---
CLI/UI format |

    BIGINT

JSON for payload |

    "23"

CLI/UI format for payload |

    23

### DECIMAL¶

Represents a decimal number with fixed precision and scale.

**Declaration**

    DECIMAL
    DECIMAL(p)
    DECIMAL(p, s)

    DEC
    DEC(p)
    DEC(p, s)

    NUMERIC
    NUMERIC(p)
    NUMERIC(p, s)

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
java.math.BigDecimal | ✓ | ✓ | Default
org.apache.flink.table.data.DecimalData | ✓ | ✓ | Internal data structure

**Formats**

The following table shows examples of the DECIMAL type in different formats.

JSON for data type |

    {"type":"DECIMAL","nullable":true,"precision":5,"scale":3}

---|---
CLI/UI format |

    DECIMAL(5, 3)

JSON for payload |

    "12.123"

CLI/UI format for payload |

    12.123

Declare this type by using `DECIMAL(p, s)` where `p` is the number of digits in a number (_precision_) and `s` is the number of digits to the right of the decimal point in a number (_scale_).

`p` must have a value between _1_ and _38_ (both inclusive). The default value for `p` is _10_.

`s` must have a value between _0_ and `p` (both inclusive). The default value for `s` is _0_.

The right side is padded with _0_.

The left side must be padded with spaces, like all other values.

`NUMERIC(p, s)` and `DEC(p, s)` are synonyms for this type.

### INT¶

Represents a 4-byte signed integer with values from _-2,147,483,648_ to _2,147,483,647_.

**Declaration**

    INT

    INTEGER

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
java.lang.Integer | ✓ | ✓ | Default
long | ✓ | (✓) | Output only if type is not nullable

**Formats**

The following table shows examples of the INT type in different formats.

JSON for data type |

    {"type":"INT","nullable":true}

---|---
CLI/UI format |

    INT

JSON for payload |

    "23"

CLI/UI format for payload |

    23

`INTEGER` is a synonym for this type.

### SMALLINT¶

Represents a 2-byte signed integer with values from _-32,768_ to _32,767_.

**Declaration**

    SMALLINT

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
java.lang.Short | ✓ | ✓ | Default
short | ✓ | (✓) | Output only if type is not nullable

**Formats**

The following table shows examples of the SMALLINT type in different formats.

JSON for data type |

    {"type":"SMALLINT","nullable":true}

---|---
CLI/UI format |

    SMALLINT

JSON for payload |

    "23"

CLI/UI format for payload |

    23

### TINYINT¶

Represents a 1-byte signed integer with values from _-128_ to _127_.

**Declaration**

    TINYINT

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
java.lang.Byte | ✓ | ✓ | Default
byte | ✓ | (✓) | Output only if type is not nullable

**Formats**

The following table shows examples of the TINYINT type in different formats.

JSON for data type |

    {"type":"TINYINT","nullable":true}

---|---
CLI/UI format |

    TINYINT

JSON for payload |

    "23"

CLI/UI format for payload |

    23

## Approximate numerics¶

### DOUBLE¶

Represents an 8-byte double precision floating point number.

**Declaration**

    DOUBLE

    DOUBLE PRECISION

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
java.lang.Double | ✓ | ✓ | Default
double | ✓ | (✓) | Output only if type is not nullable

**Formats**

The following table shows examples of the DOUBLE type in different formats.

JSON for data type |

    {"type":"DOUBLE","nullable":true}

---|---
CLI/UI format |

    DOUBLE

JSON for payload |

    "1.1111112120000001E7"

CLI/UI format for payload |

    1.1111112120000001E7

`DOUBLE PRECISION` is a synonym for this type.

### FLOAT¶

Represents a 4-byte single precision floating point number.

**Declaration**

    FLOAT

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
java.lang.Float | ✓ | ✓ | Default
float | ✓ | (✓) | Output only if type is not nullable

**Formats**

The following table shows examples of the FLOAT type in different formats.

JSON for data type |

    {"type":"FLOAT","nullable":true}

---|---
CLI/UI format |

    FLOAT

JSON for payload |

    "1.1111112E7"

CLI/UI format for payload |

    1.1111112E7

Compared to the SQL standard, this type doesn’t take parameters.

## Date and time¶

### DATE¶

Represents a date consisting of `year-month-day` with values ranging from `0000-01-01` to `9999-12-31`.

**Declaration**

    DATE

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
java.time.LocalDate | ✓ | ✓ | Default
java.sql.Date | ✓ | ✓ |
java.lang.Integer | ✓ | ✓ | Describes the number of days since Unix epoch
int | ✓ | (✓) | Describes the number of days since Unix epoch. Output only if type is not nullable.

**Formats**

The following table shows examples of the DATE type in different formats.

JSON for data type |

    {"type":"DATE","nullable":true}

---|---
CLI/UI format |

    DATE

JSON for payload |

    "2023-04-06"

CLI/UI format for payload |

    2023-04-06

Compared to the SQL standard, the range starts at year `0000`.

### INTERVAL DAY TO SECOND¶

Data type for a group of day-time interval types.

**Declaration**

    INTERVAL DAY
    INTERVAL DAY(p1)
    INTERVAL DAY(p1) TO HOUR
    INTERVAL DAY(p1) TO MINUTE
    INTERVAL DAY(p1) TO SECOND(p2)
    INTERVAL HOUR
    INTERVAL HOUR TO MINUTE
    INTERVAL HOUR TO SECOND(p2)
    INTERVAL MINUTE
    INTERVAL MINUTE TO SECOND(p2)
    INTERVAL SECOND
    INTERVAL SECOND(p2)

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
java.time.Duration | ✓ | ✓ | Default
java.lang.Long | ✓ | ✓ | Describes the number of milliseconds
long | ✓ | (✓) | Describes the number of milliseconds. Output only if type is not nullable.

**Formats**

The following table shows examples of the INTERVAL DAY TO SECOND type in different formats.

JSON for data type |

    {"type":"INTERVAL_DAY_TIME","nullable":true,"precision":1,"fractionalPrecision":3,"resolution":"DAY_TO_SECOND"}

---|---
CLI/UI format |

    INTERVAL DAY(1) TO SECOND(3)

JSON for payload |

    "+2 07:33:20.000"

CLI/UI format for payload |

    +2 07:33:20.000

Declare this type by using the above combinations, where `p1` is the number of digits of days (_day precision_) and `p2` is the number of digits of fractional seconds (_fractional precision_).

`p1` must have a value between _1_ and _6_ (both inclusive). If no `p1` is specified, it is equal to _2_ by default.

`p2` must have a value between _0_ and _9_ (both inclusive). If no `p2` is specified, it is equal to _6_ by default.

The type must be parameterized to one of these resolutions with up to nanosecond precision:

  * Interval of days
  * Interval of days to hours
  * Interval of days to minutes
  * Interval of days to seconds
  * Interval of hours
  * Interval of hours to minutes
  * Interval of hours to seconds
  * Interval of minutes
  * Interval of minutes to seconds
  * Interval of seconds

An interval of day-time consists of `+days hours:months:seconds.fractional` with values ranging from `-999999 23:59:59.999999999` to `+999999 23:59:59.999999999`. The value representation is the same for all types of resolutions. For example, an interval of seconds of _70_ is always represented in an interval-of-days-to-seconds format (with default precisions): `+00 00:01:10.000000`.

Formatting intervals are tricky, because they have different resolutions:

  * DAY
  * DAY_TO_HOUR
  * DAY_TO_MINUTE
  * DAY_TO_SECOND
  * HOUR
  * HOUR_TO_MINUTE
  * HOUR_TO_SECOND
  * MINUTE
  * MINUTE_TO_SECOND
  * SECOND

Depending on the resolution, use:

    INTERVAL DAY(1)
    INTERVAL DAY(1) TO HOUR
    INTERVAL DAY(1) TO MINUTE
    INTERVAL DAY(1) TO SECOND(3)
    INTERVAL HOUR
    INTERVAL HOUR TO MINUTE
    INTERVAL HOUR TO SECOND(3)
    INTERVAL MINUTE
    INTERVAL MINUTE TO SECOND(3)
    INTERVAL SECOND(3)

### INTERVAL YEAR TO MONTH¶

Data type for a group of year-month interval types.

**Declaration**

    INTERVAL YEAR
    INTERVAL YEAR(p)
    INTERVAL YEAR(p) TO MONTH
    INTERVAL MONTH

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
java.time.Period | ✓ | ✓ | Default. Ignores the `days` part.
java.lang.Integer | ✓ | ✓ | Describes the number of months.
int | ✓ | (✓) | Describes the number of months. Output only if type is not nullable.

**Formats**

The following table shows examples of the INTERVAL YEAR TO MONTH type in different formats.

JSON for data type |

    {"type":"INTERVAL_YEAR_MONTH","nullable":true,"precision":4,"resolution":"YEAR_TO_MONTH"}

---|---
CLI/UI format |

    INTERVAL YEAR(4) TO MONTH

JSON for payload |

    "+2000-02"

CLI/UI format for payload |

    +2000-02

Declare this type by using the above combinations, where `p` is the number of digits of years (_year precision_).

`p` must have a value between _1_ and _4_ (both inclusive). If no year precision is specified, `p` is equal to _2_.

The type must be parameterized to one of these resolutions:

  * Interval of years
  * Interval of years to months
  * Interval of months

An interval of year-month consists of `+years-months` with values ranging from `-9999-11` to `+9999-11`.

The value representation is the same for all types of resolutions. For example, an interval of months of _50_ is always represented in an interval-of-years-to-months format (with default year precision): `+04-02`.

Formatting intervals are tricky, because they have different resolutions:

  * YEAR
  * YEAR_TO_MONTH
  * MONTH

Depending on the resolution, use:

    INTERVAL YEAR(4)
    INTERVAL YEAR(4) TO MONTH
    INTERVAL MONTH

### TIME¶

Represents a time _without_ timezone consisting of `hour:minute:second[.fractional]` with up to nanosecond precision and values ranging from `00:00:00.000000000` to `23:59:59.999999999`.

**Declaration**

    TIME
    TIME(p)

    TIME_WITHOUT_TIME_ZONE
    TIME_WITHOUT_TIME_ZONE(p)

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
java.time.LocalTime | ✓ | ✓ | Default
java.sql.Time | ✓ | ✓ |
java.lang.Integer | ✓ | ✓ | Describes the number of milliseconds of the day.
int | ✓ | (✓) | Describes the number of milliseconds of the day. Output only if type is not nullable.
java.lang.Long | ✓ | ✓ | Describes the number of nanoseconds of the day.
long | ✓ | (✓) | Describes the number of nanoseconds of the day. Output only if type is not nullable.

**Formats**

The following table shows examples of the TIME type in different formats.

JSON for data type |

    {"type":"TIME_WITHOUT_TIME_ZONE","nullable":true,"precision":3}

---|---
CLI/UI format |

    TIME(3)

JSON for payload |

    "10:56:22.541"

CLI/UI format for payload |

    10:56:22.541

Declare this type by using `TIME(p)`, where `p` is the number of digits of fractional seconds (_precision_).

`p` must have a value between _0_ and _9_ (both inclusive). If no precision is specified, `p` is equal to _0_.

Compared to the SQL standard, leap seconds (`23:59:60` and `23:59:61`) are not supported, as the semantics are closer to `java.time.LocalTime`.

A time _with_ timezone is not provided.

`TIME` acts like a pure string and isn’t related to a time zone of any kind, including UTC.

`TIME WITHOUT TIME ZONE` is a synonym for this type.

### TIMESTAMP¶

Represents a timestamp _without_ timezone consisting of `year-month-day hour:minute:second[.fractional]` with up to nanosecond precision and values ranging from `0000-01-01 00:00:00.000000000` to `9999-12-31 23:59:59.999999999`.

**Declaration**

    TIMESTAMP
    TIMESTAMP(p)

    TIMESTAMP WITHOUT TIME ZONE
    TIMESTAMP(p) WITHOUT TIME ZONE

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
java.time.LocalDateTime | ✓ | ✓ | Default
java.sql.Timestamp | ✓ | ✓ |
org.apache.flink.table.data.TimestampData | ✓ | ✓ | Internal data structure

**Formats**

The following table shows examples of the TIMESTAMP type in different formats.

JSON for data type |

    {"type":"TIMESTAMP_WITHOUT_TIME_ZONE","nullable":true,"precision":3}

---|---
CLI/UI format |

    TIMESTAMP(3)

JSON for payload |

    "2023-04-06 10:59:32.628"

CLI/UI format for payload |

    2023-04-06 10:59:32.628

Declare this type by using `TIMESTAMP(p)`, where `p` is the number of digits of fractional seconds (_precision_).

`p` must have a value between _0_ and _9_ (both inclusive). If no precision is specified, `p` is equal to _6_.

A space separates the date and time parts.

Compared to the SQL standard, leap seconds (`23:59:60` and `23:59:61`) are not supported, as the semantics are closer to `java.time.LocalDateTime`.

A conversion from and to `BIGINT` (a JVM `long` type) is not supported, as this would imply a timezone, but this type is time-zone free. For more `java.time.Instant`-like semantics use `TIMESTAMP_LTZ`.

`TIMESTAMP` acts like a pure string and isn’t related to a time zone of any kind, including UTC.

`TIMESTAMP WITHOUT TIME ZONE` is a synonym for this type.

### TIMESTAMP_LTZ¶

Represents a timestamp with the _local_ timezone consisting of `year-month-day hour:minute:second[.fractional] zone` with up to nanosecond precision and values ranging from `0000-01-01 00:00:00.000000000 +14:59` to `9999-12-31 23:59:59.999999999 -14:59`.

**Declaration**

    TIMESTAMP_LTZ
    TIMESTAMP_LTZ(p)

    TIMESTAMP WITH LOCAL TIME ZONE
    TIMESTAMP(p) WITH LOCAL TIME ZONE

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
java.time.Instant | ✓ | ✓ | Default
java.lang.Integer | ✓ | ✓ | Describes the number of seconds since Unix epoch.
int | ✓ | (✓) | Describes the number of seconds since Unix epoch. Output only if type is not nullable.
java.lang.Long | ✓ | ✓ | Describes the number of milliseconds since Unix epoch.
long | ✓ | (✓) | Describes the number of milliseconds since Unix epoch. Output only if type is not nullable.
java.sql.Timestamp | ✓ | ✓ | Describes the number of milliseconds since Unix epoch.
org.apache.flink.table.data.TimestampData | ✓ | ✓ | Internal data structure

**Formats**

The following table shows examples of the TIMESTAMP_LTZ type in different formats.

JSON for data type |

    {"type":"TIMESTAMP_WITH_LOCAL_TIME_ZONE","nullable":true,"precision":3}

---|---
CLI/UI format |

    TIMESTAMP(3) WITH LOCAL TIME ZONE

JSON for payload |

    "2023-04-06 11:06:47.224"

CLI/UI format for payload |

    2023-04-06 11:06:47.224

Declare this type by using `TIMESTAMP_LTZ(p)`, where `p` is the number of digits of fractional seconds (_precision_).

`p` must have a value between _0_ and _9_ (both inclusive). If no precision is specified, `p` is equal to _6_.

Leap seconds (`23:59:60` and `23:59:61`) are not supported, as the semantics are closer to `java.time.OffsetDateTime`.

Compared to `TIMESTAMP WITH TIME ZONE`, the timezone offset information is _not_ stored physically in every datum. Instead, the type assumes `java.time.Instant` semantics in the UTC timezone at the edges of the table ecosystem. Every datum is interpreted in the local timezone configured in the current session for computation and visualization.

This type fills the gap between time-zone free and time-zone mandatory timestamp types by allowing the interpretation of UTC timestamps according to the configured session timezone.

`TIMESTAMP_LTZ` resembles a `TIMESTAMP` without a timezone, but the string always considers the sessions/query’s timezone. Internally, it is always in the UTC time zone.

If you require the short format, prefer `TIMESTAMP_LTZ(3)`.

`TIMESTAMP WITH LOCAL TIME ZONE` is a synonym for this type.

### TIMESTAMP and TIMESTAMP_LTZ comparison¶

Although TIMESTAMP and TIMESTAMP_LTZ are similarly named, they represent different concepts.

TIMESTAMP_LTZ

  * TIMESTAMP_LTZ in SQL is similar to the `Instant` class in Java.
  * TIMESTAMP_LTZ represents a _moment_ , or a specific point in the UTC timeline.
  * TIMESTAMP_LTZ stores time as a UTC integer, which can be converted dynamically to every other timezone.
  * When printing or casting TIMESTAMP_LTZ as a character string, the `sql.local-time-zone` setting is considered.

TIMESTAMP

  * TIMESTAMP in SQL is similar to `LocalDateTime` in Java.
  * TIMESTAMP has no time zone or offset from UTC, so it can’t represent a moment.
  * TIMESTAMP stores time as character string, not related to any timezone.

### TIMESTAMP WITH TIME ZONE¶

Represents a timestamp with time zone consisting of `year-month-day hour:minute:second[.fractional]` zone with up to nanosecond precision and values ranging from `0000-01-01 00:00:00.000000000 +14:59` to `9999-12-31 23:59:59.999999999 -14:59`.

**Declaration**

    TIMESTAMP WITH TIME ZONE
    TIMESTAMP(p) WITH TIME ZONE

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
java.time.OffsetDateTime | ✓ | ✓ | Default
java.time.ZonedDateTime | ✓ |  | Ignores the zone ID

Compared to TIMESTAMP_LTZ, the time zone offset information is stored physically in every datum. It is used individually for every computation, visualization, or communication to external systems.

## Collection data types¶

### ARRAY¶

Represents an array of elements with same subtype.

**Declaration**

    ARRAY<t>
    t ARRAY

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
t[] | ✓ | ✓ | Default. Depends on the subtype.
java.util.List<t> | ✓ | ✓ |
subclass of java.util.List<t> | ✓ |  |
org.apache.flink.table.data.ArrayData | ✓ | ✓ | Internal data structure

**Formats**

The following table shows examples of the ARRAY type in different formats.

JSON for data type |

    {"type":"ARRAY","nullable":true,"elementType":{"type":"INTEGER","nullable":true}}

---|---
CLI/UI format |

    ARRAY<INT>

JSON for payload |

    ["1", "2", "3", null]

CLI/UI format for payload |

    [1, 2, 3, NULL]

Declare this type by using `ARRAY<t>`, where `t` is the data type of the contained elements.

Compared to the SQL standard, the maximum cardinality of an array cannot be specified and is fixed at _2,147,483,647_. Also, any valid type is supported as a subtype.

`t ARRAY` is a synonym for being closer to the SQL standard. For example, `INT ARRAY` is equivalent to `ARRAY<INT>`.

### MAP¶

Represents an associative array that maps keys (including `NULL`) to values (including `NULL`).

**Declaration**

    MAP<kt, vt>

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
java.util.Map<kt, vt> | ✓ | ✓ | Default
subclass of java.util.Map<kt, vt> | ✓ |  |
org.apache.flink.table.data.MapData | ✓ | ✓ | Internal data structure

**Formats**

The following table shows examples of the MAP type in different formats.

JSON for data type |

    {"type":"MAP","nullable":true,"keyType":{"type":"INTEGER","nullable":true},"valueType":{"type":"VARCHAR","nullable":true,"length":2147483647}}

---|---
CLI/UI format |

    MAP<STRING>

JSON for payload |

    [["1", "a"], ["2", "b"], [null, "c"]]

CLI/UI format for payload |

    {1=a, 2=b, NULL=c}

Declare this type by using `MAP<kt, vt>` where `kt` is the data type of the key elements and `vt` is the data type of the value elements.

A map can’t contain duplicate keys. Each key can map to at most one value.

There is no restriction of element types. It is the responsibility of the user to ensure uniqueness.

The map type is an extension to the SQL standard.

### MULTISET¶

Represents a multiset (=bag).

**Declaration**

    MULTISET<t>
    t MULTISET

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
java.util.Map<t, java.lang.Integer> | ✓ | ✓ | Default. Assigns each value to an integer multiplicity.
subclass of java.util.Map<t, java.lang.Integer> | ✓ |  |
org.apache.flink.table.data.MapData | ✓ | ✓ | Internal data structure

**Formats**

The following table shows examples of the MULTISET type in different formats.

JSON for data type |

    {"type":"MULTISET","nullable":true,"elementType":{"type":"INTEGER","nullable":true}}

---|---
CLI/UI format |

    MULTISET<INT>

JSON for payload |

    [["a", "1"], ["b", "2"], [null, "1"]]

CLI/UI format for payload |

    {a=1, b=2, NULL=1}

Declare this type by using `MULTISET<t>` where `t` is the data type of the contained elements.

Unlike a set, the multiset allows for multiple instances for each of its elements with a common subtype. Each unique value (including `NULL`) is mapped to some multiplicity.

There is no restriction of element types; it is the responsibility of the user to ensure uniqueness.

`t MULTISET` is a synonym for being closer to the SQL standard. For example, `INT MULTISET` is equivalent to `MULTISET<INT>`.

### ROW¶

Represents a sequence of fields.

**Declaration**

    ROW<name0 type0, name1 type1, ...>
    ROW<name0 type0 'description0', name1 type1 'description1', ...>

    ROW(name0 type0, name1 type1, ...)
    ROW(name0 type0 'description0', name1 type1 'description1', ...)

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
org.apache.flink.types.Row | ✓ | ✓ | Default
org.apache.flink.table.data.RowData | ✓ | ✓ | Internal data structure

**Formats**

The following table shows examples of the ROW type in different formats.

JSON for data type |

    {"type":"ROW","nullable":true,"fields":[{"name":"a","fieldType":{"type":"INTEGER","nullable":true}},{"name":"b","fieldType":{"type":"VARCHAR","nullable":true,"length":2147483647}}]}

---|---
CLI/UI format |

    MULTISET<INT>

JSON for payload |

    [["a", "1"], ["b", "2"], [null, "1"]]

CLI/UI format for payload |

    {a=1, b=2, NULL=1}

Declare this type by using `ROW<n0 t0 'd0', n1 t1 'd1', ...>`, where `n` is the unique name of a field, `t` is the logical type of a field, `d` is the description of a field.

A field consists of a field name, field type, and an optional description. The most specific type of a row of a table is a row type. In this case, each column of the row corresponds to the field of the row type that has the same ordinal position as the column.

To create a table with a row type, use the following syntax:

    CREATE TABLE table_with_row_types (
       `Customer` ROW<name STRING, age INT>,
       `Order` ROW<id BIGINT, title STRING>
    );

To insert a row into a table with a row type, use the following syntax:

    INSERT INTO table_with_row_types VALUES
       (('Alice', 30), (101, 'Book')),
       (('Bob', 25), (102, 'Laptop')),
       (('Charlie', 35), (103, 'Phone')),
       (('Diana', 28), (104, 'Tablet')),
       (('Eve', 22), (105, 'Headphones'));

To work with fields from a row, use dot notation:

    SELECT `Customer`.name, `Customer`.age, `Order`.id, `Order`.title
    FROM table_with_row_types
    WHERE `Customer`.age > 30;

Compared to the SQL standard, an optional field description simplifies the handling with complex structures.

A row type is similar to the `STRUCT` type known from other non-standard-compliant frameworks.

`ROW(...)` is a synonym for being closer to the SQL standard. For example, `ROW(fieldOne INT, fieldTwo BOOLEAN)` is equivalent to `ROW<fieldOne INT, fieldTwo BOOLEAN>`.

If the fields of the data type contain characters other than `[A-Za-z_]`, use escaping notation. Double backticks escape the backtick character, for example:

    ROW<`a-b` INT, b STRING, `weird_col``_umn` STRING>

Rows fields can contain comments, for example:

    {"type":"ROW","nullable":true,"fields":[{"name":"a","fieldType":{"type":"INTEGER","nullable":true},"description":"hello"}]}

Format using single quotes. Double single quotes escape single quotes, for example:

    ROW<a INT 'This field''s content'>

## Other data types¶

### BOOLEAN¶

Represents a boolean with a (possibly) three-valued logic of `TRUE`, `FALSE`, and `UNKNOWN`.

**Declaration**

    BOOLEAN

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
java.lang.Boolean | ✓ | ✓ | Default
boolean | ✓ | (✓) | Output only if type is not nullable.

**Formats**

The following table shows examples of the BOOLEAN type in different formats.

JSON for data type |

    {"type":"BOOLEAN","nullable":true}

---|---
CLI/UI format |

    NULL

JSON for payload |

    null

CLI/UI format for payload |

    NULL

### NULL¶

Data type for representing untyped `NULL` values.

**Declaration**

    NULL

**Bridging to JVM types**

Java Type | Input | Output | Notes
---|---|---|---
java.lang.Object | ✓ | ✓ | Default
any class |  | (✓) | Any non-primitive type.

**Formats**

The following table shows examples of the NULL type in different formats.

JSON for data type |

    {"type":"NULL"}

---|---
CLI/UI format |

    NULL

JSON for payload |

    null

CLI/UI format for payload |

    NULL

The NULL type is an extension to the SQL standard. A NULL type has no other value except `NULL`, thus, it can be cast to any nullable type similar to JVM semantics.

This type helps in representing unknown types in API calls that use a `NULL` literal as well as bridging to formats such as JSON or Avro that define such a type as well.

This type is not very useful in practice and is described here only for completeness.

## Casting¶

Flink SQL can perform casting between a defined input type and target type. While some casting operations can always succeed regardless of the input value, others can fail at runtime when there’s no way to create a value for the target type. For example, it’s always possible to convert `INT` to `STRING`, but you can’t always convert a `STRING` to `INT`.

During the planning stage, the query validator rejects queries for invalid type pairs with a `ValidationException`, for example, when trying to cast a `TIMESTAMP` to an `INTERVAL`. Valid type pairs that can fail at runtime are accepted by the query validator, but this requires you to handle cast failures correctly.

In Flink SQL, casting can be performed by using one of these two built-in functions:

  * [CAST](functions/comparison-functions.html#flink-sql-cast-function): The regular cast function defined by the SQL standard. It can fail the job if the cast operation is fallible and the provided input is not valid. Type inference preserves the nullability of the input type.
  * [TRY_CAST](functions/comparison-functions.html#flink-sql-try-cast-function): An extension to the regular cast function that returns `NULL` if the cast operation fails. Its return type is always nullable.

For example:

    -- returns 42 of type INT NOT NULL
    SELECT CAST('42' AS INT);

    -- returns NULL of type VARCHAR
    SELECT CAST(NULL AS VARCHAR);

    -- throws an exception and fails the job
    SELECT CAST('non-number' AS INT);

    -- returns 42 of type INT
    SELECT TRY_CAST('42' AS INT);

    -- returns NULL of type VARCHAR
    SELECT TRY_CAST(NULL AS VARCHAR);

    -- returns NULL of type INT
    SELECT TRY_CAST('non-number' AS INT);

    -- returns 0 of type INT NOT NULL
    SELECT COALESCE(TRY_CAST('non-number' AS INT), 0);

The following matrix shows the supported cast pairs, where “Y” means supported, “!” means fallible, and “N” means unsupported:

Input / Target | CHAR¹ / VARCHAR¹ / STRING | BINARY¹ / VARBINARY¹ / BYTES | BOOLEAN | DECIMAL | TINYINT | SMALLINT | INTEGER | BIGINT | FLOAT | DOUBLE | DATE | TIME | TIMESTAMP | TIMESTAMP_LTZ | INTERVAL | ARRAY | MULTISET | MAP | ROW
---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---
CHAR / VARCHAR / STRING | Y | ! | ! | ! | ! | ! | ! | ! | ! | ! | ! | ! | ! | ! | N | N | N | N | N
BINARY / VARBINARY / BYTES | Y | Y | N | N | N | N | N | N | N | N | N | N | N | N | N | N | N | N | N
BOOLEAN | Y | N | Y | Y | Y | Y | Y | Y | Y | Y | N | N | N | N | N | N | N | N | N
DECIMAL | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | N | N | N | N | N | N | N | N
TINYINT | Y | N | Y | Y | Y | Y | Y | Y | Y | Y | N | N | N² | N² | N | N | N | N | N
SMALLINT | Y | N | Y | Y | Y | Y | Y | Y | Y | Y | N | N | N² | N² | N | N | N | N | N
INTEGER | Y | N | Y | Y | Y | Y | Y | Y | Y | Y | N | N | N² | N² | Y⁵ | N | N | N | N
BIGINT | Y | N | Y | Y | Y | Y | Y | Y | Y | Y | N | N | N² | N² | Y⁶ | N | N | N | N
FLOAT | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | N | N | N | N | N | N | N | N
DOUBLE | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | N | N | N | N | N | N | N | N
DATE | Y | N | N | N | N | N | N | N | N | N | Y | N | Y | Y | N | N | N | N | N
TIME | Y | N | N | N | N | N | N | N | N | N | N | Y | Y | Y | N | N | N | N | N
TIMESTAMP | Y | N | N | N | N | N | N | N | N | N | Y | Y | Y | Y | N | N | N | N | N
TIMESTAMP_LTZ | Y | N | N | N | N | N | N | N | N | N | Y | Y | Y | Y | N | N | N | N | N
INTERVAL | Y | N | N | N | N | N | Y⁵ | Y⁶ | N | N | N | N | N | N | Y | N | N | N | N
ARRAY | Y | N | N | N | N | N | N | N | N | N | N | N | N | N | N | !³ | N | N | N
MULTISET | Y | N | N | N | N | N | N | N | N | N | N | N | N | N | N | N | !³ | N | N
MAP | Y | N | N | N | N | N | N | N | N | N | N | N | N | N | N | N | N | !³ | N
ROW | Y | N | N | N | N | N | N | N | N | N | N | N | N | N | N | N | N | N | !³

Notes:

  1. All the casting to constant length or variable length also trims and pads, according to the type definition.
  2. `TO_TIMESTAMP` and `TO_TIMESTAMP_LTZ` must be used instead of `CAST`/ `TRY_CAST`.
  3. Supported iff the children type pairs are supported. Fallible iff the children type pairs are fallible.
  4. Supported iff the `RAW` class and serializer are equals.
  5. Supported iff `INTERVAL` is a `MONTH TO YEAR` range.
  6. Supported iff `INTERVAL` is a `DAY TO TIME` range.

Note

A cast of a `NULL` value always returns `NULL`, regardless of whether the function used is [CAST](functions/comparison-functions.html#flink-sql-cast-function) or [TRY_CAST](functions/comparison-functions.html#flink-sql-try-cast-function).

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
