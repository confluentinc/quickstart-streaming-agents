---
document_id: flink_operate-and-deploy_manage-connections_chunk_6
source_file: flink_operate-and-deploy_manage-connections.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/manage-connections.html
title: Manage Flink Connections in Confluent Cloud for Apache Flink
chunk_index: 6
total_chunks: 10
---

information, see [confluent_flink_connection data source](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/data-sources/confluent_flink_connection).

## List connections¶

Flink SQLConfluent Cloud ConsoleConfluent CLIREST APITerraform

In the Confluent Cloud Console or in the Flink SQL shell, run the [SHOW CONNECTIONS](../reference/statements/show.html#flink-sql-show-connections) statement to list the connections.

    SHOW CONNECTIONS;

Your output should resemble:

                    Creation Date          |           Name           | Environment | Cloud |  Region   |    Type     |            Endpoint             |    Data    | Status | Status Detail
    ---------------------------------+--------------------------+-------------+-------+-----------+-------------+---------------------------------+------------+--------+----------------
      2025-08-13 21:05:15.035376     | azureopenai-connection-2 | env-a1b2c3  | aws   | us-west-2 | AZUREOPENAI | https://<your-project-endpoint> | <REDACTED> |        |
      +0000 UTC                      |                          |             |       |           |             |                                 |            |        |
      2025-08-13 22:04:57.972969     | azure-openai-connection  | env-a1b2c3  | aws   | us-west-2 | AZUREOPENAI | https://<your-project-endpoint> | <REDACTED> |        |
      +0000 UTC                      |                          |             |       |           |             |                                 |            |        |

  1. In the navigation menu, click **Environments** , and click the tile for the environment where you’re using Flink SQL.

  2. In the navigation menu, click **Integrations**.

  3. Click **Connections**.

The available connections are listed.

Run the [confluent flink connection list](https://docs.confluent.io/confluent-cli/current/command-reference/flink/connection/confluent_flink_connection_list.html) command to list connections in the specified environment.

Listing connections requires the following inputs:

    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"
    export ENV_ID="<environment-id>" # example: "env-a1b2c3"

Run the following command to list connections in the specified environment.

    confluent flink connection list
      --cloud ${CLOUD_PROVIDER} \
      --region ${CLOUD_REGION} \
      --environment ${ENV_ID}

Your output should resemble:

              Creation Date          |           Name           | Environment | Cloud |  Region   |    Type     |            Endpoint             |    Data    | Status | Status Detail
    ---------------------------------+--------------------------+-------------+-------+-----------+-------------+---------------------------------+------------+--------+----------------
      2025-08-13 21:05:15.035376     | azureopenai-connection-2 | env-a1b2c3  | aws   | us-west-2 | AZUREOPENAI | https://<your-project-endpoint> | <REDACTED> |        |
      +0000 UTC                      |                          |             |       |           |             |                                 |            |        |
      2025-08-13 22:04:57.972969     | azure-openai-connection  | env-a1b2c3  | aws   | us-west-2 | AZUREOPENAI | https://<your-project-endpoint> | <REDACTED> |        |
      +0000 UTC                      |                          |             |       |           |             |                                 |            |        |

List the connections in your environment by sending a GET request to the [Connections endpoint](/cloud/current/api.html#tag/Connections-\(sqlv1\)/operation/listSqlv1Connections).

* This request uses your Cloud API key instead of the Flink API key.

Listing the connections in your environment requires the following inputs:

    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ORG_ID="<organization-id>" # example: "b0b21724-4586-4a07-b787-d0bb5aacbf87"
    export ENV_ID="<environment-id>" # example: "env-a1b2c3"

Run the following command to list the connections in your environment.

    curl --request GET \
      --url "https://flink.region.provider.confluent.cloud/sql/v1/organizations/${ORG_ID}/environments/${ENV_ID}/connections" \
      --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}"

Your output should resemble:

Response from a request to list connections

    {
      "api_version": "sql/v1",
      "kind": "ConnectionList",
      "metadata": {
        "first": "https://flink.us-west1.aws.confluent.cloud/sql/v1/environments/env-abc123/connections",
        "last": "",
        "prev": "",
        "next": "https://flink.us-west1.aws.confluent.cloud/sql/v1/environments/env-abc123/connections?page_token=UvmDWOB1iwfAIBPj6EYb",
