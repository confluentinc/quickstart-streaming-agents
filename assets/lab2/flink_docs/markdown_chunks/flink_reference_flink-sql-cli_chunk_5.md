---
document_id: flink_reference_flink-sql-cli_chunk_5
source_file: flink_reference_flink-sql-cli.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/flink-sql-cli.html
title: Confluent CLI commands with Confluent Cloud for Apache Flink
chunk_index: 5
total_chunks: 6
---

Run the [confluent flink compute-pool update](https://docs.confluent.io/confluent-cli/current/command-reference/flink/compute-pool/confluent_flink_compute-pool_update.html) command to update a compute pool.

Updating a compute pool may require the following inputs, depending on the command:

    export COMPUTE_POOL_NAME=<compute-pool-name> # human-readable name, for example, "my-compute-pool"
    export COMPUTE_POOL_ID="<compute-pool-id>" # example: "lfcp-8m03rm"
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"
    export MAX_CFU="<max-cfu>" # example: 5

Run the following command to update a compute pool in the specified environment.

    confluent flink compute-pool update ${COMPUTE_POOL_ID} \
      --environment ${ENV_ID} \
      --name ${COMPUTE_POOL_NAME} \
      --max-cfu ${MAX_CFU}

Your output should resemble:

    +-------------+----------------------+
    | Current     | false                |
    | ID          | lfcp-xxd6og          |
    | Name        | renamed-compute-pool |
    | Environment | env-z3y2x1           |
    | Current CFU | 0                    |
    | Max CFU     | 10                   |
    | Cloud       | AWS                  |
    | Region      | us-east-1            |
    | Status      | PROVISIONED          |
    +-------------+----------------------+

### Set the current compute pool¶

Run the [confluent flink compute-pool use](https://docs.confluent.io/confluent-cli/current/command-reference/flink/compute-pool/confluent_flink_compute-pool_use.html) command to use a compute pool in subsequent commands.

Setting a compute pool requires the following inputs:

    export COMPUTE_POOL_ID="<compute-pool-id>" # example: "lfcp-8m03rm"
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"

Run the following commands to set the current compute pool in the specified environment. First, you must run the `confluent environment use` command to set the current environment.

    confluent environment use ${ENV_ID} && \
    confluent flink compute-pool use ${COMPUTE_POOL_ID}

Your output should resemble:

    Using environment "env-z3y2x1".
    Using Flink compute pool "lfcp-xxd6og".

### Unset the current compute pool¶

Run the [confluent flink compute-pool unset](https://docs.confluent.io/confluent-cli/current/command-reference/flink/compute-pool/confluent_flink_compute-pool_unset.html) command to unset the current compute pool.

Run the following command to unset the current compute pool.

    confluent flink compute-pool unset

Your output should resemble:

    Unset Flink compute pool "lfcp-xxd6og".

### Delete a compute pool¶

Run the [confluent flink compute-pool delete](https://docs.confluent.io/confluent-cli/current/command-reference/flink/compute-pool/confluent_flink_compute-pool_delete.html) command to delete a compute pool.

Run the following command to delete a compute pool in the specified environment. The optional `--force` flag skips the confirmation prompt.

    confluent flink compute-pool delete ${COMPUTE_POOL_ID} \
      --environment ${ENV_ID}
      --force

Your output should resemble:

    Deleted Flink compute pool "lfcp-xxd6og".
