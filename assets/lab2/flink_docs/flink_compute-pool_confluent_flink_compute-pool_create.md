---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/compute-pool/confluent_flink_compute-pool_create.html
title: confluent flink compute-pool create
hierarchy: ['confluent-cli', 'command-reference', 'compute-pool', 'confluent_flink_compute-pool_create.html']
scraped_date: 2025-09-05T13:49:34.210783
---

# confluent flink compute-pool create¶

## Description¶

CloudOn-Premises

Create a Flink compute pool.

    confluent flink compute-pool create <name> [flags]

Create a Flink compute pool in Confluent Platform.

    confluent flink compute-pool create <resourceFilePath> [flags]

## Flags¶

CloudOn-Premises

        --cloud string         REQUIRED: Specify the cloud provider as "aws", "azure", or "gcp".
        --region string        REQUIRED: Cloud region for Flink (use "confluent flink region list" to see all).
        --max-cfu int32        Maximum number of Confluent Flink Units (CFU). (default 5)
        --environment string   Environment ID.
    -o, --output string        Specify the output format as "human", "json", or "yaml". (default "human")

        --environment string                  REQUIRED: Name of the Flink environment.
        --url string                          Base URL of the Confluent Manager for Apache Flink (CMF). Environment variable "CONFLUENT_CMF_URL" may be set in place of this flag.
        --client-key-path string              Path to client private key for mTLS authentication. Environment variable "CONFLUENT_CMF_CLIENT_KEY_PATH" may be set in place of this flag.
        --client-cert-path string             Path to client cert to be verified by Confluent Manager for Apache Flink. Include for mTLS authentication. Environment variable "CONFLUENT_CMF_CLIENT_CERT_PATH" may be set in place of this flag.
        --certificate-authority-path string   Path to a PEM-encoded Certificate Authority to verify the Confluent Manager for Apache Flink connection. Environment variable "CONFLUENT_CMF_CERTIFICATE_AUTHORITY_PATH" may be set in place of this flag.
    -o, --output string                       Specify the output format as "human", "json", or "yaml". (default "human")

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## Examples¶

CloudOn-Premises

Create Flink compute pool “my-compute-pool” in AWS with 5 CFUs.

    confluent flink compute-pool create my-compute-pool --cloud aws --region us-west-2 --max-cfu 5

No examples.

## See Also¶

  * [confluent flink compute-pool](index.html#confluent-flink-compute-pool) \- Manage Flink compute pools.
