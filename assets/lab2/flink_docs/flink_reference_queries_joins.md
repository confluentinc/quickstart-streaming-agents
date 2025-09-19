---
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/joins.html
title: SQL Join Queries in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'queries', 'joins.html']
scraped_date: 2025-09-05T13:49:12.666518
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

## Temporal joins¶

A _temporal join_ joins one table with another table that is updated over time. This join is made possible by linking both tables using a time attribute, which allows the join to consider the historical changes in the table. When viewing the table at a specific point in time, the join becomes a time-versioned join.

In a temporal join, the join condition is based on a time attribute, and the join result includes all rows that satisfy the temporal relationship. A common use case for temporal joins is analyzing financial data, which often includes information that changes over time, such as stock prices, interest rates, and exchange rates.

### Event-time temporal joins¶

Event-time temporal joins are used to join two or more tables based on a common event time. Event time is the time at which an event occurred, which is typically embedded in the data itself. With Confluent Cloud for Apache Flink, you can use the [$rowtime](../statements/create-table.html#flink-sql-system-columns-rowtime) system column to get the timestamp from an Apache Kafka® record. This is also used for the default [watermark](../../../_glossary.html#term-watermark) strategy in Confluent Cloud.

Temporal joins take an arbitrary table (left input/probe side) and correlate each row to the corresponding row’s relevant version in the versioned table (right input/build side). Flink uses the SQL syntax of FOR SYSTEM_TIME AS OF to perform this operation from the SQL:2011 standard.

The syntax of a temporal join is as follows:

    SELECT [column_list]
    FROM table1 [AS <alias1>]
    [LEFT] JOIN table2 FOR SYSTEM_TIME AS OF table1.{ rowtime } [AS <alias2>]
    ON table1.column-name1 = table2.column-name1

With an event-time attribute, you can retrieve the value of a key as it was at some point in the past. This enables joining the two tables at a common point in time. The versioned table stores all versions, identified by time, since the last watermark.

For example, suppose you have a table of orders, each with prices in different currencies. To properly normalize this table to a single currency, such as USD, each order needs to be joined with the proper currency conversion rate from the point in time when the order was placed.

    CREATE TABLE orders (
        order_id    STRING,
        price       DECIMAL(32,2),
        currency    STRING
    );
    
    CREATE TABLE currency_rates (
        currency STRING,
        conversion_rate DECIMAL(32, 2),
        PRIMARY KEY(currency) NOT ENFORCED
    );
    
    SELECT
         orders.order_id,
         orders.price,
         orders.currency,
         currency_rates.conversion_rate
    FROM orders
    LEFT JOIN currency_rates FOR SYSTEM_TIME AS OF orders.`$rowtime`
    ON orders.currency = currency_rates.currency;

The event-time temporal join requires the primary key contained in the equivalence condition of the temporal join condition. In this example, the primary key `currency_rates.currency` in the `currency_rates` table is constrained in the `condition orders.currency = currency_rates.currency` expression.

With temporal joins, there’s some indeterminate amount of latency involved. In the example with `orders` and `currency_rates`, when enriching a particular order, an event-time temporal join waits until the watermark on the currency-rate stream reaches the timestamp of that order, because only then is it reasonable to be confident that the result of the join is being produced with complete knowledge of the relevant exchange-rate data.

Event-time temporal joins can’t guarantee perfectly correct results. Despite having waited for the watermark, the most relevant exchange-rate record could still be late, in which case the join will be executed using an earlier version of the exchange rate.

If the enrichment stream has infrequent updates, this will cause problems, because of the behavior of watermarking on idle streams. The operator, like any operator with two input streams, normally waits for the watermarks on both incoming streams to reach the desired timestamp before taking action.

## Array expansion¶

Returns a new row for each element in the given array. Unnesting `WITH ORDINALITY` is not yet supported.

    SELECT order_id, tag
    FROM orders CROSS JOIN UNNEST(tags) AS t (tag)

