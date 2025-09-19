---
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/explain.html
title: SQL EXPLAIN Statement in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'statements', 'explain.html']
scraped_date: 2025-09-05T13:48:57.610409
---

# EXPLAIN Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables viewing and analyzing the query plans of Flink SQL statements.

## Syntax¶

    EXPLAIN { <query_statement> | <insert_statement> | <statement_set> | CREATE TABLE ... AS SELECT ... }
    
    <statement_set>:
    STATEMENT SET
    BEGIN
      -- one or more INSERT INTO statements
      { INSERT INTO <select_statement>; }+
    END;

## Description¶

The EXPLAIN statement provides detailed information about how Flink executes a specified query or INSERT statement. EXPLAIN shows:

  * The optimized physical execution plan
  * If the [changelog mode](create-table.html#flink-sql-create-table-with-changelog-mode) is not append-only, details about the changelog mode per operator
  * Upsert keys and primary keys where applicable
  * Table source and sink details

This information is valuable for understanding query performance, optimizing complex queries, and debugging unexpected results.

Use the EXPLAIN statement in conjunction with the [Flink SQL Query Profiler](../../operate-and-deploy/query-profiler.html#flink-sql-query-profiler) to understand the physical plan of your query.

## Example queries¶

### Basic query analysis¶

This example analyzes a query finding users who clicked but never placed an order:

    EXPLAIN
    SELECT c.*
    FROM `examples`.`marketplace`.`clicks` c
    LEFT JOIN (
      SELECT DISTINCT customer_id
      FROM `examples`.`marketplace`.`orders`
    ) o ON c.user_id = o.customer_id
    WHERE o.customer_id IS NULL;

The output shows the physical plan and operator details:

    == Physical Plan ==
    
    StreamSink [11]
      +- StreamCalc [10]
        +- StreamJoin [9]
          +- StreamExchange [3]
          :  +- StreamCalc [2]
          :    +- StreamTableSourceScan [1]
          +- StreamExchange [8]
            +- StreamGroupAggregate [7]
              +- StreamExchange [6]
                +- StreamCalc [5]
                  +- StreamTableSourceScan [4]
    
    == Physical Details ==
    
    [1] StreamTableSourceScan
    Table: `examples`.`marketplace`.`clicks`
    Changelog mode: append
    State size: low
    
    [4] StreamTableSourceScan
    Table: `examples`.`marketplace`.`orders`
    Changelog mode: append
    State size: low
    
    [7] StreamGroupAggregate
    Changelog mode: retract
    Upsert key: (customer_id)
    State size: medium
    
    [8] StreamExchange
    Changelog mode: retract
    Upsert key: (customer_id)
    
    [9] StreamJoin
    Changelog mode: retract
    State size: medium
    
    [10] StreamCalc
    Changelog mode: retract
    
    [11] StreamSink
    Table: Foreground
    Changelog mode: retract
    State size: low

Note that the `[11] StreamSink Table: Foreground` in the output indicates this is a preview execution plan. For more accurate optimization analysis, it’s recommended to test queries using either the final target table or CREATE TABLE AS statements, which will determine the optimal primary key and changelog mode for your specific use case.

### Creating tables¶

This example shows creating a new table from a query:

    EXPLAIN
    CREATE TABLE clicks_without_orders AS
    SELECT c.*
    FROM `examples`.`marketplace`.`clicks` c
    LEFT JOIN (
      SELECT DISTINCT customer_id
      FROM `examples`.`marketplace`.`orders`
    ) o ON c.user_id = o.customer_id
    WHERE o.customer_id IS NULL;

The output includes sink information for the new table:

    == Physical Plan ==
    
    StreamSink [11]
      +- StreamCalc [10]
        +- StreamJoin [9]
          +- StreamExchange [3]
          :  +- StreamCalc [2]
          :    +- StreamTableSourceScan [1]
          +- StreamExchange [8]
            +- StreamGroupAggregate [7]
              +- StreamExchange [6]
                +- StreamCalc [5]
                  +- StreamTableSourceScan [4]
    
    == Physical Details ==
    
    [1] StreamTableSourceScan
    Table: `examples`.`marketplace`.`clicks`
    Changelog mode: append
    State size: low
    
    [4] StreamTableSourceScan
    Table: `examples`.`marketplace`.`orders`
    Changelog mode: append
    State size: low
    
    [7] StreamGroupAggregate
    Changelog mode: retract
    Upsert key: (customer_id)
    State size: medium
    
    [8] StreamExchange
    Changelog mode: retract
    Upsert key: (customer_id)
    
    [9] StreamJoin
    Changelog mode: retract
    State size: medium
    
    [10] StreamCalc
    Changelog mode: retract
    
    [11] StreamSink
    Table: `catalog`.`database`.`clicks_without_orders`
    Changelog mode: retract
    State size: low

### Inserting values¶

This example shows inserting static values:

    EXPLAIN
    INSERT INTO orders VALUES
      (1, 1001, '2023-02-24', 50.0),
      (2, 1002, '2023-02-25', 60.0),
      (3, 1003, '2023-02-26', 70.0);

The output shows a simple insertion plan:

    == Physical Plan ==
    
    StreamSink [3]
      +- StreamCalc [2]
        +- StreamValues [1]
    
    == Physical Details ==
    
    [1] StreamValues
    Changelog mode: append
    State size: low
    
    [3] StreamSink
    Table: `catalogs`.`database`.`orders`
    Changelog mode: append
    State size: low

### Multiple operations¶

This example demonstrates operation reuse across multiple inserts:

    EXPLAIN STATEMENT SET
    BEGIN
      INSERT INTO low_orders SELECT * from `orders` where price < 100;
      INSERT INTO high_orders SELECT * from `orders` where price > 100;
    END;

The output shows table scan reuse:

    == Physical Plan ==
    
    StreamSink [3]
      +- StreamCalc [2]
        +- StreamTableSourceScan [1]
    
    StreamSink [5]
      +- StreamCalc [4]
        +- (reused) [1]
    
    == Physical Details ==
    
    [1] StreamTableSourceScan
    Table: `examples`.`marketplace`.`orders`
    Changelog mode: append
    State size: low
    
    [3] StreamSink
    Table: `catalog`.`database`.`low_orders`
    Changelog mode: append
    State size: low
    
    [5] StreamSink
    Table: `catalog`.`database`.`high_orders`
    Changelog mode: append
    State size: low

### Window functions¶

This example shows window functions and self-joins:

    EXPLAIN
    WITH windowed_customers AS (
      SELECT * FROM TABLE(
        TUMBLE(TABLE `examples`.`marketplace`.`customers`, DESCRIPTOR($rowtime), INTERVAL '1' MINUTE)
      )
    )
    SELECT
        c1.window_start,
        c1.city,
        COUNT(DISTINCT c1.customer_id) as unique_customers,
        COUNT(c2.customer_id) as total_connections
    FROM
        windowed_customers c1
        JOIN windowed_customers c2
        ON c1.city = c2.city
        AND c1.customer_id < c2.customer_id
        AND c1.window_start = c2.window_start
    GROUP BY
        c1.window_start,
        c1.city
    HAVING
        COUNT(DISTINCT c1.customer_id) > 5;

The output shows the complex processing required for windowed aggregations:

    == Physical Plan ==
    
    StreamSink [14]
      +- StreamCalc [13]
        +- StreamGroupAggregate [12]
          +- StreamExchange [11]
            +- StreamCalc [10]
              +- StreamJoin [9]
                +- StreamExchange [8]
                :  +- StreamCalc [7]
                :    +- StreamWindowTableFunction [6]
                :      +- StreamCalc [5]
                :        +- StreamChangelogNormalize [4]
                :          +- StreamExchange [3]
                :            +- StreamCalc [2]
                :              +- StreamTableSourceScan [1]
                +- (reused) [8]
    
    == Physical Details ==
    
    [1] StreamTableSourceScan
    Table: `examples`.`marketplace`.`customers`
    Primary key: (customer_id)
    Changelog mode: upsert
    Upsert key: (customer_id)
    State size: low
    
    [2] StreamCalc
    Changelog mode: upsert
    Upsert key: (customer_id)
    
    [3] StreamExchange
    Changelog mode: upsert
    Upsert key: (customer_id)
    
    [4] StreamChangelogNormalize
    Changelog mode: retract
    Upsert key: (customer_id)
    State size: medium
    
    [5] StreamCalc
    Changelog mode: retract
    Upsert key: (customer_id)
    
    [6] StreamWindowTableFunction
    Changelog mode: retract
    State size: low
    
    [7] StreamCalc
    Changelog mode: retract
    
    [8] StreamExchange
    Changelog mode: retract
    
    [9] StreamJoin
    Changelog mode: retract
    State size: medium
    
    [10] StreamCalc
    Changelog mode: retract
    
    [11] StreamExchange
    Changelog mode: retract
    
    [12] StreamGroupAggregate
    Changelog mode: retract
    Upsert key: (window_start,city)
    State size: medium
    
    [13] StreamCalc
    Changelog mode: retract
    Upsert key: (window_start,city)
    
    [14] StreamSink
    Table: Foreground
    Changelog mode: retract
    Upsert key: (window_start,city)
    State size: low

## Understanding the output¶

### Reading physical plans¶

The physical plan shows how Flink executes your query. Each operation is numbered and indented to show its position in the execution flow. Indentation indicates data flow, with each operator passing results to its parent.

### Changelog modes¶

Changelog modes describe how operators handle data modifications:

  * **Append:** The operator processes only insert operations. New rows are simply added.
  * **Upsert:** The operator handles both inserts and updates. It uses an “upsert key” to identify rows. If a row with a given key exists already, the operator updates it; otherwise, it inserts a new row.
  * **Retract:** The operator handles inserts, updates, and deletes. Updates are typically represented as a retraction (deletion) of the old row followed by an insertion of the new row. Deletes are represented as retractions.

Operators change changelog modes when different update patterns are needed, such as when moving from streaming reads to aggregations.

### Data movement¶

The physical details section shows how data moves between operators. Watch for:

  * Exchange operators indicating data redistribution
  * Changes in upsert keys showing where data must be reshuffled
  * Operator reuse marked by “(reused)” references

### State size¶

Each operator in the physical plan includes a “State Size” property indicating its memory requirements during execution:

  * LOW: Minimal state maintenance, typically efficient memory usage
  * MEDIUM: Moderate state requirements, may need attention with high cardinality
  * HIGH: Significant state maintenance that requires careful management

When operators show HIGH state size, you should configure a state TTL to prevent unbounded state growth. Without TTL configuration, these operators can accumulate unlimited state over time, potentially leading to resource exhaustion and the statement ending up in a `DEGRADED` state.

    SET 'sql.state-ttl' = '12 hours';

For MEDIUM state size, consider TTL settings if your data has high cardinality or frequent updates per key.

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

### Data movement and distribution¶

StreamExchange

Redistributes/exchanges data between parallel instances. For example, when you write a query with a GROUP BY clause, Flink might use a HASH exchange to ensure all records with the same key are processed by the same task:

    -- Appears in plans with GROUP BY on a different key than the source distribution
    SELECT customer_id, COUNT(*)
       FROM orders
       GROUP BY customer_id;

StreamUnion

Combines results from multiple queries.

    SELECT * FROM european_orders
    UNION ALL
    SELECT * FROM american_orders;

StreamExpand

Generates multiple rows from a single row for CUBE, ROLLUP, and GROUPING SETS.

    SELECT
        department,
        brand,
        COUNT(*) as product_count,
        COUNT(DISTINCT vendor) as vendor_count
    FROM products
    GROUP BY CUBE(department, brand)
    HAVING COUNT(*) > 1;

### Specialized operations¶

StreamChangelogNormalize

Converts upsert-based changelog streams (based on primary key) into retract-based streams (with explicit +/- records) to support correct aggregation results in streaming queries.

    -- Appears when processing versioned data, like a table that uses upsert semantics
    SELECT COUNT(*) as cnt
    FROM products;

StreamAsyncCalc

Executes user-defined functions. This operator allows for non-blocking execution of user-defined functions (UDFs).

    SELECT
        my_udf(name)
    FROM customers;

StreamWindowTableFunction

Applies windowing operations as table functions.

    SELECT * FROM TABLE(
         TUMBLE(TABLE orders, DESCRIPTOR($rowtime), INTERVAL '1' HOUR)
       );

StreamCorrelate

Handles correlated subqueries (UNNEST) and table function calls.

    EXPLAIN
    SELECT
        product_id,
        product_name,
        tag
    FROM (
        VALUES
            (1, 'Laptop', ARRAY['electronics', 'computers']),
            (2, 'Phone', ARRAY['electronics', 'mobile'])
    ) AS products (product_id, product_name, tags)
    CROSS JOIN UNNEST(tags) AS t (tag);

StreamMatch

Executes [pattern-matching operations](../queries/match_recognize.html#flink-sql-pattern-recognition) using MATCH_RECOGNIZE.

    SELECT *
       FROM orders
       MATCH_RECOGNIZE (
         PARTITION BY customer_id
         ORDER BY $rowtime
         MEASURES
           COUNT(*) as order_count
         PATTERN (A B+)
         DEFINE
           A as price > 100,
           B as price <= 100
       );

## Optimizing query performance¶

### Minimizing data movement¶

Data shuffling impacts performance. When examining EXPLAIN output:

  * Look for exchange operators and upsert key changes.
  * Consider keeping compatible partitioning keys through your query.
  * Watch for opportunities to reduce data redistribution.

Pay special attention to data skew when designing your queries. If a particular key value appears much more frequently than others, it can lead to uneven processing where a single parallel instance becomes overwhelmed handling that key’s data. Consider strategies like adding additional dimensions to your keys or pre-aggregating hot keys to distribute the workload more evenly.

### Using operator reuse¶

Flink automatically reuses operators when possible. In EXPLAIN output:

  * Look for “(reused)” references showing optimization.
  * Consider restructuring queries to enable more reuse.
  * Verify that similar operations share scan results.

### Optimizing sink configuration¶

When working with sinks in upsert mode, it’s crucial to align your primary and upsert keys for optimal performance:

  * Whenever possible, configure the primary key to be identical to the upsert key.
  * Having different primary and upsert keys in upsert mode can lead to significant performance degradation.
  * If you must use different keys, carefully evaluate the performance impact and consider restructuring your query to align these keys.

