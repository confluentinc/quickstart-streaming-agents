---
document_id: flink_reference_datatypes_chunk_4
source_file: flink_reference_datatypes.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/datatypes.html
title: Flink SQL Data Types in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 10
---

this type doesn’t take parameters.

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
