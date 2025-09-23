---
source_url: https://docs.confluent.io/cloud/current/flink/concepts/statements.html
title: Flink SQL Statements in Confluent Cloud for Apache Flink
hierarchy: ['concepts', 'statements.html']
scraped_date: 2025-09-05T13:45:37.757981
---

# Flink SQL Statements in Confluent Cloud for Apache Flink¶

In Confluent Cloud for Apache Flink®, a _statement_ represents a high-level resource that’s created when you enter a SQL query.

Each statement has a property that holds the SQL query that you entered. Based on the SQL query, the statement may be one of these kinds:

  * A metadata operation, or [DDL statement](../reference/statements/overview.html#flink-sql-statements-overview)
  * A _background statement_ , which writes data back to a table/topic while running in the background
  * A _foreground statement_ , which writes data back to the UI or a client.

In all of these cases, the statement represents any SQL statement for [Data Definition Language (DDL)](../reference/statements/overview.html#flink-sql-statements-overview), [Data Manipulation Language (DML)](../reference/queries/overview.html#flink-sql-queries), and Data Query Language (DQL).

When you submit a SQL query, Confluent Cloud creates a statement resource. You can create a statement resource from any Confluent-supported interface, including the SQL shell, Confluent CLI, Cloud Console, the [REST API](../operate-and-deploy/flink-rest-api.html#flink-rest-api), and [Terraform](../../clusters/terraform-provider.html#confluent-terraform-provider-resources-flink).

The SQL query within a statement is immutable, which means that you can’t make changes to the SQL query once it’s been submitted. If you need to edit a statement, stop the running statement and create a new statement.

You can change the [security principal](../operate-and-deploy/flink-rbac.html#flink-rbac) for the statement. If a statement is running under a user account, you can change it to run under a service account by using the Confluent Cloud Console, Confluent CLI, the [REST API](../operate-and-deploy/flink-rest-api.html#flink-rest-api-update-statement), or the [Terraform provider](../../clusters/terraform-provider.html#confluent-terraform-provider). Running a statement under a service account provides better security and stability, ensuring that your statements aren’t affected by changes in user status or authorization.

Also, you can change the compute pool that runs a statement. This can be useful if you’re close to maxing out the resources in one pool.

You must stop the statement before changing the principal or compute pool, then restart the statement after the change.

Confluent Cloud for Apache Flink enforces a 30-day retention for statements in terminal states. For example, once a statement transitions to the STOPPED state, it no longer consumes compute and is deleted after 30 days.

If there is no consumer for the results of a foreground statement for five minutes or longer, Confluent Cloud moves the statement to the STOPPED state.

## Limit on query text size¶

Confluent Cloud for Apache Flink has a limit of **4 MB** on the size of query text. This limit includes string and binary literals that are part of the query.

The maximum length of a statement name is 72 characters.

If you combine multiple SQL statements into a single semicolon-separated string, the length limit applies to the entire string.

If the query size is greater than the 4 MB limit, you receive the following error.

    This query is too large to process (exceeds 4194304 bytes).

    This can happen due to:

    * Complex query structure.
    * Too many columns selected or expanded due to * usage.
    * Multiple table joins.
    * Large number of conditions.

    Try simplifying your query or breaking it into smaller parts.

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

## Data lifecycle¶

Broadly speaking, the Flink SQL lifecycle is:

  * Data is read into a Flink table from Kafka via the Flink connector for Kafka.

  * Data is processed using SQL statements.

  * Data is processed using Flink task managers (managed by Confluent and not exposed to users), which are part of the Flink runtime. Some data may be stored temporarily as state in Flink while it’s being processed

  * Data is returned to the user as a result-set.

    * The result-set may be bounded, in which case the query terminates.
    * The result-set may be unbounded, in which case the query runs until canceled manually.

OR

  * Data is written back out to one or more tables.

    * Data is stored in Kafka topics.
    * Schema for the table is stored in Flink Metastore and synchronized out to Schema Registry.

## Flink SQL Data Definition Language (DDL) statements¶

Data Definition Language (DDL) statements are imperative verbs that define metadata in Flink SQL by adding, changing, or deleting tables. Data Definition Language statements modify metadata only and don’t operate on data. Use these statements with declarative [Flink SQL Queries](../reference/queries/overview.html#flink-sql-queries) to create your Flink SQL applications.

Flink SQL makes it simple to develop streaming applications using standard SQL. It’s easy to learn Flink SQL if you’ve ever worked with a database or SQL-like system that’s ANSI-SQL 2011 compliant.

## Available DDL statements¶

These are the available DDL statements in Confluent Cloud for Flink SQL.

ALTER

  * [ALTER MODEL Statement in Confluent Cloud for Apache Flink](../reference/statements/alter-model.html#flink-sql-alter-model)
  * [ALTER TABLE Statement in Confluent Cloud for Apache Flink](../reference/statements/alter-table.html#flink-sql-alter-table)
  * [ALTER VIEW Statement in Confluent Cloud for Apache Flink](../reference/statements/alter-view.html#flink-sql-alter-view)

CREATE

  * [CREATE FUNCTION Statement](../reference/statements/create-function.html#flink-sql-create-function)
  * [CREATE MODEL Statement in Confluent Cloud for Apache Flink](../reference/statements/create-model.html#flink-sql-create-model)
  * [CREATE TABLE Statement in Confluent Cloud for Apache Flink](../reference/statements/create-table.html#flink-sql-create-table)
  * [CREATE VIEW Statement in Confluent Cloud for Apache Flink](../reference/statements/create-view.html#flink-sql-create-view)

DESCRIBE

  * [DESCRIBE Statement in Confluent Cloud for Apache Flink](../reference/statements/describe.html#flink-sql-describe)

DROP

  * [DROP MODEL Statement in Confluent Cloud for Apache Flink](../reference/statements/drop-model.html#flink-sql-drop-model)
  * [DROP TABLE Statement in Confluent Cloud for Apache Flink](../reference/statements/drop-table.html#flink-sql-drop-table)
  * [DROP VIEW Statement in Confluent Cloud for Apache Flink](../reference/statements/drop-view.html#flink-sql-drop-view)

EXPLAIN

  * [EXPLAIN Statement in Confluent Cloud for Apache Flink](../reference/statements/explain.html#flink-sql-explain)

RESET

  * [RESET Statement in Confluent Cloud for Apache Flink](../reference/statements/reset.html#flink-sql-reset-statement)

SET

  * [SET Statement in Confluent Cloud for Apache Flink](../reference/statements/set.html#flink-sql-set-statement)

SHOW

  * [SHOW Statements in Confluent Cloud for Apache Flink](../reference/statements/show.html#flink-sql-show)

USE

  * [USE CATALOG Statement in Confluent Cloud for Apache Flink](../reference/statements/use-catalog.html#flink-sql-use-catalog-statement)
  * [USE <database_name> Statement in Confluent Cloud for Apache Flink](../reference/statements/use-database.html#flink-sql-use-database-statement)
