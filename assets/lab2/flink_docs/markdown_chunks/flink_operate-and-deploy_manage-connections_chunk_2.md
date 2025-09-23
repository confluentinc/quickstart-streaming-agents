---
document_id: flink_operate-and-deploy_manage-connections_chunk_2
source_file: flink_operate-and-deploy_manage-connections.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/manage-connections.html
title: Manage Flink Connections in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 10
---

time in Confluent’s’ sole discretion.

## Create a connection¶

Flink SQLConfluent Cloud ConsoleConfluent CLIREST APITerraform

  1. In the Confluent Cloud Console or in the Flink SQL shell, run the [CREATE CONNECTION](../reference/statements/create-connection.html#flink-sql-create-connection) statement to create a connection.

The following example creates an OpenAI connection with an API key.

         CREATE CONNECTION `my-connection`
           WITH (
             'type' = 'OPENAI',
             'endpoint' = 'https://<your-endpoint>.openai.azure.com/openai/deployments/<deployment-name>/chat/completions?api-version=2025-01-01-preview',
             'api-key' = '<your-api-key>'
           );

The following example creates a MongoDB connection with basic authorization.

         CREATE CONNECTION `my-mongodb-connection`
           WITH (
             'type' = 'MONGODB',
             'endpoint' = 'mongodb+srv://myCluster.mongodb.net/myDatabase',

             'username' = '<atlas-user-name>',
             'password' = '<atlas-password>'
           );

  2. Run the [CREATE TABLE](../reference/statements/create-table.html#flink-sql-create-table) statement to create a table that uses the connection.

The following example creates a MongoDB external table that uses the MongoDB connection.

         -- Use the MongoDB connection to create a MongoDB external table.
         CREATE TABLE mongodb_movies_full_text_search (
             title STRING,
             plot STRING
         ) WITH (
             'connector' = 'mongodb',
             'mongodb.connection' = 'my-mongodb-connection',
             'mongodb.database' = 'sample_mflix',
             'mongodb.collection' = 'movies',
             'mongodb.index' = 'default'
         );

  1. In the navigation menu, click **Environments** , and click the tile for the environment where you’re using Flink SQL.

  2. In the navigation menu, click **Integrations**.

  3. Click **Connections** , then click **Add connection**.

The available services are listed.

  4. Click the tile of the service you want to connect to, and click **Continue**.

The **Define endpoint and credentials** page opens.

  5. In the **Endpoint** textbox, enter the URL for the service you want to connect to.

  6. In the following fields, enter your credentials, which may be an API key, a username/password pair, or another type of credential, like a Service Account Key, depending on the service.

  7. Click **Continue**.

The **Review and launch** page opens.

  8. In the **Cloud provider** and **Region** dropdowns, select the cloud provider and region where your Flink statements run.

Important

You can access the connection only from a workspace that is in the same region as the connection.

  9. Click **Create connection**.

The connection is created and you can use it in your Flink statements.

Note

You can edit the credentials later, but you can’t change the other properties, like the cloud provider or region.

Run the [confluent flink connection create](https://docs.confluent.io/confluent-cli/current/command-reference/flink/connection/confluent_flink_connection_create.html) command to create a connection.

Creating a connection requires the following inputs. Credentials vary by service.

    export CONNECTION_NAME="<connection-name>" # human-readable name, for example, "azure-openai-connection"
    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"
    export ENV_ID="<environment-id>" # example: "env-a1b2c3"
    export CONNECTION_TYPE="<connection-type>" # example: "azureopenai"
    export ENDPOINT="<endpoint>" # example: "https://<your-project>.openai.azure.com/openai/deployments/<deployment-name>/chat/completions?api-version=2025-01-01-preview"
    export API_KEY="<api-key>"

Run the following command to create a connection in the specified cloud provider and environment.

    confluent flink connection create ${CONNECTION_NAME} \
      --cloud ${CLOUD_PROVIDER} \
      --region ${CLOUD_REGION} \
      --environment ${ENV_ID} \
      --type ${CONNECTION_TYPE} \
      --endpoint ${ENDPOINT} \
      --api-key ${API_KEY}

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
