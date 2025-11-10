---
document_id: flink_configure_access-control_chunk_1
source_file: flink_configure_access-control.md
source_url: https://docs.confluent.io/platform/current/flink/configure/access-control.html
title: Access Control for Confluent Manager for Apache Flink
chunk_index: 1
total_chunks: 3
---

# Configure Access Control for Confluent Manager for Apache Flink¶

Confluent Manager for Apache Flink® models its access control around six resource types, which different types of users have access to. For a general description of role-based access control, see [Use Role-Based Access Control (RBAC) for Authorization in Confluent Platform](../../security/authorization/rbac/overview.html#rbac-overview). Following is a list of the resources that are available in Confluent Manager for Apache Flink® for Flink SQL, and their descriptions:

  * **Flink Application** : Defines a Flink application, which starts the Flink Cluster in Application mode. Depending on their assigned role, developers have access to their Flink environment to create, update, and view Flink applications.
  * **Flink Environment** : The environment contains where and how to deploy the application, such as the Kubernetes namespace or central configurations that cannot be overridden. You can use Flink environments to separate the privileges of different teams or organizations. System administrators are responsible for managing the Flink environments and provisioning them correctly.
  * **Flink Statement** : Statements are the resource in CMF used to execute and maintain SQL queries.
  * **Flink Secret** : These are resources that manage the confidential data that can be used by Flink Statements. At present, they can either be used for kafka connection configuration or schema registry configuration.
  * **Flink Catalog** : Provides Kafka topics as tables with schemas derived from Schema Registry.
  * **Flink ComputePool** : In CMF, the compute resources that are used to execute a SQL statement.

## Understanding RBAC Role Types¶

RBAC roles in Confluent Platform are categorised into two main types:

  * **Cluster-level roles** : Cluster-level roles grant permissions on all resources of a particular type across the entire cluster. They are not bound to any specific resources. These provide permissions across a wide scope.
  * **Resource level roles** : Resource-level roles grant permissions on specific resources that must be explicitly specified. Generally used to provide a more fine-grained permission management.

## Cluster identifiers¶

To create role bindings, you need the cluster identifiers for the components in your CMF deployment. For CMF, you use the following cluster identifiers:

  * `cmf`: Always set to the CMF-id, which is the identifier for the CMF cluster. Currently, changing this ID is not supported.
  * `flinkEnvironment`: your environment name

Important

Currently, only a single instance of CMF is supported per MDS installation.

The following example command shows how to create a role binding with the identifiers for your cluster.

Example:

    confluent iam rbac role-binding create \
    --principal User:<user> \
    --role DeveloperRead \
    --cmf CMF-id \
    --flink-environment <flink-environment-name>
    --resource FlinkApplication:<flink-application-name>

## Resources¶

CMF provides the following resources.

  * In the cluster CMF-id:
    * Flink Environment
    * Flink Catalog
    * Flink Secret
  * In the cluster Flink Environment:
    * Flink Application
    * Flink Statement
    * Flink ComputePool
