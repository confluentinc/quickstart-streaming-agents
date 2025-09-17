---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/artifact/confluent_flink_artifact_describe.html
title: confluent flink artifact describe
hierarchy: ['confluent-cli', 'command-reference', 'artifact', 'confluent_flink_artifact_describe.html']
scraped_date: 2025-09-05T13:52:54.667619
---

# confluent flink artifact describe¶

## Description¶

Describe a Flink UDF artifact.

    confluent flink artifact describe <id> [flags]

## Flags¶

        --cloud string         REQUIRED: Specify the cloud provider as "aws", "azure", or "gcp".
        --region string        REQUIRED: Cloud region for Flink (use "confluent flink region list" to see all).
        --environment string   Environment ID.
        --context string       CLI context name.
    -o, --output string        Specify the output format as "human", "json", or "yaml". (default "human")

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## Examples¶

Describe Flink UDF artifact.

    confluent flink artifact describe --cloud aws --region us-west-2 --environment env-123456 cfa-123456

## See Also¶

  * [confluent flink artifact](index.html#confluent-flink-artifact) \- Manage Flink UDF artifacts.
