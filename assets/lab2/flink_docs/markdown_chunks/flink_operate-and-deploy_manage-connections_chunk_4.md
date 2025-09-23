---
document_id: flink_operate-and-deploy_manage-connections_chunk_4
source_file: flink_operate-and-deploy_manage-connections.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/manage-connections.html
title: Manage Flink Connections in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 10
---

more information, see [confluent_flink_connection resource](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/resources/confluent_flink_connection).

## View details for a connection¶

Flink SQLConfluent Cloud ConsoleConfluent CLIREST APITerraform

In the Confluent Cloud Console or in the Flink SQL shell, run the [DESCRIBE CONNECTION](../reference/statements/describe.html#flink-sql-describe) statement to get details about a connection.

    DESCRIBE CONNECTION `my-connection`;

Your output should resemble:

    +---------------+------------------------------------+
    | Creation Date | 2025-08-13 22:04:57.972969         |
    |               | +0000 UTC                          |
    | Name          | azure-openai-connection            |
    | Environment   | env-a1b2c3                         |
    | Cloud         | aws                                |
    | Region        | us-west-2                          |
    | Type          | AZUREOPENAI                        |
    | Endpoint      | https://<your-project-endpoint>    |
    | Data          | <REDACTED>                         |
    | Status        |                                    |
    +---------------+------------------------------------+

  1. In the navigation menu, click **Environments** , and click the tile for the environment where you’re using Flink SQL.
  2. In the navigation menu, click **Integrations**.
  3. Click **Connections**.
  4. In the listed connections, find the one you want to view. If you have many connections in the list, use the search bar to find the connection.
  5. Click the connection name to view the connection details.

Run the [confluent flink connection describe](https://docs.confluent.io/confluent-cli/current/command-reference/flink/connection/confluent_flink_connection_describe.html) command to get details about a connection.

Describing a connection requires the following inputs:

    export CONNECTION_NAME="<connection-name>" # example: "azure-openai-connection"
    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"
    export ENV_ID="<environment-id>" # example: "env-a1b2c3"

Run the following command to get details about a connection.

    confluent flink connection describe ${CONNECTION_NAME} \
      --cloud ${CLOUD_PROVIDER} \
      --region ${CLOUD_REGION} \
      --environment ${ENV_ID}

Your output should resemble:

    +---------------+------------------------------------+
    | Creation Date | 2025-08-13 22:04:57.972969         |
    |               | +0000 UTC                          |
    | Name          | azure-openai-connection            |
    | Environment   | env-a1b2c3                         |
    | Cloud         | aws                                |
    | Region        | us-west-2                          |
    | Type          | AZUREOPENAI                        |
    | Endpoint      | https://<your-project-endpoint>    |
    | Data          | <REDACTED>                         |
    | Status        |                                    |
    +---------------+------------------------------------+

Get the details about a connection in your environment by sending a GET request to the [Connections endpoint](/cloud/current/api.html#tag/Connections-\(sqlv1\)/operation/getSqlv1Connection).

* This request uses your Cloud API key instead of the Flink API key.

Getting details about a connection requires the following inputs:

    export CONNECTION_NAME="<connection-name>" # example: "my-openai-connection"
    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ORG_ID="<organization-id>" # example: "b0b21724-4586-4a07-b787-d0bb5aacbf87"
    export ENV_ID="<environment-id>" # example: "env-a1b2c3"

Run the following command to get details about the connection specified in the CONNECTION_NAME environment variable.

    curl --request GET \
      --url "https://flink.region.provider.confluent.cloud/sql/v1/organizations/${ORG_ID}/environments/${ENV_ID}/connections/${CONNECTION_NAME}" \
      --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}"

Your output should resemble:

Response from a request to read a connection

    {
      "api_version": "sql/v1",
      "kind": "Connection",
      "metadata": {
        "self": "https://flink.us-west1.aws.confluent.cloud/sql/v1/organizations/org-abc/environments/env-123/connections/my-openai-connection",
        "resource_name": "",
        "created_at": "2006-01-02T15:04:05-07:00",
        "updated_at": "2006-01-02T15:04:05-07:00",
        "deleted_at": "2006-01-02T15:04:05-07:00",
        "uid": "12345678-1234-1234-1234-123456789012",
        "resource_version": "a23av"
      },
      "name": "my-openai-connection",
      "spec": {
        "connection_type":
