---
document_id: flink_concepts_overview_chunk_4
source_file: flink_concepts_overview.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/overview.html
title: Stream Processing Concepts in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 4
---

achieve high throughput and low-latency.

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
