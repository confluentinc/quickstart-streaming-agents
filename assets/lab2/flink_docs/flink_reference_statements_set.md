---
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/set.html
title: SQL SET Statement in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'statements', 'set.html']
scraped_date: 2025-09-05T13:49:01.908852
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

## Available SET Options¶

These are the available configuration options available by using the SET statement in Confluent Cloud for Apache Flink.

For a comparison of option names with corresponding options in Apache Flink, see [Configuration options](../../concepts/comparison-with-apache-flink.html#flink-comparison-with-open-source-config-options).

### Table options¶

Key | Default | Type | Description  
---|---|---|---  
sql.current-catalog | (None) | String | Defines the current catalog. Semantically equivalent with [USE CATALOG [catalog_name]](use-catalog.html#flink-sql-use-catalog-statement). Required if object identifiers are not fully qualified.  
sql.current-database | (None) | String | Defines the current database. Semantically equivalent with [USE [database_id]](use-database.html#flink-sql-use-database-statement). Required if object identifiers are not fully qualified.  
sql.dry-run | `false` | Boolean | If `true`, the statement is parsed and validated but not executed.  
sql.inline-result | `false` | Boolean | If `true`, query results are returned inline.  
sql.local-time-zone | “UTC” | String | Specifies the local time zone offset for [TIMESTAMP_LTZ](../datatypes.html#flink-sql-timestamp-ltz) conversions. When converting to data types that don’t include a time zone (for example, TIMESTAMP, TIME, or simply STRING), this time zone is used. The input for this option is either a Time Zone Database (TZDB) ID, like “America/Los_Angeles”, or fixed offset, like “GMT+03:00”.  
sql.snapshot.mode | “off” | String | Specifies the mode for snapshot queries. Valid values are “now” and “off”. If not specified, the default value is “now”. For more information, see [Snapshot Queries in Confluent Cloud for Apache Flink](../../concepts/snapshot-queries.html#flink-sql-snapshot-queries).  
sql.state-ttl | 0 ms | Duration | Specifies a minimum time interval for how long idle state, which is state that hasn’t been updated, is retained. The system decides on actual clearance after this interval. If set to the default value of `0`, no clearance is performed.  
sql.tables.initial-offset-from | (None) | String | Specifies the name of a reference statement from which to carry over topic offsets when creating a new statement. Applies only when replacing an existing statement in the same organization, environment, and region. For details, see [Carry Over Offsets](../../operate-and-deploy/carry-over-offsets.html#flink-sql-carry-over-offsets).  
sql.tables.scan.bounded.timestamp-millis | (None) | Long | Overwrites [scan.bounded.timestamp-millis](create-table.html#flink-sql-create-table-with-scan-bounded-timestamp-millis) for Confluent-native tables used in newly created queries. This option is not applied if the table uses a value that differs from the default value.  
sql.tables.scan.bounded.mode | (None) | `GlobalScanBoundedMode` | Overwrites [scan.bounded.mode](create-table.html#flink-sql-create-table-with-scan-bounded-mode) for Confluent-native tables used in newly created queries. This option is not applied if the table uses a value that differs from the default value.  
sql.tables.scan.idle-timeout | (None) | Duration | Specifies the timeout interval for progressive idleness detection. Setting this value to `0` disables idleness detection. For more information, see [Progressive idleness detection](create-table.html#flink-sql-watermark-clause-progressive-idleness).  
sql.tables.scan.watermark-alignment.max-allowed-drift | 5 min | Duration | Specifies the maximum allowed drift for watermark alignment across different splits or partitions to ensure even processing. Setting to `0` disables watermark alignment, which can prevent performance bottlenecks and latency for queries that don’t require event-time semantics, like regular joins, non-windowed aggregations, and ETL. Intended for advanced use-cases, because incorrect use can cause issues, for example, state growth, in queries that depend on event-time. For more information, see [Watermark alignment](../../concepts/timely-stream-processing.html#flink-sql-watermarks-watermark-alignment).  
sql.tables.scan.startup.timestamp-millis | (None) | Long | Overwrites [scan.startup.timestamp-millis](create-table.html#flink-sql-create-table-with-scan-startup-timestamp-millis) for Confluent-native tables used in newly created queries. This option is not applied if the table uses a value that differs from the default value.  
sql.tables.scan.startup.mode | (None) | `GlobalScanStartupMode` | Overwrites [scan.startup.mode](create-table.html#flink-sql-create-table-with-scan-startup-mode) for Confluent-native tables used in newly created queries. This option is not applied if the table uses a value that differs from the default value.  
sql.tables.scan.source-operator-parallelism | (None) | Int | Specifies the parallelism of the source operator for tables. This option is not applied if the table has already set a value.  
  
### Flink SQL shell options¶

The following SET options are available only in the Flink SQL shell.

In a Cloud Console workspace, the only `client` option you can set is `client.statement-name`.

Key | Default | Type | Description  
---|---|---|---  
client.output-format | standard | String | Output format. Valid values are “standard” or “plain-text”.  
client.results-timeout | 600000 | Long | Total amount of time, in milliseconds, to wait before timing out the request waiting for results to be ready.  
client.service-account | (None) | String | Service account to use instead of running statements attached to your user account. For more information, see [Production workloads (service accounts)](../../operate-and-deploy/flink-rbac.html#flink-rbac-grant-sa-and-user-permission-for-sql-statements).  
client.statement-name | (None) | String | Give your Flink statement a meaningful name that can help you identify it more easily. Instead of an autogenerated name, like `123e4567-e89b-12d3`, this sets the statement name to the given value. To avoid naming conflicts, the name resets itself after successful submission. The underscore character (`_`) and period character (`.`) are not supported.  
  
