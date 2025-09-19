---
document_id: flink_concepts_timely-stream-processing_chunk_4
source_file: flink_concepts_timely-stream-processing.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/timely-stream-processing.html
title: Time and Watermarks in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 5
---

The current watermark at both of the window operators is 1:17, because this is the furthest behind of the watermarks coming into the windows from the Kafka sources.

The furthest behind of all four Kafka partitions determines the overall progress of the windows.

### Watermark alignment¶

Watermark alignment enables you to specify how tightly synchronized your streams should be, preventing any of the sources from getting too far ahead of the others. It addresses the problem of temporal joins between streams with progressively diverging timestamps.

When performing temporal joins between two streams, if one stream is significantly ahead of the other, data from the leading stream must be buffered while waiting for the watermark of the lagging stream to advance. As timestamps diverge further, the buffering requirements grow, potentially causing performance degradation and operational issues, like checkpointing failures.

Watermark alignment enables you to pause reading from streams that are too far ahead, enabling lagging streams to catch up and preventing the situation from worsening. This feature is particularly valuable when joining streams that have naturally diverging timestamps, such as when one data source produces events more frequently or with different timing characteristics than another.

Watermark alignment provides these benefits:

  * Reduces memory buffering requirements
  * Improves performance by preventing excessive data buffering
  * Prevents operational problems like checkpointing failures
  * Provides control over stream synchronization

In Confluent Cloud for Apache Flink, watermark alignment is enabled by default.

Set the `sql.tables.scan.watermark-alignment.max-allowed-drift` session option to change the maximum allowed deviation, or _watermark drift_.

The default maximum watermark drift is 5 minutes. This value matches it with the default maximum idleness detection timeout, which is also 5 minutes. Otherwise, watermark alignment would occur while Flink waits for a partition to switch to idle, potentially wasting CPU resources.

Only increase the watermark alignment’s maximum allowed drift to match the idleness timeout when you increase the idleness timeout.

Decreasing the watermark alignment’s maximum allowed drift may be justified if records throughput, expressed as records per minute of event time, is too large for windowed/temporal operators to buffer the default 5 minutes of the data _and_ the window’s length is lower than 5 minutes.
