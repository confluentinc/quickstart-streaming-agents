---
document_id: flink_reference_flink-sql-information-schema_chunk_4
source_file: flink_reference_flink-sql-information-schema.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/flink-sql-information-schema.html
title: SQL Information Schema in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 4
---

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
