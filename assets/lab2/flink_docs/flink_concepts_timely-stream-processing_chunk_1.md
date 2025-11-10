---
document_id: flink_concepts_timely-stream-processing_chunk_1
source_file: flink_concepts_timely-stream-processing.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/timely-stream-processing.html
title: Time and Watermarks in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 5
---

# Time and Watermarks in Confluent Cloud for Apache Flink¶

Timely stream processing is an extension of stateful stream processing that incorporates time into the computation. It’s commonly used for time series analysis, aggregations based on windows, and event processing where the time of occurrence is important.

If you’re working with timely Apache Flink® applications on Confluent Cloud, it’s important to consider certain factors to ensure optimal performance. Learn more about these considerations in the following sections.

## Notions of time: Event Time and Processing Time¶

When referring to _time_ in a streaming program, like when you define windows, different notions of time may apply.

### Processing time¶

Processing time refers to the system time of the machine that’s executing the operation.

When a streaming program runs on processing time, all time-based operations, like time windows, use the system clock of the machines that run the operator.

An hourly processing time window includes all records that arrived at a specific operator between the times when the system clock indicated the full hour.

For example, if an application begins running at 9:15 AM, the first hourly processing time window includes events processed between 9:15 AM and 10:00 AM, the next window includes events processed between 10:00 AM and 11:00 AM, and so on.

Processing time is the simplest notion of time and requires no coordination between streams and machines. It provides the best performance and the lowest latency. But in distributed and asynchronous environments, processing time doesn’t provide determinism, because it’s susceptible to the speed at which records arrive in the system, like from a message queue, to the speed at which records flow between operators inside the system, and to outages (scheduled, or otherwise).

### Event time¶

Event time is the time that each individual event occurred on its producing device. This time is typically embedded within the records before they enter Flink, and this _event timestamp_ can be extracted from each record.

In event time, the progress of time depends on the data, not on any wall clocks. Event-time programs must specify how to generate _event-time watermarks_ , which is the mechanism that signals progress in event time. This watermarking mechanism is described in the Event Time and Watermarks section.

In a perfect world, event-time processing would yield completely consistent and deterministic results, regardless of when events arrive, or their ordering. But unless the events are known to arrive in-order (by timestamp), event-time processing incurs some latency while waiting for out-of-order events. Because it’s only possible to wait for a finite period of time, this places a limit on how deterministic event-time applications can be.

Assuming all of the data has arrived, event-time operations behave as expected, and produce correct and consistent results even when working with out-of-order or late events, or when reprocessing historic data.

For example, an hourly event-time window contains all records that carry an event timestamp that falls into that hour, regardless of the order in which they arrive, or when they’re processed. For more information, see Lateness.

Sometimes when an event-time program is processing live data in real-time, it uses some _processing time_ operations in order to guarantee that they are progressing in a timely fashion.

Event Time and Processing Time¶
