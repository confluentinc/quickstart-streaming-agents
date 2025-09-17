---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/artifact/confluent_flink_artifact_create.html
title: confluent flink artifact create
hierarchy: ['confluent-cli', 'command-reference', 'artifact', 'confluent_flink_artifact_create.html']
scraped_date: 2025-09-05T13:51:02.074091
---

# confluent flink artifact create¶

## Description¶

Create a Flink UDF artifact.

    confluent flink artifact create <unique-name> [flags]

## Flags¶

        --artifact-file string        REQUIRED: Flink artifact JAR file or ZIP file.
        --cloud string                REQUIRED: Specify the cloud provider as "aws", "azure", or "gcp".
        --region string               REQUIRED: Cloud region for Flink (use "confluent flink region list" to see all).
        --environment string          Environment ID.
        --runtime-language string     Specify the Flink artifact runtime language as "python" or "java". (default "java")
        --description string          Specify the Flink artifact description.
        --documentation-link string   Specify the Flink artifact documentation link.
        --context string              CLI context name.
    -o, --output string               Specify the output format as "human", "json", or "yaml". (default "human")

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## Examples¶

Create Flink artifact “my-flink-artifact”.

    confluent flink artifact create my-flink-artifact --artifact-file artifact.jar --cloud aws --region us-west-2 --environment env-123456

Create Flink artifact “flink-java-artifact”.

    confluent flink artifact create my-flink-artifact --artifact-file artifact.jar --cloud aws --region us-west-2 --environment env-123456 --description flinkJavaScalar

## See Also¶

  * [confluent flink artifact](index.html#confluent-flink-artifact) \- Manage Flink UDF artifacts.
