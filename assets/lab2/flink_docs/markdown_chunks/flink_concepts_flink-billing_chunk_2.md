---
document_id: flink_concepts_flink-billing_chunk_2
source_file: flink_concepts_flink-billing.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/flink-billing.html
title: Billing in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 2
---

prices, see [Confluent Cloud Pricing](https://www.confluent.io/confluent-cloud/pricing/).

## Pricing examples¶

Data streaming is a real-time business, and data streams oscillate on a minute-by-minute basis, creating peaks and troughs of utilization. You don’t want to allocate and overpay for processing capacity that you aren’t using. With Confluent Cloud for Apache Flink, you pay only for the processing power that you actually use.

The following examples provide additional detail on how pricing works when processing streams using Confluent Cloud for Apache Flink.

### Data exploration and discovery¶

Most SQL queries are short-running, interactive queries that help software and data engineers understand the streams they have access to. Querying the streams directly is an important and necessary step in the iterative development of apps and pipelines.

In the following example, one user executes five different queries. Unlike other Flink offerings, Confluent Cloud for Apache Flink’s serverless architecture charges you only for the five minutes when these queries are executing, with all users able to share the resources of a single compute pool. It doesn’t matter if these queries are executed by the same person, by five different people at the same time or, as shown below, at different points in the hour.

[](../../_images/flink-sql-five-queries-over-time.png)

Example pricing calculation

* Number of queries executed = 5
* Total CFU-minutes consumed = 5
* Total charge: 5 CFU-minutes x $0.0035/CFU-minute = **$0.0175**

**Note:** The charge appears on the invoice as “0.083 CFU-hours x $0.21/CFU-hour”.

### Many data streaming apps and statements¶

Data streaming architectures are composed of many applications, each with their own workload requirements. An architecture can be a mix of interactive, terminating statements and continuous, streaming statements. Confluent Cloud for Apache Flink automatically scales the processing power of the Flink compute pool up and down in real-time to ensure your apps have the processing power they need, while charging only for the minutes needed.

In the following example, five streaming statements are running in a single compute pool. The data streams are oscillating, and you can see spikes of utilization for short periods within the hour. Each statement attracts a minimum price of 1 CFU-minute ($0.0035 in this example) and is automatically scaled up and down as needed on a per-minute basis.

[](../../_images/flink-sql-five-queries-changing-workloads.png)

Statement | CFU-minutes | Statement Type
---|---|---
Q1 | 5 | Interactive
Q2 | 60 | Streaming
Q3 | 110 | Streaming
Q4 | 10 | Interactive
Q5 | 124 | Streaming
Total | 309 |

Example pricing calculation

* Number of statements executing = 5
* Total CFU-minutes consumed = 309
* Total charge: 309 CFU-minutes x $0.0035/CFU-minute = **$1.0815**

**Note:** The charge appears on the invoice as “5.15 CFU-hours x $0.21/CFU-hour”.
