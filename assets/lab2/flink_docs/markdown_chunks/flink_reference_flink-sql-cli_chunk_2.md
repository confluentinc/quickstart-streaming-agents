---
document_id: flink_reference_flink-sql-cli_chunk_2
source_file: flink_reference_flink-sql-cli.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/flink-sql-cli.html
title: Confluent CLI commands with Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 6
---

shell](../get-started/quick-start-shell.html#flink-sql-quick-start-shell) * [Confluent Terraform Provider](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs)

## Manage statements¶

Using the Confluent CLI, you can perform these actions:

  * Submit a statement
  * List statements
  * Describe a statement
  * List exceptions from a statement
  * Delete a statement
  * Update a statement

Managing Flink SQL statements may require the following inputs, depending on the command:

    export STATEMENT_NAME="<statement-name>" # example: "user-filter"
    export COMPUTE_POOL_ID="<compute-pool-id>" # example: "lfcp-8m03rm"
    export CLUSTER_ID="<kafka-cluster-id>" # example: "lkc-a1b2c3"
    export PRINCIPAL_ID="<principal-id>" # example: "sa-23kgz4" for a service account, or "u-aq1dr2" for a user account
    export SQL_CODE="<sql-statement-text>" # example: "SELECT * FROM USERS;"

For the complete CLI reference, see [confluent flink statement](https://docs.confluent.io/confluent-cli/current/command-reference/flink/statement/index.html).

### Submit a statement¶

The [confluent flink statement create](https://docs.confluent.io/confluent-cli/current/command-reference/flink/statement/confluent_flink_statement_create.html) command submits a statement in your compute pool.

Run the following command to submit a Flink SQL statement in the current compute pool with your user account.

    confluent flink statement create --sql "${SQL_CODE}"

Your output should resemble:

    +---------------+------------------------------------------------------------+
    | Creation Date | 2024-02-28 21:08:08.9749 +0000                             |
    |               | UTC                                                        |
    | Name          | cli-2024-02-28-130806-78dd77b5-16a9-40ab-9786-db95b9895eaa |
    | Statement     | Select 1;                                                  |
    | Compute Pool  | lfcp-8m09g0                                                |
    | Status        | PENDING                                                    |
    +---------------+------------------------------------------------------------+

For long-running statements, Confluent recommends submitting statements with a service account instead of your user account.

The following command submits a Flink SQL statement for the specified principal in the specified compute pool and Flink database (Kafka cluster).

    confluent flink statement create ${STATEMENT_NAME} \
      --service-account ${PRINCIPAL_ID} \
      --sql "${SQL_CODE}" \
      --compute-pool ${COMPUTE_POOL_ID} \
      --database ${CLUSTER_ID}

### List statements¶

Run the [confluent flink statement list](https://docs.confluent.io/confluent-cli/current/command-reference/flink/statement/confluent_flink_statement_list.html) command to list all of the non-deleted statements in your environment.

    confluent flink statement list

Your output should resemble:

              Creation Date         |         Name         |           Statement            | Compute Pool |  Status   |         Status Detail
    --------------------------------+----------------------+--------------------------------+--------------+-----------+---------------------------------
      2023-07-08 21:04:06 +0000 UTC | 4b1d3494-f0f7-460d-9 | INSERT INTO copytopic          | lfcp-r2j1x9  | RUNNING   |
                                    |                      | SELECT symbol,price from       |              |           |
                                    |                      | topic_datagen;                 |              |           |
      2023-07-08 21:07:04 +0000 UTC | 6c43b973-b3c6-4be8-9 | INSERT INTO copytopic          | lfcp-r2j1x9  | RUNNING   |
                                    |                      | SELECT symbol,price from       |              |           |
                                    |                      | topic_datagen;                 |              |           |
    ...

To list only the statements that you’ve created, get the context for your current Confluent Cloud login session and provide the context with the `context` option.

    confluent context list

Your output should resemble:

      Current |                          Name                          |    Platform     |            Credential
    ----------+--------------------------------------------------------+-----------------+------------------------------------
      *       |   login-<your-email-address>-https://confluent.cloud   | confluent.cloud | username-<your-email-address>

For convenience, save the context in an environment variable:

    export MY_CONTEXT="login-<your-email-address>-https://confluent.cloud"

Run the [confluent flink statement list](https://docs.confluent.io/confluent-cli/current/command-reference/flink/statement/confluent_flink_statement_list.html) command with your context.
