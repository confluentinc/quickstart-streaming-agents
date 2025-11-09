---
document_id: flink_reference_table-api_chunk_5
source_file: flink_reference_table-api.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/table-api.html
title: Table API on Confluent Cloud for Apache Flink
chunk_index: 5
total_chunks: 5
---

### Confluent table descriptor¶

A table descriptor for creating tables located in Confluent Cloud programmatically.

Compared to the regular Flink class, the `ConfluentTableDescriptor` class adds support for Confluent’s system columns and convenience methods for working with Confluent tables.

The `for_managed()` method corresponds to `TableDescriptor.for_connector("confluent")`.

JavaPython

    TableDescriptor descriptor = ConfluentTableDescriptor.forManaged()
      .schema(
        Schema.newBuilder()
          .column("i", DataTypes.INT())
          .column("s", DataTypes.INT())
          .watermark("$rowtime", $("$rowtime").minus(lit(5).seconds())) // Access $rowtime system column
          .build())
      .build();

    env.createTable("t1", descriptor);

    from pyflink.table.confluent import ConfluentTableDescriptor
    from pyflink.table import Schema, DataTypes
    from pyflink.table.expressions import col, lit

    descriptor = ConfluentTableDescriptor.for_managed() \
      .schema(
         Schema.new_builder()
           .column("i", DataTypes.INT())
           .column("s", DataTypes.INT())
           .watermark("$rowtime", col("$rowtime").minus(lit(5).seconds)) # Access $rowtime system column
           .build()) \
      .build()

    env.createTable("t1", descriptor)

## Known limitations¶

The Table API plugin is in Open Preview stage.

### Unsupported by Table API Plugin¶

The following features are not supported.

* Temporary catalog objects (including tables, views, functions)
* Custom modules
* Custom catalogs
* User-defined functions (including system functions)
* Anonymous, inline objects (including functions, data types)
* CompiledPlan features are not supported
* Batch mode
* Restrictions from Confluent Cloud
  * custom connectors/formats
  * processing time operations
  * structured data types
  * many configuration options
  * limited SQL syntax
  * batch execution mode

### Issues in Apache Flink¶

* Both catalog and database must be set, or identifiers must be fully qualified. A mixture of setting a current catalog and using two-part identifiers can cause errors.
* String concatenation with `.plus` causes errors. Instead, use `Expressions.concat`.
* Selecting `.rowtime` in windows causes errors.
* Using `.limit()` can cause errors.
