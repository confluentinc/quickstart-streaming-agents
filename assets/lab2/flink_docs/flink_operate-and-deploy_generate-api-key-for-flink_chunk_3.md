---
document_id: flink_operate-and-deploy_generate-api-key-for-flink_chunk_3
source_file: flink_operate-and-deploy_generate-api-key-for-flink.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/generate-api-key-for-flink.html
title: Generate an API key for Programmatic Access to Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 3
---

# example: "env-z3y2x1.aws.us-east-1"

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

You can manage the API key by using the Confluent CLI commands. For more information, see [confluent api-key](https://docs.confluent.io/confluent-cli/current/command-reference/api-key/index.html). Also, you can use the [REST API](https://docs.confluent.io/cloud/current/api.html#tag/API-Keys-\(iamv2\)) and Cloud Console.
