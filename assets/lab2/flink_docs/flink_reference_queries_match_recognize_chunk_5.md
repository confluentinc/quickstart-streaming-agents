---
document_id: flink_reference_queries_match_recognize_chunk_5
source_file: flink_reference_queries_match_recognize.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/match_recognize.html
title: SQL Pattern Recognition Queries in Confluent Cloud for Apache Flink
chunk_index: 5
total_chunks: 10
---

Note `DISTINCT` aggregations aren’t supported.

## Define a pattern¶

The `MATCH_RECOGNIZE` clause enables you to search for patterns in event streams using a powerful and expressive syntax that is somewhat similar to the widely used regular expression syntax.

Every pattern is constructed from basic building blocks, called _pattern variables_ , to which operators (quantifiers and other modifiers) can be applied. The whole pattern must be enclosed in brackets.

The following SQL shows an example pattern:

    PATTERN (A B+ C* D)

You can use the following operators:

  * _Concatenation_ \- a pattern like `(A B)` means that the contiguity is strict between `A` and `B`, so there can be no rows that weren’t mapped to `A` or `B` in between.
  * _Quantifiers_ \- modify the number of rows that can be mapped to the pattern variable.
    * `*` — _0_ or more rows
    * `+` — _1_ or more rows
    * `?` — _0_ or _1_ rows
    * `{ n }` — exactly _n_ rows (_n > 0_)
    * `{ n, }` — _n_ or more rows (_n ≥ 0_)
    * `{ n, m }` — between _n_ and _m_ (inclusive) rows (_0 ≤ n ≤ m, 0 < m_)
    * `{ , m }` — between _0_ and _m_ (inclusive) rows (_m > 0_)

Important

Patterns that can potentially produce an empty match aren’t supported. For example, patterns like these produce an empty match:

    PATTERN (A*)
    PATTERN (A? B*)
    PATTERN (A{0,} B{0,} C*)

### Greedy and reluctant quantifiers¶

Each quantifier can be either _greedy_ (default behavior) or _reluctant_. Greedy quantifiers try to match as many rows as possible, while reluctant quantifiers try to match as few as possible.

To see the difference, the following example shows a query where a greedy quantifier is applied to the `B` variable:

    SELECT *
    FROM Ticker
        MATCH_RECOGNIZE(
            PARTITION BY symbol
            ORDER BY rowtime
            MEASURES
                C.price AS lastPrice
            ONE ROW PER MATCH
            AFTER MATCH SKIP PAST LAST ROW
            PATTERN (A B* C)
            DEFINE
                A AS A.price > 10,
                B AS B.price < 15,
                C AS C.price > 12
        )

Given the following input:

     symbol  tax   price          rowtime
    ======= ===== ======== =====================
     XYZ     1     10       2018-09-17 10:00:02
     XYZ     2     11       2018-09-17 10:00:03
     XYZ     1     12       2018-09-17 10:00:04
     XYZ     2     13       2018-09-17 10:00:05
     XYZ     1     14       2018-09-17 10:00:06
     XYZ     2     16       2018-09-17 10:00:07

The example pattern produces the following output:

     symbol   lastPrice
    ======== ===========
     XYZ      16

If the query is modified to be reluctant, changing `B*` to `B*?`, it produces the following output:

     symbol   lastPrice
    ======== ===========
     XYZ      13
     XYZ      16

The pattern variable `B` matches only the row with price _12_ instead of swallowing the rows with prices _12_ , _13_ , and _14_.

You can’t use a greedy quantifier for the last variable of a pattern. So a pattern like `(A B*)` isn’t valid. You can work around this limitation by introducing an artificial state, like `C`, that has a negated condition of `B`. The following query shows an example.

    PATTERN (A B* C)
    DEFINE
        A AS condA(),
        B AS condB(),
        C AS NOT condB()

Note

The optional-reluctant quantifier (`A??` or `A{0,1}?`) isn’t supported.

### Time constraint¶

Especially for streaming use cases, it’s often required that a pattern finishes within a given period of time. This enables limiting the overall state size that Flink must maintain internally, even in the case of greedy quantifiers.

For this reason, Flink SQL supports the additional (non-standard SQL) `WITHIN` clause for defining a time constraint for a pattern. The clause can be defined after the `PATTERN` clause and takes an interval of millisecond resolution.

If the time between the first and last event of a potential match is longer than the given value, a match isn’t appended to the result table.

Note

It’s good practice to use the `WITHIN` clause, because it helps Flink with efficient memory management. Underlying state can be pruned once the threshold is reached.

But the `WITHIN` clause isn’t part of the SQL standard. The recommended way of dealing with time constraints might change in the future.

The following example query shows the `WITHIN` clause used with `MATCH_RECOGNIZE`.

    SELECT *
    FROM Ticker
        MATCH_RECOGNIZE(
            PARTITION BY symbol
            ORDER BY rowtime
            MEASURES
                C.rowtime AS dropTime,
                A.price - C.price AS dropDiff
            ONE ROW PER MATCH
            AFTER MATCH SKIP PAST LAST ROW
            PATTERN (A B* C) WITHIN INTERVAL '1' HOUR
            DEFINE
                B AS B.price > A.price - 10,
                C AS C.price < A.price - 10
        )
