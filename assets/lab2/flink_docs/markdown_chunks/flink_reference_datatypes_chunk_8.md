---
document_id: flink_reference_datatypes_chunk_8
source_file: flink_reference_datatypes.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/datatypes.html
title: Flink SQL Data Types in Confluent Cloud for Apache Flink
chunk_index: 8
total_chunks: 10
---

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
