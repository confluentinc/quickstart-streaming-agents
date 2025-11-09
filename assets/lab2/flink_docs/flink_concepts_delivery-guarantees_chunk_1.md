---
document_id: flink_concepts_delivery-guarantees_chunk_1
source_file: flink_concepts_delivery-guarantees.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/delivery-guarantees.html
title: Delivery Guarantees and Latency in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Delivery Guarantees and Latency in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides exactly-once semantics end-to-end by default, which mean that every input message is reflected exactly-once in the output of a [statement](statements.html#flink-sql-statements) and every output message is delivered exactly once.

To achieve this, Confluent Cloud for Apache Flink relies on Apache Flink®’s checkpointing mechanism and Kafka transactions. While checkpointing and fault tolerance falls into Confluent’s responsibility, it is important to understand the implications of how Flink reads from and writes to Kafka:

  * Flink statements write to Kafka by using transactions. Transactions are committed periodically, approximately every minute.
  * Flink by default only reads committed messages from Kafka. For more information, see [isolation.level](/platform/current/installation/configuration/consumer-configs.html#isolation-level).

This implies that depending on the delivery guarantees required by your use case, you can currently achieve different end-to-end latencies with Flink.

  * **Exactly-Once** : If you require exactly-once, the latency is roughly one minute and is dominated by the interval at which Kafka transactions are committed. In this case, ensure that all consumers of the output topics of Flink statements use `isolation.level: read_committed` or set the [Flink table option](../reference/statements/create-table.html#flink-sql-create-table-with-kafka-consumer-isolation-level) `'kafka.consumer.isolation-level' = 'read-committed'`.
  * **At-Least-Once** : If at-least-once is sufficient for your use case, you can read from the output topics with `isolation-level: read_uncommitted`, which is the default in Kafka, or set the [Flink table option](../reference/statements/create-table.html#flink-sql-create-table-with-kafka-consumer-isolation-level) `'kafka.consumer.isolation-level' = 'read-uncommitted'`. With this configuration, depending on the logic of your query, you can achieve an end-to-end latency below 100 ms, but you may see some output messages twice. This happens when Flink needs to abort a transaction that your consumer has already read. You won’t see incorrect results, but you may see the same correct result multiple times.

Note

Confluent is actively working on reducing the latency under exactly-once semantics. If your use case requires a lower latency, reach out to Support or your account manager.
