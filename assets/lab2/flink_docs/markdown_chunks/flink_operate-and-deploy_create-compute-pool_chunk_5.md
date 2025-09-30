---
document_id: flink_operate-and-deploy_create-compute-pool_chunk_5
source_file: flink_operate-and-deploy_create-compute-pool.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/create-compute-pool.html
title: Manage Flink Compute Pools in Confluent Cloud for Apache Flink
chunk_index: 5
total_chunks: 7
---

information, see [confluent_flink_compute_pool data source](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/data-sources/confluent_flink_compute_pool).

## List compute pools¶

Confluent Cloud ConsoleConfluent CLIREST APITerraform

  1. In the navigation menu, click **Environments** , and click the tile for the environment where you use Flink SQL.

  2. In the environment details page, click **Flink**.

  3. In the **Flink** page, click **Compute pools** , if it’s not selected already.

The available compute pools are listed as tiles, with details like **Max CFUs** and the cloud provider and region.

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

List the compute pools in your environment by sending a GET request to the [Compute Pools endpoint](/cloud/current/api.html#tag/Compute-Pools-\(fcpmv2\)/operation/listFcpmV2ComputePools).

* This request uses your Cloud API key instead of the Flink API key.

Listing the compute pools in your environment requires the following inputs:

    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"

Run the following command to list the compute pools in your environment.

    curl --request GET \
         --url "https://confluent.cloud/api/fcpm/v2/compute-pools?environment=${ENV_ID}&page_size=100" \
         --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}" \
         | jq -r '.data[] | .spec.display_name, {id}'

Your output should resemble:

    compute_pool_0
    {
      "id": "lfcp-j123kl"
    }
    compute_pool_2
    {
      "id": "lfcp-abc1de"
    }
    my-lfcp-01
    {
      "id": "lfcp-l2mn3o"
    }
    ...

Find your compute pool in the list and save its ID in an environment variable.

    export COMPUTE_POOL_ID="<your-compute-pool-id>"

To list all compute pools using the Confluent Terraform provider, use the [confluent_flink_compute_pool](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/data-sources/confluent_flink_compute_pool) data source and the `data` argument.

    provider "confluent" {
      cloud_api_key    = var.confluent_cloud_api_key
      cloud_api_secret = var.confluent_cloud_api_secret
    }

    data "confluent_flink_compute_pools" "all_pools" {
      environment_id = "<your-environment-id>"
    }

    output "compute_pools" {
      value = data.confluent_flink_compute_pools.all_pools.compute_pools
    }

Run the `terraform apply` or `terraform output` command. The `compute_pools` output contains a list of all compute pools in your environment.

To filter the compute pools by a specific attribute, region, availability, or name, use the `filter` argument within the `data` block.

    data "confluent_flink_compute_pools" "pools_in_us_east" {
      environment_id = "<your-environment-id>"
      filter = "region == '<region-id>'"
    }

For more information, see [confluent_flink_compute_pool](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/data-sources/confluent_flink_compute_pool).
