---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/connectivity-type/confluent_flink_connectivity-type_use.html
title: confluent flink connectivity-type use
hierarchy: ['confluent-cli', 'command-reference', 'connectivity-type', 'confluent_flink_connectivity-type_use.html']
scraped_date: 2025-09-05T13:52:58.908386
---

# confluent flink connectivity-type use¶

## Description¶

Select a Flink connectivity type for the current environment as “public” or “private”. If unspecified, the CLI will default to public connectivity type.

    confluent flink connectivity-type use <region-access> [flags]

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).
