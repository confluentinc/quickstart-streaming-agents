---
document_id: flink_jobs_sql-statements_manage-statements_chunk_2
source_file: flink_jobs_sql-statements_manage-statements.md
source_url: https://docs.confluent.io/platform/current/flink/jobs/sql-statements/manage-statements.html
title: Manage Statements with Confluent Manager for Apache Flink
chunk_index: 2
total_chunks: 2
---

flink statement exception list stmt-1

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
