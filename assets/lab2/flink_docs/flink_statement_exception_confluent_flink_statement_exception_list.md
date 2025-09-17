---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/statement/exception/confluent_flink_statement_exception_list.html
title: confluent flink statement exception list
hierarchy: ['confluent-cli', 'command-reference', 'statement', 'exception', 'confluent_flink_statement_exception_list.html']
scraped_date: 2025-09-05T13:50:44.969179
---

# confluent flink statement exception list¶

## Description¶

CloudOn-Premises

List exceptions for a Flink SQL statement.

    confluent flink statement exception list <statement-name> [flags]

List exceptions for a Flink SQL statement in Confluent Platform.

    confluent flink statement exception list <statement-name> [flags]

## Flags¶

CloudOn-Premises

        --cloud string         Specify the cloud provider as "aws", "azure", or "gcp".
        --region string        Cloud region for Flink (use "confluent flink region list" to see all).
        --environment string   Environment ID.
        --context string       CLI context name.
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

## See Also¶

  * [confluent flink statement exception](index.html#confluent-flink-statement-exception) \- Manage Flink SQL statement exceptions.
