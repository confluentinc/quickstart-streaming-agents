---
document_id: flink_operate-and-deploy_query-profiler_chunk_1
source_file: flink_operate-and-deploy_query-profiler.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/query-profiler.html
title: Flink SQL Query Profiler in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Flink SQL Query Profiler in Confluent Cloud for Apache Flink¶

The Query Profiler is a tool in Confluent Cloud for Apache Flink® that provides enhanced visibility into how a Flink SQL [statement](../concepts/statements.html#flink-sql-statements) is processing data, which enables rapid identification of bottlenecks, data skew issues, and other performance concerns.

To use the Query Profiler, see [Profile a Query](../how-to-guides/profile-query.html#flink-sql-profile-query).

The Query Profiler is a dynamic, real-time visual dashboard that provides insights into the computations performed by your Flink SQL statements. It boosts observability, enabling you to monitor running statements and diagnose performance issues during execution. The Query Profiler presents key metrics and visual representations of the performance and behavior of individual tasks, subtasks, and operators within a statement. Query Profiler is available in the Confluent Cloud Console.

[](../../_images/flink-query-profiler.gif)

Key features of the Query Profiler include:

* **Monitor in real time:** Track the live performance of your Flink SQL statements, enabling you to react quickly to emerging issues.
* **View detailed metrics:** The profiler provides a breakdown of performance metrics at various levels, including statement, task, operator, and partition levels, which helps you understand how different components of a Flink SQL job are performing.
* **Visualize data flow:** The profiler visualizes data flow as a job graph, showing how data is processed through different tasks and operators. This helps you identify operators experiencing high latency, large amounts of state, or workload imbalances.
* **Reduce manual analysis:** By offering immediate visibility into performance data, the profiler reduces the need for extensive manual logging and analysis, which can consume significant developer time. This enables you to focus on optimizing your queries and improving performance.

The Query Profiler helps you manage the complexities of stream processing applications and optimize query performance in real time.

## Available metrics¶

The Query Profiler provides the following metrics for the tasks in your Flink statements.

Metric | Definition
---|---
Backpressure | Percentage of time a task is regulating data flow to match processing speed by reducing pending events.
Busyness | The percentage of time a task is actively processing data. If a task has multiple subtasks running in parallel, Query Profiler shows the highest busyness value seen among them. Note that idleness and busyness will not always add up to 100%.
Bytes in/min | Amount of data received by a task per minute.
Bytes out/min | Amount of data sent by a task per minute.
Idleness | The percentage of time a task is not actively processing data. If a task has multiple subtasks running in parallel, Query Profiler shows the highest idleness value seen among them. Note that idleness and busyness do not always add up to 100%.
Messages in/min | Number of events the task receives per minute.
Messages out/min | Number of events the task sends out per minute.
State size | Amount of data stored by the task during processing to track information across events.
Watermark | Timestamp Flink uses to track event time progress and handle out-of-order events.

The Query Profiler provides the following metrics for the operators in your Flink statements.

Metric | Definition
---|---
Messages in/min | Number of events the operator receives per minute.
Messages out/min | Number of events the operator sends out per minute.
State size | Amount of data stored by the operator during processing to track information across events.
Watermark | Timestamp Flink uses to track event time progress and handle out-of-order events.

The Query Profiler provides the following metrics for the Kafka partitions in your data source(s).

Metric | Definition
---|---
Active | Percentage of time the partition is active. An active partition processes events and creates watermarks to keep your statements running smoothly.
Blocked | Percentage of time the partition is blocked. A blocked partition is overwhelmed with data, causing delays in the watermark calculation.
Idle | Percentage of time the partition is idle. An idle partition has not received any events for a certain time period and is not contributing to the watermark calculation.
