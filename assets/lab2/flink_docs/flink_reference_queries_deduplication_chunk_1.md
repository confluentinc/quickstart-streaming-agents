---
document_id: flink_reference_queries_deduplication_chunk_1
source_file: flink_reference_queries_deduplication.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/deduplication.html
title: SQL Deduplication Queries in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Deduplication Queries in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables removing duplicate rows over a set of columns in a Flink SQL table.

## Syntax¶

    SELECT [column_list]
    FROM (
       SELECT [column_list],
         ROW_NUMBER() OVER ([PARTITION BY column1[, column2...]]
           ORDER BY time_attr [asc|desc]) AS rownum
       FROM table_name)
    WHERE rownum = 1

**Parameter Specification**

Note

This query pattern must be followed exactly, otherwise, the optimizer can’t translate the query.

* `ROW_NUMBER()`: Assigns an unique, sequential number to each row, starting with one.
* `PARTITION BY column1[, column2...]`: Specifies the partition columns by the deduplicate key.
* `ORDER BY time_attr [asc|desc]`: Specifies the ordering column, which must be a [time attribute](../../concepts/timely-stream-processing.html#flink-sql-time-attributes). Flink SQL supports the [event time attribute](../../concepts/timely-stream-processing.html#flink-sql-time-attributes-event-time). Processing time is not supported in Confluent Cloud for Apache Flink. Ordering by ASC means keeping the first row, ordering by DESC means keeping the last row.
* `WHERE rownum = 1`: The `rownum = 1` is required for Flink SQL to recognize the query is deduplication.

## Description¶

Deduplication removes duplicate rows over a set of columns, keeping only the first or last row.

Flink SQL uses the `ROW_NUMBER()` function to remove duplicates, similar to its usage in [Top-N Queries in Confluent Cloud for Apache Flink](topn.html#flink-sql-top-n). Deduplication is a special case of the Top-N query, in which `N` is _1_ and row order is by event time.

In some cases, an upstream ETL job isn’t end-to-end exactly-once, which may cause duplicate records in the sink, in case of failover. Duplicate records affect the correctness of downstream analytical jobs, like `SUM` and `COUNT`, so deduplication is required before further analysis can continue.

See **deduplication** in action

Apply the [Deduplicate Topic](../../how-to-guides/deduplicate-rows.html#flink-sql-deduplicate-topic-action) action to generate a table that contains only unique records from an input table.

## Example¶

In the Flink SQL shell or in a Cloud Console workspace, run the following statement to see an example of row deduplication. It returns the first URL that the customer has visited. The rows are deduplicated by the `$rowtime` column, which is the system column mapped to the Kafka record timestamp and can be either `LogAppendTime` or `CreateTime`.

  1. Run the following statement to return the deduplicated rows.

         SELECT user_id, url, $rowtime
         FROM (
            SELECT *, $rowtime,
              ROW_NUMBER() OVER (PARTITION BY user_id
                ORDER BY $rowtime ASC) AS rownum
            FROM `examples`.`marketplace`.`clicks`)
         WHERE rownum = 1;

Your output should resemble:

         user_id    url                                  $rowtime
         3246       https://www.acme.com/product/upmtv   2024-04-16 08:04:47.365
         4028       https://www.acme.com/product/jtahp   2024-04-16 08:04:47.367
         4549       https://www.acme.com/product/ixsir   2024-04-16 08:04:47.367
