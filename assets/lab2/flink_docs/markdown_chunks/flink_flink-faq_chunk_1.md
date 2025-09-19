---
document_id: flink_flink-faq_chunk_1
source_file: flink_flink-faq.md
source_url: https://docs.confluent.io/cloud/current/flink/flink-faq.html
title: FAQ for Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 2
---

# Frequently Asked Questions for Confluent Cloud for Apache Flink¶

This topic provides answers to frequently asked questions about Confluent Cloud for Apache Flink®.

## What is Confluent Cloud for Apache Flink?¶

Confluent Cloud for Apache Flink is a fully managed, cloud-native service for stream processing using Flink SQL. It enables you to process, analyze, and transform data in real time directly on your Confluent Cloud-managed Kafka clusters.

## How do I get started with Confluent Cloud for Apache Flink?¶

Get started by clicking **SQL Workspaces** in the Confluent Cloud Console. For more information, see [Flink SQL Quick Start with Confluent Cloud Console](get-started/quick-start-cloud-console.html#flink-sql-quick-start-cloud-console).

Also, you can run the `confluent flink shell` command to start the Flink SQL shell. For more information, see [Flink SQL Shell Quick Start](get-started/quick-start-shell.html#flink-sql-quick-start-shell).

## What is a compute pool?¶

A compute pool is a dedicated set of resources, measured in CFUs, that runs your Flink SQL statements. You must create a compute pool before running statements. Multiple statements can share a compute pool, and you can scale pools up or down as needed. For more information, see [Compute Pools](concepts/compute-pools.html#flink-sql-compute-pools).

## How is Confluent Cloud for Apache Flink billed?¶

Billing is based on the number of CFUs provisioned in your compute pools and the duration for which they are running. You are charged for the resources allocated, not per statement. For more information, see [Billing](concepts/flink-billing.html#flink-sql-billing).

## What are the prerequisites for using Confluent Cloud for Apache Flink?¶

  * You need a Confluent Cloud account and an environment with Stream Governance enabled.
  * You must have the appropriate roles and permissions, for example, the [FlinkDeveloper](operate-and-deploy/flink-rbac.html#flink-rbac) role to run statements.
  * You need access to at least one compute pool.

## What sources and sinks are supported?¶

Confluent Cloud for Apache Flink supports reading from and writing to Kafka topics in your Confluent Cloud environment. In addition, you use Confluent’s [AI/ML features](../ai/overview.html#ai-overview) to perform searches on external tables. And you can use [Confluent Tableflow](../topics/tableflow/overview.html#cloud-tableflow) to materialize streams to external tables.

## How do I monitor my Flink SQL statements?¶

You can monitor statements using the Cloud Console, which provides status, metrics, and logs. For advanced monitoring, use the [Metrics API](../monitoring/metrics-api.html#metrics-api) and [Notifications for Confluent Cloud](../monitoring/configure-notifications.html#ccloud-notifications) to set up alerts for failures, lag, and resource utilization. For more information, see [Best practices for alerting](operate-and-deploy/monitor-statements.html#flink-sql-monitor-best-practices).

## What happens if my statement fails?¶

If a statement fails, you will see an error message in the Cloud Console. You can view logs and metrics to diagnose the issue. Statements can be restarted after resolving the underlying problem.

## Can I use Flink SQL to join multiple topics?¶

Yes, you can use Flink SQL to join multiple Kafka topics, perform aggregations, windowing, filtering, and more. For more information, see the [Flink SQL statements](concepts/statements.html#flink-sql-statements).

## How do I manage schema evolution?¶

Flink SQL integrates with Confluent’s [Schema Registry](../sr/schemas-manage.html#sr-prv). When reading from or writing to topics with Avro, Protobuf, or JSON Schema, Flink SQL uses the registered schemas and handles compatible schema evolution.

## How do I control access to Flink resources?¶

Access to Flink resources is managed using Role-Based Access Control (RBAC) in Confluent Cloud. Assign users and service accounts the appropriate roles, such as FlinkAdmin or FlinkDeveloper, to control what actions they can perform. For more information, see [Grant Role-Based Access](operate-and-deploy/flink-rbac.html#flink-rbac).

## How do I secure my Flink SQL jobs and data?¶

Confluent Cloud for Apache Flink uses the same security model as the rest of Confluent Cloud, including RBAC, API keys, and network controls. Make sure to assign the minimum required permissions to users and service accounts. For more information, see [Grant Role-Based Access in Confluent Cloud for Apache Flink](operate-and-deploy/flink-rbac.html#flink-rbac).
