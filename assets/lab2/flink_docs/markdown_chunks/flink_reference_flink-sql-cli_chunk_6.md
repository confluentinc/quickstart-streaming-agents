---
document_id: flink_reference_flink-sql-cli_chunk_6
source_file: flink_reference_flink-sql-cli.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/flink-sql-cli.html
title: Confluent CLI commands with Confluent Cloud for Apache Flink
chunk_index: 6
total_chunks: 6
---

Deleted Flink compute pool "lfcp-xxd6og".

## Manage regions¶

Using the Confluent CLI, you can perform these actions:

  * List available regions
  * Set the current region

Managing Flink SQL regions may require the following inputs, depending on the command:

    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"

For the complete CLI reference, see [confluent flink region](https://docs.confluent.io/confluent-cli/current/command-reference/flink/region/index.html).

### List available regions¶

Run the [confluent flink region list](https://docs.confluent.io/confluent-cli/current/command-reference/flink/region/confluent_flink_region_list.html) to see all available regions where you can run Flink statements.

    confluent flink region list

Your output should resemble:

      Current |             Name              | Cloud |        Region
    ----------+-------------------------------+-------+-----------------------
              | Belgium (europe-west1)        | gcp   | europe-west1
              | Frankfurt (eu-central-1)      | aws   | eu-central-1
              | Frankfurt (europe-west3)      | gcp   | europe-west3
              | Iowa (us-central1)            | gcp   | us-central1
              | Ireland (eu-west-1)           | aws   | eu-west-1
              | Las Vegas (us-west4)          | gcp   | us-west4
              | London (eu-west-2)            | aws   | eu-west-2
      *       | N. Virginia (us-east-1)       | aws   | us-east-1
              | N. Virginia (us-east4)        | gcp   | us-east4
              | Netherlands (westeurope)      | azure | westeurope
              | Ohio (us-east-2)              | aws   | us-east-2
              | Oregon (us-west-2)            | aws   | us-west-2
              | S. Carolina (us-east1)        | gcp   | us-east1
              | Singapore (ap-southeast-1)    | aws   | ap-southeast-1
              | Singapore (asia-southeast1)   | gcp   | asia-southeast1
              | Singapore (southeastasia)     | azure | southeastasia
              | Sydney (ap-southeast-2)       | aws   | ap-southeast-2
              | Sydney (australia-southeast1) | gcp   | australia-southeast1
              | Virginia (eastus)             | azure | eastus
              | Virginia (eastus2)            | azure | eastus2
              | Washington (westus2)          | azure | westus2

Run the following command to filter the list of available regions by cloud provider.

    confluent flink region list --cloud ${CLOUD_PROVIDER}

Your output should resemble:

      Current |            Name            | Cloud |     Region
    ----------+----------------------------+-------+-----------------
              | Frankfurt (eu-central-1)   | aws   | eu-central-1
              | Ireland (eu-west-1)        | aws   | eu-west-1
              | London (eu-west-2)         | aws   | eu-west-2
      *       | N. Virginia (us-east-1)    | aws   | us-east-1
              | Ohio (us-east-2)           | aws   | us-east-2
              | Oregon (us-west-2)         | aws   | us-west-2
              | Singapore (ap-southeast-1) | aws   | ap-southeast-1
              | Sydney (ap-southeast-2)    | aws   | ap-southeast-2

### Set the current region¶

Run the [confluent flink region use](https://docs.confluent.io/confluent-cli/current/command-reference/flink/region/confluent_flink_region_use.html) to set the current region where subsequent Flink statements run. You must have a compute pool in the region to run statements.

    confluent flink region use --cloud ${CLOUD_PROVIDER} --region ${CLOUD_REGION}

For `CLOUD_PROVIDER=aws` and `CLOUD_REGION=us-east-2`, your output should resemble:

    Using Flink region "Ohio (us-east-2)".
