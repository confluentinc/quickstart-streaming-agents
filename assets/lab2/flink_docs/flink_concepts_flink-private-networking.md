---
source_url: https://docs.confluent.io/cloud/current/flink/concepts/flink-private-networking.html
title: Private Networking with Confluent Cloud for Apache Flink
hierarchy: ['concepts', 'flink-private-networking.html']
scraped_date: 2025-09-05T13:45:54.855378
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

## Protect resources with IP Filtering¶

With IP Filtering, you can enhance security for your Flink resources (statements and workspaces) based on trusted source IP addresses. IP Filtering is an authorization feature that allows you to create IP filters for your Confluent Cloud organization that permit inbound requests only from specified IP groups. All incoming API requests that originate from IP addresses not included in your IP filters are denied.

For Flink resources, you can implement the following access controls:

  * **No public networks:** Select the predefined No Public Networks group (`ipg-none`) to block all public network access, allowing access only from private network connections. This IP group cannot be combined with other IP groups in the same filter.
  * **Public:** The default option if no IP filters are set. Flink statements and workspaces are accessible from all source networks when connecting over the public internet. While SQL queries are visible, private cluster data remains protected, and you can’t issue statements accessing private clusters.
  * **Public with restricted IP list:** Create custom IP groups containing specific CIDR blocks to allow access only from trusted networks while maintaining the same protection for private cluster data.

IP Filtering applies only to requests made over public networks and doesn’t limit requests made over private network connections. When creating IP filters for Flink resources, select the [Flink operation group](../../security/access-control/ip-filtering/manage-ip-filters.html#flink-operation-group-api-operations) to control access to all operations related to Apache Flink data.

For more information on setting IP filters, see [IP Filtering](../../security/access-control/ip-filtering/overview.html#ip-filtering) and [Manage IP Filters](../../security/access-control/ip-filtering/manage-ip-filters.html#manage-ip-filters).

The IP Filtering feature replaces the previous distinction between public and private Flink statements and workspaces. Administrators can modify access controls at any time by updating IP filters.

For data protection in Kafka clusters, access is governed by network settings of the cluster:

  * You can always read public data regardless of the connectivity, whether public or private.
  * To read or write data in a private cluster, the cluster must use private connectivity.
  * To prevent data exfiltration, you can’t write to public clusters when using private connectivity.

## Available endpoints for an environment and region¶

The following section shows the endpoints that are available for connecting to Flink. While the public endpoint is always present, others may require some effort to be created.

  * Public endpoint
  * PrivateLink Attachment
  * Private connectivity through Confluent Cloud network

The following table shows how to get the endpoint value by using different Confluent interfaces.

Interface | Location | Endpoint
---|---|---
Cloud Console | Flink **Endpoints** page | Full FQDN shown for each network connection
Confluent CLI |

    confluent flink endpoint list

| Full FQDN shown for each network connection
Network UI/API/CLI |

  * **Network management** details page in **Environment overview**
  * GET /network/
  * confluent network describe

|

  1. Read the `endpoint_suffix` attribute, for example, `<service-identifier>-abc1de.us-east-1.aws.glb.confluent.cloud`
  2. Replace `<service-identifier>` with the relevant value, for example, `flink` for Flink or `flinkpls` for Language Service.
  3. Assign in interface (UI/CLI/Terraform)

The following table shows the endpoint patterns for different DNS and cluster type combinations.

Networking | DNS | Cluster Type | Endpoints
---|---|---|---
PrivateLink | Private | Enterprise (PrivateLink Attachment) | `flink.$region.$cloud.private.confluent.cloud` `flinkpls.$region.$cloud.private.confluent.cloud`
Dedicated | `flink.dom$id.$region.$cloud.private.confluent.cloud` `flinkpls.dom$id.$region.$cloud.private.confluent.cloud`
Public | Dedicated | `flink-$nid.$region.$cloud.glb.confluent.cloud` `flinkpls-$nid.$region.$cloud.glb.confluent.cloud`
VPC Peering / Transit Gateway w/ /16 CIDR | Public | Dedicated | `flink-$nid.$region.$cloud.confluent.cloud` `flinkpls-$nid.$region.$cloud.confluent.cloud`
VPC Peering / Transit Gateway w/ /27 CIDRs | Public | Dedicated | `flink-$nid.$region.$cloud.glb.confluent.cloud` `flinkpls-$nid.$region.$cloud.glb.confluent.cloud`

### Public endpoint¶

  * Source: Always present.
  * Considerations: Can’t access Kafka private data.
  * Kafka data access and scope: Can access public cluster data (read/write) in cloud region for this organization.
  * Access to Flink statement and workspace: Configurable with IP Filtering.
  * Endpoints: `flink.<region>.<cloud>.confluent.cloud`, for example: `flink.us-east-2.aws.confluent.cloud`.

### PrivateLink Attachment¶

  * Source: Must [create a Private Link Attachment](../../networking/aws-platt.html#privatelinkattachment-create) for the environment/region.
  * Considerations: A single VPC can’t have private link connections to multiple Confluent Cloud environments. Available on AWS and Azure.
  * Can access private cluster data (read/write) in Enterprise, Dedicated or Freight clusters for the cloud region for the organization of the endpoint. Can access public cluster data (read only).
  * Access all Flink resources in the same environment and region of the endpoint
  * Endpoints: `flink.<region>.<cloud>.private.confluent.cloud`, for example: `flink.us-east-2.aws.private.confluent.cloud`

### Private connectivity through Confluent Cloud network¶

  * Source: Created with Kafka Dedicated clusters.
  * Considerations: Easiest way to use Flink when the network is created already for Dedicated clusters. Available on AWS for all types of Confluent Cloud network, and Azure for any Confluent Cloud network with Private Links.
  * Can access private cluster data (read/write) in Enterprise, Dedicated or Freight clusters for the organization of the region. Can access public cluster data (read only).
  * Access all Flink resources in the same environment and region of the endpoint

To find the endpoints from the Cloud Console or Confluent CLI, see Available endpoints for an environment and region.

## Access private networking with the Confluent CLI¶

Run the `confluent flink region --cloud <cloud-provider> --region <region>` command to select a cloud provider and region.

Run the `confluent flink endpoint list` command to list all endpoints, both public and private.

Run the `confluent flink endpoint use` to select an endpoint.

In addition to the main Flink endpoint listed here, you must have access to `flinkpls.<network>.<region>.<cloud>.private.confluent.cloud` (for private DNS resolution) or `flinkpls-<network>.<region>.<cloud>.private.confluent.cloud` (for public DNS resolution) to access the language service for autocompletion in the Flink SQL shell. In the case of public DNS resolution, routing is done transparently, but if you use private DNS resolution, you must make sure to route this endpoint from your client. For more information, see [private DNS resolution](../../networking/private-links/aws-privatelink.html#dns-resolution-options).

## Access private networking with the Cloud Console¶

By default, public networking is used, which won’t work if IP Filtering is set, and/or the cluster is private.

You can set defaults for each cloud region in an environment. For this, use the Flink **Endpoints** page.

  * The default is per-user.
  * When a default is set, it is used for all pages that access Flink, for example, the statement list, workspace list, and workspaces.
  * If no default is set, the public endpoint is used.
