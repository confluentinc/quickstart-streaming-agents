---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/endpoint/confluent_flink_endpoint_list.html
title: confluent flink endpoint list
hierarchy: ['confluent-cli', 'command-reference', 'endpoint', 'confluent_flink_endpoint_list.html']
scraped_date: 2025-09-05T13:53:01.042442
---

# confluent flink endpoint list¶

## Description¶

List Flink endpoint.

    confluent flink endpoint list [flags]

## Flags¶

        --context string   CLI context name.
    -o, --output string    Specify the output format as "human", "json", or "yaml". (default "human")

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## Examples¶

List the available Flink endpoints with current cloud provider and region.

    confluent flink endpoint list

## See Also¶

  * [confluent flink endpoint](index.html#confluent-flink-endpoint) \- Manage Flink endpoint.
