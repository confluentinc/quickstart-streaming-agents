---
document_id: flink_operate-and-deploy_generate-api-key-for-flink_chunk_1
source_file: flink_operate-and-deploy_generate-api-key-for-flink.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/generate-api-key-for-flink.html
title: Generate an API key for Programmatic Access to Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 3
---

# Generate an API Key for Access in Confluent Cloud for Apache Flink¶

To manage Flink workloads programmatically in Confluent Cloud for Apache Flink®, you need an API key that’s specific to Flink. You can use the Confluent CLI, the Confluent Cloud APIs, the Confluent Terraform Provider, or the Cloud Console to create API keys.

Before you create an API key for Flink access, decide whether you want to create long-running statements. If you need long-running statements, you should use a [service account](../../security/authenticate/workload-identities/service-accounts/overview.html#service-accounts) and create an API key for it. If you only need to run interactive queries or run statements for a short time while developing queries, you can create an API key for your user account.

A Flink API key is scoped to an environment and region pair, for example, `env-abc123.aws.us-east-2`. The key enables creating, reading, updating, and deleting Flink SQL statements.

To create an API key for Flink access by using the Confluent Cloud APIs or the Confluent Terraform Provider, you must first create a Cloud API key. This step is done automatically if you use the Confluent CLI to create an API key for Flink access.

## Create a service account (optional)¶

If you need to create long-running Flink SQL statements, create a service account principal before you create a Flink API key.

  1. Create a service account by using the [Cloud Console](../../security/authenticate/workload-identities/service-accounts/create-service-accounts.html#create-service-accounts) or the [CLI](../../security/authenticate/workload-identities/service-accounts/manage-service-accounts.html#create-service-accounts-cloud-cli).

  2. Assign the OrganizationAdmin role to the service account by following the steps in [Add a role binding to a principal](../../security/access-control/rbac/manage-role-bindings.html#cloud-rbac-assign-role-to-user).

  3. Store the service account ID in a convenient location, for example, in an environment variable:

         export PRINCIPAL_ID="<service-account-id>"
