---
document_id: flink_how-to-guides_combine-and-track-most-recent-records_chunk_1
source_file: flink_how-to-guides_combine-and-track-most-recent-records.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/combine-and-track-most-recent-records.html
title: Combine Streams and Track Most Recent Records with Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 3
---

# Combine Streams and Track Most Recent Records with Confluent Cloud for Apache Flink¶

When working with streaming data, it’s common to need to combine information from multiple sources while tracking the most recent record data. Confluent Cloud for Apache Flink® provides powerful capabilities to merge streams and maintain up-to-date information for each record, regardless of which stream it originated from.

In this guide, you learn how to run a Flink SQL statement that combines multiple data streams and keeps track of the most recent information for each record by using window functions. While this example uses order and clickstream data, the pattern can be applied to any number of streams that share a common identifier.

This topic shows the following steps:

* Step 1: Inspect the example source streams
* Step 2: Create a unified view with most recent records

## Prerequisites¶

* Access to Confluent Cloud.
* The OrganizationAdmin, EnvironmentAdmin, or FlinkAdmin role for creating compute pools, or the FlinkDeveloper role if you already have a compute pool. If you don’t have the appropriate role, contact your OrganizationAdmin or EnvironmentAdmin. For more information, see [Grant Role-Based Access in Confluent Cloud for Apache Flink](../operate-and-deploy/flink-rbac.html#flink-rbac).
* A provisioned Flink compute pool.

## Step 1: Inspect the example source streams¶

In this step, you examine the read-only `orders` and `clicks` tables in the `examples.marketplace` database to identify:

* The common identifier field that links the streams
* The unique fields from each stream that you want to track

  1. Log in to Confluent Cloud and navigate to your Flink workspace.

  2. Examine your source streams. The following example includes orders and clicks:

         -- First stream
         SELECT * FROM `examples`.`marketplace`.`orders`;

         -- Second stream
         SELECT * FROM `examples`.`marketplace`.`clicks`;

Your output from `orders` should resemble:

         order_id                                customer_id   product_id  price
         be396ae5-d7d9-4454-99d7-9b1c155d51d4    3243          1304        99.55
         79e295d3-5a0b-4127-9337-9a483794e7d4    3132          1201        21.43
         9b59d319-c37a-4088-a803-350d43bc5382    3099          1271        66.70
         8aaa9d8e-d8f7-4bb5-9d59-ce4d0cfc9a92    3181          1028        76.23
         e681fa67-3a1e-4e99-ba03-da9fb5d12845    3186          1212        69.67
         89ba7186-f927-462b-860a-68b8c9d51a06    3238          1336        76.89
         ebfec6c6-3294-444b-82e5-5a66e7dc5cd5    3233          1223        23.69

Your output from `clicks` should resemble:

         click_id                             user_id url                                user_agent                                                                      view_time
         a5c31d8b-cc93-4a48-a7d9-c1d389c83f4a 3099    https://www.acme.com/product/foxmh Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0 79
         b7d42e6f-85a1-4f7b-b1c2-d3e456789abc 3262    https://www.acme.com/product/lruuv Mozilla/5.0 (iPhone; CPU OS 9_3_5 like Mac OS X) AppleWebKit/601.1.46           108
         c8e53f7a-96b2-4a8c-c2d3-e4f567890def 3181    https://www.acme.com/product/vfzsy Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)                              33
         d9f64g8b-a7c3-4b9d-d3e4-f5g678901hij 4882    https://www.acme.com/product/zkxun Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14                       99
         e74441b6-09da-4113-b8f9-db12cee90c77 3500    https://www.acme.com/product/lruuv Mozilla/5.0 (iPhone; CPU iPhone OS 11_4_1 like Mac OS X) AppleWebKit/6...       116
         f39236ac-2646-4e5d-bab2-cd4445630529 4360    https://www.acme.com/product/vfzsy Mozilla/4.0 (compatible; Win32; WinHttp.WinHttpRequest.5)                       52
         3f3b06df-aa2b-417e-833e-ccc232536c4a 4171    https://www.acme.com/product/foxmh Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) C...        82
         ee9fe475-5420-410d-90ae-47987eba32d5 4095    https://www.acme.com/product/ifgcb Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/1...        119
         e75faa6f-78d3-45e0-817e-1338381f53a2 4904    https://www.acme.com/product/ffnsl Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like ...         36
         77c6acbb-eb71-4a49-96e5-714f8b024c98 4681    https://www.acme.com/product/zkxun Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.11) Gecko GranParadiso/3...    67
