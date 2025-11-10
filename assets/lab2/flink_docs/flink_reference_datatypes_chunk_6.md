---
document_id: flink_reference_datatypes_chunk_6
source_file: flink_reference_datatypes.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/datatypes.html
title: Flink SQL Data Types in Confluent Cloud for Apache Flink
chunk_index: 6
total_chunks: 10
---

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
