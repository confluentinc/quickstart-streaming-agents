---
document_id: flink_operate-and-deploy_create-compute-pool_chunk_1
source_file: flink_operate-and-deploy_create-compute-pool.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/create-compute-pool.html
title: Manage Flink Compute Pools in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 7
---

# Manage Compute Pools in Confluent Cloud for Apache Flink¶

A [compute pool](../concepts/compute-pools.html#flink-sql-compute-pools) represents the compute resources that are used to run your [SQL statements](../concepts/statements.html#flink-sql-statements). The resources provided by a compute pool are shared among all statements that use it. It enables you to limit or guarantee resources as your use cases require. A compute pool is bound to a region. There is no cost for creating compute pools.

To create a compute pool, you need the OrganizationAdmin, EnvironmentAdmin, or FlinkAdmin RBAC role.

In addition to the Cloud Console, Confluent provides these tools for creating and managing Flink compute pools:

  * [Confluent CLI](../reference/flink-sql-cli.html#flink-cli-manage-compute-pools)
  * [Confluent Cloud REST API](flink-rest-api.html#flink-rest-api-manage-compute-pools)
  * [Confluent Terraform provider](../../clusters/terraform-provider.html#confluent-terraform-provider-resources-flink)
