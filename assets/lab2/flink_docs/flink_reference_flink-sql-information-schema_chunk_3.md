---
document_id: flink_reference_flink-sql-information-schema_chunk_3
source_file: flink_reference_flink-sql-information-schema.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/flink-sql-information-schema.html
title: SQL Information Schema in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 4
---

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
