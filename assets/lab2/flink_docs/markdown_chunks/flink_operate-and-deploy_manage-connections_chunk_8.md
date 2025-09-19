---
document_id: flink_operate-and-deploy_manage-connections_chunk_8
source_file: flink_operate-and-deploy_manage-connections.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/manage-connections.html
title: Manage Flink Connections in Confluent Cloud for Apache Flink
chunk_index: 8
total_chunks: 10
---

For more information, see [confluent_flink_connection](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/data-sources/confluent_flink_connection).

## Update a connection¶

You can update only the credentials for a connection.

Flink SQLConfluent Cloud ConsoleConfluent CLIREST APITerraform

In the Confluent Cloud Console or in the Flink SQL shell, run the [ALTER CONNECTION](../reference/statements/alter-connection.html#flink-sql-alter-connection) statement to update the connection.

    ALTER CONNECTION `my-connection` SET ('api-key' = '<new-api-key>');

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

  4. In the listed connections, find the one you want to update, and click the options icon (**⋮**).

  5. In the context menu, click **Edit connection**.

  6. In the credentials fields, enter the new credentials for the connection.

  7. Click **Save changes**.

The connection is updated, and you can use it in your Flink statements.

Run the [confluent flink connection update](https://docs.confluent.io/confluent-cli/current/command-reference/flink/connection/confluent_flink_connection_update.html) command to update a connection.

Updating a connection requires the following inputs. Credentials vary by service.

    export CONNECTION_NAME="<connection-name>" # example: "azure-openai-connection"
    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"
    export ENV_ID="<environment-id>" # example: "env-a1b2c3"
    export ENDPOINT="<endpoint>" # example: "https://<your-project>.openai.azure.com/openai/deployments/<deployment-name>/chat/completions?api-version=2025-01-01-preview"
    export NEWAPI_KEY="<new-api-key>"

Run the following command to update a connection.

    confluent flink connection update ${CONNECTION_NAME} \
      --cloud ${CLOUD_PROVIDER} \
      --region ${CLOUD_REGION} \
      --environment ${ENV_ID} \
      --endpoint ${ENDPOINT} \
      --api-key ${NEWAPI_KEY}

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

Update a connection in your environment by sending a PATCH request to the [Connections endpoint](/cloud/current/api.html#tag/Connections-\(sqlv1\)/operation/updateSqlv1Connection).

  * This request uses your Cloud API key instead of the Flink API key.

Updating a connection requires the following inputs:

    export CONNECTION_NAME="<connection-name>" # example: "my-openai-connection"
    export CONNECTION_TYPE="<connection-type>" # example: "OPENAI"
    export ENDPOINT="<endpoint>" # example: "https://api.openai.com/v1/chat/completions"
    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ORG_ID="<organization-id>" # example: "b0b21724-4586-4a07-b787-d0bb5aacbf87"
    export ENV_ID="<environment-id>" # example: "env-a1b2c3"
    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"
    export JSON_DATA="<payload-string>"

The following JSON shows an example payload. The `auth_data` key varies by service.

    {
      "name": "${CONNECTION_NAME}",
      "spec": {
        "connection_type": "${CONNECTION_TYPE}",
        "endpoint": "${ENDPOINT}",
        "auth_data": {
          "kind": "PlaintextProvider",
          "data": "string"
        }
      },
      "metadata": {}
    }
