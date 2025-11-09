---
document_id: flink_reference_queries_match_recognize_chunk_7
source_file: flink_reference_queries_match_recognize.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/match_recognize.html
title: SQL Pattern Recognition Queries in Confluent Cloud for Apache Flink
chunk_index: 7
total_chunks: 10
---

the beginning of the result.

## Pattern navigation¶

The `DEFINE` and `MEASURES` clauses enable navigating within the list of rows that (potentially) match a pattern.

This section discusses navigation for declaring conditions or producing output results.

### Pattern variable referencing¶

A _pattern variable reference_ enables referencoing a set of rows mapped to a particular pattern variable in the `DEFINE` or `MEASURES` clauses.

For example, the expression `A.price` describes a set of rows mapped so far to `A` plus the current row, if the query tries to match the current row to `A`. If an expression in the `DEFINE` / `MEASURES` clause requires a single row, for example, `A.price` or `A.price > 10`, it selects the last value belonging to the corresponding set.

If no pattern variable is specified, for example, `SUM(price)`, an expression references the default pattern variable `*`, which references all variables in the pattern. In other words, it creates a list of all the rows mapped so far to any variable plus the current row.

#### Example¶

For a more thorough example, consider the following pattern and corresponding conditions.

    PATTERN (A B+)
    DEFINE
      A AS A.price >= 10,
      B AS B.price > A.price AND SUM(price) < 100 AND SUM(B.price) < 80

The following table describes how these conditions are evaluated for each incoming event.

The table consists of the following columns:

* `#` \- the row identifier that uniquely identifies an incoming row in the lists `[A.price]` / `[B.price]` / `[price]`.
* `price` \- the price of the incoming row.
* `[A.price]`/ `[B.price]`/ `[price]` \- describe lists of rows which are used in the `DEFINE` clause to evaluate conditions.
* `Classifier` \- the classifier of the current row which indicates the pattern variable the row is mapped to.
* `A.price`/ `B.price`/ `SUM(price)`/ `SUM(B.price)` \- describes the result after those expressions have been evaluated.

    == ===== ========== ========= ============== ================== ======= ======= ========== ============

#  price Classifier [A.price] [B.price]      [price]            A.price B.price SUM(price) SUM(B.price)

    == ===== ========== ========= ============== ================== ======= ======= ========== ============
    #1 10    -> A       #1        -              -                  10      -       -          -
    #2 15    -> B       #1        #2             #1, #2             10      15      25         15
    #3 20    -> B       #1        #2, #3         #1, #2, #3         10      20      45         35
    #4 31    -> B       #1        #2, #3, #4     #1, #2, #3, #4     10      31      76         66
    #5 35               #1        #2, #3, #4, #5 #1, #2, #3, #4, #5 10      35      111        101
    == ===== ========== ========= ============== ================== ======= ======= ========== ============

The table shows that the first row is mapped to pattern variable `A`, and subsequent rows are mapped to pattern variable `B`. But the last row doesn’t fulfill the `B` condition, because the sum over all mapped rows, `SUM(price)`, and the sum over all rows in `B` exceed the specified thresholds.

### Logical offsets¶

_Logical offsets_ enable navigation within the events that were mapped to a particular pattern variable. This can be expressed with two corresponding functions.

Offset functions | Description
---|---
`LAST(variable.field, n)` | Returns the value of the field from the event that was mapped to the _n_ -th _last_ element of the variable. The counting starts at the last element mapped.
`FIRST(variable.field, n)` | Returns the value of the field from the event that was mapped to the _n_ -th element of the variable. The counting starts at the first element mapped.

#### Examples¶

For a more thorough example, consider the following pattern and corresponding conditions:

    PATTERN (A B+)
    DEFINE
      A AS A.price >= 10,
      B AS (LAST(B.price, 1) IS NULL OR B.price > LAST(B.price, 1)) AND
           (LAST(B.price, 2) IS NULL OR B.price > 2 * LAST(B.price, 2))

The following table describes how these conditions are evaluated for each incoming event.

The table consists of the following columns:

* `price` \- the price of the incoming row.
* `Classifier` \- the classifier of the current row which indicates the pattern variable the row is mapped to.
* `LAST(B.price, 1)`/ `LAST(B.price, 2)` \- describes the result after these expressions have been evaluated.

    ===== ========== ================ ================ ========================================================================================
    price Classifier LAST(B.price, 1) LAST(B.price, 2) Comment
    ===== ========== ================ ================ ========================================================================================
    10    -> A
    15    -> B       null             null             Notice that ``LAST(B.price, 1)`` is null
