---
document_id: flink_operate-and-deploy_best-practices_chunk_2
source_file: flink_operate-and-deploy_best-practices.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/best-practices.html
title: Best Practices for Moving SQL Statements to Production in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 2
---

consumer at the same time.

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
