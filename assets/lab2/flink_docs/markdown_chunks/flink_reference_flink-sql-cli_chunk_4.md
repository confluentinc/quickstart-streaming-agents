---
document_id: flink_reference_flink-sql-cli_chunk_4
source_file: flink_reference_flink-sql-cli.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/flink-sql-cli.html
title: Confluent CLI commands with Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 6
---

flink statement update ${STATEMENT_NAME} --stopped=false

## Manage compute pools¶

Using the Confluent CLI, you can perform these actions:

  * Create a compute pool
  * Describe a compute pool
  * List compute pools
  * Update a compute pool
  * Set the current compute pool
  * Unset the current compute pool
  * Delete a compute pool

You must be authorized to create, update, delete (`FlinkAdmin`) or use (`FlinkDeveloper`) a compute pool. For more information, see [Grant Role-Based Access in Confluent Cloud for Apache Flink](../operate-and-deploy/flink-rbac.html#flink-rbac).

Managing compute pools may require the following inputs, depending on the command:

    export COMPUTE_POOL_NAME=<compute-pool-name> # human-readable name, for example, "my-compute-pool"
    export COMPUTE_POOL_ID="<compute-pool-id>" # example: "lfcp-8m03rm"
    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"
    export MAX_CFU="<max-cfu>" # example: 5

For the complete CLI reference, see [confluent flink compute-pool](https://docs.confluent.io/confluent-cli/current/command-reference/flink/compute-pool/index.html).

### Create a compute pool¶

Run the [confluent flink compute-pool create](https://docs.confluent.io/confluent-cli/current/command-reference/flink/compute-pool/confluent_flink_compute-pool_create.html) command to create a compute pool.

Creating a compute pool requires the following inputs:

    export COMPUTE_POOL_NAME=<compute-pool-name> # human-readable name, for example, "my-compute-pool"
    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"
    export MAX_CFU="<max-cfu>" # example: 5

Run the following command to create a compute pool in the specified cloud provider and environment.

    confluent flink compute-pool create ${COMPUTE_POOL_NAME} \
      --cloud ${CLOUD_PROVIDER} \
      --region ${CLOUD_REGION} \
      --max-cfu ${MAX_CFU} \
      --environment ${ENV_ID}

Your output should resemble:

    +-------------+-----------------+
    | Current     | false           |
    | ID          | lfcp-xxd6og     |
    | Name        | my-compute-pool |
    | Environment | env-z3y2x1      |
    | Current CFU | 0               |
    | Max CFU     | 5               |
    | Cloud       | AWS             |
    | Region      | us-east-1       |
    | Status      | PROVISIONING    |
    +-------------+-----------------+

### Describe a compute pool¶

Run the [confluent flink compute-pool describe](https://docs.confluent.io/confluent-cli/current/command-reference/flink/compute-pool/confluent_flink_compute-pool_describe.html) command to get details about a compute pool.

Describing a compute pool requires the following inputs:

    export COMPUTE_POOL_ID="<compute-pool-id>" # example: "lfcp-8m03rm"
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"

Run the following command to get details about a compute pool in the specified environment.

    confluent flink compute-pool describe ${COMPUTE_POOL_ID} \
      --environment ${ENV_ID}

Your output should resemble:

    +-------------+-----------------+
    | Current     | false           |
    | ID          | lfcp-xxd6og     |
    | Name        | my-compute-pool |
    | Environment | env-z3y2x1      |
    | Current CFU | 0               |
    | Max CFU     | 5               |
    | Cloud       | AWS             |
    | Region      | us-east-1       |
    | Status      | PROVISIONED     |
    +-------------+-----------------+

### List compute pools¶

Run the [confluent flink compute-pool list](https://docs.confluent.io/confluent-cli/current/command-reference/flink/compute-pool/confluent_flink_compute-pool_list.html) command to compute pools in the specified environment.

Listing compute pools may require the following inputs, depending on the command:

    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"

Run the following command to get details about a compute pool in the specified environment.

    confluent flink compute-pool list --environment ${ENV_ID}

Your output should resemble:

      Current |     ID      |           Name            | Environment | Current CFU | Max CFU | Cloud |  Region   |   Status
    ----------+-------------+---------------------------+-------------+-------------+---------+-------+-----------+--------------
      *       | lfcp-xxd6og | my-compute-pool           | env-z3y2x1  |           0 |       5 | AWS   | us-east-1 | PROVISIONED
              | lfcp-8m03rm | test-blue-compute-pool    | env-z3q9rd  |           0 |      10 | AWS   | us-east-1 | PROVISIONED
    ...

### Update a compute pool¶
