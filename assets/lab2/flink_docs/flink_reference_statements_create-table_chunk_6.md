---
document_id: flink_reference_statements_create-table_chunk_6
source_file: flink_reference_statements_create-table.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-table.html
title: SQL CREATE TABLE Statement in Confluent Cloud for Apache Flink
chunk_index: 6
total_chunks: 14
---

SELECT id, name FROM source_table;

## LIKE¶

The CREATE TABLE LIKE clause enables creating a new table with the same schema as an existing table. It is a combination of SQL features and can be used to extend or exclude certain parts of the original table. The clause must be defined at the top-level of a CREATE statement and applies to multiple parts of the table definition.

Use the LIKE options to control the merging logic of table features. You can control the merging behavior of:

  * CONSTRAINTS - Constraints such as primary key. and unique keys.
  * GENERATED - Computed columns.
  * METADATA - Metadata columns.
  * OPTIONS - Table options.
  * PARTITIONS - Partition options.
  * WATERMARKS - Watermark strategies.

with three different merging strategies:

  * INCLUDING - Includes the feature of the source table and fails on duplicate entries, for example, if an option with the same key exists in both tables.
  * EXCLUDING - Does not include the given feature of the source table.
  * OVERWRITING - Includes the feature of the source table, overwrites duplicate entries of the source table with properties of the new table. For example, if an option with the same key exists in both tables, the option from the current statement is used.

Additionally, you can use the INCLUDING/EXCLUDING ALL option to specify what should be the strategy if no specific strategy is defined. For example, if you use EXCLUDING ALL INCLUDING WATERMARKS, only the watermarks are included from the source table.

If you provide no LIKE options, INCLUDING ALL OVERWRITING OPTIONS is used as a default.

### Example¶

The following CREATE TABLE statement defines a table named `t` that has 5 physical columns and three metadata columns.

    CREATE TABLE t (
      `user_id` BIGINT,
      `item_id` BIGINT,
      `price` DOUBLE,
      `behavior` STRING,
      `created_at` TIMESTAMP(3),
      `price_with_tax` AS `price` * 1.19,
      `event_time` TIMESTAMP_LTZ(3) METADATA FROM 'timestamp',
      `partition` BIGINT METADATA VIRTUAL,
      `offset` BIGINT METADATA VIRTUAL
    );

You can run the following CREATE TABLE LIKE statement to define table `t_derived`, which contains the physical and computed columns of `t`, drops the metadata and default watermark strategy, and applies a custom watermark strategy on `event_time`.

    CREATE TABLE t_derived (
        WATERMARK FOR `created_at` AS `created_at` - INTERVAL '5' SECOND
    )
    LIKE t (
        EXCLUDING WATERMARKS
        EXCLUDING METADATA
    );
