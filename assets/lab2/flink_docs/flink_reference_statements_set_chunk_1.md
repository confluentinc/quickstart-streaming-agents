---
document_id: flink_reference_statements_set_chunk_1
source_file: flink_reference_statements_set.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/set.html
title: SQL SET Statement in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 3
---

# SET Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables setting Flink SQL shell properties to different values.

## Syntax¶

    SET 'key' = 'value';

## Description¶

Modify or list the Flink SQL shell configuration.

If no key and value are specified, `SET` prints all of the properties that you have assigned for the session.

To reset a session property to its default value, use the [RESET Statement in Confluent Cloud for Apache Flink](reset.html#flink-sql-reset-statement).

Note

In a Cloud Console workspace, the SET statement can’t be run separately and must be submitted along with another Flink SQL statement, like SELECT, CREATE, or INSERT, for example:

    SET 'sql.current-catalog' = 'default';
    SET 'sql.current-database' = 'cluster_0';
    SELECT * FROM pageviews;

## Example¶

The following examples show how to run a `SET` statement in the Flink SQL shell.

    SET 'table.local-time-zone' = 'America/Los_Angeles';

Your output should resemble:

    Statement successfully submitted.
    Statement phase is COMPLETED.
    configuration updated successfully.

To list the current session settings, run the `SET` command with no parameters.

    SET;

Your output should resemble:

     Statement successfully submitted.
     Statement phase is COMPLETED.
    +-----------------------+--------------------------+
    |          Key          |          Value           |
    +-----------------------+--------------------------+
    | catalog               | default (default)        |
    | default_database      | <your_cluster> (default) |
    | table.local-time-zone | America/Los_Angeles      |
    +-----------------------+--------------------------+

The `SET;` operation is not supported in Cloud Console workspaces.
