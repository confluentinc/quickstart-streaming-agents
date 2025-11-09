---
document_id: flink_operate-and-deploy_manage-connections_chunk_9
source_file: flink_operate-and-deploy_manage-connections.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/manage-connections.html
title: Manage Flink Connections in Confluent Cloud for Apache Flink
chunk_index: 9
total_chunks: 10
---

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
