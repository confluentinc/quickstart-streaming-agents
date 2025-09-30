---
document_id: flink_reference_queries_match_recognize_chunk_6
source_file: flink_reference_queries_match_recognize.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/match_recognize.html
title: SQL Pattern Recognition Queries in Confluent Cloud for Apache Flink
chunk_index: 6
total_chunks: 10
---

The query detects a price drop of _10_ that happens within an interval of _1_ hour.

Assume the query is used to analyze the following ticker data.

    symbol         rowtime         price    tax
    ======  ====================  ======= =======
    'ACME'  '01-Apr-11 10:00:00'   20      1
    'ACME'  '01-Apr-11 10:20:00'   17      2
    'ACME'  '01-Apr-11 10:40:00'   18      1
    'ACME'  '01-Apr-11 11:00:00'   11      3
    'ACME'  '01-Apr-11 11:20:00'   14      2
    'ACME'  '01-Apr-11 11:40:00'   9       1
    'ACME'  '01-Apr-11 12:00:00'   15      1
    'ACME'  '01-Apr-11 12:20:00'   14      2
    'ACME'  '01-Apr-11 12:40:00'   24      2
    'ACME'  '01-Apr-11 13:00:00'   1       2
    'ACME'  '01-Apr-11 13:20:00'   19      1

The query produces the following results:

    symbol         dropTime         dropDiff
    ======  ====================  =============
    'ACME'  '01-Apr-11 13:00:00'      14

The resulting row represents a price drop from _15_ (at `01-Apr-11 12:00:00`) to `1` (at `01-Apr-11 13:00:00`). The `dropDiff` column contains the price difference.

Even though prices also drop by higher values, for example, by _11_ (between `01-Apr-11 10:00:00` and `01-Apr-11 11:40:00`), the time difference between those two events is larger than _1_ hour, they don’t produce a match.

## Output mode¶

The _output mode_ describes how many rows should be emitted for every found match. The SQL standard describes two modes:

  * `ALL ROWS PER MATCH`
  * `ONE ROW PER MATCH`

In Flink SQL, the only supported output mode is `ONE ROW PER MATCH`, and it always produces one output summary row for each found match.

The schema of the output row is a concatenation of `[partitioning columns] + [measures columns]`, in that order.

The following example shows the output of a query defined as:

    SELECT *
    FROM Ticker
        MATCH_RECOGNIZE(
            PARTITION BY symbol
            ORDER BY rowtime
            MEASURES
                FIRST(A.price) AS startPrice,
                LAST(A.price) AS topPrice,
                B.price AS lastPrice
            ONE ROW PER MATCH
            PATTERN (A+ B)
            DEFINE
                A AS LAST(A.price, 1) IS NULL OR A.price > LAST(A.price, 1),
                B AS B.price < LAST(A.price)
        )

For the following input rows:

     symbol   tax   price          rowtime
    ======== ===== ======== =====================
     XYZ      1     10       2018-09-17 10:00:02
     XYZ      2     12       2018-09-17 10:00:03
     XYZ      1     13       2018-09-17 10:00:04
     XYZ      2     11       2018-09-17 10:00:05

The query produces the following output:

     symbol   startPrice   topPrice   lastPrice
    ======== ============ ========== ===========
     XYZ      10           13         11

The pattern recognition is partitioned by the `symbol` column. Even though not explicitly mentioned in the `MEASURES` clause, the partitioned column is added at the beginning of the result.
