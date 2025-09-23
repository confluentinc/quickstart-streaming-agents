---
document_id: flink_concepts_statements_chunk_1
source_file: flink_concepts_statements.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/statements.html
title: Flink SQL Statements in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 3
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
