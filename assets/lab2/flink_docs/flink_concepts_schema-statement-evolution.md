---
source_url: https://docs.confluent.io/cloud/current/flink/concepts/schema-statement-evolution.html
title: Schema and Statement Evolution with Confluent Cloud for Apache Flink
hierarchy: ['concepts', 'schema-statement-evolution.html']
scraped_date: 2025-09-05T13:46:24.927446
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

## Schema compatibility modes¶

When a statement is created, it must be bootstrapped from its source tables. For this, Flink must be able to read the source tables from the beginning (or any other specified offsets). As mentioned previously, statements use the latest schema version, at the time of statement creation, for each source table as the read schema.

You have these options for handling changes to base schemas:

  * Compatibility Mode FULL or FULL_TRANSITIVE
  * BACKWARD_TRANSITIVE compatibility mode and upgrade consumers first
  * Compatibility groups and migration rules

To maximize compatibility with Flink, you should use `FULL_TRANSITIVE` or `FULL` as the schema compatibility mode, which eases migrations. Note that in Confluent Cloud, the default compatibility mode is `BACKWARD`.

Sometimes, you may need to make changes beyond what the `FULL_TRANSITIVE` and `FULL` modes enable, so Confluent Cloud for Apache Flink gives you the additional options of BACKWARD_TRANSITIVE compatibility mode and Compatibility groups and migration rules for handling changes to base schemas.

### Compatibility Mode FULL or FULL_TRANSITIVE¶

If you use the `FULL` or `FULL_TRANSITIVE` compatibility mode, the order you upgrade your statements doesn’t matter. `FULL` limits the changes that you can make to your tables to adding and removing optional fields. You can make any compatible changes to the source tables, and none of the statements that reference them will break.

### BACKWARD_TRANSITIVE compatibility mode and upgrade consumers first¶

`BACKWARD_TRANSITIVE` mandates that consumers are upgraded prior to producers. This means that if you evolve your schema according to the `BACKWARD_TRANSITIVE` rules (delete fields, add optional fields), you always need to upgrade all statements that are reading from the corresponding source tables before producing any records to the table that uses the next schema version, as described in Query Evolution.

### Compatibility groups and migration rules¶

If you need to make a non-compatible change to a table, either using `FULL` or `BACKWARD_TRANSITIVE`, Confluent Cloud for Apache Flink also supports compatibility groups and migration rules. For more information, see [Data Contracts for Schema Registry on Confluent Cloud](../../sr/fundamentals/data-contracts.html#sr-data-contracts).

Note

If you need to make changes to your schemas that aren’t possible under schema compatibility mode `FULL`, use compatibility mode `FULL` for all topics and rely on compatibility groups and migration rules.

## Statements and schema evolution¶

When following the practices in the previous section, statements won’t fail when fields are added or optional fields are removed from its source tables, but these new fields aren’t picked up or forwarded to the sink tables. They are ignored by any previously created statements, and the `*`-operators are not evaluated dynamically when the schema changes.

Note

If you’re interested in to providing feedback about configuring statements to pick up schema changes of sources tables dynamically, reach out to Confluent Support or your account manager.

## Query evolution¶

As stated previously, the query in a statement is immutable. But you may encounter situations in which you want to change the logic of a long-running statement:

  * You may have to fix a bug in your query. For example, you may have to handle an arithmetic error that occurs only when the statement has already existed for a long time by adding another branch in a `CASE` clause.
  * You may want to evolve the logic of your statement.
  * You want your statement to pick up configuration updates to any of the catalog objects that it references, like tables or functions.

The general strategy for query evolution is to replace the existing statement and the corresponding tables it maintains with a new statement and new tables, as shown in the following steps:

  1. Use `CREATE TABLE ... AS ...` to create a new version of the table, `orders_with_customers_v2`.
  2. Wait until the new statement has caught up with latest messages of its source tables, which means that the “Messages Behind” metric is close to zero. Note that Confluent Cloud Autopilot automatically configures the statement to catch up as quickly as the compute resources provided by the assigned compute pool allow.
  3. Migrate all consumers to the new tables. The best way to find all downstream consumers of a table topic in Confluent Cloud is to use [Stream Lineage](../../stream-governance/stream-lineage.html#cloud-stream-lineage).
  4. Stop the `orders-with-customers-v1-1` statement.

This base strategy has these features:

  * It works for any type of statement.
  * It requires that all relevant input messages are retained in the source tables.
  * It requires existing consumers to switch to different topics manually, and thereby reading the `…v2` table from earliest or any manually specified offset.

You can adjust the base strategy in multiple ways, depending on your circumstances.

### Limit reprocessing to a partial history¶

Compared to the base strategy, this strategy limits the messages that are reprocessed to a subset of the messages retained in the source tables.

You may not want to reprocess the full history of messages that’s retained in all source table, but instead specify a different starting offset. For this, you can override the `scan.startup.mode` that is defined for the table, which by default is `earliest`, using [dynamic table option hints](../reference/statements/hints.html#flink-sql-hints).

     SET 'sql.state-ttl' = '1h';
     SET 'client.statement-name' = 'orders-with-customers-v2-1';
     CREATE TABLE orders_with_customers_v2
     PRIMARY KEY (orders.order_id)
     DISTRIBUTED INTO 10 BUCKETS
     AS
     SELECT
       orders.order_id,
       orders.product,
       to_minor_currency(v_orders.price),
       customers.*,
     FROM orders /*+ OPTIONS('scan.startup.mode' = 'timestamp', 'scan.startup.timestamp-millis' = '1717763226336') */
     JOIN customers /*+ OPTIONS('scan.startup.mode' = 'timestamp', 'scan.startup.timestamp-millis' = '1717763226336') */
     ON orders.customer_id = customers.id;

Alternatively, you can set this by using statement properties, like `sql.tables.scan.startup.mode`, and the [SET](../reference/statements/set.html#flink-sql-set-statement) statement. While dynamic table option hints enable you to configure the starting offset for each table independently, the statement properties affect the starting offset for _all_ tables that this statement reads from.

When reprocessing a partial history of the source tables, and depending on your query, you may want to add an additional filter predicate to your tables, to avoid incorrect results. For example, if your query performs windowed aggregations on ten-minute tumbling windows, you may want to start reading from exactly the beginning of a window to avoid an incomplete window at the start. This could be achieved by adding a `WHERE event_time > '<timestamp>'` clause to the respective source tables, where `event_time` is the name of the column that is used for windowing, and `<timestamp>` lies within the history of messages that are reprocessed and aligns with the start of one of the ten-minute windows, for example, `2024-06-11 15:40:00`.

#### Special case: Carrying over offsets of previous statements¶

When a statement is stopped, `status.latest_offsets` contains the latest offset for each partition of each of the source tables:

    status:
        latestOffsets:
            topic1: partition:0,offset:23;partition:1,offset:65
            topic2: partition:0,offset:53;partition:1,offset:56
        latestOffsetsTimestamp:

you can use these offsets to specify the starting offsets to a new statement by using dynamic table option hints, so the new statement continues exactly where the previous statement left off.

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

## Related content¶

Flink implements many techniques from the Dataflow Model. For a good introduction to event time and watermarks, have a look at these articles.

  * [Data Contracts](../../sr/fundamentals/data-contracts.html#sr-data-contracts)
  * [Stream Lineage](../../stream-governance/stream-lineage.html#cloud-stream-lineage)
  * [HINTS](../reference/statements/hints.html#flink-sql-hints)
  * [CREATE TABLE](../reference/statements/create-table.html#flink-sql-create-table)
  * [SET](../reference/statements/set.html#flink-sql-set-statement)

Note

This website includes content developed at the [Apache Software Foundation](https://www.apache.org/) under the terms of the [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0.html).
