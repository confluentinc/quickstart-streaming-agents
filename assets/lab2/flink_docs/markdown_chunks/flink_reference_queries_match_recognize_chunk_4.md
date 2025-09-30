---
document_id: flink_reference_queries_match_recognize_chunk_4
source_file: flink_reference_queries_match_recognize.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/match_recognize.html
title: SQL Pattern Recognition Queries in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 10
---

DESC, price ASC` is not.

## Define and measures¶

The `DEFINE` and `MEASURES` keywords have similar meanings to the `WHERE` and `SELECT` clauses in a simple SQL query.

The `MEASURES` clause defines what will be included in the output of a matching pattern. It can project columns and define expressions for evaluation. The number of produced rows depends on the output mode setting.

The `DEFINE` clause specifies conditions that rows have to fulfill in order to be classified to a corresponding pattern variable. If a condition isn’t defined for a pattern variable, a default condition is used, which evaluates to TRUE for every row.

For a more detailed explanation about expressions that can be used in those clauses, see event stream navigation.

### Aggregations¶

Aggregations can be used in `DEFINE` and `MEASURES` clauses. [Built-in functions](../functions/overview.html#flink-sql-functions-overview) are supported.

Aggregate functions are applied to each subset of rows mapped to a match. To understand how these subsets are evaluated, see event stream navigation section.

The task of the following example is to find the longest period of time for which the average price of a ticker did not go below a certain threshold. It shows how expressible `MATCH_RECOGNIZE` can become with aggregations. The following query performs this task.

    SELECT *
    FROM Ticker
        MATCH_RECOGNIZE (
            PARTITION BY symbol
            ORDER BY rowtime
            MEASURES
                FIRST(A.rowtime) AS start_tstamp,
                LAST(A.rowtime) AS end_tstamp,
                AVG(A.price) AS avgPrice
            ONE ROW PER MATCH
            AFTER MATCH SKIP PAST LAST ROW
            PATTERN (A+ B)
            DEFINE
                A AS AVG(A.price) < 15
        ) MR;

Given this query and following input values:

    symbol         rowtime         price    tax
    ======  ====================  ======= =======
    'ACME'  '01-Apr-11 10:00:00'   12      1
    'ACME'  '01-Apr-11 10:00:01'   17      2
    'ACME'  '01-Apr-11 10:00:02'   13      1
    'ACME'  '01-Apr-11 10:00:03'   16      3
    'ACME'  '01-Apr-11 10:00:04'   25      2
    'ACME'  '01-Apr-11 10:00:05'   2       1
    'ACME'  '01-Apr-11 10:00:06'   4       1
    'ACME'  '01-Apr-11 10:00:07'   10      2
    'ACME'  '01-Apr-11 10:00:08'   15      2
    'ACME'  '01-Apr-11 10:00:09'   25      2
    'ACME'  '01-Apr-11 10:00:10'   25      1
    'ACME'  '01-Apr-11 10:00:11'   30      1

The query accumulates events as part of the pattern variable `A`, as long as their average price doesn’t exceed `15`. For example, such a limit exceeding happens at `01-Apr-11 10:00:04`. The following period exceeds the average price of `15` again at `01-Apr-11 10:00:11`.

Here are results of the query:

     symbol       start_tstamp       end_tstamp          avgPrice
    =========  ==================  ==================  ============
    ACME       01-APR-11 10:00:00  01-APR-11 10:00:03     14.5
    ACME       01-APR-11 10:00:05  01-APR-11 10:00:10     13.5

Aggregations can be applied to expressions, but only if they reference a single pattern variable. For example, `SUM(A.price * A.tax)` is valid, but `AVG(A.price * B.tax)` is not.

Note

`DISTINCT` aggregations aren’t supported.
