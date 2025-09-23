---
document_id: flink_reference_statements_explain_chunk_2
source_file: flink_reference_statements_explain.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/explain.html
title: SQL EXPLAIN Statement in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 5
---

physical plan of your query.

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
