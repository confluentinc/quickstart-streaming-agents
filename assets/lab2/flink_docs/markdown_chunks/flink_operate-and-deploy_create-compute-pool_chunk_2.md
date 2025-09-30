---
document_id: flink_operate-and-deploy_create-compute-pool_chunk_2
source_file: flink_operate-and-deploy_create-compute-pool.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/create-compute-pool.html
title: Manage Flink Compute Pools in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 7
---

API](flink-rest-api.html#flink-rest-api-manage-compute-pools) * [Confluent Terraform provider](../../clusters/terraform-provider.html#confluent-terraform-provider-resources-flink)

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
