---
document_id: flink_reference_flink-sql-information-schema_chunk_1
source_file: flink_reference_flink-sql-information-schema.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/flink-sql-information-schema.html
title: SQL Information Schema in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 4
---

# Information Schema in Confluent Cloud for Apache Flink¶

An _information schema_ , or data dictionary, is a standard SQL schema with a collection of predefined views that enable accessing metadata about objects in Confluent Cloud for Apache Flink®. The Confluent INFORMATION_SCHEMA is based on the [SQL-92 ANSI Information Schema](https://datacadamia.com/data/type/relation/sql/information_schema), with the addition of views and functions that are specific to Confluent Cloud for Apache Flink. The ANSI standard uses “catalog” to refer to a database. In Confluent Cloud, “schema” refers to a database. Conceptually, the terms are equivalent.

The views in the INFORMATION_SCHEMA provide information about database objects, such as tables, columns, and constraints. The views are organized into tables that you can query by using standard SQL statements.

For example, you can use the INFORMATION_SCHEMA.COLUMNS table to get details about the columns in a table, like the column name, data type, and whether it allows null values.

Similarly, you can use the INFORMATION_SCHEMA.TABLES table to get information about the tables in a catalog, like the table name, schema, and number of rows.

Every Flink catalog has a corresponding INFORMATION_SCHEMA, so you can always run a statement like `SELECT (...) FROM <catalog-name>.INFORMATION_SCHEMA.TABLES WHERE (...)`.

Global views are available in every INFORMATION_SCHEMA, which means that you can query for information across catalogs. For example, you can query the global INFORMATION_SCHEMA.CATALOGS view to list all catalogs.

The information schema is a powerful tool for querying metadata about your Flink catalogs and databases, and you can use it for a variety of purposes, such as generating reports, documenting a schema, and troubleshooting performance issues.

The following views are supported in the Confluent INFORMATION_SCHEMA:

  * CATALOGS
  * COLUMNS
  * INFORMATION_SCHEMA_CATALOG_NAME
  * KEY_COLUMN_USAGE
  * SCHEMATA / DATABASES
  * TABLES
  * TABLE_CONSTRAINTS
  * TABLE_OPTIONS

## Query syntax in INFORMATION_SCHEMA¶

Metadata queries on the INFORMATION_SCHEMA tables support the following syntax.

Supported data types:

  * INT
  * STRING

Supported operators:

  * SELECT
  * WHERE
  * UNION ALL

Supported expressions:

  * CAST(NULL AS dt), CAST(x as dt)
  * UNION ALL (see this example)
  * AND, OR
  * = , <>, IS NULL, IS NOT NULL
  * AS
  * STRING and INT literals

The following limitations apply to INFORMATION_SCHEMA:

  * You can use INFORMATION_SCHEMA views only in SELECT statements, not in INSERT INTO statements.
  * You can’t use INFORMATION_SCHEMA in joins with real tables.
  * Only the previously listed equality and basic expressions are supported.
