---
document_id: flink_concepts_batch-and-stream-processing_chunk_1
source_file: flink_concepts_batch-and-stream-processing.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/batch-and-stream-processing.html
title: Batch and Stream Processing in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 2
---

# Batch and Stream Processing in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® supports both batch and stream processing, which enables you to process data in either finite (bounded) or infinite (unbounded) modes. Understanding the differences between these modes is crucial for designing efficient data pipelines and analytics solutions.

## Overview¶

Flink is a distributed processing engine that excels at both batch and stream processing. While both modes share the same underlying engine and APIs, they have distinct characteristics, optimizations, and use cases.

In Confluent Cloud for Apache Flink, batch mode is available by using snapshot queries.

## Batch processing¶

Batch processing in Flink operates on _bounded datasets_ , which are finite, static collections of data. This processing mode has the following key characteristics.

* It processes complete, finite datasets, like files or database snapshots.
* Batch jobs run to completion and then terminate.
* It is optimized for throughput, focusing on processing large volumes of data efficiently.
* Batch processing can sort, aggregate, and join across the entire dataset.
* The system can drop state as soon as it is no longer needed.
* Use cases: \- Historical data analysis \- ETL (Extract, Transform, Load) operations \- Report generation \- Data warehousing

## Stream processing¶

Stream processing in Flink handles _unbounded data streams_ , which have data that arrives continuously and might never end. This processing mode has the following key characteristics.

* It processes infinite, continuous data streams, such as Kafka topics or sensor feeds.
* Stream processing jobs run indefinitely, processing data as it arrives.
* It focuses on processing data with minimal delay for low latency.
* It produces incremental results as new data arrives.
* The system must retain state to handle late or out-of-order events.
* Use cases: \- Real-time analytics \- Fraud detection \- IoT data processing \- Live dashboards

## Bounded and unbounded tables comparison¶

In Flink, tables can be either _bounded_ (batch) or _unbounded_ (streaming). The following table compares the key differences between these two modes.

Aspect | Bounded Mode (Batch) | Unbounded Mode (Streaming)
---|---|---
Data Size | Finite (static) | Infinite (dynamic, continuous)
Processing Style | Batch processing | Real-time/continuous processing
Query Semantics | All data available at once | Data arrives over time
State Management | Minimal, can drop state when done | Must retain state for late/out-of-order data
Use Cases | ETL, reporting, historical analytics | Real-time analytics, monitoring, alerting

## Differences between batch and stream processing¶

The following table compares the important differences between batch and stream processing.

Aspect | Batch Processing | Stream Processing
---|---|---
Data Model | Processes complete, finite datasets. | Processes infinite, continuous data streams.
Execution Model | Jobs run to completion. | Jobs run continuously.
Latency vs. Throughput | Optimized for high throughput. | Optimized for low latency.
State Management | Minimal state, which is dropped when no longer needed. | Robust state, which is retained for late or out-of-order data.
Fault Tolerance | Can restart from the beginning. | Requires checkpointing for fault recovery.
Query Semantics | All data is available at once, so global operations are possible. | Data arrives over time, so results are incremental.
SQL/API Differences |

* **ORDER BY** : You can use any sort order.
* **Windowing** : Supports time-based windows on static data.
* **Deduplication** : Deduplication is global.

|

* **ORDER BY** : The primary sort must be on a time attribute.
* **Windowing** : Uses windows to scope aggregations over unbounded data.
* **Deduplication** : Deduplication is incremental and often uses windows.
* **Session Windows** : Supported.

## Unified processing model¶

One important advantage of Flink is its _unified processing model_. This means that the same runtime engine handles both batch and streaming. The engine treats batch processing as a special case of stream processing. The same APIs and operators work for both modes. You can use the same code for both batch and streaming applications.

This unified approach enables you to:

* Build applications that process both historical and real-time data.
* Seamlessly transition between batch and streaming modes.
* Maintain consistent semantics across processing modes.
* Leverage the same tools and libraries for both paradigms.
