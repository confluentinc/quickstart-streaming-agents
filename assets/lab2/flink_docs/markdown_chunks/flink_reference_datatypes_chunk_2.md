---
document_id: flink_reference_datatypes_chunk_2
source_file: flink_reference_datatypes.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/datatypes.html
title: Flink SQL Data Types in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 10
---

but it exists in protocols.

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
