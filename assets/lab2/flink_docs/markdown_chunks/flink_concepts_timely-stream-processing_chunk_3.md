---
document_id: flink_concepts_timely-stream-processing_chunk_3
source_file: flink_concepts_timely-stream-processing.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/timely-stream-processing.html
title: Time and Watermarks in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 5
---

The following diagram shows an example of events and watermarks flowing through parallel streams, and operators tracking event time.

Parallel data streams and operators with events and watermarks¶

### Lateness¶

It’s possible that certain elements violate the watermark condition, meaning that even after the _Watermark(t)_ has occurred, more elements with timestamp _t’ <= t_ occur.

In many real-world systems, certain elements can be delayed for arbitrary lengths of time, making it impossible to specify a time by which all elements of a certain event timestamp will have occurred. Furthermore, even if the lateness can be bounded, delaying the watermarks by too much is often not desirable, because it causes too much delay in the evaluation of event-time windows.

For this reason, streaming programs may explicitly expect some _late_ elements. Late elements are elements that arrive after the system’s event time clock, as signaled by the watermarks, has already passed the time of the late element’s timestamp.

Currently, Flink does not support late events or allowed lateness.

### Windowing¶

Aggregating events, for example in counts and sums, works differently with streams than in batch processing. For example, it’s impossible to count all elements in a stream, because streams are, in general, infinite (unbounded). Instead, aggregates on streams, like counts and sums, are scoped by _windows_ , like as _“count over the last 5 minutes”_ , or _“sum of the last 100 elements”_.

Time windows and count windows on a data stream¶

Windows can be _time driven_ , for example, “every 30 seconds”, or _data driven_ , for example, “every 100 elements”.

There are different types of windows, for example:

  * **Tumbling windows:** no overlap
  * **Sliding windows:** with overlap
  * **Session windows:** punctuated by a gap of inactivity

For more information, see:

  * [Window Aggregation Queries in Confluent Cloud for Apache Flink](../reference/queries/window-aggregation.html#flink-sql-window-aggregation)
  * [Window Deduplication Queries in Confluent Cloud for Apache Flink](../reference/queries/window-deduplication.html#flink-sql-window-deduplication)
  * [Window Join Queries in Confluent Cloud for Apache Flink](../reference/queries/window-join.html#flink-sql-window-join)
  * [Window Top-N Queries in Confluent Cloud for Apache Flink](../reference/queries/window-topn.html#flink-sql-window-top-n)
  * [Windowing Table-Valued Functions (Windowing TVFs) in Confluent Cloud for Apache Flink](../reference/queries/window-tvf.html#flink-sql-window-tvfs)

### Watermarks and windows¶

In the following example, the source is a Kafka topic with 4 partitions.

The Flink job is running with a parallelism of 2, and each instance of the Kafka source reads from 2 partitions.

Each event has a key, shown as a letter from A to D, and a timestamp.

The events shown in bold text have already been read. The events in gray, to the left of the read position, will be read next.

The events that have already been read are shuffled by key into the window operators, where the events are counted by key for each hour.

Example Flink job graph with windows and watermarks.¶

Because the hour from 1 to 2 o’clock hasn’t been finalized yet, the windows keep track of the counters for that hour. There have been two events for key A for that hour, one event for key B, and so on.

Because events for the following hour have already begun to appear, these windows also maintain counters for the hour from 2 o’clock to 3 o’clock.

These windows wait for watermarks to trigger them to produce their results. The watermarks come from the watermark generators in the Kafka source operators.

For each Kafka partition, the watermark generator keeps track of the largest timestamp seen so far, and subtracts from that an estimate of the expected out-of-orderness.

For example, for Partition 1, the largest timestamp is 1:30. Assuming that the events are at most 1 minute out of order, then the watermark for Partition 1 is 1:29.

A similar computation for Partition 3 yields a watermark of 1:30, and so on for the remaining partitions.

Each of the two Kafka source instances take as its watermark the minimum of these per-partition watermarks

From the point of view of the uppermost Kafka source operator, the watermark it produces should include a timestamp that reflects how complete the stream is that it is producing.

This stream from Kafka Source 1 includes events from both Partition 1 and Partition 3, so it can be no more complete than the furthest behind of these two partitions, which is Partition 1.

Although Partition 1 has seen an event with a timestamp as late as 1:30, it reports its watermark as 1:29, because it allowing for its events to be up to one minute out-of-order.

This same reasoning is applied as the watermarks flow downstream through the job graph. Each instance of the window operator has received watermarks from the two Kafka source instances.
