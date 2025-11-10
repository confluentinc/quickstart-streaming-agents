---
document_id: flink_reference_statements_drop-view_chunk_1
source_file: flink_reference_statements_drop-view.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/drop-view.html
title: SQL DROP VIEW Statement in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# DROP VIEW Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables dropping views using the DROP VIEW statement. When a view is dropped, its definition is removed from the catalog. The corresponding Kafka topic Flink resource reservation is removed. Any new statement referencing the dropped view will fail.

## Syntax¶

    DROP VIEW [IF EXISTS] [catalog_name.][db_name.]view_name

## Description¶

DROP VIEW removes a view from the catalog. If the view does not exist, an exception is thrown unless `IF EXISTS` is specified.

The view name can be in these formats:

  * `catalog_name.db_name.view_name`: The view with the given name is dropped from the catalog named “catalog_name” and the database named “db_name”.
  * `db_name.view_name`: The view with the given name is dropped from the current catalog of the execution table environment and the database named “db_name”.
  * `view_name`: The view with the given name is dropped from the current catalog and the current database of the execution table environment.

## Examples¶

The following example drops the `vip_customers` view.

In the Confluent CLI or in a Cloud Console workspace, run the following command:

    DROP VIEW vip_customers;

Your output should resemble:

    Statement phase is COMPLETED.

If you try to query the dropped view:

    SELECT * FROM vip_customers;

You will get an error message indicating that the view does not exist:

    [Code: 1, SQL State: 42000]: Object 'default_catalog.default_database.vip_customers' does not exist.

To avoid the error when dropping a view that may not exist, use the `IF EXISTS` clause:

    DROP VIEW IF EXISTS vip_customers;

This statement will not throw an error if the `vip_customers` view does not exist.
