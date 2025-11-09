---
document_id: flink_operate-and-deploy_manage-connections_chunk_7
source_file: flink_operate-and-deploy_manage-connections.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/manage-connections.html
title: Manage Flink Connections in Confluent Cloud for Apache Flink
chunk_index: 7
total_chunks: 10
---

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
