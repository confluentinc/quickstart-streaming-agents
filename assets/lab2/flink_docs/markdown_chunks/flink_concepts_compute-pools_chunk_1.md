---
document_id: flink_concepts_compute-pools_chunk_1
source_file: flink_concepts_compute-pools.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/compute-pools.html
title: Compute Pools in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Compute Pools in Confluent Cloud for Apache Flink¶

A compute pool in Confluent Cloud for Apache Flink® represents a set of compute resources bound to a region that is used to run your SQL statements. The resources provided by a compute pool are shared between all statements that use it.

The capacity of a compute pool is measured in [CFUs](flink-billing.html#flink-sql-cfus). Compute pools expand and shrink automatically based on the resources required by the statements using them. A compute pool without any running statements scale down to zero. The maximum size of a compute pool is configured during creation.

A compute pool is provisioned in a specific region. The statements using a compute pool can only read and write Apache Kafka® topics in the same region as the compute pool.

Compute pools fulfill two roles:

  * **Workload Isolation** : Statements in different compute pools are isolated from each other.
  * **Budgeting** : Statements within a compute pool can’t use more than the configured maximum number of [CFUs](flink-billing.html#flink-sql-cfus).

## Compute pools and isolation¶

All statements using the same compute pool compete for resources. Although Confluent Cloud’s Autopilot aims to provide each statement with the resources it needs, this might not always be possible, in particular, when the maximum resources of the compute pool are exhausted.

To avoid situations in which statements with different latency and availability requirements compete for resources, Confluent recommends using separate compute pools for different use cases, for example, ad-hoc exploration _vs._ mission-critical, long-running queries. Because statements may affect each other, Confluent recommends sharing compute pools only between statements with comparable requirements.

## Manage compute pools¶

You can use these Confluent tools to create and manage compute pools.

  * [Cloud Console](../operate-and-deploy/create-compute-pool.html#flink-sql-manage-compute-pool)
  * [Confluent CLI](../reference/flink-sql-cli.html#flink-sql-confluent-cli)
  * [REST API](../operate-and-deploy/flink-rest-api.html#flink-rest-api)
  * [Confluent Terraform Provider](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/resources/confluent_flink_compute_pool)

## Authorization¶

You must be authorized to create, update, delete (`FlinkAdmin`) or use (`FlinkDeveloper`) a compute pool. For more information, see [Grant Role-Based Access in Confluent Cloud for Apache Flink](../operate-and-deploy/flink-rbac.html#flink-rbac).

## Move statements between compute pools¶

You can move a statement from one compute pool to another. This can be useful if you’re close to maxing out the resources in one pool. To move a running statement, you must stop the statement, change its compute pool, then restart the statement.
