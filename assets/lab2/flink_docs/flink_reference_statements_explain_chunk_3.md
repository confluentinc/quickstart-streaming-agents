---
document_id: flink_reference_statements_explain_chunk_3
source_file: flink_reference_statements_explain.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/explain.html
title: SQL EXPLAIN Statement in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 5
---

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
