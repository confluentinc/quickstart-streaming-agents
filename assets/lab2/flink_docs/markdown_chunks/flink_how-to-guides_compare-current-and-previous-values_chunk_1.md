---
document_id: flink_how-to-guides_compare-current-and-previous-values_chunk_1
source_file: flink_how-to-guides_compare-current-and-previous-values.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/compare-current-and-previous-values.html
title: Compare Current and Previous Values in a Data Stream with Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Compare Current and Previous Values in a Data Stream with Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides a [LAG](../reference/functions/aggregate-functions.html#flink-sql-lag-function) function, which is a built-in function that enables you to access data from a previous event in the same row without the need for a self-join. It gives you the ability to analyze the differences between consecutive rows or to create more complex calculations based on previous events. This can be particularly useful in scenarios such as comparing daily sales values.

In this guide, you will learn how to run an Flink SQL statement that uses the LAG function to compare current and historical order values from a continuous data stream of orders data.

This topic shows the following steps:

* Step 1: Inspect the example stream
* Step 2: View aggregated results

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

## Step 2: View aggregated results¶

  1. Run the following statement to start a query on the `orders` data using the LAG function to return current and previous order data for each customer.

         SELECT $rowtime AS row_time
               , customer_id
               , order_id
               , price
               , LAG(order_id, 1) OVER (PARTITION BY customer_id ORDER BY $rowtime) previous_order_id
               , LAG(price, 1) OVER (PARTITION BY customer_id ORDER BY $rowtime) previous_order_price
           FROM examples.marketplace.orders;

Your output should resemble:

         row_time                 customer_id  order_id                               price    previous_order_id                       previous_order_price
         2024-01-11 15:42:00.557  3213         821f81d4-d912-4e0f-ab8b-88fe8d9af397   89.34    2c26a03b-4cd5-4df6-90d0-0b11916533d2    57.89
         2024-01-11 15:42:01.079  3090         57b20b43-3f52-49d8-b8bc-3a55d0440482   50.22    c913ea7b-a7dc-4b22-b966-8df3f28e8e5e    66.12
         2024-01-11 15:42:01.391  3142         8a536722-3e4f-4920-bd33-2b981179b8f8   10.77    NULL                                    NULL
         2024-01-11 15:42:01.482  3006         cabf50e8-129d-4b71-b253-894526a571c1   113.12   NULL                                    NULL
         2024-01-11 15:42:01.681  3009         fd96d839-f06b-43ef-a23f-38e4ca6849b4   78.01    d5cdafb2-ddf1-4161-8843-48ae5f46f524    102.34
         2024-01-11 15:42:01.910  3158         16165e84-d1d6-49b9-afaf-1856c4f2a751   354.11   NULL                                    NULL
         ...

  2. Note that there are some `NULL` values for `previous_order_id` and `previous_order_price`. For these customers, the current order is the first order they have made, so there is no historical previous order data to return.
