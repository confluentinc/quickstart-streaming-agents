---
document_id: flink_operate-and-deploy_manage-connections_chunk_10
source_file: flink_operate-and-deploy_manage-connections.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/manage-connections.html
title: Manage Flink Connections in Confluent Cloud for Apache Flink
chunk_index: 10
total_chunks: 10
---

For more information, see [confluent_flink_connection](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/resources/confluent_flink_connection).

## Delete a connection¶

Flink SQLConfluent Cloud ConsoleConfluent CLIREST APITerraform

In the Confluent Cloud Console or in the Flink SQL shell, run the [DROP CONNECTION](../reference/statements/drop-connection.html#flink-sql-drop-connection) statement to delete the connection.

    DROP CONNECTION `my-connection`;

  1. In the navigation menu, click **Environments** , and click the tile for the environment where you’re using Flink SQL.

  2. In the navigation menu, click **Integrations**.

  3. Click **Connections**.

  4. In the listed connections, find the one you want to delete, and click the options icon (**⋮**).

  5. In the context menu, click **Delete connection**.

  6. In the dialog, enter the connection name, and click **Confirm**.

The connection is deleted.

Run the [confluent flink connection delete](https://docs.confluent.io/confluent-cli/current/command-reference/flink/connection/confluent_flink_connection_delete.html) command to delete a connection.

Deleting a connection requires the following inputs:

    export CONNECTION_NAME="<connection-name>" # example: "azure-openai-connection"
    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"
    export ENV_ID="<environment-id>" # example: "env-a1b2c3"

Run the following command to delete a connection.

    confluent flink connection delete ${CONNECTION_NAME} \
      --cloud ${CLOUD_PROVIDER} \
      --region ${CLOUD_REGION} \
      --environment ${ENV_ID}

Your output should resemble:

    Deleted Flink connection "azure-openai-connection".

Delete a connection in your environment by sending a DELETE request to the [Connections endpoint](/cloud/current/api.html#tag/Connections-\(sqlv1\)/operation/deleteSqlv1Connection).

* This request uses your Cloud API key instead of the Flink API key.

Deleting a connection requires the following inputs:

    export CONNECTION_NAME="<connection-name>" # example: "my-openai-connection"
    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ORG_ID="<organization-id>" # example: "b0b21724-4586-4a07-b787-d0bb5aacbf87"
    export ENV_ID="<environment-id>" # example: "env-a1b2c3"

Run the following command to delete the connection specified in the CONNECTION_NAME environment variable.

    curl --request DELETE \
      --url "https://flink.region.provider.confluent.cloud/sql/v1/organizations/${ORG_ID}/environments/${ENV_ID}/connections/${CONNECTION_NAME}" \
      --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}"

To delete a connection by using the Confluent Terraform provider, use the [confluent_flink_connection](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/resources/confluent_flink_connection) resource.

  1. Find the definition for the connection resource in your Terraform configuration and copy the name of the resource. In the following example, the resource name is `main`.

         resource "confluent_flink_connection" "main" {
           display_name = "standard_connection"
           ...
           }
         }

  2. To avoid accidental deletions, review the plan before applying the `destroy` command.

         terraform plan -destroy -target=confluent_flink_connection.main

  3. To delete the connection, run the following command to target the specific resource. This command deletes only the connection and not other resources.

         terraform apply -destroy -target=confluent_flink_connection.main

To remove all resources defined in your Terraform configuration file, including the connection, run the `terraform destroy` command.

         terraform destroy

For more information, see [confluent_flink_connection](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/resources/confluent_flink_connection).
