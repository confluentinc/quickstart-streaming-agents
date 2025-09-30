---
document_id: flink_concepts_flink_chunk_1
source_file: flink_concepts_flink.md
source_url: https://docs.confluent.io/platform/current/flink/concepts/flink.html
title: Understand Apache Flink
chunk_index: 1
total_chunks: 3
---

# Understand Flink¶

Apache Flink® is a distributed system and requires effective allocation and management of compute resources in order to execute streaming applications. It integrates with common cluster resource managers. Currently, you can deploy Confluent Platform for Apache Flink with Kubernetes.

This section contains an overview of Flink’s architecture and describes how its main components interact to execute applications and recover from failures.

## Flink cluster anatomy¶

The Flink runtime consists of two types of processes: a JobManager and one or more TaskManagers.

  * The JobManager coordinates the distributed execution of a Flink Application. With Confluent Platform for Apache Flink, you deploy in Kubernetes application mode, and there is a one-to-one mapping between an Application and a Flink cluster.
  * The TaskManagers (also called workers) execute the tasks of a dataflow, and buffer and exchange the data streams. There must always be at least one TaskManager. The smallest unit of resource scheduling in a TaskManager is a task slot. The number of task slots in a TaskManager indicates the number of concurrent processing tasks. Note that multiple operators may execute in a task slot. Each TaskManager is a JVM process.

## Flink Applications and Environments¶

A Flink Application in Confluent Platform for Apache Flink is any user program that contains a Flink job, along with some configuration. The execution of the job occurs in an Environment. In Confluent Platform for Apache Flink there are APIs to create and update both Applications and Environments. For more information, see [Applications](../jobs/applications/overview.html#cmf-applications), [Environments](../configure/environments.html#cmf-environments), and [Client and APIs for Confluent Manager for Apache Flink Overview](../clients-api/overview.html#cmf-operations).

## Flink APIs¶

Flink offers different levels of abstraction for developing streaming/batch applications. The following image shows the Flink API levels.

[](../../_images/flink-APIs.png)

Following is a description of the Flink APIs:

  * **SQL** provides the highest level of abstraction for Flink. This abstraction is similar to the _Table API_ both in semantics and expressiveness, but represents programs as SQL query expressions. The Flink SQL abstraction interacts with the Table API, and SQL queries can be executed over tables defined in the Table API.
  * The **Table API** is a declarative DSL centered around _tables_ , which may be dynamically changing tables (when representing streams). [The Table API](https://nightlies.apache.org/flink/flink-docs-release-1.19/docs/dev/table/tableapi/) follows the (extended) relational model: Tables have a schema attached, similar to tables in relational databases, and the Table API provides comparable operations, such as select, project, join, group-by, aggregate, and more. Table API programs declaratively define what logical operation should be done rather than specifying exactly how the code for the operation looks. Though the Table API is extensible by various types of user-defined functions, it is less expressive than the Core APIs, and more concise to use, meaning you write less code. In addition, Table API programs go through an optimizer that applies optimization rules before execution. You can seamlessly convert between tables and DataStream APIs enabling programs to mix the Table API with the DataStream API.
  * The **DataStream API** offers the common building blocks for data processing, like various forms of user-specified transformations, joins, aggregations, windows, state, etc. Data types processed in [DataStream API](https://nightlies.apache.org/flink/flink-docs-release-1.19/docs/dev/datastream/overview/) are represented as classes in the respective programming languages. In addition, you can also use the lower-level Process Function operation with the DataStream API, so it is possible to use the lower-level abstraction when necessary.
  * The lowest level of abstraction offers stateful and timely stream processing with the **Process Function** operator. The [ProcessFunction](https://nightlies.apache.org/flink/flink-docs-release-1.19/docs/dev/datastream/operators/process_function/) operator, which is embedded in [DataStream API](https://nightlies.apache.org/flink/flink-docs-release-1.19/docs/dev/datastream/overview/) enables users to freely process events from one or more streams, and provides consistent, fault tolerant state. In addition, users can register event time and processing time callbacks, allowing programs to realize sophisticated computations. In practice, many applications don’t need the low-level abstractions offered by the Process Function operation, and can instead use the [DataStream API](https://nightlies.apache.org/flink/flink-docs-release-1.19/docs/dev/datastream/overview/) for bounded and unbounded streams.
  * The DataSet API has been deprecated.
