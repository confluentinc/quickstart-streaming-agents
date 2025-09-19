---
document_id: flink_reference_statements_explain_chunk_4
source_file: flink_reference_statements_explain.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/explain.html
title: SQL EXPLAIN Statement in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 5
---

or frequent updates per key.

## Physical operators¶

Below is a reference of common operators you may see in EXPLAIN output, along with examples of SQL that typically produces them.

### Basic operations¶

StreamTableSourceScan

Reads data from a source table. The foundation of any query reading from a table.

    SELECT * FROM orders;

StreamCalc

Performs row-level computations and filtering. Appears when using WHERE clauses or expressions in SELECT.

    SELECT amount * 1.1 as amount_with_tax
    FROM orders
    WHERE status = 'completed';

StreamValues

Generates literal row values. Commonly seen with [INSERT](../queries/insert-values.html#flink-sql-insert-values-statement) statements.

    INSERT INTO orders VALUES (1, 'pending', 100);

StreamSink

Writes results to a destination. Present in any INSERT or when displaying query results. Supports two modes of operation:

  * Append-only: Each record is treated as a new event, which displays as **State size: Low**.
  * Upsert-materialize: Maintains state to handle updates/deletes based on key fields. which displays as **State size: High**.

    INSERT INTO order_summaries
    SELECT status, COUNT(*)
    FROM orders
    GROUP BY status;

### Aggregation operations¶

StreamGroupAggregate

Performs [grouping and aggregation](../queries/group-aggregation.html#flink-sql-group-aggregation). Created by GROUP BY clauses.

    SELECT customer_id, SUM(price)
    FROM orders
    GROUP BY customer_id;

StreamLocalWindowAggregate and StreamGlobalWindowAggregate

These operators implement Flink two-phase aggregation strategy for distributed stream processing. They work together to compute aggregations efficiently across multiple parallel instances while maintaining exactly-once processing semantics.

The LocalGroupAggregate performs initial aggregation within each parallel task, maintaining partial results in its state. The GlobalGroupAggregate then combines these partial results to produce final aggregations. This two-phase approach appears in both regular GROUP BY operations and windowed aggregations.

For [window operations](../queries/window-tvf.html#flink-sql-window-tvfs), these operators appear as StreamLocalWindowAggregate and StreamGlobalWindowAggregate. Here’s an example that triggers their use:

    SELECT window_start, window_end, SUM(price) as total_price
       FROM TABLE(
           TUMBLE(TABLE orders, DESCRIPTOR($rowtime), INTERVAL '10' MINUTES))
       GROUP BY window_start, window_end;

### Join operations¶

StreamJoin

Performs standard stream-to-stream [joins](../queries/joins.html#flink-sql-joins).

    SELECT o.*, c.name
    FROM orders o
    JOIN customers c ON o.customer_id = c.id;

StreamTemporalJoin

Joins streams using [temporal](../queries/joins.html#flink-sql-event-time-temporal-joins) (time-versioned) semantics.

    SELECT
         orders.*,
         customers.*
    FROM orders
    LEFT JOIN customers FOR SYSTEM_TIME AS OF orders.`$rowtime`
    ON orders.customer_id = customers.customer_id;

StreamIntervalJoin

Joins streams within a [time interval](../queries/joins.html#flink-sql-interval-joins).

    SELECT *
    FROM orders o, clicks c
    WHERE o.customer_id = c.user_id
    AND o.`$rowtime` BETWEEN c.`$rowtime` - INTERVAL '1' MINUTE AND c.`$rowtime`;

StreamWindowJoin

Joins streams within [defined windows](../queries/window-join.html#flink-sql-window-join).

    SELECT *
    FROM (
        SELECT * FROM TABLE(TUMBLE(TABLE clicks, DESCRIPTOR($rowtime), INTERVAL '5' MINUTES))
    ) c
    JOIN (
        SELECT * FROM TABLE(TUMBLE(TABLE orders, DESCRIPTOR($rowtime), INTERVAL '5' MINUTES))
    ) o
    ON c.user_id = o.customer_id
        AND c.window_start = o.window_start
        AND c.window_end = o.window_end;

### Ordering and ranking¶

StreamRank

Computes the smallest or largest values ([Top-N queries](../queries/topn.html#flink-sql-top-n)).

    SELECT product_id, price
    FROM (
      SELECT *,
        ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY price DESC) AS row_num
      FROM orders)
    WHERE row_num <= 5;

StreamLimit

[Limits](../queries/limit.html#flink-sql-limit) the number of returned rows.

    SELECT * FROM orders LIMIT 10;

StreamSortLimit

Combines [sorting with row limiting](../queries/orderby.html#flink-sql-order-by).

    SELECT * FROM orders ORDER BY $rowtime LIMIT 10;

StreamWindowRank

Computes the smallest or largest values within window boundaries ([Window Top-N queries](../queries/window-topn.html#flink-sql-window-top-n)).

    SELECT *
      FROM (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY window_start, window_end ORDER BY price DESC) as rownum
        FROM (
          SELECT window_start, window_end, customer_id, SUM(price) as price, COUNT(*) as cnt
          FROM TABLE(
            TUMBLE(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '10' MINUTES))
          GROUP BY window_start, window_end, customer_id
        )
      ) WHERE rownum <= 3;
