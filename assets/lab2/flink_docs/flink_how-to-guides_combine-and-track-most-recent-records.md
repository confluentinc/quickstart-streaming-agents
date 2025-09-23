---
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/combine-and-track-most-recent-records.html
title: Combine Streams and Track Most Recent Records with Confluent Cloud for Apache Flink
hierarchy: ['how-to-guides', 'combine-and-track-most-recent-records.html']
scraped_date: 2025-09-05T13:47:26.653904
---

# Combine Streams and Track Most Recent Records with Confluent Cloud for Apache Flink¶

When working with streaming data, it’s common to need to combine information from multiple sources while tracking the most recent record data. Confluent Cloud for Apache Flink® provides powerful capabilities to merge streams and maintain up-to-date information for each record, regardless of which stream it originated from.

In this guide, you learn how to run a Flink SQL statement that combines multiple data streams and keeps track of the most recent information for each record by using window functions. While this example uses order and clickstream data, the pattern can be applied to any number of streams that share a common identifier.

This topic shows the following steps:

  * Step 1: Inspect the example source streams
  * Step 2: Create a unified view with most recent records

## Prerequisites¶

  * Access to Confluent Cloud.
  * The OrganizationAdmin, EnvironmentAdmin, or FlinkAdmin role for creating compute pools, or the FlinkDeveloper role if you already have a compute pool. If you don’t have the appropriate role, contact your OrganizationAdmin or EnvironmentAdmin. For more information, see [Grant Role-Based Access in Confluent Cloud for Apache Flink](../operate-and-deploy/flink-rbac.html#flink-rbac).
  * A provisioned Flink compute pool.

## Step 1: Inspect the example source streams¶

In this step, you examine the read-only `orders` and `clicks` tables in the `examples.marketplace` database to identify:

  * The common identifier field that links the streams
  * The unique fields from each stream that you want to track

  1. Log in to Confluent Cloud and navigate to your Flink workspace.

  2. Examine your source streams. The following example includes orders and clicks:

         -- First stream
         SELECT * FROM `examples`.`marketplace`.`orders`;

         -- Second stream
         SELECT * FROM `examples`.`marketplace`.`clicks`;

Your output from `orders` should resemble:

         order_id                                customer_id   product_id  price
         be396ae5-d7d9-4454-99d7-9b1c155d51d4    3243          1304        99.55
         79e295d3-5a0b-4127-9337-9a483794e7d4    3132          1201        21.43
         9b59d319-c37a-4088-a803-350d43bc5382    3099          1271        66.70
         8aaa9d8e-d8f7-4bb5-9d59-ce4d0cfc9a92    3181          1028        76.23
         e681fa67-3a1e-4e99-ba03-da9fb5d12845    3186          1212        69.67
         89ba7186-f927-462b-860a-68b8c9d51a06    3238          1336        76.89
         ebfec6c6-3294-444b-82e5-5a66e7dc5cd5    3233          1223        23.69

Your output from `clicks` should resemble:

         click_id                             user_id url                                user_agent                                                                      view_time
         a5c31d8b-cc93-4a48-a7d9-c1d389c83f4a 3099    https://www.acme.com/product/foxmh Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0 79
         b7d42e6f-85a1-4f7b-b1c2-d3e456789abc 3262    https://www.acme.com/product/lruuv Mozilla/5.0 (iPhone; CPU OS 9_3_5 like Mac OS X) AppleWebKit/601.1.46           108
         c8e53f7a-96b2-4a8c-c2d3-e4f567890def 3181    https://www.acme.com/product/vfzsy Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)                              33
         d9f64g8b-a7c3-4b9d-d3e4-f5g678901hij 4882    https://www.acme.com/product/zkxun Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14                       99
         e74441b6-09da-4113-b8f9-db12cee90c77 3500    https://www.acme.com/product/lruuv Mozilla/5.0 (iPhone; CPU iPhone OS 11_4_1 like Mac OS X) AppleWebKit/6...       116
         f39236ac-2646-4e5d-bab2-cd4445630529 4360    https://www.acme.com/product/vfzsy Mozilla/4.0 (compatible; Win32; WinHttp.WinHttpRequest.5)                       52
         3f3b06df-aa2b-417e-833e-ccc232536c4a 4171    https://www.acme.com/product/foxmh Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) C...        82
         ee9fe475-5420-410d-90ae-47987eba32d5 4095    https://www.acme.com/product/ifgcb Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/1...        119
         e75faa6f-78d3-45e0-817e-1338381f53a2 4904    https://www.acme.com/product/ffnsl Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like ...         36
         77c6acbb-eb71-4a49-96e5-714f8b024c98 4681    https://www.acme.com/product/zkxun Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.11) Gecko GranParadiso/3...    67

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

## Key considerations¶

When applying this pattern, consider:

  * All streams must have a common identifier field
  * Timestamp fields should be consistent across streams
  * NULL handling may need adjustment based on your use case

### Why UNION ALL vs. JOIN?¶

While it might seem natural to use a `JOIN` to combine data from multiple streams, the `UNION ALL` approach shown in this pattern offers several important advantages for streaming use cases.

Consider what would happen with a join-based approach:

    SELECT
      COALESCE(o.customer_id, c.user_id) as customer_id,
      o.order_id,
      o.product_id,
      o.price,
      c.url,
      c.user_agent,
      c.view_time
    FROM orders o
    FULL OUTER JOIN clicks c
    ON o.customer_id = c.user_id

This join would need to maintain state for both streams to match records, leading to several challenges in a streaming context:

#### State management and performance¶

When using a join, Flink must maintain state for both sides of the join operation to match records. This state grows over time as new records arrive, consuming more resources. In contrast, the `UNION ALL` pattern simply combines records as they arrive, without needing to maintain state for matching.

#### Handling late-arriving data¶

With a join, if a click record arrives late, Flink would need to match it against all historical order records for that customer. Similarly, a late order would need to be matched against historical clicks. This can lead to reprocessing of historical data and potential out-of-order results. The `UNION ALL` pattern handles each record independently, making late-arriving data much simpler to process.

#### Append-only output¶

The combination of `UNION ALL` with window functions produces an append-only output stream, where each record contains the complete latest state for a customer at the time of each event. When materializing these results, you can:

  * Use an append-only table to maintain the history of how each customer’s state changed over time
  * Use an upsert table to maintain only the current state for each customer

For example, when new events arrive for customer 3099 (first an order, then a click):

    customer_id  order_id                                product_id  price    url                                        user_agent                                                                          view_time  rowtime
    3099         e681fa67-3a1e-4e99-ba03-da9fb5d12845    1424        89.99    NULL                                       NULL                                                                                NULL       2024-10-22T08:21:08.620Z
    3099         e681fa67-3a1e-4e99-ba03-da9fb5d12845    1424        89.99    https://www.acme.com/product/vfzsy         Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0     45         2024-10-22T08:21:09.620Z

Each event produces a new output record with the complete latest state for that customer.

In contrast, a join produces a changelog output where existing records may be updated, requiring downstream systems to handle inserts, updates, and deletions.
