---
document_id: flink_reference_statements_create-view_chunk_1
source_file: flink_reference_statements_create-view.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-view.html
title: SQL CREATE VIEW Statement in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# CREATE VIEW Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables creating views based on statement expressions by using the CREATE VIEW statement. With Flink views, you can encapsulate complex queries and reference them like regular tables.

## Syntax¶

    CREATE VIEW [IF NOT EXISTS] [catalog_name.][db_name.]view_name
      [( columnName [, columnName ]* )] [COMMENT view_comment]
      AS statement_expression

## Description¶

Create a view with the given statement expression. If a view with the same name already exists in the catalog, an exception is thrown.

If you specify IF NOT EXISTS, nothing happens if the view exists already.

The view name can be in these formats:

  * `catalog_name.db_name.view_name`: The view is registered with the catalog named “catalog_name” and the database named “db_name”.
  * `db_name.view_name`: The view is registered into the current catalog of the execution table environment and the database named “db_name”.
  * `view_name`: The view is registered into the current catalog and the database of the execution table environment.

A view created with the CREATE VIEW statement acts as a virtual table that refers to the result of the specified statement expression. The statement expression can be any valid SELECT statement supported by Flink SQL.

## Views vs. tables¶

Views in Flink are similar to tables in that they can be referenced in SQL queries just like regular tables. But there are some key differences:

  * Views are read-only and can’t be used as sinks in INSERT statements. Tables support both read and write operations.
  * Views don’t have a physical representation and are computed on-the-fly when referenced in a statement.
  * Creating a view results in creating a special Kafka topic. This Flink resource only reserves the name and doesn’t store data. Creating a table results in creating a regular Kafka topic that stores data and corresponding key and value schemas in Confluent Schema Registry.
  * Views are lightweight and store only the statement expression.

Despite these differences, views and tables share the same namespace in Flink. This means a view can’t have the same fully qualified name as an existing table in the same catalog and database.

## Usage¶

The following CREATE VIEW statement defines a view named `orders_by_customer` that computes the total order value per customer from an `orders` table.

    CREATE VIEW customer_orders AS
    SELECT customer_id, SUM(price) AS total_spent
    FROM `examples`.`marketplace`.`orders`
    GROUP BY customer_id;

You can then use this view in queries as if it were a table:

    SELECT customer_id, total_spent
    FROM customer_orders
    WHERE total_spent > 1000;

This statement retrieves all customers with a total order value greater than 1000, leveraging the aggregation already computed in the `orders_by_customer` view.
