---
document_id: flink_reference_statements_set_chunk_2
source_file: flink_reference_statements_set.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/set.html
title: SQL SET Statement in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 3
---

supported in Cloud Console workspaces.

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
