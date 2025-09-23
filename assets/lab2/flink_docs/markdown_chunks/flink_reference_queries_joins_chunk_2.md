---
document_id: flink_reference_queries_joins_chunk_2
source_file: flink_reference_queries_joins.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/joins.html
title: SQL Join Queries in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 2
---

the correctness of the result.

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
