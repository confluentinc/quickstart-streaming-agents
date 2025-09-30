---
document_id: flink_concepts_flink_chunk_2
source_file: flink_concepts_flink.md
source_url: https://docs.confluent.io/platform/current/flink/concepts/flink.html
title: Understand Apache Flink
chunk_index: 2
total_chunks: 3
---

DataSet API has been deprecated.

## Stream processing¶

Streams are the de-facto way to create data. Whether the data comprises events from web servers, trades from a stock exchange, or sensor readings from a machine on a factory floor, data is created as part of a stream.

When you analyze data, you can either organize your processing around `bounded` or `unbounded` streams, and which of these paradigms you choose has significant consequences.

**Batch processing** describes processing a bounded data stream. In this mode of operation, you can choose to ingest the entire dataset before producing any results. This makes it possible, for example, to sort the data, compute global statistics, or produce a final report that summarizes all of the input.

**Stream processing** , involves unbounded data streams. Conceptually, at least, the input may never end, and so you must continuously process the data as it arrives.

A Confluent Platform for Flink application can consume real-time data from streaming sources like message queues or distributed logs, like Apache Kafka®. But Flink can also consume bounded, historic data from a variety of data sources. Similarly, the streams of results being produced by a Flink application can be sent to a wide variety of systems that can be connected as sinks.

### Parallel dataflows¶

Programs in Flink are inherently parallel and distributed. During execution, a stream has one or more **stream partitions** , and each operator has one or more **operator subtasks**. The operator subtasks are independent of one another, and execute in different threads and possibly on different machines or containers.

The number of operator subtasks is the **parallelism** of that particular operator. Different operators of the same program may have different levels of parallelism.

[](../../_images/flink-sql-parallel-dataflow.png)

A parallel dataflow in Flink with condensed view (above) and parallelized view (below).¶

Streams can transport data between two operators in a _one-to-one_ (or forwarding) pattern, or in a _redistributing_ pattern:

  * **One-to-one** streams (for example between the Source and the map() operators in the figure above) preserve the partitioning and ordering of the elements. That means that subtask[1] of the map() operator will see the same elements in the same order as they were produced by subtask[1] of the Source operator.
  * **Redistributing** streams (as between map() and keyBy/window above, as well as between keyBy/window and Sink) change the partitioning of streams. Each operator subtask sends data to different target subtasks, depending on the selected transformation. Examples are keyBy() (which re-partitions by hashing the key), broadcast(), or rebalance() (which re-partitions randomly). In a redistributing exchange the ordering among the elements is only preserved within each pair of sending and receiving subtasks (for example, subtask[1] of map() and subtask[2] of keyBy/window). So, for example, the redistribution between the keyBy/window and the Sink operators shown above introduces non-determinism regarding the order in which the aggregated results for different keys arrive at the Sink.

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
