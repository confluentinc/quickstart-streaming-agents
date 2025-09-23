---
document_id: flink_operate-and-deploy_create-compute-pool_chunk_4
source_file: flink_operate-and-deploy_create-compute-pool.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/create-compute-pool.html
title: Manage Flink Compute Pools in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 7
---

more information, see [confluent_flink_compute_pool resource](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/resources/confluent_flink_compute_pool).

## View details for a compute pool¶

Confluent Cloud ConsoleConfluent CLIREST APITerraform

  1. In the navigation menu, click **Environments** , and click the tile for the environment where you use Flink SQL.

  2. In the environment details page, click **Flink**.

  3. In the **Flink** page, click **Compute pools** , if it’s not selected already.

The available compute pools are listed as tiles, with details like **Max CFUs** and the cloud provider and region.

  4. If the tile for your compute pool isn’t visible, start typing in the **Search pools** textbox to filter the view.

  5. Click the tile for your compute pool to open the details page, which shows information like consumption metrics and Flink SQL statements that are associated with the compute pool.

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

Get the details about a compute pool in your environment by sending a GET request to the [Compute Pools endpoint](/cloud/current/api.html#tag/Compute-Pools-\(fcpmv2\)/operation/getFcpmV2ComputePool).

* This request uses your Cloud API key instead of the Flink API key.

Getting details about a compute pool requires the following inputs:

    export COMPUTE_POOL_ID="<compute-pool-id>" # example: "lfcp-8m03rm"
    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"

Run the following command to get details about the compute pool specified in the COMPUTE_POOL_ID environment variable.

    curl --request GET \
      --url "https://api.confluent.cloud/fcpm/v2/compute-pools/${COMPUTE_POOL_ID}?environment=${ENV_ID}" \
      --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}"

Your output should resemble:

Response from a request to read a compute pool

    {
        "api_version": "fcpm/v2",
        "id": "lfcp-6g7h8i",
        "kind": "ComputePool",
        "metadata": {
            "created_at": "2024-02-27T22:44:27.18964Z",
            "resource_name": "crn://confluent.cloud/organization=b0b21724-4586-4a07-b787-d0bb5aacbf87/environment=env-z3y2x1/flink-region=aws.us-east-1/compute-pool=lfcp-6g7h8i",
            "self": "https://api.confluent.cloud/fcpm/v2/compute-pools/lfcp-6g7h8i",
            "updated_at": "2024-02-27T22:44:27.18964Z"
        },
        "spec": {
            "cloud": "AWS",
            "display_name": "my-compute-pool",
            "environment": {
                "id": "env-z3y2x1",
                "related": "https://api.confluent.cloud/fcpm/v2/compute-pools/lfcp-6g7h8i",
                "resource_name": "crn://confluent.cloud/organization=b0b21724-4586-4a07-b787-d0bb5aacbf87/environment=env-z3y2x1"
            },
            "http_endpoint": "https://flink.us-east-1.aws.confluent.cloud/sql/v1/organizations/b0b21724-4586-4a07-b787-d0bb5aacbf87/environments/env-z3y2x1",
            "max_cfu": 5,
            "region": "us-east-1"
        },
        "status": {
            "current_cfu": 0,
            "phase": "PROVISIONED"
        }
    }

To view details for a compute pool by using the Confluent Terraform provider, use the [confluent_flink_compute_pool](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/data-sources/confluent_flink_compute_pool) data source and the `data` argument.

    data "confluent_flink_compute_pool" "example_using_id" {
      id = "lfcp-abc123"
      environment {
        id = "<your-environment-id>"
      }
    }

    output "example_using_id" {
      value = data.confluent_flink_compute_pool.example_using_id
    }

    data "confluent_flink_compute_pool" "example_using_name" {
      display_name = "my_compute_pool"
      environment {
        id = "<your-environment-id>"
      }
    }

    output "example_using_name" {
      value = data.confluent_flink_compute_pool.example_using_name
    }

Run the `terraform apply` or `terraform output` command. The `example_using_id` and `example_using_name` output contains details for the compute pool with the specified ID or name.

For more information, see [confluent_flink_compute_pool data source](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/data-sources/confluent_flink_compute_pool).
