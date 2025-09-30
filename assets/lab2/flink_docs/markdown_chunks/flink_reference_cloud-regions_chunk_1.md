---
document_id: flink_reference_cloud-regions_chunk_1
source_file: flink_reference_cloud-regions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/cloud-regions.html
title: Supported Cloud Regions for Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Supported Cloud Regions for Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® is available on AWS, Azure, and Google Cloud.

Flink is supported in the following regions.

* AWS supported regions
* Azure supported regions
* Google Cloud supported regions

You can see the regions where Confluent Cloud for Apache Flink is supported by using the Confluent Cloud Console, the Confluent CLI, and the Flink REST API.

* List regions by using Cloud Console, Confluent CLI, or REST API

## AWS supported regions¶

Regions | Networking
---|---
ap-east-1 | Public and private
ap-northeast-1 | Public and private
ap-northeast-2 | Public and private
ap-south-1 | Public and private
ap-southeast-1 | Public and private
ap-southeast-2 | Public and private
ca-central-1 | Public and private
eu-central-1 | Public and private
eu-north-1 | Public and private
eu-west-1 | Public and private
eu-west-2 | Public and private
me-south-1 | Public and private
sa-east-1 | Public and private
us-east-1 | Public and private
us-east-2 | Public and private
us-west-2 | Public and private

## Azure supported regions¶

Regions | Networking
---|---
australiaeast | Public and private
brazilsouth | Public and private
canadacentral | Public and private
centralindia | Public and private
centralus | Public and private
eastasia | Public and private
eastus | Public and private
eastus2 | Public and private
francecentral | Public and private
germanywestcentral | Public and private
northeurope | Public and private
southcentralus | Public and private
southeastasia | Public and private
spaincentral | Public and private
uaenorth | Public and private
uksouth | Public and private
westeurope | Public and private
westus2 | Public and private
westus3 | Public and private

## Google Cloud supported regions¶

Regions | Networking
---|---
asia-south1 | Public and private
asia-south2 | Public
asia-southeast1 | Public and private
asia-southeast2 | Public
australia-southeast1 | Public
europe-west1 | Public and private
europe-west2 | Public and private
europe-west3 | Public and private
europe-west4 | Public and private
northamerica-northeast1 | Public and private
northamerica-northeast2 | Public and private
us-central1 | Public and private
us-east1 | Public and private
us-east4 | Public and private
us-west1 | Public and private
us-west2 | Public and private
us-west4 | Public and private

## List regions by using Cloud Console, Confluent CLI, or REST API¶

You can see the regions where Confluent Cloud for Apache Flink is supported by using the Confluent Cloud Console, the Confluent CLI, or the Flink REST API.

Confluent Cloud ConsoleConfluent CLIREST API

  1. Log in to Confluent Cloud and navigate to your environment.

  2. Click **Flink** and ensure that **Compute pools** is selected.

  3. Click **Add compute pool**.

In the **Create compute pool** page, you can browse the available cloud providers and regions.

  1. Log in to Confluent Cloud.

         confluent login --organization-id ${ORG_ID} --prompt

  2. Use the [Confluent CLI](https://docs.confluent.io/confluent-cli/current/command-reference/flink/region/confluent_flink_region_list.html) command to see the regions where Confluent Cloud for Apache Flink is supported.

         confluent flink region list

Your output should resemble:

         Current |              Name              | Cloud |        Region
         ----------+--------------------------------+-------+-----------------------
                   | Belgium (europe-west1)         | GCP   | europe-west1
                   | Canada (ca-central-1)          | AWS   | ca-central-1
                   | Iowa (centralus)               | AZURE | centralus
         ...

Use `grep` to filter the list by cloud provider. For example, the following command shows the AWS regions where Flink is available.

         confluent flink region list | grep -i aws

Your output should resemble:

         | Canada (ca-central-1)          | AWS   | ca-central-1
         | Frankfurt (eu-central-1)       | AWS   | eu-central-1
         | Ireland (eu-west-1)            | AWS   | eu-west-1
         ...

Send a GET request to the Flink REST API [Regions endpoint](/cloud/current/api.html#tag/Regions-\(fcpmv2\)/operation/listFcpmV2Regions) to list the available regions. For more information, see [List Flink Regions](../operate-and-deploy/flink-rest-api.html#flink-rest-api-list-regions).
