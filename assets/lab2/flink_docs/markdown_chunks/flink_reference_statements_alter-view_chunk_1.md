---
document_id: flink_reference_statements_alter-view_chunk_1
source_file: flink_reference_statements_alter-view.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/alter-view.html
title: SQL ALTER VIEW Statement in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# ALTER VIEW Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables modifying properties of an existing view.

## Syntax¶

    ALTER VIEW [catalog_name.][db_name.]view_name RENAME TO new_view_name

    ALTER VIEW [catalog_name.][db_name.]view_name AS new_statement_expression

## Description¶

ALTER VIEW enables you to change the name of a view or modify the statement expression that defines the view.

The first syntax enables renaming a view within the same catalog and database. The new view name must not already exist in the catalog and database.

The second syntax enables changing the underlying statement that defines the view. The new statement expression must be a valid SELECT statement supported by Flink SQL. The schema of the new statement expression must be compatible with the schema of the existing view.

## Examples¶

The following examples show frequently encountered scenarios with ALTER VIEW.

### Rename a view¶

In the Confluent CLI or in a Cloud Console workspace, run the following commands to rename a view.

  1. Create a view.

         CREATE VIEW customer_orders AS
         SELECT customer_id, SUM(price) AS total_spent
         FROM `examples`.`marketplace`.`orders`
         GROUP BY customer_id;

  2. Rename the view.

         ALTER VIEW customer_orders RENAME TO vip_customers;

Your output should resemble:

         Statement phase is COMPLETED.

  3. Query the renamed view.

         SELECT * FROM vip_customers;

The statement now references the view by its new name.

### Change the statement expression of a view¶

  1. View the current definition of the view.

         SHOW CREATE VIEW vip_customers;

Your output should resemble:

         +------------------------------------------------------------------------------+
         |                              SHOW CREATE VIEW                                |
         +------------------------------------------------------------------------------+
         | CREATE VIEW vip_customers AS SELECT customer_id, SUM(price) AS total_spent   |
         | FROM orders                                                                  |
         | GROUP BY customer_id;                                                        |
         +------------------------------------------------------------------------------+

  2. Change the statement expression of the view.

         ALTER VIEW vip_customers AS
         SELECT customer_id, SUM(price) AS total_spent, COUNT(*) AS order_count
         FROM `examples`.`marketplace`.`orders`
         GROUP BY customer_id
         HAVING SUM(price) > 1000;

Your output should resemble:

         Statement phase is COMPLETED.

  3. View the updated definition of the view.

         SHOW CREATE VIEW vip_customers;

Your output should resemble:

         +-----------------------------------------------------------------------------------------------------+
         |                                         SHOW CREATE VIEW                                            |
         +-----------------------------------------------------------------------------------------------------+
         | CREATE VIEW vip_customers AS SELECT customer_id, SUM(price) AS total_spent, COUNT(*) AS order_count |
         | FROM orders                                                                                         |
         | GROUP BY customer_id                                                                                |
         | HAVING SUM(price) > 1000;                                                                           |
         +-----------------------------------------------------------------------------------------------------+

The view now includes an additional `order_count` column representing the number of orders per customer, and filters for only those customers who have spent more than 1000.
