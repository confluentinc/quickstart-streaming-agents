---
document_id: flink_reference_queries_match_recognize_chunk_10
source_file: flink_reference_queries_match_recognize.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/match_recognize.html
title: SQL Pattern Recognition Queries in Confluent Cloud for Apache Flink
chunk_index: 10
total_chunks: 10
---

row to continue the matching.

## Time attributes¶

To apply some subsequent queries on top of the `MATCH_RECOGNIZE` it may be necessary to use [time attributes](../../concepts/timely-stream-processing.html#flink-sql-time-attributes). There are two functions for selecting these:

`MATCH_ROWTIME([rowtime_field])`

Returns the timestamp of the last row that was mapped to the given pattern.

The function accepts zero or one operand, which is a field reference with rowtime attribute. If there is no operand, the function returns the rowtime attribute with TIMESTAMP type. Otherwise, the return type is same as the operand type.

The resulting attribute is a rowtime attribute that you can use in subsequent time-based operations, like interval joins and group window or over-window aggregations.

## Control memory consumption¶

Memory consumption is an important consideration when writing `MATCH_RECOGNIZE` queries, because the space of potential matches is built in a breadth-first-like manner. This means that you must ensure that the pattern can finish, preferably with a reasonable number of rows mapped to the match, as they have to fit into memory.

For example, the pattern must not have a quantifier without an upper limit that accepts every single row. Such a pattern could look like this:

    PATTERN (A B+ C)
    DEFINE
      A as A.price > 10,
      C as C.price > 20

This query maps every incoming row to the `B` variable, so it never finishes. This query could be fixed, for example, by negating the condition for `C`:

    PATTERN (A B+ C)
    DEFINE
      A as A.price > 10,
      B as B.price <= 20,
      C as C.price > 20

Also, the query could be fixed by using the reluctant quantifier:

    PATTERN (A B+? C)
    DEFINE
      A as A.price > 10,
      C as C.price > 20

Note

The `MATCH_RECOGNIZE` clause doesn’t use a configured state retention time.

You may want to use the WITHIN clause <flink-sql-pattern-recognition-time-constraint> for this purpose.

## Known limitations¶

The Flink SQL implementation of the `MATCH_RECOGNIZE` clause is an ongoing effort, and some features of the SQL standard are not yet supported.

Unsupported features include:

  * Pattern expressions
    * Pattern groups - this means that e.g. quantifiers can not be applied to a subsequence of the pattern. Thus, `(A (B C)+)` is not a valid pattern.
    * Alterations - patterns like `PATTERN((A B | C D) E)`, which means that either a subsequence `A B` or `C D` has to be found before looking for the `E` row.
    * `PERMUTE` operator - which is equivalent to all permutations of variables that it was applied to e.g. `PATTERN (PERMUTE (A, B, C))` = `PATTERN (A B C | A C B | B A C | B C A | C A B | C B A)`.
    * Anchors - `^, $`, which denote beginning/end of a partition, those do not make sense in the streaming context and will not be supported.
    * Exclusion - `PATTERN ({- A -} B)` meaning that `A` will be looked for but will not participate in the output. This works only for the `ALL ROWS PER MATCH` mode.
    * Reluctant optional quantifier - `PATTERN A??` only the greedy optional quantifier is supported.
  * `ALL ROWS PER MATCH` output mode - which produces an output row for every row that participated in the creation of a found match. This also means:
    * The only supported semantic for the `MEASURES` clause is `FINAL`.
    * `CLASSIFIER` function, which returns the pattern variable that a row was mapped to, is not yet supported.
  * `SUBSET` \- which allows creating logical groups of pattern variables and using those groups in the `DEFINE` and `MEASURES` clauses.
  * Physical offsets - `PREV/NEXT`, which indexes all events seen rather than only those that were mapped to a pattern variable (as in the logical offsets case).
  * `MATCH_RECOGNIZE` is supported only for SQL. There is no equivalent in the Table API.
  * Aggregations
    * Distinct aggregations are not supported.
