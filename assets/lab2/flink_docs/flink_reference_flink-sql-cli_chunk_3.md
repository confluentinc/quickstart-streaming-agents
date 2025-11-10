---
document_id: flink_reference_flink-sql-cli_chunk_3
source_file: flink_reference_flink-sql-cli.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/flink-sql-cli.html
title: Confluent CLI commands with Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 6
---

confluent flink statement list ${MY_CONTEXT}

Your output should resemble:

              Creation Date          |                            Name                            | Statement | Compute Pool |  Status   | Status Detail
    ---------------------------------+------------------------------------------------------------+-----------+--------------+-----------+----------------
      2024-02-28 21:08:08.9749 +0000 | cli-2024-02-28-130806-78dd77b5-16a9-40ab-9786-db95b9895eaa | Select 1; | lfcp-8m09g0  | COMPLETED |
      UTC                            |                                                            |           |              |           |
    ...

To list only the statements in your compute pool, provide the compute pool ID with the `--compute-pool` option.

    confluent flink statement list --compute-pool ${COMPUTE_POOL_ID}

### Describe a statement¶

Run the [confluent flink statement describe](https://docs.confluent.io/confluent-cli/current/command-reference/flink/statement/confluent_flink_statement_describe.html) command to view the details of an existing statement.

    confluent flink statement describe ${STATEMENT_NAME}

Your output should resemble:

              Creation Date         |        Name        | Statement  | Compute Pool |  Status   | Status Detail
    --------------------------------+--------------------+------------+--------------+-----------+----------------
      2023-07-19 19:26:52 +0000 UTC | fdc6cbf5-038a-408c | show jobs; | lfcp-a1b2c3  | COMPLETED |

### List exceptions from a statement¶

Run the [confluent flink statement exception list](https://docs.confluent.io/confluent-cli/current/command-reference/flink/statement/exception/confluent_flink_statement_exception_list.html) command to get exceptions that have been thrown by a statement.

    confluent flink statement exception list ${STATEMENT_NAME}

### Delete a statement¶

Run the [confluent flink statement delete](https://docs.confluent.io/confluent-cli/current/command-reference/flink/statement/confluent_flink_statement_delete.html) command to delete an existing statement permanently.

* All of its resources, like checkpoints, are also deleted.
* Deleting a statement stops charges for its use.

    confluent flink statement delete ${STATEMENT_NAME}

Your output should resemble:

    Deleted Flink SQL statement "ac23db14-b5dc-49fb-b".

### Update a statement¶

Run the [confluent flink statement delete](https://docs.confluent.io/confluent-cli/current/command-reference/flink/statement/confluent_flink_statement_update.html) command to stop an existing statement or resume a stopped statement.

    # Request to stop a statement.
    confluent flink statement update ${STATEMENT_NAME} --stopped=true

    # Request to resume a stopped statement.
    confluent flink statement update ${STATEMENT_NAME} --stopped=false
