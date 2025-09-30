---
document_id: flink_concepts_overview_chunk_3
source_file: flink_concepts_overview.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/overview.html
title: Stream Processing Concepts in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 4
---

and receiving subtasks (for example, subtask[1] of map() and subtask[2] of keyBy/window). So, for example, the redistribution between the keyBy/window and the Sink operators shown above introduces non-determinism regarding the order in which the aggregated results for different keys arrive at the Sink.

### Timely stream processing¶

For most streaming applications it is very valuable to be able re-process historic data with the same code that is used to process live data - and to produce deterministic, consistent results, regardless.

It can also be crucial to pay attention to the order in which events occurred, rather than the order in which they are delivered for processing, and to be able to reason about when a set of events is (or should be) complete. For example, consider the set of events involved in an e-commerce transaction, or financial trade.

These requirements for timely stream processing can be met by using event time timestamps that are recorded in the data stream, rather than using the clocks of the machines processing the data.

### Stateful stream processing¶

Flink operations can be stateful. This means that how one event is handled can depend on the accumulated effect of all the events that came before it. State may be used for something simple, such as counting events per minute to display on a dashboard, or for something more complex, such as computing features for a fraud detection model.

A Flink application is run in parallel on a distributed cluster. The various parallel instances of a given operator will execute independently, in separate threads, and in general will be running on different machines.

The set of parallel instances of a stateful operator is effectively a sharded key-value store. Each parallel instance is responsible for handling events for a specific group of keys, and the state for those keys is kept locally.

The following diagram shows a job running with a parallelism of two across the first three operators in the job graph, terminating in a sink that has a parallelism of one. The third operator is stateful, and a fully-connected network shuffle is occurring between the second and third operators. This is being done to partition the stream by some key, so that all of the events that need to be processed together will be.

[](../../_images/flink-sql-parallel-job.png)

A Flink job running with a parallelism of two.¶

State is always accessed locally, which helps Flink applications achieve high throughput and low-latency.
