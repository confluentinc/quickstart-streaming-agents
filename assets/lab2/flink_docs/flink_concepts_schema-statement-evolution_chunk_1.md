---
document_id: flink_concepts_schema-statement-evolution_chunk_1
source_file: flink_concepts_schema-statement-evolution.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/schema-statement-evolution.html
title: Schema and Statement Evolution with Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 4
---

# Schema and Statement Evolution with Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables evolving your statements over time as your schemas change.

This topic describes these concepts:

* How you can evolve your statements and the tables they maintain over time.
* How statements behave when the schema of their source tables change.

## Example¶

Throughout this topic, the following statement is used as a running example.

    SET 'sql.state-ttl' = '1h';
    SET 'client.statement-name' = 'orders-with-customers-v1-1';

    CREATE FUNCTION to_minor_currency
    AS 'io.confluent.flink.demo.toMinorCurrency'
    USING JAR 'confluent-artifact://ccp-lzj320/ver-4y0qw7';

    CREATE TABLE v_orders AS SELECT order.* FROM sales_lifecycle_events WHERE order != NULL;

    CREATE TABLE orders_with_customers_v1
    PRIMARY KEY (v_orders.order_id)
    DISTRIBUTED INTO 10 BUCKETS
    AS
    SELECT
      v_orders.order_id,
      v_orders.product,
      to_minor_currency(v_orders.price),
      customers.*,
    FROM v_orders
    JOIN customers FOR SYSTEM TIME AS OF orders.$rowtime
    ON v_orders.customer_id = customers.id;

The `orders_with_customers_v1` table uses a user-defined function named `to_minor_currency` and joins a table named `v_orders` with the up-to-date customer information from the customers table.

## Fundamentals¶

### Mutability of statements and tables¶

A statement has the following components:

* an **immutable** query, for example:

        SELECT
          v_orders.product,
          to_minor_currency(v_orders.price),
          customers.*
        FROM orders
        JOIN customers FOR SYSTEM TIME AS OF orders.$rowtime
        ON v_orders.customer_id = customers.id;

* **immutable** statement properties, for example:

        'sql.state-ttl' = '1h'

* a **mutable** principal, that is, the user or service account under which this statement runs.

The principal and compute pool are mutable when stopping and resuming the statement. Note that stopping and resume the statement results in a temporarily higher materialization delay and latency.

The query and options of a statement `(SELECT ...)` are immutable, which means that you can’t change them after the statement has been created.

Note

If your use case requires a lower latency, reach out to Confluent Support or your account manager.

The table which the statement is writing to has these components:

* An immutable name, for example: `orders_with_customers_v1`.

* Mutable constraints, for example:

        PRIMARY KEY (v_orders.order_id)

* A mutable watermark definition.

* a mutable column definition

* partially mutable table options

The name of a table is immutable, because it maps one-to-one to the underlying topic, which you can’t rename.

The watermark strategy is mutable by using the `ALTER TABLE ... MODIFY/DROP WATERMARK ...;` statement. For more information, see [ALTER TABLE Statement in Confluent Cloud for Apache Flink](../reference/statements/alter-table.html#flink-sql-alter-table).

The table options of the table are mutable by using the `ALTER TABLE SET (...);` statement. For more information, see [ALTER TABLE Statement in Confluent Cloud for Apache Flink](../reference/statements/alter-table.html#flink-sql-alter-table).

The constraints are partially mutable by using the `ALTER TABLE ADD/DROP PRIMARY KEY` statement.

### Statements take a snapshot of their dependencies¶

A statement almost always references other catalog objects such as tables and functions. In the current example, the `orders_with_customers_v1` table references these objects:

* A table named `customers`.
* A table named `v_orders`.
* A user-defined function named `to_minor_currency`.

When a statement is created, it takes a snapshot of the configuration of all the catalog objects that it depends on. Changes, or the deletion of these objects from the catalog, are not propagated to existing statements, which means that:

* A change to the watermark strategy of a source table is not picked up by existing statements that reference the table.
* A change to a table option of a source table is not picked up by existing statements that reference the table.
* A change to the implementation of a user-defined functions is not picked up by existing statements that reference the function.

If an underlying physical resource is deleted that statements require at runtime, like the topic, the statements transition into the FAILED, STOPPED, or RECOVERING state, depending on which resource was deleted.
