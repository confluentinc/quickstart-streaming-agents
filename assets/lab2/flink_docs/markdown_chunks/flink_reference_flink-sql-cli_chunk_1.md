---
document_id: flink_reference_flink-sql-cli_chunk_1
source_file: flink_reference_flink-sql-cli.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/flink-sql-cli.html
title: Confluent CLI commands with Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 6
---

# Confluent CLI commands with Confluent Cloud for Apache Flink¶

Manage Flink SQL statements and compute pools in Confluent Cloud for Apache Flink® by using the [confluent flink ](https://docs.confluent.io/confluent-cli/current/command-reference/flink/index.html) commands in the Confluent CLI. To see the available commands, use the `--help` option.

    confluent flink statement --help
    confluent flink compute-pool --help
    confluent flink region --help

Use the Confluent CLI to manage these features:

  * Statements
  * Compute pools
  * Regions

For the complete CLI reference, see [confluent flink statement](https://docs.confluent.io/confluent-cli/current/command-reference/flink/index.html).

In addition to the CLI, you can manage Flink statements and compute pools by using these Confluent tools:

  * [Flink SQL REST API](../operate-and-deploy/flink-rest-api.html#flink-rest-api)
  * [Cloud Console](../get-started/quick-start-cloud-console.html#flink-sql-quick-start-run-sql-statement)
  * [SQL shell](../get-started/quick-start-shell.html#flink-sql-quick-start-shell)
  * [Confluent Terraform Provider](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs)
