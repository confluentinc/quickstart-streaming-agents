---
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/manage-connections.html
title: Manage Flink Connections in Confluent Cloud for Apache Flink
hierarchy: ['operate-and-deploy', 'manage-connections.html']
scraped_date: 2025-09-05T13:46:47.029180
---

# Manage Connections in Confluent Cloud for Apache Flink¶

A connection in Confluent Cloud for Apache Flink® represents an external service that is used in your Flink statements. Connections are used to access external services, such as databases, APIs, and other systems, from your Flink statements.

To create a connection, you need the OrganizationAdmin, EnvironmentAdmin, or FlinkAdmin RBAC role.

Confluent Cloud for Apache Flink makes a best-effort attempt to redact sensitive values from the CREATE CONNECTION and ALTER CONNECTION statements by masking the values for the known sensitive keys. In Confluent Cloud Console, the sensitive values are redacted in the Flink SQL workspace if you navigate away from the workspace and return, or if you reload the page in the browser. Alternatively, you can use the Confluent CLI commands to create and manage connections.

In addition, if syntax in the CREATE CONNECTION statement is incorrect, Confluent Cloud for Apache Flink may not detect the secrets. For example, if you type `CREATE CONNECTION my_conn WITH ('ap-key' = 'x')`, Flink won’t redact the `x`, because `api-key` is misspelled.

Note

Connection resources are an Open Preview feature in Confluent Cloud.

A Preview feature is a Confluent Cloud component that is being introduced to gain early feedback from developers. Preview features can be used for evaluation and non-production testing purposes or to provide feedback to Confluent. The warranty, SLA, and Support Services provisions of your agreement with Confluent do not apply to Preview features. Confluent may discontinue providing preview releases of the Preview features at any time in Confluent’s’ sole discretion.

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

Create a connection in your environment by sending a POST request to the [Connections](/cloud/current/api.html#tag/Connections-\(sqlv1\)/operation/createSqlv1Connection) endpoint.

Creating a connection requires the following inputs. Credentials vary by service.

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

Quotation mark characters in the JSON string must be escaped, so the payload string to send resembles the following:

    export JSON_DATA="{
      \"name\": \"${CONNECTION_NAME}\",
      \"spec\": {
        \"connection_type\": \"${CONNECTION_TYPE}\",
        \"endpoint\": \"${ENDPOINT}\",
        \"auth_data\": {
          \"kind\": \"PlaintextProvider\",
          \"data\": \"string\"
        }
      },
      \"metadata\": {}
    }"

The following command sends a POST request to create a connection.

    curl --request POST \
      --url "https://flink.region.provider.confluent.cloud/sql/v1/organizations/${ORG_ID}/environments/${ENV_ID}/connections" \
      --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}" \
      --header 'content-type: application/json' \
      --data "${JSON_DATA}"

Your output should resemble:

Response from a request to create a connection 

    {
      "api_version": "sql/v1",
      "kind": "Connection",
      "metadata": {
        "self": "https://flink.us-west1.aws.confluent.cloud/sql/v1/organizations/org-abc/environments/env-a1b2c3/connections/my-openai-connection",
        "resource_name": "",
        "created_at": "2006-01-02T15:04:05-07:00",
        "updated_at": "2006-01-02T15:04:05-07:00",
        "deleted_at": "2006-01-02T15:04:05-07:00",
        "uid": "12345678-1234-1234-1234-123456789012",
        "resource_version": "a23av"
      },
      "name": "my-openai-connection",
      "spec": {
        "connection_type": "OPENAI",
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "auth_data": {
          "kind": "PlaintextProvider",
          "data": "string"
        }
      },
      "status": {
        "phase": "READY",
        "detail": "Lookup failed: ai.openai.com"
         }
       }
    }

To create a connection by using the Confluent Terraform provider, use the [confluent_flink_connection](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/resources/confluent_flink_connection) resource.

  1. Configure your Terraform file. Provide your Confluent Cloud API key and secret.
         
         terraform {
           required_providers {
             confluent = {
               source = "confluentinc/confluent"
               version = "2.38.0"
             }
           }
         }
         
         provider "confluent" {
           cloud_api_key    = var.confluent_cloud_api_key    # optionally use CONFLUENT_CLOUD_API_KEY env var
           cloud_api_secret = var.confluent_cloud_api_secret # optionally use CONFLUENT_CLOUD_API_SECRET env var
         }

  2. Define the `confluent_flink_connection` resource with the required parameters, like `display_name`, `cloud`, `region`, and the environment ID.
         
         resource "confluent_flink_connection" "openai-connection" {
           organization {
               id = data.confluent_organization.main.id
           }
           environment {
               id = data.confluent_environment.staging.id
           }
           compute_pool {
               id = confluent_flink_compute_pool.example.id
           }
           principal {
               id = confluent_service_account.app-manager-flink.id
           }
           rest_endpoint = data.confluent_flink_region.main.rest_endpoint
           credentials {
               key    = confluent_api_key.env-admin-flink-api-key.id
               secret = confluent_api_key.env-admin-flink-api-key.secret
           }
         
           display_name = "connection1"
           type = "OPENAI"
           endpoint = "https://api.openai.com/v1/chat/completions"
           api_key ="API_Key_value"
         
           lifecycle {
               prevent_destroy = true
           }
         }

  3. Run the `terraform apply` command to create the resources.
         
         terraform apply

For more information, see [confluent_flink_connection resource](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/resources/confluent_flink_connection).

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
        "connection_type": "OPENAI",
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "auth_data": {
          "kind": "PlaintextProvider",
          "data": "string"
        }
      },
      "status": {
        "phase": "READY",
        "detail": "Lookup failed: ai.openai.com"
      }
    }

To view details for a connection by using the Confluent Terraform provider, use the [confluent_flink_connection](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/data-sources/confluent_flink_connection) data source.

    data "confluent_flink_connection" "existing_connection" {
      organization {
         id = "<your-organization-id>"
      }
      environment {
         id = "<your-environment-id>"
      }
      compute_pool {
         id = "<your-compute-pool-id>"
      }
      principal {
         id = "<your-service-account-id>"
      }
      rest_endpoint = "<your-flink-rest-endpoint>"
      credentials {
         key    = "<your-flink-api-key>"
         secret = "<your-flink-api-secret>"
      }
      display_name = "my_connection"
      type         = "JDBC"
    }
    
    output "connection_endpoint" {
      value = data.confluent_flink_connection.existing_connection.endpoint
    }

Run the `terraform apply` or `terraform output` command. The `connection_endpoint` output contains details for the connection.

To inspect specific attributes after your configuration has been applied, run the `terraform output` command.

    terraform output connection_endpoint

For more information, see [confluent_flink_connection data source](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/data-sources/confluent_flink_connection).

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
        "total_size": 123,
        "self": "https://flink.us-west1.aws.confluent.cloud/sql/v1/environments/env-123/connections"
      },
      "data": [
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
            "connection_type": "OPENAI",
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "auth_data": {
              "kind": "PlaintextProvider",
              "data": "string"
            }
         }
       },
       "status": {
         "phase": "READY",
         "detail": "Lookup failed: ai.openai.com"
          }
        }
      ]
    }

The Confluent Terraform provider does not support a plural data source or enumeration method that enables you to list all existing connection resources in one operation.

To view all connections, you must use Flink SQL, Confluent Cloud Console, the CLI, or the REST API.

If you use the Flink SQL REST API, you could integrate the response list into Terraform workflows by scripting an external data source that queries the Flink SQL API, and using an `external` provider, parses the results and feeds them into Terraform. This is a custom integration, not a supported feature.

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

Quotation mark characters in the JSON string must be escaped, so the payload string to send resembles the following:

    export JSON_DATA="{
      \"name\": \"${CONNECTION_NAME}\",
      \"spec\": {
        \"connection_type\": \"${CONNECTION_TYPE}\",
        \"endpoint\": \"${ENDPOINT}\",
        \"auth_data\": {
          \"kind\": \"PlaintextProvider\",
          \"data\": \"string\"
        }
      },
      \"metadata\": {}
    }"

The following command sends a PUT request to update a connection.

    curl --request PUT \
      --url "https://flink.region.provider.confluent.cloud/sql/v1/organizations/${ORG_ID}/environments/${ENV_ID}/connections/${CONNECTION_NAME}" \
      --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}" \
      --header 'content-type: application/json' \
      --data "${JSON_DATA}"

Your output should resemble:

Response from a request to update a connection 

    {
      "api_version": "sql/v1",
      "kind": "Connection",
      "metadata": {
        "self": "https://flink.us-west1.aws.confluent.cloud/sql/v1/organizations/org-abc/environments/env-a1b2c3/connections/my-openai-connection",
        "resource_name": "",
        "created_at": "2006-01-02T15:04:05-07:00",
        "updated_at": "2006-01-02T15:04:05-07:00",
        "deleted_at": "2006-01-02T15:04:05-07:00",
        "uid": "12345678-1234-1234-1234-123456789012",
        "resource_version": "a23av"
      },
      "name": "my-openai-connection",
      "spec": {
        "connection_type": "OPENAI",
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "auth_data": {
          "kind": "PlaintextProvider",
          "data": "string"
        }
      },
      "status": {
        "phase": "READY",
        "detail": "Lookup failed: ai.openai.com"
         }
       }
    }

To update a connection by using the Confluent Terraform provider, use the [confluent_flink_connection](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/resources/confluent_flink_connection) resource.

  1. Find the definition for the connection resource in your Terraform configuration, for example:
         
         resource "confluent_flink_connection" "openai-connection" {
           ...
           credentials {
               api_key    = confluent_api_key.env-admin-flink-api-key.id
           }
         }

  2. Modify the attributes of the `confluent_flink_connection` resource in the Terraform configuration file. The following example updates the `api_key` attribute.
         
         resource "confluent_flink_connection" "openai-connection" {
            ...
            credentials {
                api_key    = confluent_api_key.env-admin-flink-api-key.id # Updated value
            }
          }

  3. Run the `terraform apply` command to update the connection with the new configuration.
         
         terraform apply

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

## Related content¶

Note

This website includes content developed at the [Apache Software Foundation](https://www.apache.org/) under the terms of the [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0.html).
