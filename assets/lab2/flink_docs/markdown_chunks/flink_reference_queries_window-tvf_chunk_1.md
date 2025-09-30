---
document_id: flink_reference_queries_window-tvf_chunk_1
source_file: flink_reference_queries_window-tvf.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/window-tvf.html
title: SQL Windowing Table-Valued Functions in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 7
---

# Windowing Table-Valued Functions (Windowing TVFs) in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides several window table-valued functions (TVFs) for dividing the elements of a table into windows.

## Description¶

Windows are central to processing infinite streams. Windows split the stream into “buckets” of finite size, over which you can apply computations. This document focuses on how windowing is performed in Confluent Cloud for Apache Flink and how you can benefit from windowed functions.

Flink provides several window table-valued functions (TVF) to divide the elements of your table into windows, including:

  * Tumble Windows
  * Hop Windows
  * Cumulate Windows
  * Session Windows (not supported in batch mode)

Note that each element can logically belong to more than one window, depending on the windowing table-valued function you use. For example, HOP windowing creates overlapping windows in which a single element can be assigned to multiple windows.

Windowing TVFs are Flink-defined Polymorphic Table Functions (abbreviated PTF). PTF is part of the [SQL 2016 standard](https://www.iso.org/standard/78938.html), a special table-function, but can have a table as a parameter. PTF is a powerful feature to change the shape of a table. Because PTFs are used semantically like tables, their invocation occurs in a `FROM` clause of a `SELECT` statement.

These are frequently-used computations based on windowing TVF:

  * [Window Aggregation](window-aggregation.html#flink-sql-window-aggregation)
  * [Window TopN](window-topn.html#flink-sql-window-top-n)
  * [Window Join](window-join.html#flink-sql-window-join)
  * [Window Deduplication](window-deduplication.html#flink-sql-window-deduplication)

## Window functions¶

Flink provides 4 built-in windowing TVFs: `TUMBLE`, `HOP`, `CUMULATE` and `SESSION`. The return value of windowing TVF is a new relation that includes all columns of original relation as well as additional 3 columns named “window_start”, “window_end”, “window_time” to indicate the assigned window.

  * In streaming mode, the “window_time” field is a [time attribute](../../concepts/timely-stream-processing.html#flink-sql-time-attributes) of the window.
  * In batch mode, the “window_time” field is an attribute of type `TIMESTAMP` or `TIMESTAMP_LTZ` based on input time field type.

The “window_time” field can be used in subsequent time-based operations, for example, another windowing TVF, [interval-join](joins.html#flink-sql-interval-joins), or [over aggregation](over-aggregation.html#flink-sql-over-aggregation). The value of `window_time` always equal to `window_end - 1ms`.

## Window alignment¶

Time-based window boundaries align with clock seconds, minutes, hours, and days. For example, assume that you have events with these timestamps (in UTC):

  * 00:59:00.000
  * 00:59:30.000
  * 01:00:15.000

If you put these events into hour-long tumbling windows, the first two land in the window for `00:00:00-00:59:59.999`, and the third event lands in the following hour.

## Supported time units¶

Window TVFs support the following [time units](../functions/datetime-functions.html#flink-sql-time-interval-and-point-unit-specifiers):

  * SECOND
  * MINUTE
  * HOUR
  * DAY

MONTH and YEAR time units are not currently supported.
