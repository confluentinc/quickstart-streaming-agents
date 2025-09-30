---
document_id: flink_concepts_flink-private-networking_chunk_1
source_file: flink_concepts_flink-private-networking.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/flink-private-networking.html
title: Private Networking with Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 3
---

# Private Networking with Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® supports private networking on AWS, Azure, and Google Cloud. This feature enables Flink to securely read and write data stored in Confluent Cloud clusters that are located in private networking, with no data flowing to the public internet. With private networking, you can use Flink and Apache Kafka® together for stream processing in Confluent Cloud, even in the most stringent regulatory environments.

Confluent Cloud for Apache Flink supports private networking for AWS and Azure in all regions where Flink is supported. Google Cloud supports private networking in most regions where Flink is supported. For the regions that support Flink private networking, see [Supported Cloud Regions](../reference/cloud-regions.html#flink-cloud-regions).

## Connectivity options¶

There are a number of ways to access Flink with private networking. In all cases, they allow access to all types of private clusters (Enterprise, Dedicated, Freight), with all types of connectivity (VNET/VPC, Peering, Transit Gateway, PNI).

  * PrivateLink Attachment: Works with any type of cluster and is available on AWS and Azure.
  * Confluent Cloud network (CCN): Available on AWS for all types of network and Azure for Private Links.
    * If you already have an existing Confluent Cloud network, this is the easiest way to get started, but it works only on AWS when a Confluent Cloud network is already configured.
    * If you need to create a new Confluent Cloud network, follow the steps in [Create Confluent Cloud Network on AWS](../../networking/ccloud-network/aws.html#create-ccloud-network-aws).

### PrivateLink Attachment¶

A PrivateLink Attachment is a resource that enables you to connect to Confluent serverless products, like Enterprise clusters and Flink.

For Flink, the new PrivateLink Attachment is used only to establish a connection between your clients (like Cloud Console UI, Confluent CLI, Terraform, apps using the Confluent REST API) and Flink. Flink-to-Kafka is routed internally within Confluent Cloud. As a result, this PLATT is used only for submitting statements and fetching results from the client.

  * For Dedicated clusters, regardless of the Kafka cluster connection type (Private Link, Peering, or Transit Gateway), Flink requires that you define a PLATT in the same region of the cluster, even if a private link exists for the Dedicated cluster.
  * For Enterprise clusters, you can reuse the same PLATT used by your Enterprise clusters.

By creating a PrivateLink Attachment to a Confluent Cloud environment in a region, you are enabling Flink statements created in that environment to securely access data in any of the Flink clusters in the same region, regardless of their environment. Access to the Flink clusters is governed by RBAC.

Also, a PrivateLink Attachment enables your data-movement components in Confluent Cloud, including Flink statements and cluster links, to move data between all of the private networks in the organization, including the Confluent Cloud networks associated with any Dedicated Kafka clusters.

For more information, see [Enable private networking with PrivateLink Attachment](../operate-and-deploy/private-networking.html#flink-sql-enable-private-networking-pla).

### Confluent Cloud network (CCN)¶

If you have an existing [Confluent Cloud network](../../networking/overview.html#ccloud-network-overview), this is the easiest way to get set up, but it works only on AWS and Azure when a Confluent Cloud network is configured already and at least one Kafka Dedicated cluster exists in the environment and region where you need to use Flink.

For existing Kafka Dedicated users, this option requires no effort to configure, if everything is already configured for Kafka.

If a reverse proxy is not set up, this requires setup for Flink or the use of a VM within the VPC to access Flink.

To create a Confluent Cloud network, follow the steps in [Create Confluent Cloud Network on AWS](../../networking/ccloud-network/aws.html#create-ccloud-network-aws).

For more information, see [Enable private networking with Confluent Cloud Network](../operate-and-deploy/private-networking.html#flink-sql-enable-private-networking-ccn).
