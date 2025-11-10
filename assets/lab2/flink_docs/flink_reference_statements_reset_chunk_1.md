---
document_id: flink_reference_statements_reset_chunk_1
source_file: flink_reference_statements_reset.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/reset.html
title: SQL RESET Statement in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# RESET Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables resetting Flink SQL shell properties to default values.

## Syntax¶

    RESET 'key';

## Description¶

Reset the Flink SQL shell configuration to the default settings.

If no key is specified, all properties are set to their default values.

To assign a session property, use the [SET Statement in Confluent Cloud for Apache Flink](set.html#flink-sql-set-statement).

## Example¶

The following examples show how to run a `RESET` statement in the Flink SQL shell.

    RESET 'table.local-time-zone';

Your output should resemble:

    configuration key "table.local-time-zone" has been reset successfully.
    +------------------------+---------------------+
    |          Key           |        Value        |
    +------------------------+---------------------+
    | client.service-account | <unset> (default)   |
    | sql.local-time-zone    | GMT+02:00 (default) |
    +------------------------+---------------------+

    RESET;

    configuration has been reset successfully.
    +------------------------+---------------------+
    |          Key           |        Value        |
    +------------------------+---------------------+
    | client.service-account | <unset> (default)   |
    | sql.local-time-zone    | GMT+02:00 (default) |
    +------------------------+---------------------+
