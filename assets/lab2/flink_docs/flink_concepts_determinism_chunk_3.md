---
document_id: flink_concepts_determinism_chunk_3
source_file: flink_concepts_determinism.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/determinism.html
title: Determinism with continuous Flink SQL queries in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 3
---

functions are mainly temporal functions.

## Determinism in stream processing¶

A core difference between streaming and batch is the unboundedness of the data. Flink SQL abstracts streaming processing as the [continuous query on dynamic tables](dynamic-tables.html#flink-sql-dynamic-tables-and-continuous-queries). So the dynamic function in the batch query example is equivalent to a non-deterministic function in a streaming processing, where logically every change in the base table triggers the query to be executed.

If the `clicks` log table in the previous example is from an Apache Kafka® topic that’s continuously written, the same query in stream mode returns a `CURRENT_TIMESTAMP` that changes over time.

    SELECT CURRENT_TIMESTAMP, * FROM clicks;

For example:

    +-------------------------+------+---------------------+------------+
    |       CURRENT_TIMESTAMP |  uid |               cTime |        url |
    +-------------------------+------+---------------------+------------+
    | 2023-08-23 17:25:46.831 | Mary | 2023-08-22 12:00:01 |      /home |
    | 2023-08-23 17:25:47.001 |  Bob | 2023-08-22 12:00:01 |      /home |
    | 2023-08-23 17:25:47.310 | Mary | 2023-08-22 12:00:05 | /prod?id=1 |
    +-------------------------+------+---------------------+------------+

### Non-determinism in streaming¶

In addition to the non-deterministic functions, these are other factors that may generate non-determinism:

  1. Non-deterministic back read of a source connector.
  2. Querying based on [processing time](timely-stream-processing.html#flink-sql-time-attributes-processing-time). Processing time is not supported in Confluent Cloud for Apache Flink.
  3. Clearing internal state data based on TTL.

#### Non-deterministic back read of source connector¶

For Flink SQL, the determinism provided is limited to the computation only, because it doesn’t store user data itself. Here, it’s necessary to distinguish between the managed internal state in streaming mode and the user data itself. If the source connector’s implementation can’t provide deterministic back read, it brings non-determinism to the input data, which may produce non-deterministic results.

Common examples are inconsistent data for multiple reads from a same offset, or requests for data that no longer exists because of the retention time, for example, when the requested data is beyond the configured TTL of a Kafka topic.

#### Clear internal state data based on TTL¶

Because of the unbounded nature of stream processing, the internal state data maintained by long-running streaming queries in operations like [regular join](../reference/queries/joins.html#flink-sql-regular-joins) and [group aggregation](../reference/queries/group-aggregation.html#flink-sql-group-aggregation) (non-windowed aggregation) may continuously increase. Setting a state TTL to clean up internal state data is often a necessary compromise but may make the computation results non-deterministic.

The impact of the non-determinism on different queries is different. For some queries it only produces non-deterministic results, which means that the query works, but multiple runs fail to produce consistent results. But other queries can produce more serious effects, like incorrect results or runtime errors. The main cause of these failures is “non-deterministic update”.

### Non-deterministic update in streaming¶

Flink implements a complete incremental update mechanism based on the [continuous query on dynamic tables](dynamic-tables.html#flink-sql-dynamic-tables-and-continuous-queries) abstraction. All operations that need to generate incremental messages maintain complete internal state data, and the operation of the entire query pipeline, including the complete DAG from source to sink operators, relies on the guarantee of correct delivery of update messages between operators, which can be broken by non-determinism, leading to errors.

What is a “non-deterministic Update” (NDU)? Update messages (the changelog) may contain these kinds of message types:

  * Insert (I)
  * Delete (D)
  * Update_Before (UB)
  * Update_After (UA)

In an insert-only changelog pipeline, there’s no NDU problem. When there is an update message containing at least one message D, UB, UA in addition to I, the update key of the message, which can be regarded as the primary key of the changelog, is deduced from the query.

  * When the update key can be deduced, the operators in the pipeline maintain the internal state by the update key.
  * When the update key can’t be deduced, it’s possible that the primary key isn’t defined in the CDC source table or sink table, or some operations can’t be deduced from the semantics of the query.

All operators maintaining internal state can only process update (D/UB/UA) messages through complete rows. Sink nodes work in retract mode when no primary key is defined, and delete operations are performed by complete rows.

This means that in the update-by-row mode, all the update messages received by the operators that need to maintain the state can’t be interfered by the non-deterministic column values, otherwise it will cause NDU problems resulting in computation errors. For a query pipeline with update messages that can’t derive the update key, the following points are the most important sources of NDU problems:

  1. Non-deterministic functions, including scalar, table, aggregate functions, built-in or custom ones
  2. LookupJoin on an evolving source
  3. CDC source carries metadata fields, like system columns, that don’t belong to the row entity itself

Exceptions caused by cleaning internal state data based on TTL are discussed separately as a runtime fault-tolerant handling strategy. For more information, see [FLINK-24666](https://issues.apache.org/jira/browse/FLINK-24666).
