---
document_id: flink_reference_queries_joins_chunk_1
source_file: flink_reference_queries_joins.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/joins.html
title: SQL Join Queries in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 2
---

# Join Queries in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables join data streams over Flink SQL dynamic tables.

## Description¶

Flink supports complex and flexible join operations over dynamic tables. There are a number of different types of joins to account for the wide variety of semantics that queries may require.

By default, the order of joins is not optimized. Tables are joined in the order in which they are specified in the `FROM` clause.

You can tweak the performance of your join queries, by listing the tables with the lowest update frequency first and the tables with the highest update frequency last. Make sure to specify tables in an order that doesn’t yield a cross join (Cartesian product), which aren’t supported and would cause a query to fail.

## Regular joins¶

Regular joins are the most generic type of join in which any new row, or changes to either side of the join, are visible and affect the whole join result.

For example, if there is a new record on the left side, it is joined with all of the previous and future records on the right side when the join fields are equal.

    SELECT * FROM orders
    INNER JOIN Product
    ON orders.productId = Product.id

For streaming queries, the grammar of regular joins is the most flexible and enables any kind of updates (insert, update, delete) on the input table. But this operation has important implications: it requires keeping both sides of the join input in state forever, so the required state for computing the query result might grow indefinitely, depending on the number of distinct input rows of all input tables and intermediate join results.

### INNER Equi-JOIN¶

Returns a simple Cartesian product restricted by the join condition.

Only equi-joins are supported, i.e., joins that have at least one conjunctive condition with an equality predicate. Arbitrary cross or theta joins aren’t supported.

    SELECT *
    FROM orders
    INNER JOIN Product
    ON orders.product_id = Product.id

### OUTER Equi-JOIN¶

Returns all rows in the qualified Cartesian product (i.e., all combined rows that pass its join condition), plus one copy of each row in an outer table for which the join condition did not match with any row of the other table.

Flink supports LEFT, RIGHT, and FULL outer joins.

Only equi-joins are supported, i.e., joins that have at least one conjunctive condition with an equality predicate. Arbitrary cross or theta joins aren’t supported.

    SELECT *
    FROM orders
    LEFT JOIN Product
    ON orders.product_id = Product.id

    SELECT *
    FROM orders
    RIGHT JOIN Product
    ON orders.product_id = Product.id

    SELECT *
    FROM orders
    FULL OUTER JOIN Product
    ON orders.product_id = Product.id

## Interval joins¶

An interval join returns a simple Cartesian product restricted by the join condition and a time constraint.

An interval join requires at least one equi-join predicate and a join condition that bounds the time on both sides. Two appropriate range predicates can define such a condition (`<`, `<=`, `>=`, `>`), a BETWEEN predicate, or a single equality predicate that compares [time attributes](../../concepts/timely-stream-processing.html#flink-sql-time-attributes) of both input tables.

For example, the following query joins all orders with their corresponding shipments if the order was shipped four hours after the order was received.

    SELECT *
    FROM orders o, Shipments s
    WHERE o.id = s.order_id
    AND o.order_time BETWEEN s.ship_time - INTERVAL '4' HOUR AND s.ship_time

The following predicates are examples of valid interval join conditions:

* `ltime = rtime`
* `ltime >= rtime AND ltime < rtime + INTERVAL '10' MINUTE`
* `ltime BETWEEN rtime - INTERVAL '10' SECOND AND rtime + INTERVAL '5' SECOND`

For streaming queries, compared to the regular join, interval join only supports append-only tables with time attributes. Because time attributes increase quasi-monotonically, Flink can remove old values from its state without affecting the correctness of the result.
