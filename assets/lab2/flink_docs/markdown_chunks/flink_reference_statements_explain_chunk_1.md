---
document_id: flink_reference_statements_explain_chunk_1
source_file: flink_reference_statements_explain.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/explain.html
title: SQL EXPLAIN Statement in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 5
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
