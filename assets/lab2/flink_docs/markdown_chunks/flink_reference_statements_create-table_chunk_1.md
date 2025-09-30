---
document_id: flink_reference_statements_create-table_chunk_1
source_file: flink_reference_statements_create-table.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-table.html
title: SQL CREATE TABLE Statement in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 14
---

# CREATE TABLE Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables creating tables backed by Apache Kafka® topics by using the CREATE TABLE statement. With Flink tables, you can run SQL queries on streaming data in Kafka topics.

## Syntax¶

    CREATE TABLE [IF NOT EXISTS] [catalog_name.][db_name.]table_name
      (
        { <physical_column_definition> |
          <metadata_column_definition> |
          <computed_column_definition> |
          <column_in_vector_db_provider> }[ , ...n]
        [ <watermark_definition> ]
        [ <table_constraint> ][ , ...n]
      )
      [COMMENT table_comment]
      [DISTRIBUTED BY (distribution_column_name1, distribution_column_name2, ...) INTO n BUCKETS]
      WITH (key1=value1, key2=value2, ...)
      [ LIKE source_table [( <like_options> )] | AS select_query ]

    <physical_column_definition>:
      column_name column_type [ <column_constraint> ] [COMMENT column_comment]

    <metadata_column_definition>:
      column_name column_type METADATA [ FROM metadata_key ] [ VIRTUAL ]

    <computed_column_definition>:
      column_name AS computed_column_expression [COMMENT column_comment]

    <column_in_vector_db_provider>
      column_name column_type

    <watermark_definition>:
      WATERMARK FOR rowtime_column_name AS watermark_strategy_expression

    <table_constraint>:
      [CONSTRAINT constraint_name] PRIMARY KEY (column_name, ...) NOT ENFORCED

    <like_options>:
    {
     { INCLUDING | EXCLUDING } { ALL | CONSTRAINTS | PARTITIONS } |
     { INCLUDING | EXCLUDING | OVERWRITING } { GENERATED | OPTIONS | WATERMARKS }
    }

## Description¶

Register a table into the current or specified catalog. When a table is registered, you can use it in SQL queries.

The CREATE TABLE statement always creates a backing Kafka topic as well as the corresponding schema subjects for key and value.

Trying to create a table with a name that exists in the catalog causes an exception.

The table name can be in these formats:

* `catalog_name.db_name.table_name`: The table is registered with the catalog named “catalog_name” and the database named “db_name”.
* `db_name.table_name`: The table is registered into the current catalog of the execution table environment and the database named “db_name”.
* `table_name`: The table is registered into the current catalog and the database of the execution table environment.

A table registered with the CREATE TABLE statement can be used as both table source and table sink. Flink can’t determine whether the table is used as a source or a sink until it’s referenced in a [DML query](../queries/overview.html#flink-sql-queries).

The following sections show the options and clauses that are available with the CREATE TABLE statement.

* Physical / Regular Columns
* Metadata columns
* Computed columns
* System columns
* Watermark clause
* PRIMARY KEY constraint
* DISTRIBUTED BY clause
* CREATE TABLE AS SELECT (CTAS)
* LIKE
* WITH options

## Usage¶

This following CREATE TABLE statement registers a table named `t1` in the current catalog. Also, it creates a backing Kafka topic and corresponding value-schema. By default, the table is registered as append-only, uses AVRO serializers, and reads from the earliest offset.

    CREATE TABLE t1 (
      `id` BIGINT,
      `name` STRING,
      `age` INT,
      `salary` DECIMAL(10,2),
      `active` BOOLEAN,
      `created_at` TIMESTAMP_LTZ(3)
    );

You can override defaults by specifying WITH options. The following SQL registers the table in retraction mode, so you can use the table to sink the results of a [streaming join](../queries/joins.html#flink-sql-joins).

    CREATE TABLE t2 (
      `id` BIGINT,
      `name` STRING,
      `age` INT,
      `salary` DECIMAL(10,2),
      `active` BOOLEAN,
      `created_at` TIMESTAMP_LTZ(3)
    ) WITH (
      'changelog.mode' = 'retract'
    );

## Physical / Regular Columns¶

Physical or regular columns are the columns that define the structure of the table and the data types of its fields.

Each physical column is defined by a name and a data type, and optionally, a column constraint. You can use the column constraint to specify additional properties of the column, such as whether it is a unique key.

Example

The following SQL shows how to declare physical columns of various types in a table named `t1`. For available column types, see [Data Types](../datatypes.html#flink-sql-datatypes).

    CREATE TABLE t1 (
      `id` BIGINT,
      `name` STRING,
      `age` INT,
      `salary` DECIMAL(10,2),
      `active` BOOLEAN,
      `created_at` TIMESTAMP_LTZ(3)
    );
