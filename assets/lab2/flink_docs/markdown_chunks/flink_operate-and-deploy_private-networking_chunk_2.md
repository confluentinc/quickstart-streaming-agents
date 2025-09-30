---
document_id: flink_operate-and-deploy_private-networking_chunk_2
source_file: flink_operate-and-deploy_private-networking.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/private-networking.html
title: Enable Private Networking with Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 2
---

shell and Confluent Cloud Console.

## Enable private networking with PrivateLink Attachment¶

Private networking with [PrivateLink Attachment](../concepts/flink-private-networking.html#flink-sql-private-networking-connectivity-options-pla) works with any type of cluster and is available on AWS and Azure.

### Prerequisites¶

* Access to Confluent Cloud.
* The [OrganizationAdmin](../../security/access-control/rbac/predefined-rbac-roles.html#organizationadmin-role), [EnvironmentAdmin](../../security/access-control/rbac/predefined-rbac-roles.html#environmentadmin-role), or [NetworkAdmin](../../security/access-control/rbac/predefined-rbac-roles.html#networkadmin-role) role to enable Flink private networking for an environment.
* A VPC in AWS, a VNet in Azure, or a VPC in Google Cloud.

### Overview¶

In this walkthrough, you perform the following steps.

  1. Set up a PrivateLink attachment
     1. Create a PrivateLink Attachment.
     2. Create a private endpoint.
        * For AWS, create a VPC Interface Endpoint to the PrivateLink Attachment.
        * For Azure, create a private endpoint that’s associated with the PrivateLink Attachment.
        * For Google Cloud, create a private endpoint that’s associated with the PrivateLink Attachment.
     3. Create a PrivateLink Attachment Connection.
     4. Set up DNS resolution.
  2. Connect to the private network: If your client is not in the VPC or VNet, enable the Cloud Console or Confluent CLI to connect to your private network.

When the previous steps are completed, you can use Flink over your private network from the Confluent Cloud Console or Confluent CLI. The experience is the same as with public networking.

### Step 1: Set up a PrivateLink Attachment and connection¶

In AWS, Azure, or Google Cloud, follow these steps to create a PrivateLink Attachment, a private endpoint, a PrivateLink Attachment Connection, and set up a DNS resolution.

AWSAzureGoogle Cloud

  1. In Confluent Cloud, create a [PrivateLinkAttachment](../../networking/aws-platt.html#privatelinkattachment-create).
  2. In AWS, create a [VPC Interface Endpoint to the PrivateLinkAttachment service](../../networking/aws-platt.html#privatelinkattachment-endpoint-create).
  3. In Confluent Cloud, create a [PrivateLinkAttachmentConnection](../../networking/aws-platt.html#privatelinkattachment-connection-create).
  4. Set up a [DNS resolution](../../networking/aws-platt.html#privatelinkattachment-dns).

  1. In Confluent Cloud, create a [PrivateLinkAttachment](../../networking/azure-platt.html#privatelinkattachment-create-az).
  2. In Azure, create a [private endpoint](../../networking/azure-platt.html#privatelinkattachment-endpoint-create-az).
  3. In Confluent Cloud, create a [PrivateLinkAttachmentConnection](../../networking/azure-platt.html#privatelinkattachment-connection-create-az).
  4. Set up a [DNS resolution](../../networking/azure-platt.html#privatelinkattachment-dns-az).

  1. In Confluent Cloud, create a [PrivateLinkAttachment](../../networking/gcp-platt.html#privatelinkattachment-create-gc).

PrivateLink Attachments are powered by Private Service Connect.

  2. In Google Cloud, [create a Private Service Connect endpoint](../../networking/gcp-platt.html#private-service-connect-gc-create-endpoint-esku) to the service attachment URI you get in Step 1.

If you use the Confluent Cloud Console for configuration, this step is merged into the next step and shows up as the first and second steps in access point creation.

  3. In Confluent Cloud, [create a PrivateLink Attachment Connection](../../networking/gcp-platt.html#private-service-connect-gc-create-connection-esku) for the Private Service Connect endpoint you created.

A PrivateLink Attachment Connection is required for each Private Service Connect endpoint.

  4. Set up a [DNS resolution](../../networking/gcp-platt.html#private-service-connect-gc-dns-records-esku).

### Step 2: Connect to the network with Cloud Console or Confluent CLI¶

If your client is not in the VPC or VNet, enable the Confluent Cloud Console or Confluent CLI to connect to your private network.

If you don’t connect from a machine in the VPC or VNet, you see the following error.

To connect to Confluent Cloud with your PrivateLink Attachment, see [Use Confluent Cloud with Private Networking](../../networking/ccloud-console-access.html#ccloud-console-access-networking).

One way to connect is to set up a [reverse proxy](../../networking/ccloud-console-access.html#proxied-access).

  1. Create an EC2 instance.

  2. Connect to the instance with SSH.

  3. Install NGINX.

  4. Configure Routing Table.

  5. Set up DNS resolution: point to the Flink regional endpoints you use, as described in Step 6 of [Configure a proxy](../../networking/ccloud-console-access.html#proxied-access).

         <Public IP Address of VM instance> <Flink-private-endpoint>

`<Flink-private-endpoint>` will resemble `flink.<region>.<cloud>.private.confluent.cloud`, for example: `flink.us-east-2.aws.private.confluent.cloud`.

Find the DNS part of the PrivateLink Attachment by navigating to your environment’s **Network management** page and finding the **DNS domain** setting.

You can find the full list of supported Flink regions by using the [Regions endpoint API](flink-rest-api.html#flink-rest-api-list-regions).

Once networking is set up in Cloud Console, the interface uses the correct endpoint automatically, either public or private, based on the presence of a PrivateLink Attachment. If the connection is private, access to the Flink private network works transparently.
