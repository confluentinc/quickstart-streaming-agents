---
document_id: flink_configure_environments_chunk_1
source_file: flink_configure_environments.md
source_url: https://docs.confluent.io/platform/current/flink/configure/environments.html
title: Confluent Manager for Apache Flink Environments
chunk_index: 1
total_chunks: 1
---

# Configure Environments in Confluent Manager for Apache Flink¶

An Flink environment in Confluent Manager for Apache Flink® (CMF) groups a set of Flink applications together.

Flink environments fulfill two main roles:

  * Isolation: [Access control](access-control.html#cmf-access-control) for individual team members is managed at the Environment-level (logical isolation). Flink applications that belong to an Environment are deployed to the same Kubernetes namespace (physical isolation).
  * Share configuration: Flink configuration at the Environment level has precedence over Flink configuration for individual Flink applications. This can be used to enforce configuration options and avoid redundant configuration. A common use case is setting a common observability configuration, or checkpoint storage destination for all Flink clusters in an environment.

For example, you might configure `dev` and `prod` environments or regional environments for your organization.

Flink configuration options, such as for the storage location of Flink checkpoints, are expected to differ between different environments, such as dev and prod. Instead of requiring individual Flink applications to configure these options and keep track of which environment they are running in, setting these options at the Environment-level makes management easier and separates concerns between platform operators and developers nicely.

## Manage Flink environments¶

You can use these tools to create and manage environments:

  * [REST APIs for Confluent Manager for Apache Flink](../clients-api/rest.html#af-rest-api)
  * [Confluent CLI reference](/confluent-cli/current/command-reference/flink/index.html)
  * [Confluent for Kubernetes](../clients-api/flink-cfk.html#cmf-cfk)

## Isolation between environments¶

Flink environments enable logical isolation of Flink applications that are managed by CMF.

For physical isolation, the Environment specifies the target Kubernetes namespace to deploy the Flink application to.

## Authorization¶

For role-based access control (RBAC), the Flink environment is used as the scope to [control access](../../security/authorization/acls/overview.html#acls-authorization). You can grant individual users access to specific Environments to read/manage Flink applications.
