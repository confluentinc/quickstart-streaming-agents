---
document_id: flink_reference_datatypes_chunk_5
source_file: flink_reference_datatypes.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/datatypes.html
title: Flink SQL Data Types in Confluent Cloud for Apache Flink
chunk_index: 5
total_chunks: 10
---

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
