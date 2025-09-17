---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/statement/confluent_flink_statement_resume.html
title: confluent flink statement resume
hierarchy: ['confluent-cli', 'command-reference', 'statement', 'confluent_flink_statement_resume.html']
scraped_date: 2025-09-05T13:52:09.279282
---

# confluent flink statement resume¶  
  
## Description¶

CloudOn-Premises

Resume a Flink SQL statement.

    confluent flink statement resume <name> [flags]

Resume a Flink SQL statement in Confluent Platform.

    confluent flink statement resume <statement-name> [flags]

## Flags¶

CloudOn-Premises

    --principal string      A user or service account the statement runs as.
    --compute-pool string   Flink compute pool ID.
    --cloud string          Specify the cloud provider as "aws", "azure", or "gcp".
    --region string         Cloud region for Flink (use "confluent flink region list" to see all).
    --environment string    Environment ID.
    --context string        CLI context name.

    --environment string                  REQUIRED: Name of the Flink environment.
    --url string                          Base URL of the Confluent Manager for Apache Flink (CMF). Environment variable "CONFLUENT_CMF_URL" may be set in place of this flag.
    --client-key-path string              Path to client private key for mTLS authentication. Environment variable "CONFLUENT_CMF_CLIENT_KEY_PATH" may be set in place of this flag.
    --client-cert-path string             Path to client cert to be verified by Confluent Manager for Apache Flink. Include for mTLS authentication. Environment variable "CONFLUENT_CMF_CLIENT_CERT_PATH" may be set in place of this flag.
    --certificate-authority-path string   Path to a PEM-encoded Certificate Authority to verify the Confluent Manager for Apache Flink connection. Environment variable "CONFLUENT_CMF_CERTIFICATE_AUTHORITY_PATH" may be set in place of this flag.

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## Examples¶

CloudOn-Premises

Request to resume the currently stopped statement “my-statement” using original principal id and under the original compute pool.

    confluent flink statement resume my-statement

Request to resume the currently stopped statement “my-statement” using service account “sa-123456”.

    confluent flink statement resume my-statement --principal sa-123456

Request to resume the currently stopped statement “my-statement” using user account “u-987654”.

    confluent flink statement resume my-statement --principal u-987654

Request to resume the currently stopped statement “my-statement” and under a different compute pool “lfcp-123456”.

    confluent flink statement resume my-statement --compute-pool lfcp-123456

Request to resume the currently stopped statement “my-statement” using service account “sa-123456” and under a different compute pool “lfcp-123456”.

    confluent flink statement resume my-statement --principal sa-123456 --compute-pool lfcp-123456

No examples.

## See Also¶

  * [confluent flink statement](index.html#confluent-flink-statement) \- Manage Flink SQL statements.
