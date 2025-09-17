---
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/generate-api-key-for-flink.html
title: Generate an API key for Programmatic Access to Confluent Cloud for Apache Flink
hierarchy: ['operate-and-deploy', 'generate-api-key-for-flink.html']
scraped_date: 2025-09-05T13:46:42.266731
---

# Generate an API Key for Access in Confluent Cloud for Apache Flink¶

To manage Flink workloads programmatically in Confluent Cloud for Apache Flink®, you need an API key that’s specific to Flink. You can use the Confluent CLI, the Confluent Cloud APIs, the Confluent Terraform Provider, or the Cloud Console to create API keys.

Before you create an API key for Flink access, decide whether you want to create long-running statements. If you need long-running statements, you should use a [service account](../../security/authenticate/workload-identities/service-accounts/overview.html#service-accounts) and create an API key for it. If you only need to run interactive queries or run statements for a short time while developing queries, you can create an API key for your user account.

A Flink API key is scoped to an environment and region pair, for example, `env-abc123.aws.us-east-2`. The key enables creating, reading, updating, and deleting Flink SQL statements.

To create an API key for Flink access by using the Confluent Cloud APIs or the Confluent Terraform Provider, you must first create a Cloud API key. This step is done automatically if you use the Confluent CLI to create an API key for Flink access.

## Create a service account (optional)¶

If you need to create long-running Flink SQL statements, create a service account principal before you create a Flink API key.

  1. Create a service account by using the [Cloud Console](../../security/authenticate/workload-identities/service-accounts/create-service-accounts.html#create-service-accounts) or the [CLI](../../security/authenticate/workload-identities/service-accounts/manage-service-accounts.html#create-service-accounts-cloud-cli).

  2. Assign the OrganizationAdmin role to the service account by following the steps in [Add a role binding to a principal](../../security/access-control/rbac/manage-role-bindings.html#cloud-rbac-assign-role-to-user).

  3. Store the service account ID in a convenient location, for example, in an environment variable:
         
         export PRINCIPAL_ID="<service-account-id>"

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

You can use the Confluent CLI to generate an API key for Flink access. For more information, see [confluent api-key create ](https://docs.confluent.io/confluent-cli/current/command-reference/api-key/confluent_api-key_create.html).

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
         export ENV_REGION_ID="<environment-id>.<cloud-region>" # example: "env-z3y2x1.aws.us-east-1"

The ENV_REGION_ID variable is a concatenation of your environment ID and the cloud provider region of your Kafka cluster, separated by a `.` character. To see the available regions, run the `confluent flink region list` command.

  3. Run the following command to send a POST request to the `api-keys` endpoint. The REST API uses basic authentication, which means that you provide a base64-encoded string made from your Cloud API key and secret in the request header.
         
         curl --request POST \
           --url 'https://api.confluent.cloud/iam/v2/api-keys' \
           --header "Authorization: Basic $(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)" \
           --header 'content-type: application/json' \
           --data "{"spec":{"display_name":"flinkapikey","owner":{"id":"${PRINCIPAL_ID}"},"resource":{"api_version":"fcpm/v2","id":"${ENV_REGION_ID}"}}}"

Your output should resemble:
         
         {
           "api_version": "iam/v2",
           "id": "KJDYFDMBOBDNQEIU",
           "kind": "ApiKey",
           "metadata": {
             "created_at": "2023-12-15T23:10:20.406556Z",
             "resource_name": "crn://api.confluent.cloud/organization=b0b21724-4586-4a07-b787-d0bb5aacbf87/user=u-lq1dr3/api-key=KJDYFDMBOBDNQEIU",
             "self": "https://api.confluent.cloud/iam/v2/api-keys/KJDYFDMBOBDNQEIU",
             "updated_at": "2023-12-15T23:10:20.406556Z"
           },
           "spec": {
             "description": "",
             "display_name": "flinkapikey",
             "owner": {
               "api_version": "iam/v2",
               "id": "u-lq1dr3",
               "kind": "User",
               "related": "https://api.confluent.cloud/iam/v2/users/u-lq2dr7",
               "resource_name": "crn://api.confluent.cloud/organization=b0b21724-4586-4a07-b787-d0bb5aacbf87/user=u-lq2dr7"
             },
             "resource": {
               "api_version": "fcpm/v2",
               "id": "env-z3q9rd.aws.us-east-1",
               "kind": "Region",
               "related": "https://api.confluent.cloud/fcpm/v2/regions?cloud=aws",
               "resource_name": "crn://api.confluent.cloud/organization=b0b21724-4586-4a07-b787-d0bb5aacbf87/environment=env-z3q9rd/flink-region=aws.us-east-1"
             },
             "secret": "B0BYFzyd0bb5Q58ZZJJYV52mbwDDHnZx21f0gOTz2k6Qv2V9I4KraVztwFOlQx6z"
           }
         }

You can use the [Confluent Terraform Provider](../../clusters/terraform-provider.html#confluent-terraform-provider) to generate an API key for Flink access.

Follow the steps in [Sample Project for Confluent Terraform Provider](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/guides/sample-project) and use the configuration shown in [Example Flink API Key](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/resources/confluent_api_key#example-flink-api-key).

When your API key and secret are generated, save them in environment variables for later use.

    export FLINK_API_KEY="<flink-api-key>"
    export FLINK_API_SECRET="<flink-api-secret>"

You can manage the API key by using the Confluent CLI commands. For more information, see [confluent api-key ](https://docs.confluent.io/confluent-cli/current/command-reference/api-key/index.html). Also, you can use the [REST API](https://docs.confluent.io/cloud/current/api.html#tag/API-Keys-\(iamv2\)) and Cloud Console.

## Next steps¶

  * [Flink SQL REST API](flink-rest-api.html#flink-rest-api)

## Related content¶

  * [Manage API Keys](../../security/authenticate/workload-identities/service-accounts/api-keys/manage-api-keys.html#cloud-cloud-api-keys)
  * [Confluent CLI commands with Confluent Cloud for Apache Flink](../reference/flink-sql-cli.html#flink-sql-confluent-cli)

Note

This website includes content developed at the [Apache Software Foundation](https://www.apache.org/) under the terms of the [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0.html).
