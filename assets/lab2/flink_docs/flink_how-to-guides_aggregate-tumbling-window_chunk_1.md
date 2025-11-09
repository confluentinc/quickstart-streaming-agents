---
document_id: flink_how-to-guides_aggregate-tumbling-window_chunk_1
source_file: flink_how-to-guides_aggregate-tumbling-window.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/aggregate-tumbling-window.html
title: Aggregate a Data Stream in a Tumbling Window with Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Aggregate a Stream in a Tumbling Window with Confluent Cloud for Apache Flink¶

Aggregation over windows is central to processing streaming data. Confluent Cloud for Apache Flink® supports [Windowing Table-Valued Functions (Windowing TVFs) in Confluent Cloud for Apache Flink](../reference/queries/window-tvf.html#flink-sql-window-tvfs), a SQL-standard syntax for splitting an infinite stream into windows of finite size and computing aggregations within each window. This is often used to find the min/max/average within a group, finding the first or last record or calculating totals.

In this guide, you will learn how to run an Flink SQL statement that identifies the maximum and minimum orders from a continuous data stream of orders data.

This topic shows the following steps:

* Step 1: Inspect the example stream
* Step 2: View aggregated results in a tumbling window

## Prerequisites¶

* Access to Confluent Cloud.
* The OrganizationAdmin, EnvironmentAdmin, or FlinkAdmin role for creating compute pools, or the FlinkDeveloper role if you already have a compute pool. If you don’t have the appropriate role, contact your OrganizationAdmin or EnvironmentAdmin. For more information, see [Grant Role-Based Access in Confluent Cloud for Apache Flink](../operate-and-deploy/flink-rbac.html#flink-rbac).
* A provisioned Flink compute pool.

## Step 1: Inspect the example stream¶

In this step, you query the read-only `orders` table in the `examples.marketplace` database to inspect the stream for fields that you can mask.

  1. Log in to Confluent Cloud and navigate to your Flink workspace.

  2. In the **Use catalog** dropdown, select your environment.

  3. In the **Use database** dropdown, select your Kafka cluster.

  4. Run the following statement to inspect the example `orders` stream.

         SELECT * FROM examples.marketplace.orders;

Your output should resemble:

         order_id                                customer_id   product_id  price
         68362284-34df-41a3-87fb-50b79647b786    3195          1267        47.48
         6e03663e-d20b-4a23-848a-aec959d794e3    3094          1412        50.92
         84217b5d-7dcb-46d1-9600-675a3734a3ed    3038          1094        83.56
         ...

## Step 2: View aggregated results in a tumbling window¶

  1. Run the following statement to start a windowed query on the `orders` data.

         SELECT
           window_start,
           window_end,
           MIN(price) as minimum_order_value,
           MAX(price) as maximum_order_value
         FROM TABLE(TUMBLE(TABLE examples.marketplace.orders, DESCRIPTOR($rowtime), INTERVAL '10' SECOND))
         GROUP BY window_start, window_end;

Your output should resemble:

         window_start            window_end              minimum_order_value maximum_order_value
         2023-09-12 08:54:20.000 2023-09-12 08:54:30.000 10.05               99.75
         2023-09-12 08:54:30.000 2023-09-12 08:54:40.000 10.22               99.88
         2023-09-12 08:54:40.000 2023-09-12 08:54:50.000 10.09               150.45
         ...

The Flink statement created with this query identifies the minimum and maximum order value in each 10-second window.
