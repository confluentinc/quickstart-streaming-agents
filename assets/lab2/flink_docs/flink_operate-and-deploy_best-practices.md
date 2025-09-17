---
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/best-practices.html
title: Best Practices for Moving SQL Statements to Production in Confluent Cloud for Apache Flink
hierarchy: ['operate-and-deploy', 'best-practices.html']
scraped_date: 2025-09-05T13:46:51.352919
---

# Move SQL Statements to Production in Confluent Cloud for Apache Flink¶

When you move your Flink SQL statements to production in Confluent Cloud for Apache Flink®, consider the following recommendations and best practices.

  * Validate your watermark strategy
  * Validate or disable idleness handling
  * Choose the correct Schema Registry compatibility type
  * Separate workloads of different priorities into separate compute pools
  * Use event-time temporal joins instead of streaming joins
  * Implement state time-to-live (TTL)
  * Use service account API keys for production
  * Assign custom names to Flink SQL statements

## Validate your watermark strategy¶

When moving your Flink SQL statements to production, it’s crucial to validate your [watermark](../../_glossary.html#term-watermark) strategy. [Watermarks](../concepts/timely-stream-processing.html#flink-sql-timely-stream-processing) in Flink track the progress of event time and provide a way to trigger time-based operations.

Confluent Cloud for Apache Flink provides a [default watermark strategy](../reference/functions/datetime-functions.html#flink-sql-source-watermark-function) for all tables, whether they’re created automatically from a Kafka topic or from a [CREATE TABLE](../reference/statements/create-table.html#flink-sql-create-table) statement. The default watermark strategy is applied on the [$rowtime](../reference/statements/create-table.html#flink-sql-system-columns-rowtime) system column, which is mapped to the associated timestamp of a Kafka record. Watermarks for this default strategy are calculated per Kafka partition, and at least 250 events are required per partition.

Here are some situations when you need to define your own [custom watermark strategy](../reference/statements/create-table.html#flink-sql-watermark-clause):

  * When the event time needs to be based on data from the payload and not the timestamp of the Kafka record.
  * If a delay of longer than 7 days can occur.
  * When events might not arrive in the exact order they were generated.
  * When data may arrive late due to network latency or processing delays.

## Validate or disable idleness handling¶

One critical aspect to consider when moving your Flink SQL statements to production is the handling of idleness in data streams. If no events arrive within a certain time (timeout duration) on a Kafka partition, that partition is marked as idle and does not contribute to the watermark calculation until a new event comes in. This situation creates a problem: if some partitions continue to receive events while others are idle, the overall watermark computation, which is based on the minimum across all parallel watermarks, may be inaccurately held back.

Confluent Cloud for Apache Flink dynamically adjusts the consideration of idle partitions in watermark calculations with Confluent’s Progressive Idleness feature. The idle-time detection starts small at 15 seconds but grows linearly with the age of the statement up to a maximum of 5 minutes. Progressive Idleness can cause wrong watermarks if a partition is marked as idle too quickly, and this can cause the system to move ahead too quickly, impacting data processing.

When you move your Flink SQL statement into production, make sure that you have validated how you want to handle idleness. You can configure or disable this behavior by using the [sql.tables.scan.idle-timeout](../reference/statements/set.html#flink-sql-set-statement-config-options) option.

## Choose the correct Schema Registry compatibility type¶

The Confluent Schema Registry plays a pivotal role in ensuring that the schemas of the data flowing through your Kafka topics are consistent, compatible, and evolve in a controlled manner. One of the key decisions in this process is selecting the appropriate [schema compatibility type](../../sr/fundamentals/schema-evolution.html#sr-compatibility-types).

Consider using `FULL_TRANSITIVE` compatibility to ensure that any new schema is fully compatible with all previous versions of the schema. This comprehensive check minimizes the risk of introducing changes that could disrupt data-processing applications relying on the data. When choosing any of the other compatibility modes, you need to consider the consequences on currently-running statements, especially since a Flink statement is both a producer and a consumer at the same time.

## Separate workloads of different priorities into separate compute pools¶

All statements using the same [compute pools](../concepts/compute-pools.html#flink-sql-compute-pools) compete for resources. Although the Confluent Cloud Autopilot aims to provide each statement with the resources it needs, this may not always be possible, in particular, when the maximum resources of the compute pool are exhausted.

To avoid situations in which statements with different latency and availability requirements compete for resources, consider using separate compute pools for different use cases, for example, ad-hoc exploration _vs._ mission-critical, long-running queries. Because statements may affect each other, you should share compute pools only between statements with comparable requirements.

## Use event-time temporal joins instead of streaming joins¶

When processing data streams, choosing the right type of join operation is crucial for efficiency and performance. Event-time temporal joins offer significant advantages over regular streaming joins.

Temporal joins are particularly useful when the join condition is based on a [time attribute](../concepts/timely-stream-processing.html#flink-sql-time-attributes). They enable you to join a primary stream with a historical version of another table, using the state of that table as it existed at the time of the event. This results in more efficient processing, because it avoids the need to keep large amounts of state in memory. Traditional streaming joins involve keeping a stateful representation of all joined records, which can be inefficient and resource-intensive, especially with large datasets or high-velocity streams. Also, event-time temporal joins typically result in insert-only outputs, when your inputs are also insert-only, which means that once a record is processed and joined, it is not updated or deleted later. Streaming joins often need to handle updates and deletions.

When moving to production, prefer using temporal joins wherever applicable to ensure your data processing is efficient and performant. Avoid traditional streaming joins unless necessary, as they can lead to increased resource consumption and complexity.

## Implement state time-to-live (TTL)¶

Some stateful operations in Flink require storing state, like streaming joins and pattern matching. Managing this state effectively is crucial for application performance, resource optimization, and cost reduction. The state time-to-live (TTL) feature enables specifying a minimum time interval for how long state, meaning state that is not updated, is retained. This mechanism ensures that state is cleared at some time after the idle duration. When moving to production, you should configure the [sql.state-ttl](../reference/statements/set.html#flink-sql-set-statement-config-options) setting carefully to balance performance versus correctness of the results.

## Use service account API keys for production¶

[API keys](../../security/authenticate/workload-identities/service-accounts/api-keys/overview.html#cloud-api-keys) for Confluent Cloud can be created with [user accounts](../../security/authenticate/user-identities/user-accounts/overview.html#user-accounts) and [service accounts](../../security/authenticate/workload-identities/service-accounts/overview.html#service-accounts). A service account is intended to provide an identity for an application or service that needs to perform programmatic operations within Confluent Cloud. When moving to production, ensure that only service account API keys are used. Avoid user account API keys, except for development and testing. If a user leaves and a user account is deleted, all API keys created with that user account are deleted, and applications might break.

## Assign custom names to Flink SQL statements¶

Custom naming facilitates easier management, monitoring, and debugging of your streaming applications by providing clear, identifiable references to specific operations or data flows. You can do this easily by using the [client.statement-name](../reference/statements/set.html#flink-sql-set-statement-config-options) option.

## Review error handling and monitoring best practices¶

Review these topics:

  * [Error handling and recovery](monitor-statements.html#flink-sql-monitor-error-handling)
  * [Best practices for alerting](monitor-statements.html#flink-sql-monitor-best-practices)
  * [Notifications](monitor-statements.html#flink-sql-monitor-notifications)

## Related content¶

  * [Flink Compute Pools](../concepts/compute-pools.html#flink-sql-compute-pools)
  * [Billing on Confluent Cloud for Apache Flink](../concepts/flink-billing.html#flink-sql-billing)
  * [Managing and Monitoring Statements](monitor-statements.html#flink-sql-monitor-statements-with-cloud-console)

Note

This website includes content developed at the [Apache Software Foundation](https://www.apache.org/) under the terms of the [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0.html).
