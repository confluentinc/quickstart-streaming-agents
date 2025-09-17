---
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/create-compute-pool.html
title: Manage Flink Compute Pools in Confluent Cloud for Apache Flink
hierarchy: ['operate-and-deploy', 'create-compute-pool.html']
scraped_date: 2025-09-05T13:46:44.755485
---

# Manage Compute Pools in Confluent Cloud for Apache Flink¶

A [compute pool](../concepts/compute-pools.html#flink-sql-compute-pools) represents the compute resources that are used to run your [SQL statements](../concepts/statements.html#flink-sql-statements). The resources provided by a compute pool are shared among all statements that use it. It enables you to limit or guarantee resources as your use cases require. A compute pool is bound to a region. There is no cost for creating compute pools.

To create a compute pool, you need the OrganizationAdmin, EnvironmentAdmin, or FlinkAdmin RBAC role.

In addition to the Cloud Console, Confluent provides these tools for creating and managing Flink compute pools:

  * [Confluent CLI](../reference/flink-sql-cli.html#flink-cli-manage-compute-pools)
  * [Confluent Cloud REST API](flink-rest-api.html#flink-rest-api-manage-compute-pools)
  * [Confluent Terraform provider](../../clusters/terraform-provider.html#confluent-terraform-provider-resources-flink)

## Create a compute pool¶

Confluent Cloud ConsoleConfluent CLIREST APITerraform

  1. In the navigation menu, click **Environments** , and click the tile for the environment where you want to use Flink SQL.

  2. In the environment details page, click **Flink**.

  3. In the **Flink** page, click **Compute pools** , if it’s not selected already.

  4. Click **Create compute pool** to open the **Create compute pool** page.

  5. In the **Region** dropdown, select the region that hosts the data you want to process with SQL, or use any region if you just want to try out Flink using sample data. Click **Continue**.

  6. In the **Pool name** textbox, enter “my-compute-pool”.

  7. In the **Max CFUs** dropdown, select **10**. For more information, see [CFUs](../concepts/flink-billing.html#flink-sql-cfus).

Note

You can increase the Max CFUs value later, but decreasing Max CFUs is not supported.

  8. Click **Continue** , and on the **Review and create** page, click **Finish**.

A tile for your compute pool appears on the **Flink** page. It shows the pool in the **Provisioning** state. It may take a few minutes for the pool to enter the **Running** state.

Tip

The tile for your compute pool provides the Confluent CLI command for using the pool from the CLI. Learn more about the CLI in the [Flink SQL Shell Quick Start](../get-started/quick-start-shell.html#flink-sql-quick-start-shell).

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

Create a compute pool in your environment by sending a POST request to the [Compute Pools endpoint](/cloud/current/api.html#tag/Compute-Pools-\(fcpmv2\)/operation/createFcpmV2ComputePool).

  * This request uses your Cloud API key instead of the Flink API key.

Creating a compute pool requires the following inputs:

    export COMPUTE_POOL_NAME="<compute-pool-name>" # human readable name, for example: "my-compute-pool"
    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"
    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"
    export MAX_CFU="<max-cfu>" # example: 5
    export JSON_DATA="<payload-string>"

The following JSON shows an example payload. The `network` key is optional.

    {
      "spec": {
        "display_name": "${COMPUTE_POOL_NAME}",
        "cloud": "${CLOUD_PROVIDER}",
        "region": "${CLOUD_REGION}",
        "max_cfu": ${MAX_CFU},
        "environment": {
          "id": "${ENV_ID}"
        },
        "network": {
          "id": "n-00000",
          "environment": "string"
        }
      }
    }

Quotation mark characters in the JSON string must be escaped, so the payload string to send resembles the following:

    export JSON_DATA="{
      \"spec\": {
        \"display_name\": \"${COMPUTE_POOL_NAME}\",
        \"cloud\": \"${CLOUD_PROVIDER}\",
        \"region\": \"${CLOUD_REGION}\",
        \"max_cfu\": ${MAX_CFU},
        \"environment\": {
          \"id\": \"${ENV_ID}\"
        }
      }
    }"

The following command sends a POST request to create a compute pool.

    curl --request POST \
      --url https://api.confluent.cloud/fcpm/v2/compute-pools \
      --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}" \
      --header 'content-type: application/json' \
      --data "${JSON_DATA}"

Your output should resemble:

Response from a request to create a compute pool 

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
            "phase": "PROVISIONING"
        }
    }

To create a compute pool by using the Confluent Terraform provider, use the [confluent_flink_compute_pool](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/resources/confluent_flink_compute_pool) resource.

  1. Configure your Terraform file. Provide your Confluent Cloud API key and secret.
         
         terraform {
           required_providers {
             confluent = {
               source = "confluentinc/confluent"
               version = "2.38.0"
             }
           }
         }
         
         provider "confluent" {
           cloud_api_key    = var.confluent_cloud_api_key    # optionally use CONFLUENT_CLOUD_API_KEY env var
           cloud_api_secret = var.confluent_cloud_api_secret # optionally use CONFLUENT_CLOUD_API_SECRET env var
         }

  2. Define the environment where the compute pool will be created.
         
         resource "confluent_environment" "development" {
           display_name = "Development"
           lifecycle {
             prevent_destroy = true
           }
         }

  3. Define the `confluent_flink_compute_pool` resource with the required parameters, like `display_name`, `cloud`, `region`, `max_cfu`, and the environment ID.
         
         resource "confluent_flink_compute_pool" "main" {
           display_name = "standard_compute_pool"
           cloud        = "AWS"
           region       = "us-east-1"
           max_cfu      = 5
         
           environment {
             id = confluent_environment.development.id
           }
         }

  4. Run the `terraform apply` command to create the resources.
         
         terraform apply

  5. If you need to import an existing compute pool, use the `terraform import` command.
         
         export CONFLUENT_CLOUD_API_KEY="<cloud_api_key>"
         export CONFLUENT_CLOUD_API_SECRET="<cloud_api_secret>"
         terraform import confluent_flink_compute_pool.main <your-environment-id>/<compute-pool-id>

For more information, see [confluent_flink_compute_pool resource](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/resources/confluent_flink_compute_pool).

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

## Update a compute pool¶

You can update the name of the compute pool, its environment, and the MAX_CFUs setting. You can increase the Max CFUs value, but decreasing Max CFUs is not supported.

Confluent Cloud ConsoleConfluent CLIREST APITerraform

  1. In the navigation menu, click **Environments** , and click the tile for the environment where you use Flink SQL.

  2. In the environment details page, click **Flink**.

  3. In the **Flink** page, click **Compute pools** , if it’s not selected already.

  4. In the listed compute pools, find the one you want to update, and click the options icon (**⋮**).

  5. In the context menu, click either **Edit display name** or **Edit max CFUs** and follow the instructions in the dialog.

  6. Click the tile for your compute pool to open the details page.

In the details page, you can update the compute pool’s description or add metadata tags. Also, you can manage Flink SQL statements that are associated with the compute pool.

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

Update a compute pool in your environment by sending a PATCH request to the [Compute Pools endpoint](/cloud/current/api.html#tag/Compute-Pools-\(fcpmv2\)/operation/updateFcpmV2ComputePool).

  * This request uses your Cloud API key instead of the Flink API key.

Updating a compute pool requires the following inputs:

    export COMPUTE_POOL_ID="<compute-pool-id>" # example: "lfcp-8m03rm"
    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"
    export MAX_CFU="<max-cfu>" # example: 5
    export JSON_DATA="<payload-string>"

The following JSON shows an example payload. The `network` key is optional.

    {
      "spec": {
        "display_name": "${COMPUTE_POOL_NAME}",
        "max_cfu": ${MAX_CFU},
        "environment": {
          "id": "${ENV_ID}"
        }
      }
    }

Quotation mark characters in the JSON string must be escaped, so the payload string to send resembles the following:

    export JSON_DATA="{
      \"spec\": {
        \"display_name\": \"${COMPUTE_POOL_NAME}\",
        \"max_cfu\": ${MAX_CFU},
        \"environment\": {
          \"id\": \"${ENV_ID}\"
        }
      }
    }"

Run the following command to update the compute pool specified in the COMPUTE_POOL_ID environment variable.

    curl --request PATCH \
      --url "https://api.confluent.cloud/fcpm/v2/compute-pools/${COMPUTE_POOL_ID}" \
      --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}" \
      --header 'content-type: application/json' \
      --data "${JSON_DATA}"

To update a compute pool by using the Confluent Terraform provider, use the [confluent_flink_compute_pool](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/resources/confluent_flink_compute_pool) resource.

  1. Find the definition for the compute pool resource in your Terraform configuration, for example:
         
         resource "confluent_flink_compute_pool" "example" {
           cloud  = "AWS"
           region = "us-west-2"
           max_cfu = 10
           # other required parameters
         }

  2. Modify the attributes of the `confluent_flink_compute_pool` resource in the Terraform configuration file. The following example updates the `max_cfu` attribute.
         
         resource "confluent_flink_compute_pool" "example" {
           cloud  = "AWS"
           region = "us-west-2"
           max_cfu = 20 # Updated value
           # other required parameters
         }

  3. Run the `terraform apply` command to update the compute pool with the new configuration.
         
         terraform apply

For more information, see [confluent_flink_compute_pool](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/resources/confluent_flink_compute_pool).

## Delete a compute pool¶

Confluent Cloud ConsoleConfluent CLIREST APITerraform

  1. In the navigation menu, click **Environments** , and click the tile for the environment where you want to use Flink SQL.
  2. In the environment details page, click **Flink**.
  3. In the **Flink** page, click **Compute pools** , if it’s not selected already.
  4. In the listed compute pools, find the one you want to delete, and click the options icon (**⋮**).
  5. In the context menu, click **Delete compute pool** , and in the dialog, enter the compute pool name to confirm deletion.

Run the [confluent flink compute-pool delete](https://docs.confluent.io/confluent-cli/current/command-reference/flink/compute-pool/confluent_flink_compute-pool_delete.html) command to delete a compute pool.

Run the following command to delete a compute pool in the specified environment. The optional `--force` flag skips the confirmation prompt.

    confluent flink compute-pool delete ${COMPUTE_POOL_ID} \
      --environment ${ENV_ID}
      --force

Your output should resemble:

    Deleted Flink compute pool "lfcp-xxd6og".

Delete a compute pool in your environment by sending a DELETE request to the [Compute Pools endpoint](/cloud/current/api.html#tag/Compute-Pools-\(fcpmv2\)/operation/deleteFcpmV2ComputePool).

  * This request uses your Cloud API key instead of the Flink API key.

Deleting a compute pool requires the following inputs:

    export COMPUTE_POOL_ID="<compute-pool-id>" # example: "lfcp-8m03rm"
    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"

Run the following command to delete the compute pool specified in the COMPUTE_POOL_ID environment variable.

    curl --request DELETE \
      --url "https://api.confluent.cloud/fcpm/v2/compute-pools/${COMPUTE_POOL_ID}?environment=${ENV_ID}" \
      --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}"

To delete a compute pool by using the Confluent Terraform provider, use the [confluent_flink_compute_pool](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/resources/confluent_flink_compute_pool) resource.

  1. Define the compute pool resource in your Terraform configuration file, for example:
         
         resource "confluent_flink_compute_pool" "main" {
           display_name = "standard_compute_pool"
           cloud        = "AWS"
           region       = "us-east-1"
           max_cfu      = 5
           environment {
             id = "<your-environment-id>"
           }
         }

  2. To avoid accidental deletions, review the plan before applying the `destroy` command.
         
         terraform plan -destroy -target=confluent_flink_compute_pool.main

  3. To delete the compute pool, run the following command to target the specific resource. This command deletes only the compute pool and not other resources.
         
         terraform apply -destroy -target=confluent_flink_compute_pool.main

To remove all resources defined in your Terraform configuration file, including the compute pool, run the `terraform destroy` command.
         
         terraform destroy

For more information, see [confluent_flink_compute_pool](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/resources/confluent_flink_compute_pool).

## Related content¶

  * [Flink Compute Pools](../concepts/compute-pools.html#flink-sql-compute-pools)
  * [Billing on Confluent Cloud for Apache Flink](../concepts/flink-billing.html#flink-sql-billing)

Note

This website includes content developed at the [Apache Software Foundation](https://www.apache.org/) under the terms of the [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0.html).
