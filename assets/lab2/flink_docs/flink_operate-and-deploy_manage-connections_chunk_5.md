---
document_id: flink_operate-and-deploy_manage-connections_chunk_5
source_file: flink_operate-and-deploy_manage-connections.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/manage-connections.html
title: Manage Flink Connections in Confluent Cloud for Apache Flink
chunk_index: 5
total_chunks: 10
---

"OPENAI",
        "endpoint": "<https://api.openai.com/v1/chat/completions>",
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
