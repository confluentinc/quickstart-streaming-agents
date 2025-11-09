---
document_id: flink_configure_access-control_chunk_3
source_file: flink_configure_access-control.md
source_url: https://docs.confluent.io/platform/current/flink/configure/access-control.html
title: Access Control for Confluent Manager for Apache Flink
chunk_index: 3
total_chunks: 3
---

AuditAdmin * Operator * DeveloperWrite

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
