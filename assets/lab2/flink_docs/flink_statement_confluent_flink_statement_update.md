---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/statement/confluent_flink_statement_update.html
title: confluent flink statement update
hierarchy: ['confluent-cli', 'command-reference', 'statement', 'confluent_flink_statement_update.html']
scraped_date: 2025-09-05T13:50:49.233453
---

# confluent flink statement update¶

## Description¶

Update a Flink SQL statement.

    confluent flink statement update <name> [flags]

## Flags¶

    --principal string      A user or service account the statement runs as.
    --compute-pool string   Flink compute pool ID.
    --stopped               Request to stop or resume the statement.
    --cloud string          Specify the cloud provider as "aws", "azure", or "gcp".
    --region string         Cloud region for Flink (use "confluent flink region list" to see all).
    --environment string    Environment ID.
    --context string        CLI context name.

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## Examples¶

Request to resume the currently stopped statement “my-statement” using original principal id and under the original compute pool.

    confluent flink statement update my-statement --stopped=false

Request to resume the currently stopped statement “my-statement” using service account “sa-123456”.

    confluent flink statement update my-statement --stopped=false --principal sa-123456

Request to resume the currently stopped statement “my-statement” using user account “u-987654”.

    confluent flink statement update my-statement --stopped=false --principal u-987654

Request to resume the currently stopped statement “my-statement” and under a different compute pool “lfcp-123456”.

    confluent flink statement update my-statement --stopped=false --compute-pool lfcp-123456

Request to resume the currently stopped statement “my-statement” using service account “sa-123456” and under a different compute pool “lfcp-123456”.

    confluent flink statement update my-statement --stopped=false --principal sa-123456 --compute-pool lfcp-123456

Request to stop the currently running statement “my-statement”.

    confluent flink statement update my-statement --stopped=true

## See Also¶

  * [confluent flink statement](index.html#confluent-flink-statement) \- Manage Flink SQL statements.
