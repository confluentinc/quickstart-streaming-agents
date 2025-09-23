---
document_id: flink_reference_queries_select_chunk_3
source_file: flink_reference_queries_select.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/select.html
title: SQL SELECT statement in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 3
---

<https://acme.com/index.html> 1692812175 10.0.0.1 <https://acme.com/index.html> 1692812175

## Examples¶

The following examples show frequently encountered scenarios with SELECT.

### Most minimal statement¶

Syntax

    SELECT 1;

Properties

* Statement is bounded

### Check local time zone is configured correctly¶

Syntax

    SELECT NOW();

Properties

* Statement is bounded
* NOW() returns a TIMSTAMP_LTZ(3), so if the client is configured correctly, it should show a timestamp in your local time zone.

### Combine multiple tables into one¶

Syntax

    CREATE TABLE t_union_1 (i INT);
    CREATE TABLE t_union_2 (i INT);
    TABLE t_union_1 UNION ALL TABLE t_union_2;

    -- alternate syntax
    SELECT * FROM t_union_1
    UNION ALL
    SELECT * FROM t_union_2;

### Get insights into the current watermark¶

Syntax

    CREATE TABLE t_watermarked_insight (s STRING) DISTRIBUTED INTO 1 BUCKETS;

    INSERT INTO t_watermarked_insight VALUES ('Bob'), ('Alice'), ('Charly');

    SELECT $rowtime, CURRENT_WATERMARK($rowtime) FROM t_watermarked_insight;

The output resembles:

    $rowtime                EXPR$1
    2024-04-29 11:59:01.080 NULL
    2024-04-29 11:59:01.093 2024-04-04 15:27:37.433
    2024-04-29 11:59:01.094 2024-04-04 15:27:37.433

Properties

* The CURRENT_WATERMARK function returns the watermark that arrived at the operator evaluating the SELECT statement.
* The returned watermark is the minimum of all inputs, across all tables/topics and their partitions.
* If a common watermark was not received from all inputs, the function returns NULL.
* The CURRENT_WATERMARK function takes a [time attribute](../../concepts/timely-stream-processing.html#flink-sql-time-attributes), which is a column that has WATERMARK FOR defined.

A watermark is always emitted after the row has been processed, so the first row always has a NULL watermark.

Because the default watermark algorithm requires at least 250 records, initially it assumes the maximum lag of 7 days plus a safety margin of 7 days.

The watermark quickly (exponentially) goes down as more data arrives.

Sources emit watermarks every 200 ms, but within the first 200 ms they emit per row for powering examples like this.

### Flatten fields into columns¶

Syntax

    CREATE TABLE t_flattening (i INT, r1 ROW<i INT, s STRING>, r2 ROW<other INT>);

    SELECT r1.*, r2.* FROM t_flattening;

Properties
    You can apply the `*` operator on nested data, which enables flattening fields into columns of the table.
