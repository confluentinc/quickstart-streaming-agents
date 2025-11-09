---
document_id: flink_concepts_snapshot-queries_chunk_2
source_file: flink_concepts_snapshot-queries.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/snapshot-queries.html
title: Snapshot Queries in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 2
---

see [Run a Snapshot Query](../how-to-guides/run-snapshot-query.html#flink-sql-run-snapshot-query).

## Technical Details¶

  * **Timestamp Resolution** : Timestamps are processed with millisecond precision
  * **State Handling** : For tables with state (like aggregations), Flink reconstructs the state by processing all relevant records up to the specified timestamp
  * **Parallelism** : Queries are automatically parallelized across available compute resources
  * **Resource Optimization** : Flink uses Kafka’s time index to quickly locate the relevant offsets, minimizing unnecessary data scanning

## Relationship to Batch Mode¶

Snapshot queries are closely related to Flink’s batch processing mode. When you execute a snapshot query:

  * Flink automatically switches to batch mode processing
  * The query processes a finite, bounded dataset up to the current timestamp
  * The computation benefits from batch optimizations like sort-merge joins
  * Resources are released once the query completes
  * Results are deterministic and reproducible

This behavior contrasts with streaming queries which:

  * Process continuous, unbounded data streams
  * Maintain persistent state and resources
  * Produce incremental, real-time results
  * May give different results when rerun due to new data

## Billing¶

Snapshot queries are billed in CFUs, in the same way that streaming queries are. For more information, see [Flink Billing](../../billing/overview.html#flink-billing).
