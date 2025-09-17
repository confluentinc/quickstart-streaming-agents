---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/compute-pool/confluent_flink_compute-pool_delete.html
title: confluent flink compute-pool delete
hierarchy: ['confluent-cli', 'command-reference', 'compute-pool', 'confluent_flink_compute-pool_delete.html']
scraped_date: 2025-09-05T13:49:42.819048
---

# confluent flink compute-pool delete¶

## Description¶

CloudOn-Premises

Delete one or more Flink compute pools.

    confluent flink compute-pool delete <id-1> [id-2] ... [id-n] [flags]

Delete one or more Flink compute pools in Confluent Platform, a compute pool can only be deleted if there are no statements associated with it.

    confluent flink compute-pool delete <name-1> [name-2] ... [name-n] [flags]

## Flags¶

CloudOn-Premises

    --force                Skip the deletion confirmation prompt.
    --environment string   Environment ID.
    --context string       CLI context name.

    --environment string                  REQUIRED: Name of the Flink environment.
    --url string                          Base URL of the Confluent Manager for Apache Flink (CMF). Environment variable "CONFLUENT_CMF_URL" may be set in place of this flag.
    --client-key-path string              Path to client private key for mTLS authentication. Environment variable "CONFLUENT_CMF_CLIENT_KEY_PATH" may be set in place of this flag.
    --client-cert-path string             Path to client cert to be verified by Confluent Manager for Apache Flink. Include for mTLS authentication. Environment variable "CONFLUENT_CMF_CLIENT_CERT_PATH" may be set in place of this flag.
    --certificate-authority-path string   Path to a PEM-encoded Certificate Authority to verify the Confluent Manager for Apache Flink connection. Environment variable "CONFLUENT_CMF_CERTIFICATE_AUTHORITY_PATH" may be set in place of this flag.
    --force                               Skip the deletion confirmation prompt.

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## See Also¶

  * [confluent flink compute-pool](index.html#confluent-flink-compute-pool) \- Manage Flink compute pools.
