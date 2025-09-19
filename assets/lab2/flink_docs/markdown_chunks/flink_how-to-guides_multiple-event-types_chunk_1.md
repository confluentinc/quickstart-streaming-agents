---
document_id: flink_how-to-guides_multiple-event-types_chunk_1
source_file: flink_how-to-guides_multiple-event-types.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/multiple-event-types.html
title: Handle Multiple Event Types In Tables in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 4
---

# Handle Multiple Event Types with Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides several ways to work with Kafka topics containing multiple event types. This guide explains how Flink automatically infers and handles different event type patterns, allowing you to query and process mixed event streams effectively.

## Overview¶

When working with Kafka topics containing multiple event types, Flink [automatically](../reference/serialization.html#flink-sql-serialization) infers table schemas based on the Schema Registry configuration and schema format. The following sections describe the supported approaches in order of recommendation.
