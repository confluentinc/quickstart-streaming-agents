---
document_id: flink_configure_access-control_chunk_2
source_file: flink_configure_access-control.md
source_url: https://docs.confluent.io/platform/current/flink/configure/access-control.html
title: Access Control for Confluent Manager for Apache Flink
chunk_index: 2
total_chunks: 3
---

Flink Statement * Flink ComputePool

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
