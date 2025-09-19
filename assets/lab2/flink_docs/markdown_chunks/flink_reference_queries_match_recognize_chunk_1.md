---
document_id: flink_reference_queries_match_recognize_chunk_1
source_file: flink_reference_queries_match_recognize.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/match_recognize.html
title: SQL Pattern Recognition Queries in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 10
---

# Pattern Recognition Queries in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables pattern detection in event streams.

## Syntax¶

    SELECT T.aid, T.bid, T.cid
    FROM MyTable
        MATCH_RECOGNIZE (
          PARTITION BY userid
          ORDER BY $rowtime
          MEASURES
            A.id AS aid,
            B.id AS bid,
            C.id AS cid
          PATTERN (A B C)
          DEFINE
            A AS name = 'a',
            B AS name = 'b',
            C AS name = 'c'
        ) AS T
