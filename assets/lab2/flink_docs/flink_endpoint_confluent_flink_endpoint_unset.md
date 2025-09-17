---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/endpoint/confluent_flink_endpoint_unset.html
title: confluent flink endpoint unset
hierarchy: ['confluent-cli', 'command-reference', 'endpoint', 'confluent_flink_endpoint_unset.html']
scraped_date: 2025-09-05T13:53:03.171405
---

# confluent flink endpoint unset¶

## Description¶

Unset the current Flink endpoint that was previously set with the `use` command.

    confluent flink endpoint unset [flags]

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## Examples¶

Unset the current Flink endpoint “<https://flink.us-east-1.aws.confluent.cloud>”.

    confluent flink endpoint unset

## See Also¶

  * [confluent flink endpoint](index.html#confluent-flink-endpoint) \- Manage Flink endpoint.
