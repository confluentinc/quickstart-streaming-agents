---
source_url: https://docs.confluent.io/platform/current/flink/jobs/sql-statements/manage-statements.html
title: Manage Statements with Confluent Manager for Apache Flink
hierarchy: ['platform', 'jobs', 'sql-statements', 'manage-statements.html']
scraped_date: 2025-09-05T13:53:43.935002
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

## Fetch results¶

CMF executes `SELECT` statements on a Flink cluster. The executing Flink job of a `SELECT` statement buffers its results in memory. The result rows can be retrieved from CMF via a REST endpoint.

The results of a `SELECT` statement are fetched with individual requests, with each request returning a batch of result rows. Since statements can ingest unbounded data (for example from a Kafka topic), the Flink job continuously computes possibly unbounded results. If results of a `SELECT` statement are not fetched, the Flink job’s in-memory buffer fills up and it will eventually pause processing. The job will resume once results have been fetched and the result buffer has free space.

Result fetching REST requests use a `pageToken` query parameter to iterate over the batches of result rows. The first REST request does not need a `pageToken`, but all following requests do. The REST response provides a `nextPageToken` in the `metadata.annotation` field that should be used for the next request to fetch results. The `pageToken` mechanism ensures that result rows are sequentially returned. Once result rows are returned from the REST endpoint, they might be discarded. This mean that you may not be able to fetch the results again.

Note

CMF’s result fetching mechanism is designed to support the development process and exploratory queries. It should not be used in production use cases.

The following example shows the first REST result request without `pageToken` query parameter:

    curl -v -H "Content-Type: application/json" \
    -X GET http://localhost:8080/cmf/api/v1/environments/env-1/statements/stmt-1/results

Response to first result request with `nextPageToken` in the `metadata.annotations` field:

    {
        "apiVersion": "cmf.confluent.io/v1",
        "kind": "StatementResult",
        "metadata": {
            "creationTimestamp": "2025-07-29T12:36:39.862204842Z",
            "annotations": {
                "nextPageToken": "ODQ1N3w0YmYzM2FhZS1hMGRhLTQzOGQtODQ5NS03YTg0NTAyODE2YmJ8WHZlUExDd0RYajF0dFhWWlZxLURDdTRDRnFMWWtfZkV5NUlBb3h5blhVRQ"
            }
        },
        "results": {
            "data": [
                {
                    "op": 0,
                    "row": [
                        "47464f2b882507954a972df0162a148dea301138a575e90fd081f93bb37b8c1a"
                    ]
                }
            ]
        }
    }

The following example shows the second REST request with `page-token` query parameter:

    curl -v -H "Content-Type: application/json" \
    -X GET http://localhost:8084/cmf/api/v1/environments/test/statements/stmt/results\?page-token\=ODQ1N3w0YmYzM2FhZS1hMGRhLTQzOGQtODQ5NS03YTg0NTAyODE2YmJ8WHZlUExDd0RYajF0dFhWWlZxLURDdTRDRnFMWWtfZkV5NUlBb3h5blhVRQ

Note

The CLI SQL Shell automatically fetches results of SELECT queries and visualizes their results.

## Delete statements¶

You can also delete a statement using the REST API or the Confluent CLI.

REST APIConfluent CLI

The following example shows how you can delete a Statement using the REST API:

    curl -v -H "Content-Type: application/json" \
    -X DELETE http://localhost:8080/cmf/api/v1/environments/env-1/statements/stmt-1

The following example shows how you can use the Confluent CLI to delete a statement:

    confluent --environment env-1 flink statement delete stmt-1

The deletion of a statement deletes all Kubernetes resources.
