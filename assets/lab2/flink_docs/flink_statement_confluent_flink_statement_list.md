---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/statement/confluent_flink_statement_list.html
title: confluent flink statement list
hierarchy: ['confluent-cli', 'command-reference', 'statement', 'confluent_flink_statement_list.html']
scraped_date: 2025-09-05T13:50:40.702947
---

# confluent flink statement list¶

## Description¶

CloudOn-Premises

List Flink SQL statements.

    confluent flink statement list [flags]

List Flink SQL statements in Confluent Platform.

    confluent flink statement list [flags]

## Flags¶

CloudOn-Premises

        --cloud string          Specify the cloud provider as "aws", "azure", or "gcp".
        --region string         Cloud region for Flink (use "confluent flink region list" to see all).
        --compute-pool string   Flink compute pool ID.
        --environment string    Environment ID.
        --context string        CLI context name.
    -o, --output string         Specify the output format as "human", "json", or "yaml". (default "human")
        --status string         Filter the results by statement status.

        --environment string                  REQUIRED: Name of the Flink environment.
        --compute-pool string                 Optional flag to filter the Flink statements by compute pool ID.
        --status string                       Optional flag to filter the Flink statements by statement status.
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

List running statements.

    confluent flink statement list --status running

No examples.

## See Also¶

  * [confluent flink statement](index.html#confluent-flink-statement) \- Manage Flink SQL statements.
