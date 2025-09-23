---
document_id: flink_operate-and-deploy_create-compute-pool_chunk_6
source_file: flink_operate-and-deploy_create-compute-pool.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/create-compute-pool.html
title: Manage Flink Compute Pools in Confluent Cloud for Apache Flink
chunk_index: 6
total_chunks: 7
---

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
