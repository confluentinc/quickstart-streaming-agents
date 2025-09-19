---
document_id: flink_reference_queries_match_recognize_chunk_8
source_file: flink_reference_queries_match_recognize.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/match_recognize.html
title: SQL Pattern Recognition Queries in Confluent Cloud for Apache Flink
chunk_index: 8
total_chunks: 10
---

because there is still nothing mapped to ``B``.
    20    -> B       15               null
    31    -> B       20               15
    35               31               20               Not mapped because ``35 < 2 * 20``.
    ===== ========== ================ ================ ========================================================================================

It might also make sense to use the default pattern variable with logical offsets.

In this case, an offset considers all the rows mapped so far:

    PATTERN (A B? C)
    DEFINE
      B AS B.price < 20,
      C AS LAST(price, 1) < C.price

    ===== ========== ============== =====================================================================================
    price Classifier LAST(price, 1) Comment
    ===== ========== ============== =====================================================================================
    10    -> A
    15    -> B
    20    -> C       15             ``LAST(price, 1)`` is evaluated as the price of the row mapped to the ``B`` variable.
    ===== ========== ============== =====================================================================================

If the second row didn’t map to the `B` variable, the query returns the following results:

    ===== ========== ============== =====================================================================================
    price Classifier LAST(price, 1) Comment
    ===== ========== ============== =====================================================================================
    10    -> A
    20    -> C       10             ``LAST(price, 1)`` is evaluated as the price of the row mapped to the ``A`` variable.
    ===== ========== ============== =====================================================================================

It’s also possible to use multiple pattern variable references in the first argument of the `FIRST/LAST` functions. This way, you can write an expression that accesses multiple columns, but all of them must use the same pattern variable. In other words, the value of the `LAST`/ `FIRST` function must be computed in a single row.

this means that it’s possible to use `LAST(A.price * A.tax)`, but an expression like `LAST(A.price * B.tax)` is not valid.
