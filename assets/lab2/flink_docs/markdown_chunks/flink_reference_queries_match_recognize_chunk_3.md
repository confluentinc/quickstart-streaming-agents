---
document_id: flink_reference_queries_match_recognize_chunk_3
source_file: flink_reference_queries_match_recognize.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/match_recognize.html
title: SQL Pattern Recognition Queries in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 10
---

The query partitions the `Ticker` table by the `symbol` column and orders it by the `rowtime` time attribute.

The `PATTERN` clause specifies a pattern with a starting event `START_ROW` that is followed by one or more `PRICE_DOWN` events and concluded with a `PRICE_UP` event. If such a pattern can be found, the next pattern match will be seeked at the last `PRICE_UP` event as indicated by the `AFTER MATCH SKIP TO LAST` clause.

The `DEFINE` clause specifies the conditions that need to be met for a `PRICE_DOWN` and `PRICE_UP` event. Although the `START_ROW` pattern variable is not present it has an implicit condition that is evaluated always as `TRUE`.

A pattern variable `PRICE_DOWN` is defined as a row with a price that is smaller than the price of the last row that met the `PRICE_DOWN` condition. For the initial case or when there is no last row that met the `PRICE_DOWN` condition, the price of the row should be smaller than the price of the preceding row in the pattern (referenced by `START_ROW`).

A pattern variable `PRICE_UP` is defined as a row with a price that is larger than the price of the last row that met the `PRICE_DOWN` condition.

This query produces a summary row for each period in which the price of a stock was continuously decreasing.

The exact representation of the output rows is defined in the `MEASURES` part of the query. The number of output rows is defined by the `ONE ROW PER MATCH` output mode.

     symbol       start_tstamp       bottom_tstamp         end_tstamp
    =========  ==================  ==================  ==================
    ACME       01-APR-11 10:00:04  01-APR-11 10:00:07  01-APR-11 10:00:08

The resulting row describes a period of falling prices that started at `01-APR-11 10:00:04` and achieved the lowest price at `01-APR-11 10:00:07` that increased again at `01-APR-11 10:00:08`.

## Partitioning¶

It is possible to look for patterns in partitioned data, e.g., trends for a single ticker or a particular user. This can be expressed using the `PARTITION BY` clause. The clause is similar to using `GROUP BY` for aggregations.

It is highly advised to partition the incoming data because otherwise the `MATCH_RECOGNIZE` clause will be translated into a non-parallel operator to ensure global ordering.

## Order of events¶

Flink enables searching for patterns based on time, either [event time](../../concepts/timely-stream-processing.html#flink-sql-time-attributes-event-time). Processing time is not supported in Confluent Cloud for Apache Flink.

In the case of event time, the events are sorted before they are passed to the internal pattern state machine. As a consequence, the produced output will be correct regardless of the order in which rows are appended to the table. Instead, the pattern is evaluated in the order specified by the time contained in each row.

The `MATCH_RECOGNIZE` clause assumes a [time attribute](../../concepts/timely-stream-processing.html#flink-sql-time-attributes) with ascending ordering as the first argument to `ORDER BY` clause.

For the example `Ticker` table, a definition like `ORDER BY rowtime ASC, price DESC` is valid but `ORDER BY price, rowtime` or `ORDER BY rowtime DESC, price ASC` is not.
