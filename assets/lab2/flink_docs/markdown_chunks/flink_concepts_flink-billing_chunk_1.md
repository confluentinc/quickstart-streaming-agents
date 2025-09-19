---
document_id: flink_concepts_flink-billing_chunk_1
source_file: flink_concepts_flink-billing.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/flink-billing.html
title: Billing in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 2
---

# Billing on Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® is a serverless stream-processing platform with usage-based pricing, where you are charged only for the duration that your queries are running.

You configure Flink by creating a Flink [compute pool](compute-pools.html#flink-sql-compute-pools).

You are charged for the CFUs consumed when you run statements within a compute pool. While the compute pool itself scales elastically to provide the necessary resources, your cost is determined by the actual CFUs used per minute, not the provisioned size of the pool.

You can configure the maximum size of a compute pool to limit your spending.

## CFUs¶

A CFU is a logical unit of processing power that is used to measure the resources consumed by Confluent Cloud for Apache Flink. Each Flink statement consumes a minimum of 1 CFU-minute but may consume more depending on the needs of the workload.

## CFU billing¶

You are billed for the total number of CFUs consumed inside a compute pool per minute. Usage is stated in hours in order to apply hourly pricing to minute-by-minute use. For example, 30 CFU-minutes is 0.5 CFU-hours.

CFU pricing
    $0.21/CFU-hour, calculated by the minute ($0.0035/CFU-minute)

Prices vary by [cloud region](../../billing/overview.html#cloud-billing-regional-multiplier).

## Networking fees¶

Using Flink to read and write data from Apache Kafka® doesn’t add any new Flink-specific networking fees, but you’re still responsible for the Confluent Cloud networking rates for data read from and written to your Kafka clusters. These are existing Kafka costs, not new charges created by Flink.

## Cost Management¶

You can’t define the number of CFUs required for individual statements. CFUs are counted by Confluent Cloud for Apache Flink. You can configure the maximum size of a compute pool to limit your spending by setting a parameter named MAX_CFU, which sets an upper limit on the hourly spend on the compute pool. If the size of the workload in a pool exceeds MAX_CFU, new statements are rejected. Existing workloads continue running but may experience increased latency.

Note

You can increase the MAX_CFU value after you create a compute pool, but decreasing the initial MAX_CFU value is not supported. For more information, see [Update a compute pool](../operate-and-deploy/create-compute-pool.html#flink-sql-manage-compute-pool-update).

For more information on CFU prices, see [Confluent Cloud Pricing](https://www.confluent.io/confluent-cloud/pricing/).
