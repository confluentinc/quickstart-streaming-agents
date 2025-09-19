---
document_id: flink_how-to-guides_combine-and-track-most-recent-records_chunk_3
source_file: flink_how-to-guides_combine-and-track-most-recent-records.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/combine-and-track-most-recent-records.html
title: Combine Streams and Track Most Recent Records with Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 3
---

a custom defined watermark strategy

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
