---
document_id: flink_reference_datatypes_chunk_7
source_file: flink_reference_datatypes.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/datatypes.html
title: Flink SQL Data Types in Confluent Cloud for Apache Flink
chunk_index: 7
total_chunks: 10
---

or communication to external systems.

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
