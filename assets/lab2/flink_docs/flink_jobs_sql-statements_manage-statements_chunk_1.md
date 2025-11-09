---
document_id: flink_jobs_sql-statements_manage-statements_chunk_1
source_file: flink_jobs_sql-statements_manage-statements.md
source_url: https://docs.confluent.io/platform/current/flink/jobs/sql-statements/manage-statements.html
title: Manage Statements with Confluent Manager for Apache Flink
chunk_index: 1
total_chunks: 2
---

# Manage Statements in Confluent Manager for Apache Flink¶

There are different ways to interact with a CMF Statement resource. You can rescale, stop, resume, and delete statements.

Important

The examples in the following topics assume that CMF was installed with the examples catalog enabled (`cmf.sql.examples-catalog.enabled=true`).

## Rescale statements¶

The rescaling operation changes the execution parallelism of a Statement. This operation can only be applied to Statements in a non-terminal state such as PENDING, RUNNING, STOPPED, and FAILING.

REST APIConfluent CLI

The following example shows how to rescale a Statement via the REST API, with a PUT request to update the resource with an adjusted `spec.parallelism` value.

    curl -v -H "Content-Type: application/json" \
    -X PUT http://localhost:8080/cmf/api/v1/environments/env-1/statements/stmt-1 \
    -d @/path/to/stmt-1.json

The following example shows how to rescale a Statement using the Confluent CLI. For a full list of options, see the [/confluent-cli/current/confluent flink statement rescale <command-reference/flink/statement/confluent_flink_statement_rescale.html>](/confluent-cli/current/confluent flink statement rescale <command-reference/flink/statement/confluent_flink_statement_rescale.html>) reference.

    confluent --environment env-1 flink statement rescale stmt-1 --parallelism 2

## Stop statements¶

A running statement can be stopped to pause it. While it is stopped, it is not consuming any Kubernetes resources. The stop operation can only be applied to Statements in a non-terminal state such as `PENDING`, `RUNNING`, and `FAILING`. When a running statement is stopped, Flink takes a savepoint to be able to later resume the statement without any data loss.

REST APIConfluent CLI

To stop a Statement with the REST API, use a PUT request to update the resource with a `spec.stopped` value of `true`.

    curl -v -H "Content-Type: application/json" \
    -X PUT http://localhost:8080/cmf/api/v1/environments/env-1/statements/stmt-1 \
    -d @/path/to/stmt-1.json

You can use the `stop` option with the|confluent-cli| to stop a statement:

    confluent --environment env-1 flink statement stop stmt-1

## Resume statements¶

A stopped statement can be resumed. If the statement was running before, the resume operation uses the savepoint that was taken during the stop operation to repopulate the Statement’s internal state such that the statement continues processing without data loss. The resume operation can only be applied to Statements in the `STOPPED` state.

REST APIConfluent CLI

To resume a Statement with the REST API, use a PUT request to update the resource with a `spec.stopped` value of `false`.

    curl -v -H "Content-Type: application/json" \
    -X PUT http://localhost:8080/cmf/api/v1/environments/env-1/statements/stmt-1 \
    -d @/path/to/stmt-1.json

You can use the `resume` option with the Confluent CLI to resume a statement:

    confluent --environment env-1 flink statement resume stmt-1

## List exceptions¶

Like all Flink applications, SQL statements can fail. Failures are categorized into two types:

**Compilation failures** : These are immediately reported by CMF in the status field of the response to a Statement creation request. The phase field will be set to `FAILED`, and the detail field will contain the error message.

**Execution failures** :

  * For statements that query metadata and are directly executed by CMF, failures are reported in the same manner as compilation failures.
  * For `SELECT` and `INSERT INTO` statements that are executed on a Flink cluster, CMF stores the exceptions of the ten most recent execution failures. These can be retrieved from a dedicated REST endpoint or using a Confluent CLI command.

REST APIConfluent CLI

The following GET REST request fetches the execution exceptions of Statement `stmt-1`.

    curl -v -H "Content-Type: application/json" \
    -X GET http://localhost:8080/cmf/api/v1/environments/env-1/statements/stmt-1/exceptions

The following CLI command fetches the statement exceptions of Statement `stmt-1`.

    confluent --environment env-1 flink statement exception list stmt-1
