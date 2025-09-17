---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/region/confluent_flink_region_list.html
title: confluent flink region list
hierarchy: ['confluent-cli', 'command-reference', 'region', 'confluent_flink_region_list.html']
scraped_date: 2025-09-05T13:49:08.354112
---

# confluent flink region list¶

## Description¶

List Flink regions.

    confluent flink region list [flags]

## Flags¶

        --cloud string     Specify the cloud provider as "aws", "azure", or "gcp".
        --context string   CLI context name.
    -o, --output string    Specify the output format as "human", "json", or "yaml". (default "human")

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## Examples¶

List the available Flink AWS regions.

    confluent flink region list --cloud aws

## See Also¶

  * [confluent flink region](index.html#confluent-flink-region) \- Manage Flink regions.
