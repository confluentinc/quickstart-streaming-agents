---
document_id: flink_concepts_overview_chunk_2
source_file: flink_concepts_overview.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/overview.html
title: Stream Processing Concepts in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 4
---

simplifying your data processing workflows.

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
* **Redistributing** streams (as between map() and keyBy/window above, as well as between keyBy/window and Sink) change the partitioning of streams. Each operator subtask sends data to different target subtasks, depending on the selected transformation. Examples are keyBy() (which re-partitions by hashing the key), broadcast(), or rebalance() (which re-partitions randomly). In a redistributing exchange the ordering among the elements is only preserved within each pair of sending
