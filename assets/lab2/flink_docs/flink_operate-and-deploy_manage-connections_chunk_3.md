---
document_id: flink_operate-and-deploy_manage-connections_chunk_3
source_file: flink_operate-and-deploy_manage-connections.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/manage-connections.html
title: Manage Flink Connections in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 10
---

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
