---
document_id: flink_overview_chunk_3
source_file: flink_overview.md
source_url: https://docs.confluent.io/cloud/current/flink/overview.html
title: Stream Processing with Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 3
---

#### Access from Flink to the data¶

  * For ad-hoc queries, you can use your user account, because the permissions of the current user are applied automatically without any additional setting needed.
  * For long-running statements that need to run 24/7, like [INSERT INTO](reference/queries/insert-into-from-select.html#flink-sql-insert-into-from-select-statement), you should use a [service account](../security/authenticate/workload-identities/service-accounts/overview.html#service-accounts), so the statements are not affected by a user leaving the company or changing teams.

#### Access to Flink¶

To manage Flink access, Confluent has introduced two roles. In both cases, RBAC of the user on the underlying data is still applied.

  * [FlinkDeveloper](../security/access-control/rbac/predefined-rbac-roles.html#flinkdeveloper-role): basic access to Flink, enabling users to query data and manage their own statements.
  * [FlinkAdmin](../security/access-control/rbac/predefined-rbac-roles.html#flinkadmin-role): role that enables creating and managing Flink compute pools.

#### Service accounts¶

Service accounts are available for running statements permanently. If you want to run a statement with service account permissions, an OrganizationAdmin must create an **Assigner** role binding for the user on the service account. For more information, see [Production workloads (service accounts)](operate-and-deploy/flink-rbac.html#flink-rbac-grant-sa-and-user-permission-for-sql-statements).

#### Private networking¶

Confluent Cloud for Apache Flink supports private networking on AWS, Azure, and Google Cloud, providing a simple, secure, and flexible solution that enables new scenarios while keeping your data securely in private networking.

All Kafka cluster types are supported, with any type of connectivity (public, Private Links, VPC Peering, and Transit Gateway).

For more information, see [Private Networking with Flink](concepts/flink-private-networking.html#flink-sql-private-networking).

## Cross-environment queries¶

Flink can perform cross-environment queries when using both public and private networking. This can be useful if you want to enable a single networking route from your VPC or VNET.

In this case, you can use a single environment and a single PLATT where you run all your Flink workloads and use three-part name queries, to query data in other environments, for example:

    SELECT * FROM `myEnvironment`.`myDatabase`.`myTable`;

As a result, a single routing rule is necessary on the VPC or VNet side, per region, to redirect all traffic to the Flink regional endpoint(s) using this PrivateLink Attachment Connection.

To isolate different workloads, you can create different compute pools, which enables you to control budget and scale of these workloads independently.

Data access is protected by RBAC at the Kafka cluster (Flink database) or Kafka topic (Flink table) level. If your user account or service account that runs the query doesn’t have access, Flink can’t access sources and destinations.

To access Flink statements and workspaces, you must access them from a public IP address, if authorized, or from a PLATT or Confluent Cloud Network from the same environment and region.

Flink statements themselves can then access all the environments in the same organization and region.

## Program Flink with SQL, Java, and Python¶

Confluent Cloud for Apache Flink supports programming your streaming applications in these languages:

  * [SQL](reference/sql-syntax.html#flink-sql-syntax)
  * [Java Table API](get-started/quick-start-java-table-api.html#flink-java-table-api-quick-start)
  * [Python Table API](get-started/quick-start-python-table-api.html#flink-python-table-api-quick-start)

Also, you can create custom user-defined functions and call them in your SQL statements. For more information, see [User-defined Functions](concepts/user-defined-functions.html#flink-sql-udfs).

Note

The Flink Table API is available for preview.

A Preview feature is a Confluent Cloud component that is being introduced to gain early feedback from developers. Preview features can be used for evaluation and non-production testing purposes or to provide feedback to Confluent. The warranty, SLA, and Support Services provisions of your agreement with Confluent do not apply to Preview features. Confluent may discontinue providing preview releases of the Preview features at any time in Confluent’s’ sole discretion.

Comments, questions, and suggestions related to the Table API are encouraged and can be submitted through the [established channels](get-help.html#ccloud-flink-help).

submitted through the [established channels](get-help.html#ccloud-flink-help).

## Confluent for VS Code¶

Install [Confluent for VS Code](../client-apps/vs-code-extension.html#cc-vscode-extension) to access Smart Project Templates that accelerate project setup by providing ready-to-use templates tailored for common development patterns. These templates enable you to launch new projects quickly with minimal configuration, significantly reducing setup time.
