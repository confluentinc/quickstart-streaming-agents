---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/statement/confluent_flink_statement_web-ui-forward.html
title: confluent flink statement web-ui-forward
hierarchy: ['confluent-cli', 'command-reference', 'statement', 'confluent_flink_statement_web-ui-forward.html']
scraped_date: 2025-09-05T13:52:15.685978
---

# confluent flink statement web-ui-forward¶

## Description¶

Forward the web UI of a Flink statement in Confluent Platform.

    confluent flink statement web-ui-forward <name> [flags]

## Flags¶

    --environment string                  REQUIRED: Name of the Flink environment.
    --url string                          Base URL of the Confluent Manager for Apache Flink (CMF). Environment variable "CONFLUENT_CMF_URL" may be set in place of this flag.
    --client-key-path string              Path to client private key for mTLS authentication. Environment variable "CONFLUENT_CMF_CLIENT_KEY_PATH" may be set in place of this flag.
    --client-cert-path string             Path to client cert to be verified by Confluent Manager for Apache Flink. Include for mTLS authentication. Environment variable "CONFLUENT_CMF_CLIENT_CERT_PATH" may be set in place of this flag.
    --certificate-authority-path string   Path to a PEM-encoded Certificate Authority to verify the Confluent Manager for Apache Flink connection. Environment variable "CONFLUENT_CMF_CERTIFICATE_AUTHORITY_PATH" may be set in place of this flag.
    --port uint16                         Port to forward the web UI to. If not provided, a random, OS-assigned port will be used.

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## See Also¶

  * [confluent flink statement](index.html#confluent-flink-statement) \- Manage Flink SQL statements.
