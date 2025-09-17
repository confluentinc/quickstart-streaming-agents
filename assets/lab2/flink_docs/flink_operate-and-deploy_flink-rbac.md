---
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/flink-rbac.html
title: Grant Role-Based Access for Flink SQL Statements in Confluent Cloud for Apache Flink
hierarchy: ['operate-and-deploy', 'flink-rbac.html']
scraped_date: 2025-09-05T13:45:46.328086
---

# Grant Role-Based Access in Confluent Cloud for Apache Flink¶

When deploying Flink SQL statements in production, you must configure appropriate access controls for different types of users and workloads. Confluent Cloud for Apache Flink® supports [Role-based Access Control (RBAC)](../../security/access-control/rbac/overview.html#cloud-rbac) with these roles:

  * [FlinkAdmin](../../security/access-control/rbac/predefined-rbac-roles.html#flinkadmin-role): Full access to Flink resources and compute pool management
  * [FlinkDeveloper](../../security/access-control/rbac/predefined-rbac-roles.html#flinkdeveloper-role): Limited access for running statements but not managing infrastructure
  * [Assigner](../../security/access-control/rbac/predefined-rbac-roles.html#assigner-role): Enables delegation of statement execution to service accounts

**Layered permission model:** Flink permissions follow a layered approach. Start with base permissions required for all Flink operations, then add additional layers based on what users need to accomplish.

**Operational considerations:** Use service accounts for production workloads and apply least-privilege principles by granting only the permissions needed for each use case.

For complete role definitions, see [Predefined RBAC Roles](../../security/access-control/rbac/predefined-rbac-roles.html#cloud-rbac-roles).

  * Permission layers
  * Common user scenarios
  * Production best practices
  * Access for UDF Logging
  * Audit log events
  * Reference

## Permission layers¶

Flink permissions follow a layered approach, in which each layer builds upon the previous one. This design enables you to grant only the permissions needed for each use case, following the principle of least privilege.

These are the permission layers:

  * Base/required layer: Fundamental permissions needed for all Flink operations
  * Data access layer: Read and write access to specific tables and topics
  * Table management layer: Create, alter, and delete tables
  * Administrative layer: Manage compute pools and infrastructure
  * Logging permissions layer: Access to UDF logs and audit events

Start with the base layer and add additional layers as needed for your specific use cases.

### Base/required layer¶

All Flink user accounts need these permissions.

#### Flink access¶

Choose the appropriate Flink role based on the user’s responsibilities:

  * **FlinkDeveloper:** Can create and run statements, manage workspaces and artifacts, but can’t manage compute pools
  * **FlinkAdmin:** All FlinkDeveloper capabilities plus compute pool management (create, delete, alter compute pool settings)

Run the following commands to grant the necessary permissions.

    # For most users (statement execution and development)
    confluent iam rbac role-binding create \
      --environment ${ENV_ID} \
      --principal User:${USER_ID} \
      --role FlinkDeveloper
    
    # For infrastructure administrators
    confluent iam rbac role-binding create \
      --environment ${ENV_ID} \
      --principal User:${USER_ID} \
      --role FlinkAdmin

#### Kafka Transactional-Id permissions¶

Flink uses Kafka transactions to ensure exactly-once processing semantics. All Flink statements require:

  * **DeveloperRead** on Transactional-Id `_confluent-flink_*` (to read transaction state)
  * **DeveloperWrite** on Transactional-Id `_confluent-flink_*` (to create and manage transactions)

Run the following commands to grant the necessary permissions.

    # Read transaction state
    confluent iam rbac role-binding create \
      --role DeveloperRead \
      --principal User:${USER_ID} \
      --environment ${ENV_ID} \
      --cloud-cluster ${KAFKA_ID} \
      --kafka-cluster ${KAFKA_ID} \
      --resource Transactional-Id:_confluent-flink_ \
      --prefix
    
    # Create and manage transactions
    confluent iam rbac role-binding create \
      --role DeveloperWrite \
      --principal User:${USER_ID} \
      --environment ${ENV_ID} \
      --cloud-cluster ${KAFKA_ID} \
      --kafka-cluster ${KAFKA_ID} \
      --resource Transactional-Id:_confluent-flink_ \
      --prefix

### Data access layer¶

The data access layer provides permissions for reading from and writing to existing tables in your Flink statements. This layer builds on the base layer and adds specific access to Kafka topics and Schema Registry subjects that your statements need to interact with.

#### Read from existing tables¶

When your Flink SQL statements read from tables, for example, by using a `SELECT * FROM my_table` statement, you need these roles:

  * **DeveloperRead** on the Kafka topic
  * **DeveloperRead** on the Schema Registry subject

Run the following commands to grant the necessary permissions.

    # Kafka topic read permission
    confluent iam rbac role-binding create \
      --role DeveloperRead \
      --principal User:${USER_ID} \
      --environment ${ENV_ID} \
      --cloud-cluster ${KAFKA_ID} \
      --kafka-cluster ${KAFKA_ID} \
      --resource Topic:${TOPIC_NAME}
    
    # Schema Registry subject read permission
    confluent iam rbac role-binding create \
      --role DeveloperRead \
      --principal User:${USER_ID} \
      --environment ${ENV_ID} \
      --cloud-cluster ${SR_ID} \
      --schema-registry-cluster ${SR_ID} \
      --resource Subject:${SUBJECT_NAME}

#### Write to existing tables¶

When your Flink SQL statements write to tables, for example, by using an `INSERT INTO my_sink_table` statement, you need the following roles:

  * **DeveloperWrite** on the Kafka topic
  * **DeveloperRead** on the Schema Registry subject, to validate data format

Run the following commands to grant the necessary permissions.

    # Kafka topic write permission
    confluent iam rbac role-binding create \
      --role DeveloperWrite \
      --principal User:${USER_ID} \
      --environment ${ENV_ID} \
      --cloud-cluster ${KAFKA_ID} \
      --kafka-cluster ${KAFKA_ID} \
      --resource Topic:${TOPIC_NAME}
    
    # Schema Registry subject read permission, to validate data format
    confluent iam rbac role-binding create \
      --role DeveloperRead \
      --principal User:${USER_ID} \
      --environment ${ENV_ID} \
      --cloud-cluster ${SR_ID} \
      --schema-registry-cluster ${SR_ID} \
      --resource Subject:${SUBJECT_NAME}

### Table management layer¶

The table management layer provides permissions for creating and modifying tables in your Flink statements. This layer builds on the data access layer and adds specific access to Kafka topics and Schema Registry subjects that your statements need to interact with.

#### Create new tables¶

When your Flink SQL statements create new tables, for example, by using a `CREATE TABLE` or `CREATE TABLE AS SELECT` statement, you need the following roles:

  * **DeveloperManage** on Kafka topics, to create topics
  * **DeveloperWrite** on Schema Registry subjects, to create schemas

Run the following commands to grant the necessary permissions.

    # Kafka topic create/manage permission
    confluent iam rbac role-binding create \
      --role DeveloperManage \
      --principal User:${USER_ID} \
      --environment ${ENV_ID} \
      --cloud-cluster ${KAFKA_ID} \
      --kafka-cluster ${KAFKA_ID} \
      --resource Topic:${TABLE_PREFIX} \
      --prefix
    
    # Schema Registry subject create/write permission
    confluent iam rbac role-binding create \
      --role DeveloperWrite \
      --principal User:${USER_ID} \
      --environment ${ENV_ID} \
      --cloud-cluster ${SR_ID} \
      --schema-registry-cluster ${SR_ID} \
      --resource Subject:${TABLE_PREFIX} \
      --prefix

#### Modify existing tables¶

When your Flink SQL statements modify table structures, for example, by using an `ALTER TABLE` statement for watermarks, computed columns, or column type changes, you need the following roles:

  * **DeveloperManage** on the Kafka topic, for table structure changes
  * **DeveloperWrite** on the Schema Registry subject, for schema evolution

Run the following commands to grant the necessary permissions.

    # Kafka topic manage permission, for table structure changes
    confluent iam rbac role-binding create \
      --role DeveloperManage \
      --principal User:${USER_ID} \
      --environment ${ENV_ID} \
      --cloud-cluster ${KAFKA_ID} \
      --kafka-cluster ${KAFKA_ID} \
      --resource Topic:${TABLE_NAME}
    
    # Schema Registry subject write permission, for schema evolution
    confluent iam rbac role-binding create \
      --role DeveloperWrite \
      --principal User:${USER_ID} \
      --environment ${ENV_ID} \
      --cloud-cluster ${SR_ID} \
      --schema-registry-cluster ${SR_ID} \
      --resource Subject:${TABLE_NAME}

### Administrative layer¶

The administrative layer provides permissions for managing Flink compute pools and infrastructure. This layer builds on the table management layer and adds specific access to Flink resources that your statements need to interact with.

The following roles can manage Flink compute pools and infrastructure.

FlinkAdmin

This role is for Flink-specific administrative access. It provides these capabilities:

  * Manage compute pools (create, delete, and alter compute pool settings)
  * All FlinkDeveloper capabilities (statements, workspaces, and artifacts)
  * Most common choice for Flink-focused administrators

EnvironmentAdmin

This role provides environment-wide administrative access. It provides these capabilities:

  * All Flink administrative capabilities plus broader environment management
  * Typically assigned for other reasons (managing multiple services in an environment)

OrganizationAdmin

This role provides organization-wide administrative access. It provides these capabilities:

  * All Flink administrative capabilities plus organization-wide management
  * Typically assigned for other reasons, like managing the entire organization

Use FlinkAdmin for users who primarily manage Flink infrastructure.

Users with EnvironmentAdmin or OrganizationAdmin roles already have the necessary Flink administrative capabilities.

For complete role definitions and capabilities, see [Predefined RBAC Roles in Confluent Cloud](../../security/access-control/rbac/predefined-rbac-roles.html#cloud-rbac-roles).

### Logging permissions layer¶

The logging permissions layer provides permissions for accessing [UDF logs](../how-to-guides/enable-udf-logging.html#flink-sql-enable-udf-logging) and [audit events](../../monitoring/audit-logging/event-methods/flink.html#event-methods-flink) related to your Flink statements. This layer builds on the administrative layer and adds specific access to Kafka topics that your statements need to interact with.

#### UDF logging access¶

To access UDF logs, you need these roles:

  * **FlinkAdmin** or **FlinkDeveloper** role: provides describe access to UDF logs
  * **DeveloperRead** on the UDF log topics: to read the actual log messages
  * **CloudClusterAdmin** role: can manage logging settings by enabling or disabling logging

Run the following command to grant the necessary permissions.

    confluent iam rbac role-binding create \
      --role DeveloperRead \
      --principal User:${USER_ID} \
      --environment ${ENV_ID} \
      --cloud-cluster ${LOGGING_KAFKA_ID} \
      --kafka-cluster ${LOGGING_KAFKA_ID} \
      --resource Topic:${UDF_LOG_TOPIC}

## How Flink permissions work¶

Understanding the Flink permission model helps you make informed decisions about access control and troubleshoot permission issues effectively.

### Principal-Based Access Control¶

Flink uses a _principal-based_ permission model, in which statements inherit all permissions from the principal that runs them. The principal can be a user or a service account.

The following key concepts help you understand how Flink permissions work.

  * **Statements are not principals** \- A Flink SQL statement doesn’t have its own permissions. It uses the permissions of the principal that runs it.
  * **Flexible principal assignment** \- You can run statements under your user account, which is recommended for ad-hoc queries, or under a service account, which is recommended for production workloads.
  * **Permission inheritance** \- A statement can access any data that the principal has permissions to access in that region, even across environments.

For example, if a service account has DeveloperRead on topics in multiple environments, any statement running under this service account can read from topics in all of these environments, when in the same region.

### Separation of control plane and data plane access¶

Flink separates access into two distinct planes: the control plane and the data plane. Understanding this separation is key to configuring permissions correctly.

#### Control plane access (infrastructure)¶

This is managed by Flink-specific roles and governs what actions you can perform within the Flink service.

Control plane access has these characteristics:

  * Controls who can create statements, manage compute pools, and other Flink resources
  * Managed by using FlinkAdmin and FlinkDeveloper roles
  * Environment-scoped permissions, which apply to all environments in an organization, and organization-scoped permissions, which apply to all environments in an organization

#### Data plane access (data)¶

This is managed by Kafka and Schema Registry roles and governs which data that your Flink statements can interact with.

Data plane access has these characteristics:

  * Controls which data your statements can read from and write to
  * Managed by using DeveloperRead, DeveloperWrite, and DeveloperManage roles
  * Resource-scoped permissions (topics, subjects)

Data plane access is important because a user needs permissions on both planes to execute a Flink SQL statement successfully. For example, a user might have the FlinkDeveloper role (control plane access to create a statement), but if they lack DeveloperRead on a source topic (data plane access), the statement fails at runtime. In contrast, a principal with extensive data access but no Flink role can’t create statements in the first place.

### Compute pools as shared infrastructure¶

It’s important to understand that compute pools are resources, not principals.

  * A compute pool provides the computational infrastructure for running statements.
  * Compute pools don’t have their own permissions or identity.
  * Multiple users can share the same compute pool if they have appropriate Flink roles.
  * The _principal running the statement_ determines data access, not the compute pool.

For example, users Alice and Bob both have the FlinkDeveloper role and can use the same compute pool. Alice’s statements access data based on Alice’s permissions, while Bob’s statements use Bob’s permissions, even when running on the same compute pool.

### Cross-environment data access¶

Flink statements can access data across environment boundaries based on the principal’s permissions.

For example, a statement in Environment A can read from topics in Environment B if the principal has:

  * FlinkDeveloper role in Environment A, to create the statement
  * DeveloperRead role on the topics in Environment B, to access the data

Cross-environment data access is important in these use cases:

  * Cross-environment analytics and reporting
  * Data pipeline orchestration across multiple environments
  * Centralized processing with distributed data sources

Important

Grant cross-environment permissions carefully, because a statement has broad access based on its principal’s permissions.

## Common user scenarios¶

This section describes common user scenarios and the required permission configurations for each. These scenarios follow the layered permission model, starting with base permissions and adding additional layers as needed.

Choose the scenario that best matches your use case, then follow the corresponding permission setup instructions.

### Developers¶

Assign the following permissions to developer accounts:

  * Base/Required Layer (Flink Developer role + Transactional-Id permissions)
  * Data Access Layer (read/write access to existing tables)
  * Table Management Layer (for creating and modifying tables)

Run the commands shown in the previous sections to grant the necessary permissions.

### Production workloads (service accounts)¶

For automated deployments and long-running statements, use service accounts to ensure stable identity that isn’t affected by changes to user accounts.

#### Setup options¶

Broad-access approach

  1. Create a service account and grant the EnvironmentAdmin role.
  2. Grant a user the Assigner role on the service account.
  3. Deploy statements using the service account.

Least-privilege approach

  1. Create a service account and grant base/required layer permissions.
  2. Grant specific Data Access Layer and Table Management Layer permissions as needed.
  3. Grant a user account the Assigner role on the service account.

Run the following commands to grant the necessary permissions.

    # Create service account
    confluent iam service-account create ${SA_NAME} \
      --description "${SA_DESCRIPTION}"
    
    # Broad access: Grant EnvironmentAdmin role
    confluent iam rbac role-binding create \
      --environment ${ENV_ID} \
      --principal User:${SERVICE_ACCOUNT_ID} \
      --role EnvironmentAdmin
    
    # Grant user Assigner role (for both approaches)
    confluent iam rbac role-binding create \
      --principal User:${USER_ID} \
      --resource service-account:${SERVICE_ACCOUNT_ID} \
      --role Assigner

For the least-privilege approach, run the commands in the previous layer sections, using the service account as the principal instead of a user account.

### Administrators (infrastructure management)¶

For managing compute pools and Flink infrastructure, grant an administrative layer role.

These are the administrative roles that can manage Flink infrastructure:

  * **FlinkAdmin** : Most common choice for Flink-focused administrators
  * **EnvironmentAdmin** : If they already manage other services in the environment
  * **OrganizationAdmin** : If they already manage the entire organization

## Production best practices¶

Grant permissions incrementally, starting with base permissions and adding additional layers as needed for your production use cases.

  1. **Start with base/required layer** \- Grant fundamental Flink and Kafka permissions.
  2. **Add data access** \- Grant read/write access to existing tables as needed.
  3. **Add capabilities** \- Table management, administrative access as required.
  4. **Validate each layer** \- Test functionality after adding each permission layer.

### Service account delegation pattern¶

For automated deployments, run the following command to grant the Assigner role on production service accounts.

    # CI/CD service account with Assigner role on production service accounts
    confluent iam rbac role-binding create \
      --principal User:${CICD_SA_ID} \
      --resource service-account:${PROD_SA_ID} \
      --role Assigner

## Access for UDF Logging¶

  * OrganizationAdmin and EnvironmentAdmin roles have full permission to enable and disable custom code logging.
  * The FlinkAdmin and FlinkDeveloper roles have permission to describe custom code logs.
  * The CloudClusterAdmin role can disable logging and delete logs by deleting the Kafka cluster associated with the custom logging destination.
  * Any security principal that has READ permission to the destination Kafka cluster has READ access to the actual log topics.

## Audit log events¶

Auditable event methods for the `FLINK_WORKSPACE` and `STATEMENT` resource types are triggered by operations on a Flink workspace and generate event messages that are sent to the audit log cluster, where they are stored as event records in a Kafka topic.

For more information, see [Auditable Event Methods](../../monitoring/audit-logging/event-methods/flink.html#event-methods-flink).

## Reference¶

### Permission summary by layer¶

Layer | Kafka | Schema Registry | Flink  
---|---|---|---  
Base/Required | Transactional-Id | – | FlinkDeveloper OR FlinkAdmin  
Data Access | DeveloperRead/Write | DeveloperRead/Write | –  
Table Management | DeveloperManage | DeveloperWrite | –  
Administrative | – | – | FlinkAdmin, EnvironmentAdmin, or OrganizationAdmin  
Logging | DeveloperRead (UDF logs) | – | –  
  
### Access to Flink resources¶

The following table shows which Flink resources the RBAC roles can access. “CRUD” stands for “Create, Read, Update, Delete”.

Scope | Statements | Workspaces | Compute pools | Artifacts | User-defined functions | UDF logging | AI inference models | Kafka clusters | Kafka Topics  
---|---|---|---|---|---|---|---|---|---  
EnvironmentAdmin | CRUD | CRUD | CRUD | CRUD | CRUD | CRUD | CRUD | CRUD | CRUD  
FlinkAdmin | CRUD | CRUD | CRUD | CRUD | CRUD | -R– | CRUD | – | –  
FlinkDeveloper | CRUD | CRUD | -R– | CRUD | CRUD [1] | -R– | CRUD [1] | – | –  
OrganizationAdmin | CRUD | CRUD | CRUD | CRUD | CRUD | CRUD | CRUD | CRUD | CRUD  
[1]| _(1, 2)_ Requires access to cluster.  
---|---  
  
## Related content¶

  * [Auditable Event Methods](../../monitoring/audit-logging/event-methods/flink.html#event-methods-flink)
  * [DDL Statements](../concepts/statements.html#flink-sql-statements)
  * [Manage RBAC Role Bindings](../../security/access-control/rbac/manage-role-bindings.html#manage-rbac-role-bindings)
  * [Role-based Access Control (RBAC)](../../security/access-control/rbac/overview.html#cloud-rbac)
  * [Service Accounts](../../security/authenticate/workload-identities/service-accounts/overview.html#service-accounts)
  * [UDF logs](../how-to-guides/enable-udf-logging.html#flink-sql-enable-udf-logging)

Note

This website includes content developed at the [Apache Software Foundation](https://www.apache.org/) under the terms of the [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0.html).
