---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/endpoint/confluent_flink_endpoint_use.html
title: confluent flink endpoint use
hierarchy: ['confluent-cli', 'command-reference', 'endpoint', 'confluent_flink_endpoint_use.html']
scraped_date: 2025-09-05T13:53:05.310411
---

# confluent flink endpoint use¶

## Description¶

Use a Flink endpoint as active endpoint for all subsequent Flink dataplane commands in current environment, such as `flink connection`, `flink statement` and `flink shell`.

    confluent flink endpoint use [flags]

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## Examples¶

Use “<https://flink.us-east-1.aws.confluent.cloud>” for subsequent Flink dataplane commands.

    confluent flink endpoint use "https://flink.us-east-1.aws.confluent.cloud"

## See Also¶

  * [confluent flink endpoint](index.html#confluent-flink-endpoint) \- Manage Flink endpoint.
