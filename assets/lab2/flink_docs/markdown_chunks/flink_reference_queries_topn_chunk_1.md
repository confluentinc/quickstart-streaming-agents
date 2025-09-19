---
document_id: flink_reference_queries_topn_chunk_1
source_file: flink_reference_queries_topn.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/topn.html
title: SQL Top-N queries in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 2
---

# Top-N Queries in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables finding the smallest or largest values, ordered by columns, in a table.

## Syntax¶

    SELECT [column_list]
    FROM (
      SELECT [column_list],
        ROW_NUMBER() OVER ([PARTITION BY column1[, column2...]]
          ORDER BY column1 [asc|desc][, column2 [asc|desc]...]) AS rownum
        FROM table_name)
    WHERE rownum <= N [AND conditions]

**Parameter Specification**

Note

This query pattern must be followed exactly, otherwise, the optimizer can’t translate the query.

  * `ROW_NUMBER()`: Assigns an unique, sequential number to each row, starting with one, according to the ordering of rows within the partition. Currently, Flink supports only `ROW_NUMBER` as the over window function. In the future, Flink may support `RANK()` and `DENSE_RANK()`.
  * `PARTITION BY column1[, column2...]`: Specifies the partition columns. Each partition has a Top-N result.
  * `ORDER BY column1 [asc|desc][, column2 [asc|desc]...]`: Specifies the ordering columns. The ordering directions can be different on different columns.
  * `WHERE rownum <= N`: The `rownum <= N` is required for Flink to recognize this query is a Top-N query. The `N` represents the number of smallest or largest records to retain.
  * `[AND conditions]`: You can add other conditions in the WHERE clause, but the other conditions can only be combined with `rownum <= N` using the `AND` conjunction.

## Description¶

Find the smallest or largest values, ordered by columns, in a table.

Top-N queries return the N smallest or largest values in a table, ordered by columns. Both smallest and largest values sets are considered Top-N queries. Top-N queries are useful in cases where the need is to display only the N bottom-most or the N top- most records from batch/streaming table on a condition. This result set can be used for further analysis.

Flink uses the combination of a OVER window clause and a filter condition to express a Top-N query. With the power of OVER window `PARTITION BY` clause, Flink also supports per group Top-N. For example, the top five products per category that have the maximum sales in realtime. Top-N queries are supported for SQL on batch and streaming tables.

The Top-N query is Result Updating, which means that Flink sorts the input stream according to the order key. If the top N rows have changed, the changed rows are sent downstream as retraction/update records.
