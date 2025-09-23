---
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/topn.html
title: SQL Top-N queries in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'queries', 'topn.html']
scraped_date: 2025-09-05T13:50:12.650570
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

## Examples¶

The following examples show how to specify Top-N queries on streaming tables.

The unique key of a Top-N query is the combination of partition columns and the rownum column. Also, a Top-N query can derive the unique key of upstream.

The following example shows how to get “the top five products per category that have the maximum sales in realtime”. If `product_id` is the unique key of the `ShopSales` table, the unique keys of the Top-N query are [`category`, `rownum`] and [`product_id`].

    CREATE TABLE ShopSales (
      product_id   STRING,
      category     STRING,
      product_name STRING,
      sales        BIGINT
    ) WITH (...);

    SELECT *
    FROM (
      SELECT *,
        ROW_NUMBER() OVER (PARTITION BY category ORDER BY sales DESC) AS row_num
      FROM ShopSales)
    WHERE row_num <= 5

### No ranking output optimization¶

As described in the previous example, the `rownum` field is written into the result table as one field of the unique key, which may cause many records to be written to the result table.

For example, when a record, fro example, `product-1001`, of ranking 9 is updated and its rank is upgraded to 1, all the records from ranking 1 - 9 are output to the result table as update messages. If the result table receives too many rows, it may slow the SQL job execution.

To optimize the query, omit the `rownum` field in the outer SELECT clause of the Top-N query. This approach is reasonable, because the number of Top-N rows usually isn’t large, so consumers can sort the rows themselves quickly. Without the `rownum` field, only the changed record (`product-1001`) must be sent to downstream, which can reduce much of the IO to the result table.

The following example shows how to optimize the previous Top-N example by :

    CREATE TABLE ShopSales (
      product_id   STRING,
      category     STRING,
      product_name STRING,
      sales        BIGINT
    ) WITH (...);

    -- omit row_num field from the output
    SELECT product_id, category, product_name, sales
    FROM (
      SELECT *,
        ROW_NUMBER() OVER (PARTITION BY category ORDER BY sales DESC) AS row_num
      FROM ShopSales)
    WHERE row_num <= 5

Note

In Streaming Mode, to output the above query to an external storage and have a correct result, the external storage must have the same unique key with the Top-N query. In the above example query, if the `product_id` is the unique key of the query, then the external table should also has `product_id` as the unique key.
