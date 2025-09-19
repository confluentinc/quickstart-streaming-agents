---
document_id: flink_operate-and-deploy_manage-connections_chunk_1
source_file: flink_operate-and-deploy_manage-connections.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/manage-connections.html
title: Manage Flink Connections in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 10
---

# Manage Connections in Confluent Cloud for Apache Flink¶

A connection in Confluent Cloud for Apache Flink® represents an external service that is used in your Flink statements. Connections are used to access external services, such as databases, APIs, and other systems, from your Flink statements.

To create a connection, you need the OrganizationAdmin, EnvironmentAdmin, or FlinkAdmin RBAC role.

Confluent Cloud for Apache Flink makes a best-effort attempt to redact sensitive values from the CREATE CONNECTION and ALTER CONNECTION statements by masking the values for the known sensitive keys. In Confluent Cloud Console, the sensitive values are redacted in the Flink SQL workspace if you navigate away from the workspace and return, or if you reload the page in the browser. Alternatively, you can use the Confluent CLI commands to create and manage connections.

In addition, if syntax in the CREATE CONNECTION statement is incorrect, Confluent Cloud for Apache Flink may not detect the secrets. For example, if you type `CREATE CONNECTION my_conn WITH ('ap-key' = 'x')`, Flink won’t redact the `x`, because `api-key` is misspelled.

Note

Connection resources are an Open Preview feature in Confluent Cloud.

A Preview feature is a Confluent Cloud component that is being introduced to gain early feedback from developers. Preview features can be used for evaluation and non-production testing purposes or to provide feedback to Confluent. The warranty, SLA, and Support Services provisions of your agreement with Confluent do not apply to Preview features. Confluent may discontinue providing preview releases of the Preview features at any time in Confluent’s’ sole discretion.
