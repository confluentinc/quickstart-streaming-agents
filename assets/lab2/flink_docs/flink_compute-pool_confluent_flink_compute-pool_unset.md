---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/compute-pool/confluent_flink_compute-pool_unset.html
title: confluent flink compute-pool unset
hierarchy: ['confluent-cli', 'command-reference', 'compute-pool', 'confluent_flink_compute-pool_unset.html']
scraped_date: 2025-09-05T13:50:55.677410
---

# confluent flink compute-pool unset¶

## Description¶

Unset the current Flink compute pool that was set with the `use` command.

    confluent flink compute-pool unset [flags]

## Flags¶

    -o, --output string   Specify the output format as "human", "json", or "yaml". (default "human")

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## Examples¶

Unset default compute pool:

    confluent flink compute-pool unset

## See Also¶

  * [confluent flink compute-pool](index.html#confluent-flink-compute-pool) \- Manage Flink compute pools.
