---
document_id: flink_concepts_timely-stream-processing_chunk_2
source_file: flink_concepts_timely-stream-processing.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/timely-stream-processing.html
title: Time and Watermarks in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 5
---

Event Time and Processing Time¶

## Event Time and Watermarks¶

### Event time¶

A stream processor that supports _event time_ needs a way to measure the progress of event time. For example, a window operator that builds hourly windows needs to be notified when event time has passed beyond the end of an hour, so that the operator can close the window in progress.

Event time can progress independently of _processing time_ , as measured by wall clocks. For example, in one program, the current event time of an operator may trail slightly behind the processing time, accounting for a delay in receiving the events, while both proceed at the same speed. But another streaming program might progress through weeks of event time with only a few seconds of processing, by fast-forwarding through some historic data already buffered in an Apache Kafka® topic.

### Watermarks¶

The mechanism in Flink to measure progress in event time is _watermarks_. Watermarks determine when to make progress during processing or wait for more records.

Certain SQL operations, like windows, interval joins, time-versioned joins, and MATCH_RECOGNIZE require watermarks. Without watermarks, they don’t produce output.

By default, every table has a watermark strategy applied.

A watermark means, “I have seen all records until this point in time”. It’s a `long` value that usually represents epoch milliseconds. The watermark of an operator is the minimum of received watermarks over all partitions of all inputs. It triggers the execution of time-based operations within this operator before sending the watermark downstream.

Watermarks can be emitted for every record, or they can be computed and emitted on a wall-clock interval. By default, Flink emits them every 200 ms.

The built-in function, [CURRENT_WATERMARK](../reference/functions/datetime-functions.html#flink-sql-current-watermark-function), enables printing the current watermark for the executing operator.

Providing a timestamp is a prerequisite for providing a default watermark. Without providing some timestamp, neither a watermark nor a time attribute is possible.

In Flink SQL, only time attributes can be used for time-based operations.

A time attribute must be of type `TIMESTAMP(p)` or `TIMESTAMP_LTZ(p)`, with `0 <= p <= 3`.

Defining a watermark over a timestamp makes it a time attribute. This is shown as a **ROWTIME** in a **DESCRIBE** statement.

### Watermarks and timestamps¶

Every Kafka record has a message timestamp which is part of the message format, and not in the payload or headers.

Timestamp semantics can be CreateTime (default) or LogAppendTime.

The timestamp is overwritten by the broker only if LogAppendTime is configured. Otherwise, it depends on the producer, which means that the timestamp can be user-defined, or it is set using the client’s clock if not defined by the user.

In most cases, a Kafka record’s timestamp is expressed in epoch milliseconds in UTC.

Watermarks flow as part of the data stream and carry a timestamp _t_. A _Watermark(t)_ declares that event time has reached time _t_ in that stream, meaning that there should be no more elements from the stream with a timestamp _t’ <= t_, that is, events with timestamps older or equal to the watermark.

The following diagram shows a stream of events with logical timestamps and watermarks flowing inline. In this example, the events are in order with respect to their timestamps, meaning that the watermarks are simply periodic markers in the stream.

A data stream with in-order events and watermarks¶

Watermarks are crucial for _out-of-order_ streams, as shown in the following diagram, where the events are not ordered by their timestamps. In general, a watermark declares that by this point in the stream, all events up to a certain timestamp should have arrived. Once a watermark reaches an operator, the operator can advance its internal _event time clock_ to the value of the watermark.

A data stream with out-of-order events and watermarks¶

Event time is inherited by a freshly created stream element (or elements) from either the event that produced them or from the watermark that triggered creation of these elements.

### Watermarks in parallel streams¶

Watermarks are generated at, or directly after, source functions. Each parallel subtask of a source function usually generates its watermarks independently. These watermarks define the event time at that particular parallel source.

As the watermarks flow through the streaming program, they advance the event time at the operators where they arrive. Whenever an operator advances its event time, it generates a new watermark downstream for its successor operators.

Some operators consume multiple input streams. For example, a union, or operators following a _keyBy(…)_ or _partition(…)_ function consume multiple input streams. Such an operator’s current event time is the minimum of its input streams’ event times. As its input streams update their event times, so does the operator.
