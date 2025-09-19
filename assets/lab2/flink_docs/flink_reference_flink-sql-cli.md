---
source_url: https://docs.confluent.io/cloud/current/flink/reference/flink-sql-cli.html
title: Confluent CLI commands with Confluent Cloud for Apache Flink
hierarchy: ['reference', 'flink-sql-cli.html']
scraped_date: 2025-09-05T13:47:20.069462
---

# Confluent CLI commands with Confluent Cloud for Apache Flink¶

Manage Flink SQL statements and compute pools in Confluent Cloud for Apache Flink® by using the [confluent flink ](https://docs.confluent.io/confluent-cli/current/command-reference/flink/index.html) commands in the Confluent CLI. To see the available commands, use the `--help` option.

    confluent flink statement --help
    confluent flink compute-pool --help
    confluent flink region --help

Use the Confluent CLI to manage these features:

  * Statements
  * Compute pools
  * Regions

For the complete CLI reference, see [confluent flink statement](https://docs.confluent.io/confluent-cli/current/command-reference/flink/index.html).

In addition to the CLI, you can manage Flink statements and compute pools by using these Confluent tools:

  * [Flink SQL REST API](../operate-and-deploy/flink-rest-api.html#flink-rest-api)
  * [Cloud Console](../get-started/quick-start-cloud-console.html#flink-sql-quick-start-run-sql-statement)
  * [SQL shell](../get-started/quick-start-shell.html#flink-sql-quick-start-shell)
  * [Confluent Terraform Provider](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs)

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

## Manage regions¶

Using the Confluent CLI, you can perform these actions:

  * List available regions
  * Set the current region

Managing Flink SQL regions may require the following inputs, depending on the command:

    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"

For the complete CLI reference, see [confluent flink region](https://docs.confluent.io/confluent-cli/current/command-reference/flink/region/index.html).

### List available regions¶

Run the [confluent flink region list](https://docs.confluent.io/confluent-cli/current/command-reference/flink/region/confluent_flink_region_list.html) to see all available regions where you can run Flink statements.

    confluent flink region list

Your output should resemble:

      Current |             Name              | Cloud |        Region
    ----------+-------------------------------+-------+-----------------------
              | Belgium (europe-west1)        | gcp   | europe-west1
              | Frankfurt (eu-central-1)      | aws   | eu-central-1
              | Frankfurt (europe-west3)      | gcp   | europe-west3
              | Iowa (us-central1)            | gcp   | us-central1
              | Ireland (eu-west-1)           | aws   | eu-west-1
              | Las Vegas (us-west4)          | gcp   | us-west4
              | London (eu-west-2)            | aws   | eu-west-2
      *       | N. Virginia (us-east-1)       | aws   | us-east-1
              | N. Virginia (us-east4)        | gcp   | us-east4
              | Netherlands (westeurope)      | azure | westeurope
              | Ohio (us-east-2)              | aws   | us-east-2
              | Oregon (us-west-2)            | aws   | us-west-2
              | S. Carolina (us-east1)        | gcp   | us-east1
              | Singapore (ap-southeast-1)    | aws   | ap-southeast-1
              | Singapore (asia-southeast1)   | gcp   | asia-southeast1
              | Singapore (southeastasia)     | azure | southeastasia
              | Sydney (ap-southeast-2)       | aws   | ap-southeast-2
              | Sydney (australia-southeast1) | gcp   | australia-southeast1
              | Virginia (eastus)             | azure | eastus
              | Virginia (eastus2)            | azure | eastus2
              | Washington (westus2)          | azure | westus2

Run the following command to filter the list of available regions by cloud provider.

    confluent flink region list --cloud ${CLOUD_PROVIDER}

Your output should resemble:

      Current |            Name            | Cloud |     Region
    ----------+----------------------------+-------+-----------------
              | Frankfurt (eu-central-1)   | aws   | eu-central-1
              | Ireland (eu-west-1)        | aws   | eu-west-1
              | London (eu-west-2)         | aws   | eu-west-2
      *       | N. Virginia (us-east-1)    | aws   | us-east-1
              | Ohio (us-east-2)           | aws   | us-east-2
              | Oregon (us-west-2)         | aws   | us-west-2
              | Singapore (ap-southeast-1) | aws   | ap-southeast-1
              | Sydney (ap-southeast-2)    | aws   | ap-southeast-2

### Set the current region¶

Run the [confluent flink region use](https://docs.confluent.io/confluent-cli/current/command-reference/flink/region/confluent_flink_region_use.html) to set the current region where subsequent Flink statements run. You must have a compute pool in the region to run statements.

    confluent flink region use --cloud ${CLOUD_PROVIDER} --region ${CLOUD_REGION}

For `CLOUD_PROVIDER=aws` and `CLOUD_REGION=us-east-2`, your output should resemble:

    Using Flink region "Ohio (us-east-2)".

