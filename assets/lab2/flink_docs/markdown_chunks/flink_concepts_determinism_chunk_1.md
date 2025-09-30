---
document_id: flink_concepts_determinism_chunk_1
source_file: flink_concepts_determinism.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/determinism.html
title: Determinism with continuous Flink SQL queries in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 3
---

# Determinism in Continuous Queries on Confluent Cloud for Apache Flink¶

This topic answers the following questions about determinism in Confluent Cloud for Apache Flink®:

  * What is determinism?
  * Is all batch processing deterministic?
    * Two examples of batch queries with non-deterministic results
    * Non-determinism in batch processing
  * Determinism in stream processing
    * Non-determinism in streaming
    * Non-deterministic update in streaming

## What is determinism?¶

Paraphrasing the SQL standard’s description of determinism, an operation is deterministic if it reliably computes identical results when repeated with identical input values.
