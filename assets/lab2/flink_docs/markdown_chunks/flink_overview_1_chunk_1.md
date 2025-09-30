---
document_id: flink_overview_1_chunk_1
source_file: flink_overview_1.md
source_url: https://docs.confluent.io/platform/current/flink/overview.html
title: Confluent Platform for Apache Flink Overview
chunk_index: 1
total_chunks: 1
---

# Confluent Platform for Apache Flink Overview¶

Confluent Platform for Apache Flink® brings support for Apache Flink® to Confluent Platform.

Apache Flink applications are composed of streaming dataflows that are transformed by one or more user-defined operators. These dataflows form directed acyclic graphs that start with one or more sources, and end in one or more sinks. Sources and sinks can be Apache Kafka® topics, which means that Flink integrates nicely with Confluent Platform. To learn more about Confluent Platform for Apache Flink connector support, see [Connectors](jobs/applications/supported-features.html#af-cp-connectors).

Confluent Platform for Apache Flink is fully compatible with Apache Flink. However, not all Apache Flink features are supported in Confluent Platform for Apache Flink. To learn more about what features are supported, see [Confluent Platform for Apache Flink Features and Support](jobs/applications/supported-features.html#cpflink-vs-oss).

Flink applications are deployed in Kubernetes with Confluent Manager for Apache Flink, which is a central management component that enables users to securely manage a fleet of Flink applications across multiple environments.

See the following topics to learn more and get started:

  * [Install and Configure](installation/overview.html#cpf-install)
  * [Get Started](get-started/get-started-application.html#cpf-get-started)
  * [Supported Features](jobs/applications/supported-features.html#cpflink-vs-oss)
  * [Flink Concepts](concepts/flink.html#cp-flink-concepts)
  * [Confluent Manager for Apache Flink](concepts/cmf.html#cmf)
  * [Get Help](get-help.html#cpf-get-help)
