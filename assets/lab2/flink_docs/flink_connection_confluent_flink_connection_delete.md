---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/connection/confluent_flink_connection_delete.html
title: confluent flink connection delete
hierarchy: ['confluent-cli', 'command-reference', 'connection', 'confluent_flink_connection_delete.html']
scraped_date: 2025-09-05T13:49:59.820255
---

# confluent flink connection delete¶

## Description¶

Delete one or more Flink connections.

    confluent flink connection delete <name-1> [name-2] ... [name-n] [flags]

## Flags¶

    --cloud string         REQUIRED: Specify the cloud provider as "aws", "azure", or "gcp".
    --region string        REQUIRED: Cloud region for Flink (use "confluent flink region list" to see all).
    --force                Skip the deletion confirmation prompt.
    --environment string   Environment ID.
    --context string       CLI context name.

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## See Also¶

  * [confluent flink connection](index.html#confluent-flink-connection) \- Manage Flink connections.
