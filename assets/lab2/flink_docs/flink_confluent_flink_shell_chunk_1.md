---
document_id: flink_confluent_flink_shell_chunk_1
source_file: flink_confluent_flink_shell.md
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/confluent_flink_shell.html
title: confluent flink shell
chunk_index: 1
total_chunks: 1
---

# confluent flink shell¶

## Description¶

Start Flink interactive SQL client.

    confluent flink shell [flags]

## Flags¶

    --compute-pool string      Flink compute pool ID.
    --service-account string   Service account ID.
    --database string          The database which will be used as the default database. When using Kafka, this is the cluster ID.
    --environment string       Environment ID.
    --context string           CLI context name.

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## Examples¶

For a Quick Start with examples in context, see <https://docs.confluent.io/cloud/current/flink/get-started/quick-start-shell.html>.
