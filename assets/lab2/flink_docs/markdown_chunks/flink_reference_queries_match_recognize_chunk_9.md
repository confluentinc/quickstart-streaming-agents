---
document_id: flink_reference_queries_match_recognize_chunk_9
source_file: flink_reference_queries_match_recognize.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/match_recognize.html
title: SQL Pattern Recognition Queries in Confluent Cloud for Apache Flink
chunk_index: 9
total_chunks: 10
---

* B.tax)` is not valid.

## After-match strategy¶

The `AFTER MATCH SKIP` clause specifies where to start a new matching procedure after a complete match was found.

There are four different strategies:

  * `SKIP PAST LAST ROW` \- resumes the pattern matching at the next row after the last row of the current match.
  * `SKIP TO NEXT ROW` \- continues searching for a new match starting at the next row after the starting row of the match.
  * `SKIP TO LAST variable` \- resumes the pattern matching at the last row that is mapped to the specified pattern variable.
  * `SKIP TO FIRST variable` \- resumes the pattern matching at the first row that is mapped to the specified pattern variable.

This is also a way to specify how many matches a single event can belong to. For example, with the `SKIP PAST LAST ROW` strategy, every event can belong to at most one match.

### Examples¶

To better understand the differences between these strategies consider the following example.

For the following input rows:

     symbol   tax   price         rowtime
    ======== ===== ======= =====================
     XYZ      1     7       2018-09-17 10:00:01
     XYZ      2     9       2018-09-17 10:00:02
     XYZ      1     10      2018-09-17 10:00:03
     XYZ      2     5       2018-09-17 10:00:04
     XYZ      2     10      2018-09-17 10:00:05
     XYZ      2     7       2018-09-17 10:00:06
     XYZ      2     14      2018-09-17 10:00:07

Evaluate the following query with different strategies:

    SELECT *
    FROM Ticker
        MATCH_RECOGNIZE(
            PARTITION BY symbol
            ORDER BY rowtime
            MEASURES
                SUM(A.price) AS sumPrice,
                FIRST(rowtime) AS startTime,
                LAST(rowtime) AS endTime
            ONE ROW PER MATCH
            [AFTER MATCH STRATEGY]
            PATTERN (A+ C)
            DEFINE
                A AS SUM(A.price) < 30
        )

The query returns the sum of the prices of all rows mapped to `A` and the first and last timestamp of the overall match.

The query produces different results based on which `AFTER MATCH` strategy is used:

#### `AFTER MATCH SKIP PAST LAST ROW`¶

     symbol   sumPrice        startTime              endTime
    ======== ========== ===================== =====================
     XYZ      26         2018-09-17 10:00:01   2018-09-17 10:00:04
     XYZ      17         2018-09-17 10:00:05   2018-09-17 10:00:07

The first result matched against the rows #1, #2, #3, #4.

The second result matched against the rows #5, #6, #7.

#### `AFTER MATCH SKIP TO NEXT ROW`¶

     symbol   sumPrice        startTime              endTime
    ======== ========== ===================== =====================
     XYZ      26         2018-09-17 10:00:01   2018-09-17 10:00:04
     XYZ      24         2018-09-17 10:00:02   2018-09-17 10:00:05
     XYZ      25         2018-09-17 10:00:03   2018-09-17 10:00:06
     XYZ      22         2018-09-17 10:00:04   2018-09-17 10:00:07
     XYZ      17         2018-09-17 10:00:05   2018-09-17 10:00:07

Again, the first result matched against the rows #1, #2, #3, #4.

Compared to the previous strategy, the next match includes row #2 again for the next matching. Therefore, the second result matched against the rows #2, #3, #4, #5.

The third result matched against the rows #3, #4, #5, #6.

The forth result matched against the rows #4, #5, #6, #7.

The last result matched against the rows #5, #6, #7.

#### `AFTER MATCH SKIP TO LAST A`¶

     symbol   sumPrice        startTime              endTime
    ======== ========== ===================== =====================
     XYZ      26         2018-09-17 10:00:01   2018-09-17 10:00:04
     XYZ      25         2018-09-17 10:00:03   2018-09-17 10:00:06
     XYZ      17         2018-09-17 10:00:05   2018-09-17 10:00:07

Again, the first result matched against the rows #1, #2, #3, #4.

Compared to the previous strategy, the next match includes only row #3 (mapped to `A`) again for the next matching. Therefore, the second result matched against the rows #3, #4, #5, #6.

The last result matched against the rows #5, #6, #7.

#### `AFTER MATCH SKIP TO FIRST A`¶

This combination produces a runtime exception, because one would always try to start a new match where the last one started. This would produce an infinite loop and, so it’s not valid.

In case of the `SKIP TO FIRST/LAST variable` strategy, it may be possible that there are no rows mapped to that variable, for example, for pattern `A*`. In such cases, a runtime exception is thrown, because the standard requires a valid row to continue the matching.
