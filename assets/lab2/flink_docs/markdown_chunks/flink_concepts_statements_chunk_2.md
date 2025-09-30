---
document_id: flink_concepts_statements_chunk_2
source_file: flink_concepts_statements.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/statements.html
title: Flink SQL Statements in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 3
---

breaking it into smaller parts.

## Lifecycle operations statements¶

These are the supported lifecycle operations for a statement.

Statements have a lifecycle that includes the following states:

  * **Pending** : The statement has been submitted and Flink is preparing to start running the statement.
  * **Running** : Flink is actively running the statement.
  * **Completed** : The statement has completed all of its work.
  * **Deleting** : The statement is being deleted.
  * **Failed** : The statement has encountered an error and is no longer running.
  * **Degraded** : The statement appears unhealthy, for example, no transactions have been committed for a long time, or the statement has frequently restarted recently.
  * **Stopping** : The statement is about to be stopped.
  * **Stopped** : The statement has been stopped and is no longer running.

### Submit a statement¶

  * [SQL shell](../get-started/quick-start-shell.html#flink-sql-quick-start-shell)
  * [Cloud Console](../get-started/quick-start-cloud-console.html#flink-sql-quick-start-run-sql-statement)
  * [REST API statements endpoint](../operate-and-deploy/flink-rest-api.html#flink-rest-api-submit-statement)

### List running statements¶

  * [SQL shell SHOW JOBS statement](../get-started/quick-start-shell.html#flink-sql-quick-start-shell)
  * [Confluent CLI](../reference/flink-sql-cli.html#flink-sql-confluent-cli-list-statements)
  * [Cloud Console](../operate-and-deploy/monitor-statements.html#flink-sql-monitor-statements-with-cloud-console)
  * [REST API statements endpoint](../operate-and-deploy/flink-rest-api.html#flink-rest-api-list-statements)

### Describe a statement¶

  * [Confluent CLI](../reference/flink-sql-cli.html#flink-sql-confluent-cli-describe-statement)
  * [Cloud Console](../operate-and-deploy/monitor-statements.html#flink-sql-monitor-statements-with-cloud-console)
  * [REST API statement endpoint](../operate-and-deploy/flink-rest-api.html#flink-rest-api-get-statement)

### Delete a statement¶

  * [Confluent CLI](../reference/flink-sql-cli.html#flink-sql-confluent-cli-delete-statement)
  * [Cloud Console](../operate-and-deploy/monitor-statements.html#flink-sql-monitor-statements-with-cloud-console)
  * [REST API DELETE request](../operate-and-deploy/flink-rest-api.html#flink-rest-api-delete-statement)

### List statement exceptions¶

  * [Confluent CLI](../reference/flink-sql-cli.html#flink-sql-confluent-cli-list-exceptions)
  * [Cloud Console](../operate-and-deploy/monitor-statements.html#flink-sql-monitor-statements-with-cloud-console)

### Stop and resume a statement¶

  * [Confluent CLI](../reference/flink-sql-cli.html#flink-sql-confluent-cli-update-statement)
  * [REST API UPDATE request](../operate-and-deploy/flink-rest-api.html#flink-rest-api-update-statement)
  * [Cloud Console](../operate-and-deploy/monitor-statements.html#flink-sql-monitor-statements-with-cloud-console)

## Queries in Flink¶

Flink enables issuing queries with an ANSI-standard SQL on data at rest (batch) and data in motion (streams).

These are the queries that are possible with Flink SQL.

Metadata queries
    CRUD on catalogs, databases, tables, etc. Because Flink implements ANSI-Standard SQL, Flink uses a database analogy, and similar to a database, it uses the concepts of catalogs, databases and tables. In Apache Kafka®, these concepts map to environments, Kafka clusters, and topics, respectively.
Ad-hoc / exploratory queries
    You can issue queries on a topic and see the results immediately. A query can be a batch query (“show me what happened up to now”), or a transient streaming query (“show me what happened up to now and give me updates for the near future”). In this case, when the query or the session is ended, no more compute is needed.
Streaming queries
    These queries run continuously and read data from one or more tables/topics and write results of the queries to one table/topic.

In general, Flink supports both batch and stream processing, but the exact subset of allowed operations differs slightly depending of the type of query. For more information, see [Flink SQL Queries](../reference/queries/overview.html#flink-sql-queries).

All queries are executed in streaming execution mode, whether the sources are bounded or unbounded.
