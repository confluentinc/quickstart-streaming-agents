---
document_id: flink_overview_chunk_2
source_file: flink_overview.md
source_url: https://docs.confluent.io/cloud/current/flink/overview.html
title: Stream Processing with Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 3
---

For more information, see [Billing](concepts/flink-billing.html#flink-sql-billing).

## Confluent Cloud for Apache Flink is complete¶

[](../_images/flink-unified-platform.png)

Confluent Cloud for Apache Flink is a unified platform¶

Confluent has integrated Flink deeply with Confluent Cloud to provide an enterprise-ready, complete experience that enables data discovery and processing using familiar SQL semantics.

### Confluent Cloud for Apache Flink is a regional service¶

Confluent Cloud for Apache Flink is a regional service, and you can create [compute pools](concepts/compute-pools.html#flink-sql-compute-pools) in any of the supported regions. Compute pools represent a set of resources that scale automatically between zero and their maximum size to provide all of the power required by your statements. A compute pool is bound to a region, and the resources provided by a compute pool are shared among all statements that use them.

While compute pools are created within an environment, you can query data in any topic in your Confluent Cloud organization, even if the data is in a different environment, as long as it’s in the same region. This enables Flink to do cross-cluster, cross-environment queries while providing low latency. Of course, access control with [RBAC](operate-and-deploy/flink-rbac.html#flink-rbac) still determines the data that can be read or written.

Flink can read from and write to any Kafka cluster in the same region, but by design, Confluent Cloud doesn’t allow you to query across regions. This helps you to avoid expensive data transfer charges, and also protects data locality and sovereignty by keeping reads and writes in-region.

For a list of available regions, see [Supported Cloud Regions](reference/cloud-regions.html#flink-cloud-regions).

### Metadata mapping between Kafka cluster, topics, schemas, and Flink¶

Kafka topics and schemas are always in sync with Flink, simplifying how you can process your data. Any topic created in Kafka is visible directly as a table in Flink, and any table created in Flink is visible as a topic in Kafka. Effectively, Flink provides a SQL interface on top of Confluent Cloud.

Because Flink follows the SQL standard, the terminology is slightly different from Kafka. The following table shows the mapping between Kafka and Flink terminology.

Kafka | Flink | Notes
---|---|---
Environment | Catalog | Flink can query and join data that are in any environments/catalogs
Cluster | Database | Flink can query and join data that are in different clusters/databases
Topic + Schema | Table | Kafka topics and Flink tables are always in sync. You never need to declare tables manually for existing topics. Creating a table in Flink creates a topic and the associated schema.

As a result, when you start using Flink, you can directly access all of the environments, clusters, and topics that you already have in Confluent Cloud, without any additional metadata creation.

Automatic metadata integration in Confluent Cloud for Apache Flink¶

Compared with Apache Flink, the main difference is that the [Data Definition Language (DDL) statements](reference/statements/overview.html#flink-sql-statements-overview) related to catalogs, databases, and tables act on physical objects and not only on metadata. For example, when you create a table in Flink, the corresponding topic and schema are created immediately in Confluent Cloud.

Confluent Cloud provides a unified approach to metadata management. There is one object definition, and Flink integrates directly with this definition, avoiding unnecessary duplication of metadata and making all topics immediately queryable with Flink SQL. Also, any existing schemas in [Schema Registry](../sr/schemas-manage.html#sr-prv) are used to surface fully-defined entities in Confluent Cloud. If you’re already on Confluent Cloud, you see tables automatically that are ready to query using Flink, simplifying data discovery and exploration.

### Observability¶

Confluent Cloud provides you with a curated set of metrics, exposing them through Confluent’s existing [Metrics API](../monitoring/metrics-api.html#metrics-api). If you have established observability platforms in place, Confluent Cloud provides first-class integrations with New Relic, Datadog, Grafana Cloud, and Dynatrace.

You can also monitor workloads directly within the Confluent Cloud Console. Clicking into a [compute pool](concepts/compute-pools.html#flink-sql-compute-pools) gives you insight into the health and performance of your applications, in addition to the resource consumption of your compute pool.

### Security¶

Confluent Cloud for Apache Flink has a deep integration with [Role-Based Access Control (RBAC)](operate-and-deploy/flink-rbac.html#flink-rbac), ensuring that you can easily access and process the data that you have access to, and no other data.
