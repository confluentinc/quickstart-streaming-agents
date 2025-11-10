---
document_id: flink_concepts_cmf_chunk_1
source_file: flink_concepts_cmf.md
source_url: https://docs.confluent.io/platform/current/flink/concepts/cmf.html
title: Confluent Manager for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Confluent Manager for Apache Flink¶

Confluent Manager for Apache Flink® (CMF) is a central management component that enables users to securely manage a fleet of Flink [Applications](../jobs/applications/overview.html#cmf-applications) across multiple [Environments](../configure/environments.html#cmf-environments). CMF provides:

  * Job life-cycle management for Flink jobs.
  * Integration with Confluent Platform for authentication and authorization (RBAC).
  * Well-defined REST APIs and command-line interfaces (CLIs).

The following image shows the high-level architecture of how CMF fits in.

[](../../_images/cmf-architecture.png)

CMF sits next to other Confluent Platform components such as Confluent Server and Connect. Metadata for CMF, such as existing Flink environments, is stored in an embedded database. All interactions with CMF occur through its [REST API](../clients-api/rest.html#af-rest-api). You can use these APIs directly for maximum flexibility, and the same APIs are exposed with the Confluent CLI. They are also integrated with the Confluent for Kubernetes (CFK) for a native Kubernetes experience.

Important

**Do not manually modify FlinkDeployment resources** : CMF manages FlinkDeployment resources internally and you should not modify them manually. Manual modifications to FlinkDeployment resources can cause conflicts and unexpected behavior.
