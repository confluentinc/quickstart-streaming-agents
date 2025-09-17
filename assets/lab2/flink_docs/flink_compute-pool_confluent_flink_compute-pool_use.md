---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/compute-pool/confluent_flink_compute-pool_use.html
title: confluent flink compute-pool use
hierarchy: ['confluent-cli', 'command-reference', 'compute-pool', 'confluent_flink_compute-pool_use.html']
scraped_date: 2025-09-05T13:50:53.548416
---

# confluent flink compute-pool use¶  
  
## Description¶

Choose a Flink compute pool to be used in subsequent commands which support passing a compute pool with the `--compute-pool` flag.

    confluent flink compute-pool use <id> [flags]

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## See Also¶

  * [confluent flink compute-pool](index.html#confluent-flink-compute-pool) \- Manage Flink compute pools.
