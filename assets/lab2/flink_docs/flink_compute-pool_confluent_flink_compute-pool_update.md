---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/compute-pool/confluent_flink_compute-pool_update.html
title: confluent flink compute-pool update
hierarchy: ['confluent-cli', 'command-reference', 'compute-pool', 'confluent_flink_compute-pool_update.html']
scraped_date: 2025-09-05T13:49:40.684178
---

# confluent flink compute-pool update¶

## Description¶

Update a Flink compute pool.

    confluent flink compute-pool update [id] [flags]

## Flags¶

        --name string          Name of the compute pool.
        --max-cfu int32        Maximum number of Confluent Flink Units (CFU).
        --environment string   Environment ID.
    -o, --output string        Specify the output format as "human", "json", or "yaml". (default "human")

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## Examples¶

Update name and CFU count of a Flink compute pool.

    confluent flink compute-pool update lfcp-123456 --name "new name" --max-cfu 5

## See Also¶

  * [confluent flink compute-pool](index.html#confluent-flink-compute-pool) \- Manage Flink compute pools.
