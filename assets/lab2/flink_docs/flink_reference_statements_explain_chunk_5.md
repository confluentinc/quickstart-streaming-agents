---
document_id: flink_reference_statements_explain_chunk_5
source_file: flink_reference_statements_explain.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/explain.html
title: SQL EXPLAIN Statement in Confluent Cloud for Apache Flink
chunk_index: 5
total_chunks: 5
---

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
