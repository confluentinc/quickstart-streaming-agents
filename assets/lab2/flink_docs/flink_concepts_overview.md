---
source_url: https://docs.confluent.io/cloud/current/flink/concepts/overview.html
title: Stream Processing Concepts in Confluent Cloud for Apache Flink
hierarchy: ['concepts', 'overview.html']
scraped_date: 2025-09-05T13:46:07.808343
---

# Stream Processing Concepts in Confluent Cloud for Apache Flink¶

Apache Flink® SQL, a high-level API powered by Confluent Cloud for Apache Flink, offers a simple and easy way to leverage the power of stream processing. With support for a wide variety of built-in [functions](../reference/functions/overview.html#flink-sql-functions-overview), [queries](../reference/queries/overview.html#flink-sql-queries), and [statements](statements.html#flink-sql-statements), Flink SQL provides real-time insights into streaming data. Time is a critical element in stream processing, and Flink SQL makes it easy to process data as it arrives, avoiding delays. By using SQL syntax, you can declare expressions that filter, aggregate, route, and mutate streams of data, simplifying your data processing workflows.

## Stream processing¶

Streams are the de-facto way to create data. Whether the data comprises events from web servers, trades from a stock exchange, or sensor readings from a machine on a factory floor, data is created as part of a stream.

When you analyze data, you can either organize your processing around `bounded` or `unbounded` streams, and which of these paradigms you choose has significant consequences.

**Batch processing** is the paradigm at work when you process a bounded data stream. In this mode of operation, you can choose to ingest the entire dataset before producing any results, which means that it’s possible, for example, to sort the data, compute global statistics, or produce a final report that summarizes all of the input.

[Snapshot queries](snapshot-queries.html#flink-sql-snapshot-queries) are a type of batch processing query that enables you to process a subset of data from a Kafka topic.

**Stream processing** , on the other hand, involves unbounded data streams. Conceptually, at least, the input may never end, and so you must process the data continuously as it arrives.

### Bounded and unbounded tables¶

In the context of a Flink table, **bounded mode** refers to processing data that is finite, which means that the dataset has a clear beginning and end and does not grow continuously or update over time. This is in contrast to **unbounded mode** , where data arrives as a continuous stream, potentially with no end.

The [scan.bounded.mode](../reference/statements/create-table.html#flink-sql-create-table-with-scan-bounded-mode) property controls how Flink consumes data from a Kafka topic.

A table can be bounded by committed offsets in Kafka brokers of a specific consumer group, by latest offsets, or by a user-supplied timestamp.

#### Key characteristics of bounded mode¶

  * **Finite data** : The table represents a static dataset, similar to a traditional table in a relational database or a file in a data lake. Once all records are read, there is no more data to process.
  * **Batch processing** : Operations on bounded tables are executed in batch mode. This means Flink processes all the available data, computes the results, and then the job finishes. This is suitable for use cases like ETL, reporting, and historical analysis.
  * **Optimized execution** : Since the system knows the data is finite, it can apply optimizations that are not possible with unbounded (streaming) data. For example, it can sort by any column, perform global aggregations, and use blocking operators.
  * **No need for state retention** : Unlike streaming mode, where Flink must keep state around to handle late or out-of-order events, batch mode can drop state as soon as it is no longer needed, reducing resource usage.

The following table compares the characteristics of bounded and unbounded tables.

Aspect | Bounded Mode (Batch) | Unbounded Mode (Streaming)
---|---|---
Data Size | Finite (static) | Infinite (dynamic, continuous)
Processing Style | Batch processing | Real-time/continuous processing
Query Semantics | All data available at once | Data arrives over time
State Management | Minimal, can drop state when done | Must retain state for late/out-of-order data
Use Cases | ETL, reporting, historical analytics | Real-time analytics, monitoring, alerting

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

## State management¶

### Fault tolerance via state snapshots¶

Flink is able to provide fault-tolerant, exactly-once semantics through a combination of state snapshots and stream replay. These snapshots capture the entire state of the distributed pipeline, recording offsets into the input queues as well as the state throughout the job graph that has resulted from having ingested the data up to that point. When a failure occurs, the sources are rewound, the state is restored, and processing is resumed. As depicted above, these state snapshots are captured asynchronously, without impeding the ongoing processing.

Table programs that run in streaming mode leverage all capabilities of Flink as a stateful stream processor.

In particular, a table program can be configured with a state backend and various checkpointing options for handling different requirements regarding state size and fault tolerance.

### State usage¶

Due to the declarative nature of Table API and SQL programs, it’s not always obvious where and how much state is used within a pipeline. The planner decides whether state is necessary to compute a correct result. A pipeline is optimized to claim as little state as possible given the current set of optimizer rules.

Conceptually, source tables are never kept entirely in state. An implementer deals with logical tables, named [dynamic tables](dynamic-tables.html#flink-sql-dynamic-tables). Their state requirements depend on the operations that are in use.

Queries such as `SELECT ... FROM ... WHERE` which consist only of field projections or filters are usually stateless pipelines. But operations like joins, aggregations, or deduplications require keeping intermediate results in a fault-tolerant storage for which Flink state abstractions are used.

Refer to the individual operator documentation for more details about how much state is required and how to limit a potentially ever-growing state size.

For example, a regular SQL join of two tables requires the operator to keep both input tables in state entirely. For correct SQL semantics, the runtime needs to assume that a match could occur at any point in time from both sides of the join. Flink provides [optimized window and interval joins](../reference/queries/joins.html#flink-sql-joins) that aim to keep the state size small by exploiting the concept of [watermark](../../_glossary.html#term-watermark) strategies.

Another example is the following query that computes the number of clicks per session.

    SELECT sessionId, COUNT(*) FROM clicks GROUP BY sessionId;

The `sessionId` attribute is used as a grouping key and the continuous query maintains a count for each `sessionId` it observes. The `sessionId` attribute is evolving over time and `sessionId` values are only active until the session ends, i.e., for a limited period of time. However, the continuous query cannot know about this property of `sessionId` and expects that every `sessionId` value can occur at any point of time. It maintains a count for each observed `sessionId` value. Consequently, the total state size of the query is continuously growing as more and more `sessionId` values are observed.

### Dataflow Model¶

Flink implements many techniques from the Dataflow Model. The following articles provide a good introduction to event time and [watermark](../../_glossary.html#term-watermark) strategies.

  * Blog post: [Streaming 101 by Tyler Akidau](https://www.oreilly.com/ideas/the-world-beyond-batch-streaming-101)
  * [Dataflow Model](https://research.google.com/pubs/archive/43864.pdf)
