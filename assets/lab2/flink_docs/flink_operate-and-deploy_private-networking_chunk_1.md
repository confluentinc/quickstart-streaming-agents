---
document_id: flink_operate-and-deploy_private-networking_chunk_1
source_file: flink_operate-and-deploy_private-networking.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/private-networking.html
title: Enable Private Networking with Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 2
---

# Enable Private Networking with Confluent Cloud for Apache Flink¶

You have these options for using private networking with Confluent Cloud for Apache Flink®.

  * [PrivateLink Attachment](../concepts/flink-private-networking.html#flink-sql-private-networking-connectivity-options-pla): Works with any type of cluster and is available on AWS, Azure, and Google Cloud. For more information, see [Supported Cloud Regions](../reference/cloud-regions.html#flink-cloud-regions).
  * Existing or new [Confluent Cloud network (CCN)](../concepts/flink-private-networking.html#flink-sql-private-networking-connectivity-options-ccn): Available on AWS and Azure. To create a new Confluent Cloud network, follow the steps in [Create Confluent Cloud Network on AWS](../../networking/ccloud-network/aws.html#create-ccloud-network-aws).

For more information, see [Private Networking with Confluent Cloud for Apache Flink](../concepts/flink-private-networking.html#flink-sql-private-networking).

## Enable private networking with Confluent Cloud Network¶

If you already have a [Confluent Cloud Network (CCN)](../../networking/ccloud-network/aws.html#create-ccloud-network-aws) created and configured, which is usually the case when you have any Dedicated cluster, you can use this network directly to connect to Flink.

No setup, or minimum setup, is required to configure Flink, because you can reuse connectivity to existing Private Endpoints, Peering, or Transit Gateway. To access Flink from your local client, follow these steps.

### Prerequisites¶

  * Access to Confluent Cloud.
  * The [OrganizationAdmin](../../security/access-control/rbac/predefined-rbac-roles.html#organizationadmin-role), [EnvironmentAdmin](../../security/access-control/rbac/predefined-rbac-roles.html#environmentadmin-role), or [NetworkAdmin](../../security/access-control/rbac/predefined-rbac-roles.html#networkadmin-role) role to enable Flink private networking for an environment.

### Configure DNS resolution¶

  1. Ensure your VPC is configured to route your unique Flink endpoint to Confluent Cloud.

  2. Have a client that is running within the VPC, or a proxy that reroutes your client to the VPC. For more information, see [Use the Confluent Cloud Console with Private Networking](../../networking/ccloud-console-access.html#ccloud-console-access-networking).

If you already configured 1 and 2 for Apache Kafka® you may not need any changes.

     * For public DNS resolution with endpoints that resemble `flink-<network>.<region>.<cloud>.private.confluent.cloud`: if your local machine was already configured to access Kafka, no additional setup is necessary.

     * **With PrivateLink only:** For private DNS resolution with endpoints that resemble `flink.<network>.<region>.<cloud>.private.confluent.cloud`, if routing is using `*.<network>.<region>.<cloud>.private.confluent.cloud`, no additional setup is necessary, but if your routing is using a more specific URL, you must add the Flink endpoint to your routing rules. Note that if you use a reverse proxy with a custom route added to your local host file, you must add the Flink endpoint to your host file.

Routing to `flinkpls...confluent.cloud` is necessary to enable auto-completion and error highlighting in the Flink SQL shell and Confluent Cloud Console.
