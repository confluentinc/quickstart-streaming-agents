---
document_id: flink_concepts_batch-and-stream-processing_chunk_2
source_file: flink_concepts_batch-and-stream-processing.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/batch-and-stream-processing.html
title: Batch and Stream Processing in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 2
---

and libraries for both paradigms.

## Time and watermarks¶

Time and watermarks are important concepts in Flink that help you process data correctly.

  * **Batch mode** : Time is fixed. All data is available, so event time and processing time are equivalent.
  * **Streaming mode** : Time is dynamic. Streaming mode uses watermarks to track event time progress and handle out-of-order data.
  * **Windowing** : In streaming, you use windows (tumbling, hopping, cumulative, session) to group data for aggregation. In batch, windows apply to static data.

For more information, see [Time and Watermarks](timely-stream-processing.html#flink-sql-timely-stream-processing).

## Determinism¶

Determinism is a key concept in Flink that helps you ensure that your queries always produce the same results.

  * **Batch** : Re-running a batch job on the same data yields the same result, except for non-deterministic functions like [UUID()](../reference/functions/numeric-functions.html#flink-sql-uuid-function).
  * **Streaming** : Results can vary due to timing, order of arrival, and late data. Determinism is harder to guarantee.

For more information, see [Determinism in Continuous Queries](determinism.html#flink-sql-determinism).

## Snapshot queries and batch mode¶

In Confluent Cloud for Apache Flink, batch mode is available by using snapshot queries.

  * **Snapshot queries** : These are batch queries that automatically bound the input sources as of the current time.
  * **Batch optimizations** : Batch mode enables optimizations like global sorting, blocking operators, and efficient joins. Snapshot queries benefit from these optimizations.
  * **Resource usage** : Batch jobs, which are snapshot queries in Confluent Cloud for Apache Flink, release resources when finished. Streaming jobs hold resources as long as they run.

For more information, see [Snapshot Queries](snapshot-queries.html#flink-sql-snapshot-queries).

## Examples¶

The following code example shows a batch query.

    -- Count all orders in a bounded table
    SELECT COUNT(*) FROM orders;

The following code example shows a streaming query.

    -- Count orders per minute in an unbounded stream.
    SELECT window_start, window_end, COUNT(*)
    FROM TABLE(
      TUMBLE(TABLE orders, DESCRIPTOR(order_time), INTERVAL '1' MINUTE))
    GROUP BY window_start, window_end;
