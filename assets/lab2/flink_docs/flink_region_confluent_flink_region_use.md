---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/region/confluent_flink_region_use.html
title: confluent flink region use
hierarchy: ['confluent-cli', 'command-reference', 'region', 'confluent_flink_region_use.html']
scraped_date: 2025-09-05T13:50:59.933940
---

# confluent flink region use¶  
  
## Description¶

Choose a Flink region to be used in subsequent commands which support passing a region with the `--region` flag.

    confluent flink region use [flags]

## Flags¶

    --cloud string    REQUIRED: Specify the cloud provider as "aws", "azure", or "gcp".
    --region string   REQUIRED: Cloud region for Flink (use "confluent flink region list" to see all).

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## Examples¶

Select region “N. Virginia (us-east-1)” for use in subsequent Flink commands.

    confluent flink region use --cloud aws --region us-east-1

## See Also¶

  * [confluent flink region](index.html#confluent-flink-region) \- Manage Flink regions.
