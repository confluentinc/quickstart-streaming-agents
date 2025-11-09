---
document_id: flink_concepts_autopilot_chunk_1
source_file: flink_concepts_autopilot.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/autopilot.html
title: Flink SQL Autopilot in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Flink SQL Autopilot for Confluent Cloud¶

Autopilot scales up and scales down the compute resources that SQL statements use in Confluent Cloud for Apache Flink®. Autopilot assigns resources efficiently to SQL statements submitted in Confluent Cloud and provides elastic autoscaling for the entire time the job is running. One of the biggest benefits of using Confluent Cloud for Apache Flink is the built-in Autopilot capability.

Autopilot takes care of all the work required to scale up or scale down the compute resources that a SQL statement consumes. Resources are scaled up when a SQL statement has an increased need for resources and scaled down when resources are not being used. This is all done automatically, and no manual work is required to monitor or adjust resources. This removes the complexity of managing your own infrastructure, removes the need for over-provisioning, and ensures that you never have to pay more than needed.

The autoscaling process is based on [parallelism](overview.html#flink-sql-stream-processing-concepts-parallel-dataflows), which is the number of parallel operations that occur when the SQL statement is running. A SQL statement performs at its best when it has the optimal resources for its required parallelism.

## Scaling status¶

The scaling status in the SQL workspace shows you how the statement resources are scaling. These are the possible scaling statuses.

Scaling Status | Description
---|---
Fine | The SQL statement has enough resources to run at the required parallelism.
Pending Scale Down | The SQL statement has more resources than required and will be scaled down.
Pending Scale Up | The SQL statement doesn’t have enough resources and will be scaled up.
Compute Pool Exhausted | There aren’t enough resources in the compute pool for the statement to run with the required parallelism.

### Compute Pool Exhausted¶

The compute pool has run out of resources. SQL statements may run with a reduced parallelism, which could affect the overall performance of the statement, or a statement may not be able to run at all, because all resources in the compute pool are in use.

There are two ways to resolve this situation:

* You can add more resources by increasing the [CFU limit](flink-billing.html#flink-sql-cfus) on the compute pool.
* You can stop some running statements to free up existing resources.

## Messages Behind¶

Messages Behind is another indicator of how the statement is performing. The overall goal of Autopilot is to ensure that the SQL statement keeps up with the throughput of the source tables and topics, and to keep Messages Behind as close to zero as possible. In Apache Kafka® terms, Messages Behind is the [Consumer Lag](../../monitoring/monitor-lag.html#cloud-monitoring-lag).

A low or decreasing Messages Behind value indicates that Autopilot is doing its job successfully. The following table describes scenarios in which Autopilot is scaling resources correctly or where it may be struggling.

Messages Behind and Scaling Status | Description
---|---
Messages Behind is increasing Scaling status = “Pending Scale Up” | Autopilot has identified a need for scaling up and will increase the Statement resources. Once resources have been scaled up, the Messages Behind should start decreasing.
Messages Behind is increasing Scaling status = “Fine” | There is likely a problem. Reach out to Confluent Support. For more information, see [Get Help with Confluent Cloud for Apache Flink](../get-help.html#ccloud-flink-help).
Messages Behind is not increasing Compute Pool is Exhausted | The statement resources can keep up with throughput but Autopilot needs to assign more resources to improve performance capacity. You can either add more resources by increasing the CFU limit on the compute pool or stop some running statements to free up existing resources.
