---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/artifact/confluent_flink_artifact_delete.html
title: confluent flink artifact delete
hierarchy: ['confluent-cli', 'command-reference', 'artifact', 'confluent_flink_artifact_delete.html']
scraped_date: 2025-09-05T13:52:52.540990
---

# confluent flink artifact delete¶

## Description¶

Delete one or more Flink UDF artifacts.

    confluent flink artifact delete <id-1> [id-2] ... [id-n] [flags]

## Flags¶

    --cloud string         REQUIRED: Specify the cloud provider as "aws", "azure", or "gcp".
    --region string        REQUIRED: Cloud region for Flink (use "confluent flink region list" to see all).
    --environment string   Environment ID.
    --force                Skip the deletion confirmation prompt.
    --context string       CLI context name.

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## Examples¶

Delete Flink UDF artifact.

    confluent flink artifact delete --cloud aws --region us-west-2 --environment env-123456 cfa-123456

## See Also¶

  * [confluent flink artifact](index.html#confluent-flink-artifact) \- Manage Flink UDF artifacts.
