---
source_url: https://docs.confluent.io/cloud/current/flink/reference/flink-sql-information-schema.html
title: SQL Information Schema in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'flink-sql-information-schema.html']
scraped_date: 2025-09-05T13:47:13.402402
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

## Available views¶

### CATALOGS¶

The global catalogs view.

The rows returned are limited to the schemas that you have permission to interact with.

This view is an extension to the SQL standard.

Column Name | Data Type | Nullable | Standard | Description
---|---|---|---|---
CATALOG_ID | STRING | No | No | The ID of the catalog/environment, for example, `env-xmzdkk`.
CATALOG_NAME | STRING | No | No | The human readable name of the catalog/environment, for example, `default`.

Example

Run the following code to query for all catalogs across environments.

    SELECT
      `CATALOG_ID`,
      `CATALOG_NAME`
    FROM `INFORMATION_SCHEMA`.`CATALOGS`;

### COLUMNS¶

Describes columns of tables and virtual tables (views) in the catalog.

Column Name | Data Type | Nullable | Standard | Description
---|---|---|---|---
COLUMN_NAME | STRING | No | Yes | Column reference.
COMMENT | STRING | Yes | No | An optional comment that describes the relation.
DATA_TYPE | STRING | No | Yes | Type root, for example, VARCHAR or ROW.
DISTRIBUTION_ORDINAL_POSITION | INT | Yes | No | If the table IS_DISTRIBUTED, contains the position of the key in a DISTRIBUTED BY clause.
FULL_DATA_TYPE | STRING | No | No | Fully qualified data type. for example, VARCHAR(32) or ROW<…>.
GENERATION_EXPRESSION | STRING | Yes | Yes | For computed columns.
IS_GENERATED | STRING | No | Yes | Indicates whether column is a computed column. Values are YES or NO.
IS_HIDDEN | STRING | No | No | Indicates whether a column is a system column. Values are YES or NO.
IS_METADATA | STRING | No | No | Indicates whether column is a metadata column. Values are YES or NO.
IS_PERSISTED | STRING | No | No | Indicates whether a metadata column is stored during INSERT INTO. Also YES if a physical column. Values are YES or NO.
METADATA_KEY | STRING | Yes | No | For metadata columns.
TABLE_CATALOG | STRING | No | Yes | The human readable name of the catalog.
TABLE_CATALOG_ID | STRING | No | No | The ID of the catalog.
TABLE_NAME | STRING | No | Yes | The name of the relation.
TABLE_SCHEMA | STRING | No | Yes | The human readable name of the database.
TABLE_SCHEMA_ID | STRING | No | No | The ID of the database.

Examples

This example shows a complex query. The complexity comes from reducing the number of requests. Because the views are in normal form, instead of issuing three requests, you can batch them into single one by using UNION ALL. UNION ALL avoids the need for various inner/outer joins. The result is a sparse table that contains different “sections”.

The overall schema looks like this:

    (
      section,
      column_name,
      column_pos,
      column_type,
      constraint_name,
      constraint_type,
      constraint_enforced
    )

Run the following code to list columns, like name, position, data type, and their primary key characteristics.

    (
      SELECT
        'COLUMNS' AS `section`,
        `COLUMN_NAME` AS `column_name`,
        `ORDINAL_POSITION` AS `column_pos`,
        `FULL_DATA_TYPE` AS `column_type`,
        CAST(NULL AS STRING) AS `constraint_name`,
        CAST(NULL AS STRING) AS `constraint_type`,
        CAST(NULL AS STRING) AS `constraint_enforced`
      FROM
        `<current-catalog>`.`INFORMATION_SCHEMA`.`COLUMNS`
      WHERE
        `TABLE_CATALOG` = '<current-catalog>' AND
        `TABLE_SCHEMA` = '<current-database>' AND
        `TABLE_NAME` = '<current-table>' AND
        `IS_HIDDEN` = 'NO'

    )
    UNION ALL
    (
      SELECT
        'TABLE_CONSTRAINTS' AS `section`,
        CAST(NULL AS STRING) AS `column_name`,
        CAST(NULL AS INT) AS `column_pos`,
        CAST(NULL AS STRING) AS `column_type`,
        `CONSTRAINT_NAME` AS `constraint_name`,
        `CONSTRAINT_TYPE` AS `constraint_type`,
        `ENFORCED` AS `constraint_enforced`
      FROM
        `<<CURRENT_CAT>>`.`INFORMATION_SCHEMA`.`TABLE_CONSTRAINTS`
      WHERE
        `CONSTRAINT_CATALOG` = '<current-catalog>' AND
        `CONSTRAINT_SCHEMA` = '<current-database>' AND
        `TABLE_CATALOG` = '<current-catalog>' AND
        `TABLE_SCHEMA` = '<current-database>' AND
        `TABLE_NAME` = '<current-table>'
    )
    UNION ALL
    (
      SELECT
        'KEY_COLUMN_USAGE' AS `section`,
        `COLUMN_NAME` AS `column_name`,
        `ORDINAL_POSITION` AS `column_pos`,
        CAST(NULL AS STRING) AS `column_type`,
        `CONSTRAINT_NAME` AS `constraint_name`,
        CAST(NULL AS STRING) AS `constraint_type`,
        CAST(NULL AS STRING) AS `constraint_enforced`
      FROM
        `<<CURRENT_CAT>>`.`INFORMATION_SCHEMA`.`KEY_COLUMN_USAGE`
      WHERE
        `TABLE_CATALOG` = '<current-catalog>' AND
        `TABLE_SCHEMA` = '<current-database>' AND
        `TABLE_NAME` = '<current-table>'
    );

### INFORMATION_SCHEMA_CATALOG_NAME¶

Local catalog view. Returns the name of the current information schema’s catalog.

Column Name | Data Type | Nullable | Standard | Description
---|---|---|---|---
CATALOG_ID | STRING | No | No | The ID of the catalog/environment, for example, `env-xmzdkk`.
CATALOG_NAME | STRING | No | Yes | The human readable name of the catalog/environment, for example, `default`.

Example

Run the following code to query for the name of this information schema’s catalog.

    SELECT
      `CATALOG_ID`,
      `CATALOG_NAME`
    FROM `INFORMATION_SCHEMA`.`INFORMATION_SCHEMA_CATALOG_NAME`

### KEY_COLUMN_USAGE¶

Side view of TABLE_CONSTRAINTS for key columns.

Column Name | Data Type | Nullable | Standard | Description
---|---|---|---|---
COLUMN_NAME | STRING | No | Yes | The name of the constrained column.
CONSTRAINT_CATALOG | STRING | No | Yes | Catalog name containing the constraint.
CONSTRAINT_CATALOG_ID | STRING | No | No | Catalog ID containing the constraint.
CONSTRAINT_SCHEMA | STRING | No | Yes | Schema name containing the constraint.
CONSTRAINT_SCHEMA_ID | STRING | No | No | Schema ID containing the constraint.
CONSTRAINT_NAME | STRING | No | Yes | Name of the constraint.
ORDINAL_POSITION | INT | No | Yes | The ordinal position of the column within the constraint key (starting at 1).
TABLE_CATALOG | STRING | No | Yes | The human readable name of the catalog.
TABLE_CATALOG_ID | STRING | No | No | The ID of the catalog.
TABLE_NAME | STRING | No | Yes | The name of the relation.
TABLE_SCHEMA | STRING | No | Yes | The human readable name of the database.
TABLE_SCHEMA_ID | STRING | No | No | The ID of the database.

Example

Run the following code to query for a side view of TABLE_CONSTRAINTS for key columns.

    SELECT *
    FROM `INFORMATION_SCHEMA`.`KEY_COLUMN_USAGE`

### SCHEMATA / DATABASES¶

Describes databases within the catalog.

For convenience, DATABASES is an alias for SCHEMATA.

The rows returned are limited to the schemas that you have permission to interact with.

Column Name | Data Type | Nullable | Standard | Description
---|---|---|---|---
CATALOG_ID | STRING | No | No | The ID of the catalog/environment, for example, `env-xmzdkk`.
CATALOG_NAME | STRING | No | Yes | The human readable name of the catalog/environment, for example, `default`.
SCHEMA_ID | STRING | No | No | The ID of the database/cluster, for example, `lkc-kgjwwv`.
SCHEMA_NAME | STRING | No | Yes | The human readable name of the database/cluster, for example, MyCluster.

Example

Run the following code to list all Flink databases within a catalog, (Kafka clusters within an environment), excluding information schema.

    SELECT
      `SCHEMA_ID`,
      `SCHEMA_NAME`
    FROM `INFORMATION_SCHEMA`.`SCHEMATA`
    WHERE `SCHEMA_NAME` <> 'INFORMATION_SCHEMA';

### TABLES¶

Contains the object level metadata for tables and virtual tables (views) within the catalog.

The rows returned are limited to the schemas that you have permission to interact with.

Column Name | Data Type | Nullable | Standard | Description
---|---|---|---|---
COMMENT | STRING | Yes | No | An optional comment that describes the relation.
DISTRIBUTION_ALGORITHM | STRING | Yes | No | Currently, only HASH.
DISTRIBUTION_BUCKETS | INT | Yes | No | Number of buckets, if defined.
IS_DISTRIBUTED | STRING | No | No | Indicates whether the table is bucketed using the DISTRIBUTED BY clause. Values are YES or NO.
IS_WATERMARKED | STRING | No | No | Indicates whether the table has a [watermark](../../_glossary.html#term-watermark) from the WATERMARK FOR clause. Values are YES or NO.
TABLE_CATALOG | STRING | No | Yes | The human readable name of the catalog.
TABLE_CATALOG_ID | STRING | No | No | The ID of the catalog.
TABLE_NAME | STRING | No | Yes | The name of the relation.
TABLE_SCHEMA | STRING | No | Yes | The human readable name of the database.
TABLE_SCHEMA_ID | STRING | No | No | The ID of the database.
TABLE_TYPE | STRING | No | Yes | Values are BASE TABLE or VIEW.
WATERMARK_COLUMN | STRING | Yes | No | Time attribute column for which the watermark is defined.
WATERMARK_EXPRESSION | STRING | Yes | No | Watermark expression.
WATERMARK_IS_HIDDEN | STRING | Yes | No | Indicates whether the watermark is the default, system-provided one.

Examples

Run the following code to list all tables within a catalog (Kafka topics within an environment), excluding the information schema.

    SELECT
      `TABLE_CATALOG`,
      `TABLE_SCHEMA`,
      `TABLE_NAME`
    FROM `INFORMATION_SCHEMA`.`TABLES`
    WHERE `TABLE_SCHEMA` <> 'INFORMATION_SCHEMA';

Run the following code to list all tables within a database (Kafka topics within a cluster).

    SELECT
      `TABLE_CATALOG`,
      `TABLE_SCHEMA`,
      `TABLE_NAME`
    FROM `<current-catalog>`.`INFORMATION_SCHEMA`.`TABLES`
    WHERE `TABLE_SCHEMA` = '<current-database>';

### TABLE_CONSTRAINTS¶

Side view of TABLES for all primary key constraints within the catalog.

Column Name | Data Type | Nullable | Standard | Description
---|---|---|---|---
CONSTRAINT_CATALOG | STRING | No | Yes | Catalog name containing the constraint.
CONSTRAINT_CATALOG_ID | STRING | No | No | Catalog ID containing the constraint.
CONSTRAINT_SCHEMA | STRING | No | Yes | Schema name containing the constraint.
CONSTRAINT_SCHEMA_ID | STRING | No | No | Schema ID containing the constraint.
CONSTRAINT_NAME | STRING | No | Yes | Name of the constraint.
CONSTRAINT_TYPE | STRING | No | Yes | Currently, only PRIMARY KEY.
ENFORCED | STRING | No | Yes | YES if constraint is enforced, otherwise NO.
TABLE_CATALOG | STRING | No | Yes | The human readable name of the catalog.
TABLE_CATALOG_ID | STRING | No | No | The ID of the catalog.
TABLE_NAME | STRING | No | Yes | The name of the relation.
TABLE_SCHEMA | STRING | No | Yes | The human readable name of the database.
TABLE_SCHEMA_ID | STRING | No | No | The ID of the database.

Examples

Run the following code to query for a side view of TABLES for all primary key constraints within the catalog.

    SELECT *
    FROM `INFORMATION_SCHEMA`.`TABLE_CONSTRAINTS`;

### TABLE_OPTIONS¶

Side view of TABLES for WITH.

Extension to the SQL Standard Information Schema.

Column Name | Data Type | Nullable | Description
---|---|---|---
TABLE_CATALOG | STRING | No | The human readable name of the catalog.
TABLE_CATALOG_ID | STRING | No | The ID of the catalog.
TABLE_NAME | STRING | No | The name of the relation.
TABLE_SCHEMA | STRING | No | The human readable name of the database.
TABLE_SCHEMA_ID | STRING | No | The ID of the database.
OPTION_KEY | STRING | No | Option key.
OPTION_VALUE | STRING | No | Option value.

Examples

Run the following code to query for a side view of TABLES for WITH.

    SELECT *
    FROM `INFORMATION_SCHEMA`.`TABLE_OPTIONS`;
