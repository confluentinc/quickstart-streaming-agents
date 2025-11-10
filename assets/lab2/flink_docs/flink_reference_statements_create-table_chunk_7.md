---
document_id: flink_reference_statements_create-table_chunk_7
source_file: flink_reference_statements_create-table.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-table.html
title: SQL CREATE TABLE Statement in Confluent Cloud for Apache Flink
chunk_index: 7
total_chunks: 14
---

EXCLUDING WATERMARKS EXCLUDING METADATA );

## WITH options¶

Table properties used to create a table source or sink.

Both the key and value of the expression `key1=val1` are string literals.

You can change an existing table’s property values by using the [ALTER TABLE Statement in Confluent Cloud for Apache Flink](alter-table.html#flink-sql-alter-table).

You can set the following properties when you create a table.

changelog.mode | error-handling.log.target | error-handling.mode
---|---|---
kafka.cleanup-policy | kafka.max-message-size | kafka.retention.size
kafka.retention.time | key.fields-prefix | key.format
key.format.schema-context | scan.bounded.mode | scan.bounded.timestamp-millis
scan.startup.mode | value.fields-include | value.format
value.format.schema-context |  |

### changelog.mode¶

Set the changelog mode of the connector. For more information on changelog modes, see [dynamic tables](../../concepts/dynamic-tables.html#flink-sql-dynamic-tables).

    'changelog.mode' = [append | upsert | retract]

These are the changelog modes for an inferred table:

* `append` (if uncompacted and not a Debezium envelope)
* `upsert` (if compacted)
* `retract` (if a Debezium envelope is detected and uncompacted)

These are the changelog modes for a manually created table:

* `append`
* `retract`
* `upsert`

#### Primary key interaction¶

With a primary key declared, the changelog modes have these properties:

* `append` means that every row can be treated as an independent fact.
* `retract` means that the combination of `+U` and `-U` are related and must be partitioned together.
* `upsert` means that all rows with same primary key are related and must be partitioned together

To build indices, primary keys must be partitioned together.

Encoding of changes | Default Partitioning without PK | Default Partitioning with PK | Custom Partitioning without PK | Custom Partitioning with PK
---|---|---|---|---
Each value is an insertion (+I). | round robin | hash by PK | hash by specified column(s) | hash by subset of PK
A special `op` header represents the change (+I, -U, +U, -D). The header is omitted for insertions. Append queries encoding is the same for all modes. | hash by entire value | hash by PK | hash by specified column(s) | hash by subset of PK
If value is `null`, it represents a deletion (-D). Other values are +U and the engine will normalize the changelog internally. | unsupported, PK is mandatory | hash by PK | unsupported, PK is mandatory | unsupported

#### Change type header¶

Changes for an [updating table](../../concepts/dynamic-tables.html#flink-sql-dynamic-tables-updating-table) have the change type encoded in the Kafka record as a special `op` header that represents the change (+I, -U, +U, -D). The value of the `op` header, if present, represents the kind of change that a row can describe in a changelog:

* `0`: represents INSERT (+I), an insertion operation.
* `1`: represents UPDATE_BEFORE (-U), an update operation with the previous content of the updated row.
* `2`: represents UPDATE_AFTER (+U), an update operation with new content for the updated row.
* `3`: represents DELETE (-D), a deletion operation.

The default is `0`.

For more information, see [Changelog entries](../../concepts/dynamic-tables.html#flink-sql-dynamic-tables-changelog-entries).

### error-handling.log.target¶

* Type: string
* Default: `error_log`

    'error-handling.log.target' = '<dlq_table_name>'

Specify the destination Dead Letter Queue (DLQ) table for error logs when error-handling.mode is set to `log`.

If `error-handling.log.target` isn’t set, the default is `error_log`. If the DLQ table doesn’t exist and can’t be created, the job fails.

* The principal running the CREATE TABLE or ALTER TABLE statement must have permissions to create the DLQ topic and schema. If permissions are missing, the statement fails.
* If a principal runs a SELECT or any other query, it needs permissions to write into the defined DLQ table. If permissions are missing, the statement fails.
* For more information, see [Grant Role-Based Access in Confluent Cloud for Apache Flink](../../operate-and-deploy/flink-rbac.html#flink-rbac).

### error-handling.mode¶

* Type: enum
* Default: `fail`

    'error-handling.mode' = [fail | ignore | log]

Control how Flink handles deserialization errors for a table.

The following values are supported.

* `fail`: The statement fails on error (default).
* `ignore`: The error is skipped and processing continues.
* `log`: The error is logged to a Dead Letter Queue (DLQ) table and processing continues.

When a statement reads from the table, for example, `SELECT * FROM my_table`, and a deserialization error occurs, as with a _poison pill_ , Flink handles the error based on the `error-handling.mode` setting.
