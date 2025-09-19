---
document_id: flink_jobs_sql-statements_create-statements_chunk_2
source_file: flink_jobs_sql-statements_create-statements.md
source_url: https://docs.confluent.io/platform/current/flink/jobs/sql-statements/create-statements.html
title: Create Statements with Confluent Manager for Apache Flink
chunk_index: 2
total_chunks: 2
---

"hashmap", "execution.checkpointing.interval": "60 s" }

## Create statement response¶

When CMF receives a request to create a Statement, it compiles the SQL statement. Key properties, such as the statement’s type and the result’s schema, are then saved as part of the Statement resource. If the SQL statement is incorrect and cannot be compiled, an error message is recorded instead.

CMF’s execution method varies by statement type: some statements are executed immediately, while others trigger the deployment of a Flink cluster on Kubernetes for execution. The result of an immediate execution is also saved within the Statement resource. The resource generated from the example Statement could appear as follows:

    {
      "apiVersion": "cmf.confluent.io/v1",
      "kind": "Statement",
      "metadata": {
        "creationTimestamp": "2025-07-24T16:43:47.036Z",
        "name": "stmt-1",
        "uid": "a827600e-fca9-4fd7-a047-2728f263269d",
        "updateTimestamp": "2025-07-24T16:43:47.036Z"
      },
      "spec": {
        "computePoolName": "pool",
        "flinkConfiguration": {
          "state.backend.type": "hashmap",
          "execution.checkpointing.interval": "60 s"
        },
        "parallelism": 4,
        "properties": {
          "sql.current-catalog": "examples",
          "sql.current-database": "marketplace"
        },
        "statement": "SELECT url FROM clicks WHERE url like '%a%';",
        "stopped": false
      },
      "status": {
        "detail": "Statement execution in progress.",
        "phase": "RUNNING",
        "traits": {
          "isAppendOnly": true,
          "isBounded": false,
          "schema": {
            "columns": [
              {
                "name": "url",
                "type": {
                  "length": 2147483647,
                  "nullable": false,
                  "type": "VARCHAR"
                }
              }
            ]
          },
          "sqlKind": "SELECT"
        }
      }
    }
