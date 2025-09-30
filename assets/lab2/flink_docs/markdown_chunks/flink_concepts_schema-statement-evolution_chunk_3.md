---
document_id: flink_concepts_schema-statement-evolution_chunk_3
source_file: flink_concepts_schema-statement-evolution.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/schema-statement-evolution.html
title: Schema and Statement Evolution with Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 4
---

Support or your account manager.

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
