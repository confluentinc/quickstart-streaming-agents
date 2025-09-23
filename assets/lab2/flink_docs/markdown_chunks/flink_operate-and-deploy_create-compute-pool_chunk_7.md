---
document_id: flink_operate-and-deploy_create-compute-pool_chunk_7
source_file: flink_operate-and-deploy_create-compute-pool.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/create-compute-pool.html
title: Manage Flink Compute Pools in Confluent Cloud for Apache Flink
chunk_index: 7
total_chunks: 7
---

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
