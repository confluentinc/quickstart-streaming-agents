---
document_id: flink_operate-and-deploy_carry-over-offsets_chunk_1
source_file: flink_operate-and-deploy_carry-over-offsets.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/carry-over-offsets.html
title: Carry-over Offsets in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Carry-over Offsets in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® supports carry-over offsets, which means that you can use the topic offsets from one statement to start a new statement.

Carry-over offsets provide a streamlined way to update Flink statements without data loss. This feature eliminates the manual complexity of copying offsets between statements and reduces the need to monitor statement status when deploying CI/CD pipelines.

Automatic orchestration handles the upgrade process. The system automatically waits for the old statement to stop before starting the new one, providing a seamless transition of processing between statements.

Carry-over offsets are available only when replacing an existing statement. This feature enables you to [evolve statements](../concepts/schema-statement-evolution.html#flink-sql-schema-and-statement-evolution) with exactly-once semantics across the update when the statement is “stateless”, as determined by the system. At high level, “stateless” applies to statements that can process each event independently and in any order. For other scenarios (e.g. aggregates, lag, windows, pattern matching, or use of upsert sink for example), this feature can’t be used, because the update may cause inconsistent results.

To use carry-over offsets, add the `sql.tables.initial-offset-from` property to the statement configuration when you create your new statement, for example:

In the Confluent Cloud Console and the Flink SQL shell, you can set the property via:

    SET 'sql.tables.initial-offset-from' = '<reference-statement-name>'

The `<reference-statement-name>` is the name of the statement that you want to use as the reference for the carry-over offsets.

## Considerations for carry-over offsets¶

### Regional Limitations¶

  * The referenced statement must be in the same organization, environment, and region as the new statement.
  * Cross-region offset carry-over is not supported using this property.

### Timeout Behavior¶

  * New statements will wait up to 6 hours for the referenced statement to stop.
  * If the timeout expires, the new statement will fail with an error message indicating the reason.

### Table Options Priority¶

  * Explicit table options in your SQL text take precedence over inherited offsets.
  * Only tables without explicit options will use carried-over offsets.

Example of table options priority:

    INSERT INTO output
      SELECT * FROM table1
    UNION ALL
      SELECT * FROM table2 /*+ OPTIONS('scan.startup.mode' = 'latest-offset') */;

Result: `table1` uses carried-over offsets, `table2` uses the specified `latest-offset` mode.

## Common Issues¶

### Statement Not Found Error¶

  * Verify the referenced statement name is correct.
  * Ensure the statement exists in the same org/env/region.

### Timeout Exceeded¶

  * Check if the old statement is actually stopping.
  * Verify there are no blocking conditions preventing termination.

### Invalid SQL Error¶

  * The new statement’s syntax is validated immediately upon creation.
  * Fix SQL syntax errors before the offset carry-over process begins.

### Referenced Statement Savepoint Failed¶

  * The statement failed to be submitted because the referenced statement didn’t enter a stopped state gracefully. Data inconsistencies can occur when using offsets from failed savepoints.
  * Try to resume the referenced statement and stop it again.
  * If there are still issues, contact [Confluent Support](https://support.confluent.io/).

## Examples¶

### Statement already stopped¶

You have a stopped statement named `my-original-statement`.

Create a new statement with updated logic:

    INSERT INTO enhanced_output
    SELECT
        user_id,
        event_type,
        timestamp,
        new_field
    FROM user_events
    WHERE event_type IN ('click', 'view', 'purchase')
    WITH (
        'sql.tables.initial-offset-from' = 'my-original-statement'
    );

### Statement still running¶

Your original statement `metrics-processor-v1` is still running,

    INSERT INTO enhanced_output
    SELECT
        user_id,
        event_type,
        timestamp,
        new_field
    FROM user_events
    WHERE event_type IN ('click', 'view', 'purchase')
    WITH (
        'sql.tables.initial-offset-from' = 'metrics-processor-v1'
    );

The new statement remains in the “Pending” state until you stop `metrics-processor-v1`.
