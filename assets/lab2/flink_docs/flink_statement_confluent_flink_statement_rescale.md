---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/statement/confluent_flink_statement_rescale.html
title: confluent flink statement rescale
hierarchy: ['confluent-cli', 'command-reference', 'statement', 'confluent_flink_statement_rescale.html']
scraped_date: 2025-09-05T13:52:13.551771
---

# confluent flink statement rescale¶

## Description¶

Rescale a Flink SQL statement in Confluent Platform.

    confluent flink statement rescale <statement-name> [flags]

## Flags¶

    --environment string                  REQUIRED: Name of the Flink environment.
    --parallelism int32                   REQUIRED: New parallelism of the Flink SQL statement. (default 1)
    --url string                          Base URL of the Confluent Manager for Apache Flink (CMF). Environment variable "CONFLUENT_CMF_URL" may be set in place of this flag.
    --client-key-path string              Path to client private key for mTLS authentication. Environment variable "CONFLUENT_CMF_CLIENT_KEY_PATH" may be set in place of this flag.
    --client-cert-path string             Path to client cert to be verified by Confluent Manager for Apache Flink. Include for mTLS authentication. Environment variable "CONFLUENT_CMF_CLIENT_CERT_PATH" may be set in place of this flag.
    --certificate-authority-path string   Path to a PEM-encoded Certificate Authority to verify the Confluent Manager for Apache Flink connection. Environment variable "CONFLUENT_CMF_CERTIFICATE_AUTHORITY_PATH" may be set in place of this flag.

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## See Also¶

  * [confluent flink statement](index.html#confluent-flink-statement) \- Manage Flink SQL statements.
