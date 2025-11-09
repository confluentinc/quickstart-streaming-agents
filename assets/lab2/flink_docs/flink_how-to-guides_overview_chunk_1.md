---
document_id: flink_how-to-guides_overview_chunk_1
source_file: flink_how-to-guides_overview.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/overview.html
title: How-to Guides for Developing Flink Applications on Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# How-to Guides for Confluent Cloud for Apache Flink¶

Discover how Confluent Cloud for Apache Flink® can help you accomplish common processing tasks such as joins and aggregations. This section provides step-by-step guidance on how to use Flink to process your data efficiently and effectively.

  * [Aggregate a Stream in a Tumbling Window](aggregate-tumbling-window.html#flink-sql-aggregate-tumbling-window)
  * [Combine Streams and Track Most Recent Records](combine-and-track-most-recent-records.html#flink-sql-combine-streams)
  * [Compare Current and Previous Values in a Data Stream](compare-current-and-previous-values.html#flink-sql-compare-current-and-previous-values)
  * [Convert the Serialization Format of a Topic](convert-serialization-format.html#flink-sql-convert-format)
  * [Create a User Defined Function](create-udf.html#flink-sql-create-udf)
  * [Handle Multiple Event Types](multiple-event-types.html#flink-sql-multiple-event-types)
  * [Process Schemaless Events](process-schemaless-events.html#flink-sql-schemaless-events)
  * [Resolve Common SQL Query Problems](resolve-common-query-problems.html#flink-sql-statement-advisor-warnings)
  * [Run a Snapshot Query](run-snapshot-query.html#flink-sql-run-snapshot-query)
  * [Scan and Summarize Tables](scan-and-summarize-tables.html#flink-sql-scan-and-summarize)
  * [View Time Series Data](view-time-series-data.html#flink-sql-view-time-series)

## Flink actions¶

Confluent Cloud for Apache Flink provides Flink Actions that enable you to perform specific data-processing tasks on topics with minimal configuration. These actions are designed to simplify common workloads by providing a user-friendly interface to configure and execute them.

  * [Create an Embedding](../../ai/embeddings/embedding-action.html#flink-sql-embedding-action): Convert data in a topic’s column into a vector embedding for AI model inference.
  * [Deduplicate Rows in a Table](deduplicate-rows.html#flink-sql-deduplicate-topic-action): Remove duplicate records from a topic based on specified fields, ensuring that only unique records are retained in the output topic.
  * [Mask Fields in a Table](mask-fields.html#flink-sql-mask-fields-action): Mask sensitive data in specified fields of a topic by replacing the original data with a static value.
  * [Transform a Topic](transform-topic.html#flink-sql-transform-topic-action): Change a topic’s properties by applying custom Flink SQL transformations.
