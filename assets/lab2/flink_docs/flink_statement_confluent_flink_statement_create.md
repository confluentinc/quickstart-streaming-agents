---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/statement/confluent_flink_statement_create.html
title: confluent flink statement create
hierarchy: ['confluent-cli', 'command-reference', 'statement', 'confluent_flink_statement_create.html']
scraped_date: 2025-09-05T13:50:38.566135
---

# confluent flink statement create¶  
  
## Description¶

CloudOn-Premises

Create a Flink SQL statement.

    confluent flink statement create [name] [flags]

Create a Flink SQL statement in Confluent Platform.

    confluent flink statement create [name] [flags]

## Flags¶

CloudOn-Premises

        --sql string               REQUIRED: The Flink SQL statement.
        --compute-pool string      Flink compute pool ID.
        --service-account string   Service account ID.
        --database string          The database which will be used as the default database. When using Kafka, this is the cluster ID.
        --wait                     Block until the statement is running or has failed.
        --property strings         A mechanism to pass properties in the form key=value when creating a Flink statement.
        --environment string       Environment ID.
        --context string           CLI context name.
    -o, --output string            Specify the output format as "human", "json", or "yaml". (default "human")

        --sql string                          REQUIRED: The Flink SQL statement.
        --environment string                  REQUIRED: Name of the Flink environment.
        --compute-pool string                 REQUIRED: The compute pool name to execute the Flink SQL statement.
        --parallelism uint16                  The parallelism the statement, default value is 1. (default 1)
        --catalog string                      The name of the default catalog.
        --database string                     The name of the default database.
        --flink-configuration string          The file path to hold the Flink configuration for the statement.
        --wait                                Boolean flag to block until the statement is running or has failed.
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

Create a Flink SQL statement in the current compute pool.

    confluent flink statement create --sql "SELECT * FROM table;"

Create a Flink SQL statement named “my-statement” in compute pool “lfcp-123456” with service account “sa-123456”, using Kafka cluster “my-cluster” as the default database, and with additional properties.

    confluent flink statement create my-statement --sql "SELECT * FROM my-topic;" --compute-pool lfcp-123456 --service-account sa-123456 --database my-cluster --property property1=value1,property2=value2

No examples.

## See Also¶

  * [confluent flink statement](index.html#confluent-flink-statement) \- Manage Flink SQL statements.
