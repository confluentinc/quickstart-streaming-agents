---
source_url: https://docs.confluent.io/platform/current/flink/jobs/sql-statements/create-statements.html
title: Create Statements with Confluent Manager for Apache Flink
hierarchy: ['platform', 'jobs', 'sql-statements', 'create-statements.html']
scraped_date: 2025-09-05T13:53:41.710075
---

# Create Statements with Confluent Manager for Apache Flink¶

You can create a Statement resource using the REST API or the Confluent CLI, passing a JSON document that defines the Statement resource.

Important

The examples in this topic assume that CMF was installed with the examples catalog enabled (`cmf.sql.examples-catalog.enabled=true`).

## Statement resource definition example¶

Following is a JSON document to create a Statement resource.

    {
      "apiVersion": "cmf.confluent.io/v1",
      "kind": "Statement",
      "metadata": {
        "name": "stmt-1"
      },
      "spec": {
        "statement": "SELECT url FROM clicks WHERE url like '%a%';",
        "properties": {
          "sql.current-catalog": "examples",
          "sql.current-database": "marketplace"
        },
        "flinkConfiguration": {
          "state.backend.type": "hashmap",
          "execution.checkpointing.interval": "60 s"
        },
        "computePoolName": "pool",
        "parallelism": 4,
        "stopped": false
      }
    }

The resource spec includes the following fields:

* **statement** : The SQL statement to execute.
* **computePoolName** : the name of the ComputePool on which the statement should be executed.
* **properties** : A map of properties that provide context for the compilation of the statement. Here the current CATALOG and DATABASE are configured. If not specified, the default catalog and database are used.
* **flinkConfiguration** : A map of Flink configuration parameters. Statement configuration is first merged with the Environment’s default configuration. This combined configuration is used for statement translation and passed to the Flink job that executes the Statement. Separately, the Flink configuration of the Statement’s ComputePool initializes the JobManager and TaskManager processes; an empty configuration is used if none is specified.
* **parallelism** : the Statement’s execution parallelism. If not specified, the statement is executed with parallelism = 1.
* **stopped** : This flag determines if the job is running or stopped. If omitted, the query defaults to stopped = false.

## Create statement request¶

Given the resource definition listed in the previous section, you can create a statement either using the Confluent CLI or by calling the REST API as shown in the following examples.

REST APIConfluent CLI

For a full list of options, [REST APIs](../../clients-api/rest.html#af-rest-api).

    curl -v -H "Content-Type: application/json" \
     -X POST http://cmf:8080/cmf/api/v1/environments/env-1/statements \
     -d @/path/to/stmt-1.json

The following example creates a Statement using the Confluent CLI. For a full list of options, see the [/confluent-cli/current/confluent flink statement create <command-reference/flink/statement/confluent_flink_statement_create.html>](/confluent-cli/current/confluent flink statement create <command-reference/flink/statement/confluent_flink_statement_create.html>) reference.

    confluent --environment env-1 --compute-pool pool \
    flink statement create stmt-1 \
    --catalog examples --database marketplace \
    --parallelism 4 --flink-configuration /path/to/flink-config.json \
    --sql "SELECT url FROM clicks WHERE url like '%a%';"

The Flink configuration is passed with a JSON file:

    {
      "state.backend.type": "hashmap",
      "execution.checkpointing.interval": "60 s"
    }

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
