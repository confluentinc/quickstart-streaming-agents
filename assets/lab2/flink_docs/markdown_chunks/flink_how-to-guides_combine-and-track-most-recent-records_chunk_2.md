---
document_id: flink_how-to-guides_combine-and-track-most-recent-records_chunk_2
source_file: flink_how-to-guides_combine-and-track-most-recent-records.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/combine-and-track-most-recent-records.html
title: Combine Streams and Track Most Recent Records with Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 3
---

en-US; rv:1.9.0.11) Gecko GranParadiso/3... 67

## Step 2: Create a unified view with most recent records¶

Run the following statement to combine multiple streams while tracking the most recent information for each record:

    -- This query combines order and click data, tracking the latest values
    -- for each customer's interactions across both datasets

    -- First, combine order data and clickstream data into a single structure
    -- Note: Fields not present in one source are filled with NULL
    WITH combined_data AS (
      -- Orders data with empty click-related fields
      SELECT
        customer_id,
        order_id,
        product_id,
        price,
        CAST(NULL AS STRING) AS url,        -- Click-specific fields set to NULL
        CAST(NULL AS STRING) AS user_agent, -- for order records
        CAST(NULL AS INT) AS view_time,
        $rowtime
      FROM `examples`.`marketplace`.`orders`
      UNION ALL
      -- Click data with empty order-related fields
      SELECT
        user_id AS customer_id,             -- Normalize user_id to match customer_id
        CAST(NULL AS STRING) AS order_id,   -- Order-specific fields set to NULL
        CAST(NULL AS STRING) AS product_id, -- for click records
        CAST(NULL AS DOUBLE) AS price,
        url,
        user_agent,
        view_time,
        $rowtime
      FROM `examples`.`marketplace`.`clicks`
    )
    -- For each customer, maintain the latest value for each field
    -- using window functions over the combined dataset
    SELECT
      LAST_VALUE(customer_id) OVER w AS customer_id,
      LAST_VALUE(order_id) OVER w AS order_id,
      LAST_VALUE(product_id) OVER w AS product_id,
      LAST_VALUE(price) OVER w AS price,
      LAST_VALUE(url) OVER w AS url,
      LAST_VALUE(user_agent) OVER w AS user_agent,
      LAST_VALUE(view_time) OVER w AS view_time,
      MAX($rowtime) OVER w AS rowtime      -- Track the latest event timestamp
    FROM combined_data
    -- Define window for tracking latest values per customer
    WINDOW w AS (
      PARTITION BY customer_id             -- Group all events by customer
      ORDER BY $rowtime                    -- Order by event timestamp
      ROWS BETWEEN UNBOUNDED PRECEDING     -- Consider all previous events
        AND CURRENT ROW                    -- up to the current one
    )

Your output should resemble:

    customer_id  order_id                               product_id  price    url                                user_agent                                                                         view_time rowtime
    3243         be396ae5-d7d9-4454-99d7-9b1c155d51d4   1304        99.55    NULL                               NULL                                                                               NULL      2024-10-22T08:21:07.620Z
    3132         79e295d3-5a0b-4127-9337-9a483794e7d4   1201        21.43    NULL                               NULL                                                                               NULL      2024-10-22T08:21:07.640Z
    3099         9b59d319-c37a-4088-a803-350d43bc5382   1271        66.7     https://www.acme.com/product/foxmh Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0    79        2024-10-22T08:21:07.600Z
    3262         NULL                                   NULL        NULL     https://www.acme.com/product/lruuv Mozilla/5.0 (iPhone; CPU OS 9_3_5 like Mac OS X) AppleWebKit/601.1.46              108       2024-10-22T08:21:07.637Z
    3181         8aaa9d8e-d8f7-4bb5-9d59-ce4d0cfc9a92   1028        76.23    https://www.acme.com/product/vfzsy Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)                                 33        2024-10-22T08:21:07.656Z
    3186         e681fa67-3a1e-4e99-ba03-da9fb5d12845   1212        69.67    NULL                               NULL                                                                               NULL      2024-10-22T08:21:07.660Z
    4882         NULL                                   NULL        NULL     https://www.acme.com/product/zkxun Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14                          99        2024-10-22T08:21:07.676Z
    3238         89ba7186-f927-462b-860a-68b8c9d51a06   1336        76.89    NULL                               NULL                                                                               NULL      2024-10-22T08:21:07.679Z
    3233         ebfec6c6-3294-444b-82e5-5a66e7dc5cd5   1223        23.69    NULL                               NULL                                                                               NULL      2024-10-22T08:21:07.699Z

This pattern works by:

  1. Using a Common Table Expression (CTE) to combine all streams
  2. Setting fields not present in each stream to NULL
  3. Using window functions to track the most recent data for each field
  4. Partitioning by the common identifier to group related records
  5. Ordering by the [watermark](../../_glossary.html#term-watermark) timestamp (`$rowtime`) to ensure proper temporal sequencing

You can adapt this pattern by:

* Adding more streams to the [UNION ALL](../reference/queries/set-logic.html#flink-sql-set-logic-union)
* Changing the common identifier field in the [PARTITION BY](../reference/queries/match_recognize.html#flink-sql-pattern-recognition-partitioning) clause
* Modifying the selected fields based on your needs
* Using a custom defined watermark strategy
