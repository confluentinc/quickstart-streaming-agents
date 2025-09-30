---
document_id: flink_overview_chunk_1
source_file: flink_overview.md
source_url: https://docs.confluent.io/cloud/current/flink/overview.html
title: Stream Processing with Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 3
---

# Stream Processing with Confluent Cloud for Apache Flink¶

Apache Flink® is a powerful, scalable stream processing framework for running complex, stateful, low-latency streaming applications on large volumes of data. Flink excels at complex, high-performance, mission-critical streaming workloads and is used by many companies for production stream processing applications. Flink is the de facto industry standard for stream processing.

Get Started for Free

[Sign up for a Confluent Cloud trial](https://www.confluent.io/get-started/) and get $400 of free credit.

Confluent Cloud for Apache Flink provides a cloud-native, serverless service for Flink that enables simple, scalable, and secure stream processing that integrates seamlessly with Apache Kafka®. Your Kafka topics appear automatically as queryable Flink tables, with schemas and metadata attached by Confluent Cloud.

Confluent Cloud for Apache Flink supports creating stream-processing applications by using Flink SQL, the [Flink Table API](reference/table-api.html#flink-table-api) (Java and Python), and custom [user-defined functions](concepts/user-defined-functions.html#flink-sql-udfs).

To run Flink on-premises with Confluent Platform, see [Confluent Platform for Apache Flink](/platform/current/flink/overview.html).

  * What is Confluent Cloud for Apache Flink?
  * Cloud native
  * Complete
  * Everywhere
  * Program Flink with SQL, Java, and Python
  * Confluent for VS Code

## What is Confluent Cloud for Apache Flink?¶

[](../_images/flink-kafka-ecosystem.png)

Confluent Cloud for Apache Flink integrates with the Kafka ecosystem¶

Confluent Cloud for Apache Flink is Flink re-imagined as a truly cloud-native service. Confluent’s fully managed Flink service enables you to:

  * Easily filter, join, and enrich your data streams with Flink
  * Enable high-performance and efficient stream processing at any scale, without the complexities of managing infrastructure
  * Experience Kafka and Flink as a unified platform, with fully integrated monitoring, security, and governance

When bringing Flink to Confluent Cloud, the goal was to provide a uniquely serverless experience superior to just “cloud-hosted” Flink. Kafka on Confluent Cloud goes beyond Kafka by using the [Kora engine](https://www.confluent.io/resources/report/kora-a-cloud-native-event-streaming-platform-for-kafka/), which showcases Confluent’s engineering expertise in building cloud-native data systems. Confluent’s goal is to deliver the same simplicity, security, and scalability for Flink that you expect for Kafka.

Confluent Cloud for Apache Flink is engineered to be:

  * Cloud-native: Flink is fully managed on Confluent Cloud and autoscales up and down with your workloads.
  * Complete: Flink is integrated deeply with Confluent Cloud to provide an enterprise-ready experience.
  * Everywhere: Flink is available in AWS, Azure, and Google Cloud.

Get started with Confluent Cloud for Apache Flink:

  * [Flink SQL Quick Start with Confluent Cloud Console](get-started/quick-start-cloud-console.html#flink-sql-quick-start-cloud-console)
  * [Flink SQL Shell Quick Start](get-started/quick-start-shell.html#flink-sql-quick-start-shell)

## Confluent Cloud for Apache Flink is cloud-native¶

[](../_images/flink-serverless-autoscaling.png)

Confluent Cloud for Apache Flink autoscales with your workloads¶

Confluent Cloud for Apache Flink provides a cloud-native experience for Flink. This means you can focus fully on your business logic, encapsulated in Flink SQL [statements](concepts/statements.html#flink-sql-statements), and Confluent Cloud takes care of what’s needed to run them in a secure, resource-efficient and fault-tolerant manner. You don’t need to know about or interact with Flink clusters, state backends, checkpointing, or any of the other aspects that are usually involved when operating a production-ready Flink deployment.

Fully Managed
    On Confluent Cloud, you don’t need to choose a runtime version of Flink. You’re always using the latest version and benefit from continuous improvements and innovations. All of your running statements automatically and transparently receive security patches and minor upgrades of the Flink runtime.
Autoscaling
    All of your Flink SQL statements on Confluent Cloud are monitored continuously and [auto-scaled](concepts/autopilot.html#flink-sql-autopilot) to keep up with the rate of their input topics. The resources required by a statement depend on its complexity and the throughput of topics it reads from.
Usage-based billing
    You pay only for what you use, not what you provision. Flink compute in Confluent Cloud is elastic: once you stop using the compute resources, they are deallocated, and you no longer pay for them. Coupled with the elasticity provided by scale-to-zero, you can benefit from unbounded scalability while maintaining cost efficiency. For more information, see [Billing](concepts/flink-billing.html#flink-sql-billing).
