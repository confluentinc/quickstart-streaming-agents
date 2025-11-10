---
document_id: flink_how-to-guides_resolve-common-query-problems_chunk_2
source_file: flink_how-to-guides_resolve-common-query-problems.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/resolve-common-query-problems.html
title: Resolve Common SQL Query Problems in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 2
---

to avoid large state requirements.

## Missing `window_start` or `window_end` in GROUP BY for window aggregation¶

    [Warning] Your query contains only "window_end" in the GROUP BY clause, with no corresponding "window_start".
    This means that the query is considered a regular aggregation query and not a windowed aggregation, which can
    result in unexpected, continuously updating output and higher CFU consumption. if you want a windowed aggregation
    in your query, ensure that you include both "window_start" and "window_end" in the GROUP BY clause.
    For more information, see https://cnfl.io/regular_vs_window_aggregation.

A similar warning appears if only `window_start` is included without `window_end`.

When performing windowed aggregations, using functions like `TUMBLE`, `HOP`, `CUMULATE`, `SESSION`, you typically group by the window boundaries (`window_start` and `window_end`) along with any other grouping keys. If you include only one of the window boundary columns. either `window_start` or `window_end`, in the `GROUP BY` clause, Flink interprets this as a regular, non-windowed aggregation. This leads to continuously updating results for each input row rather than a single result per window, which is usually not the intended behavior and can consume more resources.

The following example illustrates a query that triggers this warning:

    -- Incorrect GROUP BY for TUMBLE window
    SELECT window_end, SUM(price) as `sum`
    FROM TABLE(
        TUMBLE(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '10' MINUTES)
    )
    GROUP BY window_end; -- Missing window_start

To resolve this warning should it occur in a query:

Include both window boundaries
    When performing windowed aggregations, ensure that your `GROUP BY` clause includes _both_ `window_start` and `window_end`.

The following example shows the revised query that resolves this warning:

    -- Correct GROUP BY for TUMBLE window
    SELECT window_start, window_end, SUM(price) as `sum`
    FROM TUMBLE(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '10' MINUTES)
    )
    GROUP BY window_start, window_end; -- Includes both window boundaries

## Session window without a PARTITION BY key¶

    [Warning] Your query uses a SESSION window without a PARTITION BY clause.
    This results in all data being processed by a single, non-parallel task,
    which can create a significant bottleneck, leading to poor performance and
    high resource consumption. To improve performance and enable parallel
    execution, specify a PARTITION BY key in your SESSION window. For more
    information, see https://cnfl.io/session_without_partioning.

When using a SESSION window, data is grouped into sessions based on periods of activity, which are separated by a specified gap of inactivity. If you don’t include a PARTITION BY clause, all data will be sent to a single, non-parallel task to correctly identify these sessions. This creates a significant performance bottleneck and prevents the query from scaling.

The following example shows a query that triggers this warning:

    -- This query uses a SESSION window without a PARTITION BY key
    SELECT *
    FROM SESSION(
        TABLE `examples`.`marketplace`.`orders`,
        DESCRIPTOR($rowtime),
        INTERVAL '5' MINUTES
    );

To resolve this warning:

Add a PARTITION BY key
    Modify your SESSION window definition to include a PARTITION BY clause. This partitions the data by the specified key(s), allowing the sessionization to be performed independently and in parallel for each partition. This is important for performance and scalability.

The following example shows the revised query that resolves the warning:

    -- Corrected query with PARTITION BY to enable parallel execution
    SELECT *
       FROM SESSION(
           TABLE `examples`.`marketplace`.`orders` PARTITION BY customer_id,
           DESCRIPTOR($rowtime),
           INTERVAL '5' MINUTES
       );
