---
document_id: flink_concepts_schema-statement-evolution_chunk_4
source_file: flink_concepts_schema-statement-evolution.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/schema-statement-evolution.html
title: Schema and Statement Evolution with Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 4
---

This strategy enables you to evolve statements arbitrarily with **exactly-once semantics** across the update, if and only if the statement is “stateless”, which mean that every output message is affected by a single input message. The following statements are common example of “stateless” statements:

* Filters

        INSERT INTO shipped_orders
        SELECT *
        FROM orders
        WHERE status = shipped;

* Routers

        EXECUTE STATEMENT SET
        BEGIN
          INSERT INTO shipped_orders SELECT * FROM orders WHERE status = 'shipped';
          INSERT INTO cancelled_orders SELECT * FROM orders WHERE status = 'cancelled';
          INSERT INTO returned_orders SELECT * FROM orders WHERE status = 'returned';
          INSERT INTO other_orders SELECT * FROM orders WHERE status NOT IN ('returned', 'shipped', 'cancelled')
        END;

* Per-row transformations, including UDFs and array expansions:

        INSERT INTO ordered_products
        SELECT
           o.*,
           order_products.*
        FROM orders AS o
        CROSS JOIN UNNEST(orders.products) AS `order_products` (product_id, category, quantity, unit_price, net_price)

For more information, see [Carry-over Offsets](../operate-and-deploy/carry-over-offsets.html#flink-sql-carry-over-offsets).

### In-place upgrade¶

Compared to the base strategy, the in-place upgrade strategy has these features:

* It works only for tables that have a primary key, so that the new statement updates all rows written by the old statement.
* It works only for compatible changes, both semantically and in terms of the schema.
* It doesn’t require consumers to switch manually to new topics, but it does require consumers to be able to handle out-of-order, late, bulk updates to all keys.

Instead of creating a new results table, you can also replace the original `CREATE TABLE ... AS ...` statement with an INSERT INTO statement that produces updates into the same table as before. The upgrade procedure then looks like this:

  1. Stop the old `orders-with-customers-v1-1` statement.
  2. Once the old statement is stopped, create the new statement, `orders-with-customers-v1-2`.

This strategy can and often will be combined with limited reprocessing to a partial history. Specifically, in the case of an exactly-once upgrade of a stateless statement, it makes sense to continue publishing messages to the same topic, provided this was a compatible change.
