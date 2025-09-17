---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/environment/confluent_flink_environment_create.html
title: confluent flink environment create
hierarchy: ['confluent-cli', 'command-reference', 'environment', 'confluent_flink_environment_create.html']
scraped_date: 2025-09-05T13:53:28.912029
---

# confluent flink environment create¶

## Description¶

Create a Flink environment.

    confluent flink environment create <name> [flags]

## Flags¶

        --kubernetes-namespace string         REQUIRED: Kubernetes namespace to deploy Flink applications to.
        --defaults string                     JSON string defining the environment's Flink application defaults, or path to a file to read defaults from (with .yml, .yaml or .json extension).
        --statement-defaults string           JSON string defining the environment's Flink statement defaults, or path to a file to read defaults from (with .yml, .yaml or .json extension).
        --compute-pool-defaults string        JSON string defining the environment's Flink compute pool defaults, or path to a file to read defaults from (with .yml, .yaml or .json extension).
        --url string                          Base URL of the Confluent Manager for Apache Flink (CMF). Environment variable "CONFLUENT_CMF_URL" may be set in place of this flag.
        --client-key-path string              Path to client private key for mTLS authentication. Environment variable "CONFLUENT_CMF_CLIENT_KEY_PATH" may be set in place of this flag.
        --client-cert-path string             Path to client cert to be verified by Confluent Manager for Apache Flink. Include for mTLS authentication. Environment variable "CONFLUENT_CMF_CLIENT_CERT_PATH" may be set in place of this flag.
        --certificate-authority-path string   Path to a PEM-encoded Certificate Authority to verify the Confluent Manager for Apache Flink connection. Environment variable "CONFLUENT_CMF_CERTIFICATE_AUTHORITY_PATH" may be set in place of this flag.
    -o, --output string                       Specify the output format as "human", "json", or "yaml". (default "human")

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## See Also¶

  * [confluent flink environment](index.html#confluent-flink-environment) \- Manage Flink environments.
