---
document_id: flink_reference_datatypes_chunk_3
source_file: flink_reference_datatypes.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/datatypes.html
title: Flink SQL Data Types in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 10
---

but it exists in protocols.

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
