---
source_url: https://docs.confluent.io/platform/current/flink/configure/access-control.html
title: Access Control for Confluent Manager for Apache Flink
hierarchy: ['platform', 'configure', 'access-control.html']
scraped_date: 2025-09-05T13:52:30.804099
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

## Understand user roles for Flink resources¶

You grant a user access to CMF resources. The next few sections describe the roles that are available in CMF and the operations that each role can perform on the resources.

### Role permissions for Flink environments¶

The following table shows roles and the operations the role is allowed for CMF resources. For a list of all predefined RBAC roles for Confluent Platform, see [Use Predefined RBAC Roles in Confluent Platform](../../security/authorization/rbac/rbac-predefined-roles.html#rbac-predefined-roles).

Role Name: Role Scope | Create/Update FlinkEnvironment | Delete FlinkEnvironment | Create/Update FlinkApplication in FlinkEnvironment | View FlinkApplication and access the Flink Web UI in FlinkEnvironment | Add new role-bindings  
---|---|---|---|---|---  
super.user: Cluster-level | Yes | Yes | Yes | Yes | Yes  
SystemAdmin: Cluster-level | Yes | Yes | Yes | Yes | Yes  
ClusterAdmin: Cluster-level | Yes | No | Yes | Yes | No  
UserAdmin: Cluster-level | No | No | No | No | Yes  
ResourceOwner: Resource-level | No | No | Yes | Yes | Yes  
DeveloperRead: Resource-level | No | No | No | Yes | No  
DeveloperManage: Resource-level | No | No | Yes | Yes | No  
  
### Role permissions for Flink Statements¶

Role Name: Role Scope | Create/Update Flink Statement | Delete Flink Statement | View Flink Statement and access Web UI | Add new role-bindings  
---|---|---|---|---  
super.user: Cluster-level | Yes | Yes | Yes | Yes  
SystemAdmin: Cluster-level | Yes | Yes | Yes | Yes  
ClusterAdmin: Cluster-level | Yes | Yes | Yes | No  
UserAdmin: Cluster-level | No | No | No | Yes  
ResourceOwner: Resource-level | Yes | Yes | Yes | Yes  
DeveloperRead: Resource-level | No | No | No | No  
DeveloperManage: Resource-level | Yes | Yes | Yes | No  
  
Note

You can access Flink Statement Results and Exceptions only when you have edit permission on the corresponding Statement.

### Role permissions for Flink Compute Pools¶

The following table shows the roles that have access to Flink Compute Pool resources:

Role Name: Role Scope | Create/Update Flink Compute Pool | Delete Compute Pool | View Compute Pool | Add new Compute Pool  
---|---|---|---|---  
super.user: Cluster-level | Yes | Yes | Yes | Yes  
SystemAdmin: Cluster-level | Yes | Yes | Yes | Yes  
ClusterAdmin: Cluster-level | Yes | Yes | Yes | No  
UserAdmin: Cluster-level | No | No | No | Yes  
ResourceOwner: Resource-level | Yes | Yes | Yes | Yes  
DeveloperRead: Resource-level | No | No | Yes | No  
DeveloperManage: Resource-level | Yes | Yes | Yes | No  
  
### Role permissions for Flink Catalogs¶

The following table shows the roles that have access to Flink Catalog resources:

Role Name: Role Scope | Create/Update Flink Catalog | Delete Flink Catalog | View Flink Catalog | Add new role-bindings  
---|---|---|---|---  
SystemAdmin: Cluster-level | Yes | Yes | Yes | Yes  
ClusterAdmin: Cluster-level | Yes | Yes | Yes | No  
UserAdmin: Cluster-level | No | No | No | Yes  
ResourceOwner: Resource-level | Yes | Yes | Yes | Yes  
DeveloperRead: Resource-level | No | No | Yes | No  
DeveloperManage: Resource-level | Yes | Yes | Yes | No  
  
### Role Permissions for Flink Secrets¶

The following table shows the roles that have access to Flink Secret resources:

Role Name: Role Scope | Create/Update Flink Secret | Delete Flink Secret | View Flink Secret | Add new role-bindings  
---|---|---|---|---  
SystemAdmin: Cluster-level | Yes | Yes | Yes | Yes  
ClusterAdmin: Cluster-level | Yes | Yes | Yes | No  
UserAdmin: Cluster-level | No | No | No | Yes  
ResourceOwner: Resource-level | Yes | Yes | Yes | Yes  
DeveloperRead: Resource-level | No | No | Yes | No  
DeveloperManage: Resource-level | Yes | Yes | Yes | No  
  
The following roles do not have access to the CMF resources:

  * SecurityAdmin
  * AuditAdmin
  * Operator
  * DeveloperWrite

## Example Scenarios¶

Following are example scenarios and how to create role binding for those scenarios.

**Scenario** : A system administrator (u-admin) needs to manage permissions to all the Flink environments, but doesn’t need to create, update, view, or delete the environments

    confluent iam rbac role-binding create \
    --principal User:u-admin \
    --role UserAdmin \
    --cmf CMF-id

**Scenario** : A team manager needs to manage all the permissions for the Flink applications in the Flink environment confluent, but doesn’t need to create, update, view, or delete the applications.

    confluent iam rbac role-binding create \
    --principal User:u-manager \
    --role UserAdmin \
    --cmf CMF-id \
    --flink-environment confluent

Note

As you must have observed from the above example, granting UserAdmin on CMF level only allows managing permissions for the Flink environments. In order to manage permissions for the Flink applications in specific environment, you need to grant UserAdmin on the Flink environment level.

**Scenario** : A team lead needs to manage all Flink applications in an environment.

    confluent iam rbac role-binding create \
        --principal User:u-teamlead \
        --role DeveloperManage \
        --cmf CMF-id \
        --flink-environment prod-env \
        --resource FlinkApplication:"*"

This role binding will allow the team lead to manage all Flink applications in the prod-env environment, including creating and updating applications. However, for editing the applications, the lead might also need to be able to view the environment, because the defaults for the application come from the environment. For more information, see [Configure Environments in Confluent Manager for Apache Flink](environments.html#cmf-environments) and [Deploy and Manage Confluent Manager for Apache Flink Applications](../jobs/applications/overview.html#cmf-applications). To allow this, you can add a role binding for the DeveloperRead role for the environment.

    confluent iam rbac role-binding create \
        --principal User:u-teamlead \
        --role DeveloperRead \
        --cmf CMF-id \
        --resource FlinkEnvironment:prod-env

**Scenario** : A developer needs to manage a specific Flink application.

    confluent iam rbac role-binding create \
        --principal User:u-developer \
        --role DeveloperManage \
        --cmf CMF-id \
        --flink-environment prod-env \
        --resource FlinkApplication:my-flink-app

    confluent iam rbac role-binding create \
        --principal User:u-developer \
        --role DeveloperRead \
        --cmf CMF-id \
        --resource FlinkEnvironment:prod-env

If you want to prevent the developer from viewing the environment, you can remove the second role binding.

**Scenario** : On-call team needs access to all applications across all environments, but does not need to manage permissions on either the applications or the environments.

    confluent iam rbac role-binding create \
        --principal User:u-oncall \
        --role ClusterAdmin \
        --cmf CMF-id

For each environment:

    confluent iam rbac role-binding create \
        --principal User:u-oncall \
        --role ClusterAdmin \
        --cmf CMF-id \
        --flink-environment <environment-name>

Note

This permission also allows the on call team to create new environments. If you want to restrict this, you should create a ClusterAdmin for each environment. Another thing to note is that this role will still allow the user to create a new environment with the name prod-env if it doesn’t already exist.

    confluent iam rbac role-binding create \
        --principal User:u-oncall \
        --role ClusterAdmin \
        --cmf CMF-id \
        --flink-environment prod-env

**Scenario** : A developer needs to delete stale environments.

    confluent iam rbac role-binding create \
        --principal User:u-developer \
        --role SystemAdmin \
        --cmf CMF-id

