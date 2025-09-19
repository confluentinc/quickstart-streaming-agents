---
document_id: flink_concepts_flink-private-networking_chunk_2
source_file: flink_concepts_flink-private-networking.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/flink-private-networking.html
title: Private Networking with Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 3
---

networking with Confluent Cloud Network](../operate-and-deploy/private-networking.html#flink-sql-enable-private-networking-ccn).

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
