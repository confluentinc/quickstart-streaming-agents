---
document_id: flink_operate-and-deploy_generate-api-key-for-flink_chunk_2
source_file: flink_operate-and-deploy_generate-api-key-for-flink.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/generate-api-key-for-flink.html
title: Generate an API key for Programmatic Access to Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 3
---

an environment variable: export PRINCIPAL_ID="<service-account-id>"

## Generate an API Key¶

You can use the Confluent Cloud APIs, the Confluent Terraform Provider, the Confluent CLI, or the Cloud Console to create an API key for Flink access. For more information, see [Manage API Keys](../../security/authenticate/workload-identities/service-accounts/api-keys/manage-api-keys.html#cloud-cloud-api-keys).

Cloud ConsoleConfluent CLIConfluent Cloud APIsTerraform

You can use the Cloud Console to generate an API key for Flink access.

  1. Log in to the Confluent Cloud Console and navigate to the environment that hosts your data and compute pools.

  2. Click **Flink** and in the Flink overview page, click **API keys**.

  3. Click **Add API Key** to open the **Create API key** page.

  4. Select either the **My account** tile to create an API key for your user account or the **Service account** tile to create an API key for a service account.

For production Flink deployments, select the **Service account** option, and click either **Existing account** or **New account** to assign the service account principal.

  5. Click **Next** to open the **Resource scope** page.

  6. Select the cloud provider and region for the API key. Ensure that you choose the same provider and region where your data and compute pools are located.

  7. Click **Next** to open the **API key detail** page.

  8. Enter a name and a description for the new API key. This step is optional.

  9. Click **Create API key**. The **API key download** page opens.

  10. Click **Download API key** and save the key to a secure location on your local machine.

  11. Click **Complete**.

You can use the Confluent CLI to generate an API key for Flink access. For more information, see [confluent api-key create](https://docs.confluent.io/confluent-cli/current/command-reference/api-key/confluent_api-key_create.html).

  1. Log in to Confluent Cloud:

         confluent login

  2. To see the available regions for Flink, run the following command:

         confluent flink region list

Your output should resemble:

         Current |           Name           | Cloud |    Region
         ----------+--------------------------+-------+---------------
                   | Frankfurt (eu-central-1) | aws   | eu-central-1
                   | Ireland (eu-west-1)      | aws   | eu-west-1
           *       | N. Virginia (us-east-1)  | aws   | us-east-1
                   | Ohio (us-east-2)         | aws   | us-east-2

  3. Run the following command to create an API key. Enure that the environment variables are set to your values.

         # Example values for environment variables.
         export CLOUD_PROVIDER=aws
         export CLOUD_REGION=us-east-1
         export ENV_ID=env-a12b34

         # Generate the API key and secret.
         confluent api-key create \
           --resource flink \
           --cloud ${CLOUD_PROVIDER} \
           --region ${CLOUD_REGION} \
           --environment ${ENV_ID}

Your output should resemble:

         It may take a couple of minutes for the API key to be ready.
         Save the API key and secret. The secret is not retrievable later.
         +------------+------------------------------------------------------------------+
         | API Key    | ABC1DDN2BNASQVRU                                                 |
         | API Secret | B0b+xCoSPY2pSNETeuyrziWmsPmou0WP9rH0Nxed4y4/msnESzjj7kBrRWGOMu1a |
         +------------+------------------------------------------------------------------+

     * If the environment, cloud, and region flags are set globally, you can create an API key by running `confluent api-key create --resource flink`. For more information, see [Manage API Keys in Confluent Cloud](../../security/authenticate/workload-identities/service-accounts/api-keys/manage-api-keys.html#cloud-cloud-api-keys).
     * To create an API key for an existing service account, provide the `--service-account <sa-a1b2c3>` option. This enables submitting long-running Flink SQL statements.

To create an API key for Flink access by using the Confluent Cloud APIs, you must first create a Cloud API key.

To generate the Flink key, you send your Cloud API key and secret in the request header, encoded as a base64 string.

  1. Create a Cloud API key for the principal, which is either a service account or your user account. For more information, see [Add an API key](../../security/authenticate/workload-identities/service-accounts/api-keys/manage-api-keys.html#create-cloud-api-key).

  2. Assign the Cloud API key and secret to environment variables that you use in your REST API requests.

         export CLOUD_API_KEY="<cloud-api-key>"
         export CLOUD_API_SECRET="<cloud-api-secret>"
         export PRINCIPAL_ID="<service-account-id>" # or "<user-account-id>"
         export ENV_REGION_ID="<environment-id>.<cloud-region>"
