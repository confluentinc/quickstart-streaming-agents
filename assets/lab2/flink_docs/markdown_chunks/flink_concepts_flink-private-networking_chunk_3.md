---
document_id: flink_concepts_flink-private-networking_chunk_3
source_file: flink_concepts_flink-private-networking.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/flink-private-networking.html
title: Private Networking with Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 3
---

clusters when using private connectivity.

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

information, see [private DNS resolution](../../networking/private-links/aws-privatelink.html#dns-resolution-options).

## Access private networking with the Cloud Console¶

By default, public networking is used, which won’t work if IP Filtering is set, and/or the cluster is private.

You can set defaults for each cloud region in an environment. For this, use the Flink **Endpoints** page.

* The default is per-user.
* When a default is set, it is used for all pages that access Flink, for example, the statement list, workspace list, and workspaces.
* If no default is set, the public endpoint is used.
