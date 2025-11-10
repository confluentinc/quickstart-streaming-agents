---
document_id: flink_reference_queries_topn_chunk_2
source_file: flink_reference_queries_topn.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/topn.html
title: SQL Top-N queries in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 2
---

sent downstream as retraction/update records.

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
