---
document_id: flink_reference_flink-sql-information-schema_chunk_2
source_file: flink_reference_flink-sql-information-schema.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/flink-sql-information-schema.html
title: SQL Information Schema in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 4
---

and basic expressions are supported.

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
