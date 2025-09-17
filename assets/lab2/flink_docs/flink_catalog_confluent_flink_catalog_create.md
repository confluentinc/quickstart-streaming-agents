---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/catalog/confluent_flink_catalog_create.html
title: confluent flink catalog create
hierarchy: ['confluent-cli', 'command-reference', 'catalog', 'confluent_flink_catalog_create.html']
scraped_date: 2025-09-05T13:53:20.394188
---

# confluent flink catalog create¶

## Description¶

Create a Flink catalog in Confluent Platform that provides metadata about tables and other database objects such as views and functions.

    confluent flink catalog create <resourceFilePath> [flags]

## Flags¶

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

  * [confluent flink catalog](index.html#confluent-flink-catalog) \- Manage Flink catalogs in Confluent Platform.
