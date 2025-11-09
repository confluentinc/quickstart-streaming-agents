---
document_id: flink_reference_queries_statement-set_chunk_1
source_file: flink_reference_queries_statement-set.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/statement-set.html
title: SQL Statement Sets in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# EXECUTE STATEMENT SET in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables executing multiple SQL statements as a single, optimized statement by using statement sets.

## Syntax¶

    EXECUTE STATEMENT SET
    BEGIN
      -- one or more INSERT INTO statements
      { INSERT INTO <select_statement>; }+
    END;

## Description¶

Statement sets are a feature of Confluent Cloud for Apache Flink® that enables executing a set of SQL statements as a single, optimized statement. This is useful when you have multiple SQL statements that share common intermediate results, as it enables you to reuse those results and avoid unnecessary computation.

To use statement sets, you enclose one or more SQL statements in a block and execute them as a single unit. All statements in the block are optimized and executed together as a single Flink statement. Statement sets are particularly useful when you have multiple INSERT INTO statements that read from the same table or share intermediate results. By executing these statements together as a single statement, you can avoid redundant computation and improve performance.

## Example¶

The following query results in a single statement being executed which reads from an `orders` table.

  * If the status is `completed`, the `product` and `quantity` values are written to the `sales` table.
  * If the status is `returned`, the `product` and `quantity` values are written to the `returns` table.

    EXECUTE STATEMENT SET
    BEGIN
       INSERT INTO `sales` (product, quantity) SELECT product, quantity FROM orders WHERE status = 'completed';
       INSERT INTO `returns` (product, quantity) SELECT product, quantity FROM orders WHERE status = 'returned';
    END;
