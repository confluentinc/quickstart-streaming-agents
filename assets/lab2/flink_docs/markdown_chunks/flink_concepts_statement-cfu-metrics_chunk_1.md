---
document_id: flink_concepts_statement-cfu-metrics_chunk_1
source_file: flink_concepts_statement-cfu-metrics.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/statement-cfu-metrics.html
title: Statement CFU Metrics in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Statement CFU Metrics in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides detailed metrics to help you understand and manage your resource utilization. One critical aspect of this is statement CFU metrics.

## How to use statement CFU metrics¶

The statement CFU metrics give you insights into the resource consumed by individual statements running inside your compute pools.

Specifically, the statement CFU metrics enable you to:

  * **Monitor individual statement usage** : Accurately measure the number of CFUs each statement consumes over time. This metric is available for all types of statements submitted in Confluent Cloud for Apache Flink.
  * **Track resource distribution** : Understand how the resources in a compute pool are being distributed among the statements running in the compute pool.
  * **Identify high-consumption statements** : Pinpoint which statements are consuming the most CFUs, enabling you to optimize the statement’s Flink SQL code or adjust the resources available to this statement.

By monitoring statement-level CFU consumption, you can make informed decisions about your Flink application’s cost efficiency and resource utilization.

You can’t set minimum or maximum CFU limits on individual statements, but maximum CFU limits are configurable at the compute-pool level.

## Where to view statement CFU metrics?¶

The statement CFU consumption metrics are available to view in the statements summary table and in the statement side panel.

  * **Statements summary table** : Get an overview of CFU consumption for all your statements directly within the statements summary table. This provides a quick way to identify the most resource intensive statements.
  * **Statement side panel** : For a deeper dive into a statement’s resource usage, open the statement side panel. Here, you’ll find the current CFU consumption and a time-series chart that visualizes how the statement’s CFU consumption has evolved over time.

## How UDF resource consumption is represented¶

The statement CFU metric shows the resources consumed by your SQL statements and the resources consumed by any UDF instances the statement might invoke.

Resources consumed by individual UDF instances will sometimes appear as fractional CFU values. This is because multiple UDF instances can be consolidated, or “rolled into,” a single CFU of resources. Up to three instances of a UDF can be combined into one CFU.

The distribution of CFUs amongst UDFs in a compute pool is flexible. Three UDF instances across different statements can be rolled into a single CFU, as long as the statements are in the same compute pool. Also, different UDF functions and their instances can be consolidated into a single CFU, as long as they are in the same compute pool.

## Understanding differences between CFUs for compute pool and statement¶

When monitoring resource consumption in Confluent Cloud for Apache Flink, you might observe minor differences between your compute pool CFU metrics and the aggregated sum of your statement CFU metrics. These discrepancies are expected and are caused by rounding.

If your statements use UDFs, you may see a maximum discrepancy of 2 CFUs between the compute pool CFU metrics and the total sum of your statement CFU metrics.

For statements not utilizing UDFs, the maximum expected discrepancy between the compute pool CFU metrics and the total sum of your statement CFU metrics is 1 CFU.

Note

You are billed based on the compute pool CFU metrics, not on the summed total of individual statement CFU metrics.
