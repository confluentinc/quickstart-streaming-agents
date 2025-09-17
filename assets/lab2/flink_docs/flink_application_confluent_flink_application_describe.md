---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/application/confluent_flink_application_describe.html
title: confluent flink application describe
hierarchy: ['confluent-cli', 'command-reference', 'application', 'confluent_flink_application_describe.html']
scraped_date: 2025-09-05T13:53:11.699439
---

# confluent flink application describe¶

## Description¶

Describe a Flink application.

    confluent flink application describe <name> [flags]

## Flags¶

        --environment string                  REQUIRED: Name of the Flink environment.
        --url string                          Base URL of the Confluent Manager for Apache Flink (CMF). Environment variable "CONFLUENT_CMF_URL" may be set in place of this flag.
        --client-key-path string              Path to client private key for mTLS authentication. Environment variable "CONFLUENT_CMF_CLIENT_KEY_PATH" may be set in place of this flag.
        --client-cert-path string             Path to client cert to be verified by Confluent Manager for Apache Flink. Include for mTLS authentication. Environment variable "CONFLUENT_CMF_CLIENT_CERT_PATH" may be set in place of this flag.
        --certificate-authority-path string   Path to a PEM-encoded Certificate Authority to verify the Confluent Manager for Apache Flink connection. Environment variable "CONFLUENT_CMF_CERTIFICATE_AUTHORITY_PATH" may be set in place of this flag.
    -o, --output string                       Specify the output format as "json" or "yaml". (default "json")

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## See Also¶

  * [confluent flink application](index.html#confluent-flink-application) \- Manage Flink applications.
