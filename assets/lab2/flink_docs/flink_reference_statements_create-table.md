---
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-table.html
title: SQL CREATE TABLE Statement in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'statements', 'create-table.html']
scraped_date: 2025-09-05T13:48:44.871581
---

# CREATE TABLE Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables creating tables backed by Apache Kafka® topics by using the CREATE TABLE statement. With Flink tables, you can run SQL queries on streaming data in Kafka topics.

## Syntax¶

    CREATE TABLE [IF NOT EXISTS] [catalog_name.][db_name.]table_name
      (
        { <physical_column_definition> |
          <metadata_column_definition> |
          <computed_column_definition> |
          <column_in_vector_db_provider> }[ , ...n]
        [ <watermark_definition> ]
        [ <table_constraint> ][ , ...n]
      )
      [COMMENT table_comment]
      [DISTRIBUTED BY (distribution_column_name1, distribution_column_name2, ...) INTO n BUCKETS]
      WITH (key1=value1, key2=value2, ...)
      [ LIKE source_table [( <like_options> )] | AS select_query ]

    <physical_column_definition>:
      column_name column_type [ <column_constraint> ] [COMMENT column_comment]

    <metadata_column_definition>:
      column_name column_type METADATA [ FROM metadata_key ] [ VIRTUAL ]

    <computed_column_definition>:
      column_name AS computed_column_expression [COMMENT column_comment]

    <column_in_vector_db_provider>
      column_name column_type

    <watermark_definition>:
      WATERMARK FOR rowtime_column_name AS watermark_strategy_expression

    <table_constraint>:
      [CONSTRAINT constraint_name] PRIMARY KEY (column_name, ...) NOT ENFORCED

    <like_options>:
    {
     { INCLUDING | EXCLUDING } { ALL | CONSTRAINTS | PARTITIONS } |
     { INCLUDING | EXCLUDING | OVERWRITING } { GENERATED | OPTIONS | WATERMARKS }
    }

## Description¶

Register a table into the current or specified catalog. When a table is registered, you can use it in SQL queries.

The CREATE TABLE statement always creates a backing Kafka topic as well as the corresponding schema subjects for key and value.

Trying to create a table with a name that exists in the catalog causes an exception.

The table name can be in these formats:

* `catalog_name.db_name.table_name`: The table is registered with the catalog named “catalog_name” and the database named “db_name”.
* `db_name.table_name`: The table is registered into the current catalog of the execution table environment and the database named “db_name”.
* `table_name`: The table is registered into the current catalog and the database of the execution table environment.

A table registered with the CREATE TABLE statement can be used as both table source and table sink. Flink can’t determine whether the table is used as a source or a sink until it’s referenced in a [DML query](../queries/overview.html#flink-sql-queries).

The following sections show the options and clauses that are available with the CREATE TABLE statement.

* Physical / Regular Columns
* Metadata columns
* Computed columns
* System columns
* Watermark clause
* PRIMARY KEY constraint
* DISTRIBUTED BY clause
* CREATE TABLE AS SELECT (CTAS)
* LIKE
* WITH options

## Usage¶

This following CREATE TABLE statement registers a table named `t1` in the current catalog. Also, it creates a backing Kafka topic and corresponding value-schema. By default, the table is registered as append-only, uses AVRO serializers, and reads from the earliest offset.

    CREATE TABLE t1 (
      `id` BIGINT,
      `name` STRING,
      `age` INT,
      `salary` DECIMAL(10,2),
      `active` BOOLEAN,
      `created_at` TIMESTAMP_LTZ(3)
    );

You can override defaults by specifying WITH options. The following SQL registers the table in retraction mode, so you can use the table to sink the results of a [streaming join](../queries/joins.html#flink-sql-joins).

    CREATE TABLE t2 (
      `id` BIGINT,
      `name` STRING,
      `age` INT,
      `salary` DECIMAL(10,2),
      `active` BOOLEAN,
      `created_at` TIMESTAMP_LTZ(3)
    ) WITH (
      'changelog.mode' = 'retract'
    );

## Physical / Regular Columns¶

Physical or regular columns are the columns that define the structure of the table and the data types of its fields.

Each physical column is defined by a name and a data type, and optionally, a column constraint. You can use the column constraint to specify additional properties of the column, such as whether it is a unique key.

Example

The following SQL shows how to declare physical columns of various types in a table named `t1`. For available column types, see [Data Types](../datatypes.html#flink-sql-datatypes).

    CREATE TABLE t1 (
      `id` BIGINT,
      `name` STRING,
      `age` INT,
      `salary` DECIMAL(10,2),
      `active` BOOLEAN,
      `created_at` TIMESTAMP_LTZ(3)
    );

## Metadata columns¶

You can access the following table metadata as metadata columns in a table definition.

* Available metadata
* leader-epoch
* offset
* partition
* raw-key
* raw-value
* timestamp
* timestamp-type
* topic

Use the METADATA keyword to declare a metadata column.

Metadata fields are readable or readable/writable. Read-only columns must be declared VIRTUAL to exclude them during INSERT INTO operations.

Metadata columns are not registered in Schema Registry.

Example

The following CREATE TABLE statement shows the syntax for exposing metadata fields.

    CREATE TABLE t (
      `user_id` BIGINT,
      `item_id` BIGINT,
      `behavior` STRING,
      `event_time` TIMESTAMP_LTZ(3) METADATA FROM 'timestamp',
      `partition` BIGINT METADATA VIRTUAL,
      `offset` BIGINT METADATA VIRTUAL
    );

### Available metadata¶

#### headers¶

* Type: MAP NOT NULL
* Access: readable/writable

Headers of the Kafka record as a map of raw bytes.

#### leader-epoch¶

* Type: INT NULL
* Access: readable

Leader epoch of the Kafka record, if available.

#### offset¶

* Type: BIGINT NOT NULL
* Access: readable

Offset of the Kafka record in the partition.

#### partition¶

* Type: INT NOT NULL
* Access: readable

Partition ID of the Kafka record.

#### raw-key¶

* Type: BYTES NOT NULL
* Access: readable

The unique identifier or key of the Kafka record as raw bytes. The type may vary based on the serializer used, for example, STRING for `StringSerializer`.

#### raw-value¶

* Type: BYTES NOT NULL
* Access: readable

The actual message content or payload of the Kafka record as raw bytes. Contains the main data being transmitted. The type may vary based on the serializer used, for example, STRING for `StringSerializer`.

#### timestamp¶

* Type: TIMESTAMP_LTZ(3) NOT NULL
* Access: readable/writable

Timestamp of the Kafka record.

With `timestamp`, you can pass [event time](../../concepts/timely-stream-processing.html#flink-sql-event-time-and-watermarks) end-to-end. Otherwise, the sink uses the ingestion time by default.

#### timestamp-type¶

* Type: STRING NOT NULL
* Access: readable

Timestamp type of the Kafka record.

Valid values are:

* “NoTimestampType”
* “CreateTime” (also set when writing metadata)
* “LogAppendTime”

#### topic¶

* Type: STRING NOT NULL
* Access: readable

Topic name of the Kafka record.

## Computed columns¶

Computed columns are virtual columns that are not stored in the table but are computed on the fly based on the values of other columns. These virtual columns are not registered in Schema Registry.

A computed column is defined by using an expression that references one or more physical or metadata columns in the table. The expression can use arithmetic [operators](../functions/comparison-functions.html#flink-sql-comparison-and-equality-functions), [functions](../functions/overview.html#flink-sql-functions-overview), and other SQL constructs to manipulate the values of the physical and metadata columns and compute the value of the computed column.

Example

The following CREATE TABLE statement shows the syntax for declaring a `full_name` computed column by concatenating a `first_name` column and a `last_name` column.

    CREATE TABLE t (
      `id` BIGINT,
      `first_name` STRING,
      `last_name` STRING,
      `full_name` AS CONCAT(first_name, ' ', last_name)
    );

## Vector database columns¶

Confluent Cloud for Apache Flink supports read-only external tables to enable search with federated query execution on external vector databases, like MongoDB, Pinecone, and ElasticSearch.

Note

Vector Search is an Open Preview feature in Confluent Cloud.

A Preview feature is a Confluent Cloud component that is being introduced to gain early feedback from developers. Preview features can be used for evaluation and non-production testing purposes or to provide feedback to Confluent. The warranty, SLA, and Support Services provisions of your agreement with Confluent do not apply to Preview features. Confluent may discontinue providing preview releases of the Preview features at any time in Confluent’s’ sole discretion.

For more information, see [Vector Search](../../../ai/external-tables/vector-search.html#flink-sql-vector-search).

## System columns¶

Confluent Cloud for Apache Flink introduces system columns for Flink tables. System columns build on the metadata columns.

System columns can only be read and are not part of the query-to-sink schema.

System columns aren’t selected in a `SELECT *` statement, and they’re not shown in `DESCRIBE` or `SHOW CREATE TABLE` statements. The result from the `DESCRIBE EXTENDED` statement _does_ include system columns.

Both inferred and manual tables are provisioned with a set of default system columns.

### $rowtime¶

Currently, `$rowtime TIMESTAMP_LTZ(3) NOT NULL` is provided as a system column.

You can use the `$rowtime` system column to get the timestamp from a Kafka record, because `$rowtime` is exactly the Kafka record timestamp. If you want to write out `$rowtime`, you must use the timestamp metadata key.

## PRIMARY KEY constraint¶

A primary key constraint is a hint for Flink SQL to leverage for optimizations which specifies that a column or a set of columns in a table or a view are unique and they _do not_ contain null.

A primary key uniquely identifies a row in a table. No columns in a primary key can be nullable.

You can declare a primary key constraint together with a column definition (a column constraint) or as a single line (a table constraint). In both cases, it must be declared as a singleton. If you define more than one primary key constraint in the same statement, Flink SQL throws an exception.

The SQL standard specifies that a constraint can be `ENFORCED` or `NOT ENFORCED`, which controls whether the constraint checks are performed on the incoming/outgoing data. Flink SQL doesn’t own the data, so the only mode it supports is `NOT ENFORCED`. It’s your responsibility to ensure that the query enforces key integrity.

Flink SQL assumes correctness of the primary key by assuming that the column’s nullability is aligned with the columns in primary key. Connectors must ensure that these are aligned.

The `PRIMARY KEY` constraint distributes the table implicitly by the key column. A Kafka message key is defined either by an implicit DISTRIBUTED BY clause clause from a PRIMARY KEY constraint or an explicit `DISTRIBUTED BY`.

Note

In a CREATE TABLE statement, a primary key constraint alters the column’s nullability, which means that a column with a primary key constraint isn’t nullable.

Example

The following SQL statement creates a table named `latest_page_per_ip` with a primary key defined on `ip`. This statement creates a Kafka topic, a value-schema, and a key-schema. The value-schema contains the definitions for `page_url` and `ts`, while the key-schema contains the definition for `ip`.

    CREATE TABLE latest_page_per_ip (
        `ip` STRING,
        `page_url` STRING,
        `ts` TIMESTAMP_LTZ(3),
        PRIMARY KEY(`ip`) NOT ENFORCED
    );

## DISTRIBUTED BY clause¶

The `DISTRIBUTED BY` clause buckets the created table by the specified columns.

Bucketing enables a file-like structure with a small, human-enumerable key space. It groups rows that have “infinite” key space, like `user_id`, usually by using a hash function, for example:

    bucket = hash(user_id) % number_of_buckets

Kafka partitions map 1:1 to SQL buckets. The `n` BUCKETS are used for the number of partitions when creating a topic.

If `n` is not defined, the default is 6.

* The number of buckets is fixed.
* A bucket is identifiable regardless of partition.
* Bucketing is good in long-term storage for reading across partitions based on a large key space, for example, `user_id`.
* Also, bucketing is good for short-term storage for load balancing.

Every mode comes with a default distribution, so DISTRIBUTED BY is required only by power users. In most cases, a simple `CREATE TABLE t (schema);` is sufficient.

* For upsert mode, the bucket key must be equal to primary key.
* For append/retract mode, the bucket key can be a subset of the primary key.
* The bucket key can be undefined, which corresponds to a “connector defined” distribution: round robin for append, and hash-by-row for retract.

Custom distributions are possible, but currently only custom hash distributions are supported.

Example

The following SQL declares a table named `t_dist` that has one key column named `k` and 4 Kafka partitions.

    CREATE TABLE t_dist (k INT, s STRING) DISTRIBUTED BY (k) INTO 4 BUCKETS;

## PARTITIONED BY clause¶

**Deprecated** Use the DISTRIBUTED BY clause instead.

The `PARTITIONED BY` clause partitions the created table by the specified columns.

Use `PARTITIONED BY` to declare key columns in a table explicitly. A Kafka message key is defined either by an explicit `PARTITIONED BY` clause or an implicit `PARTITIONED BY` clause from a PRIMARY KEY constraint.

If compaction is enabled, the Kafka message key is overloaded with another semantic used for compaction, which influences constraints on the Kafka message key for partitioning.

Example

The following SQL declares a table named `t` that has one key column named `key` of type INT.

    CREATE TABLE t (partition_key INT, example_value STRING) PARTITIONED BY (partition_key);

## Watermark clause¶

The `WATERMARK` clause defines the [event-time attributes](../../concepts/timely-stream-processing.html#flink-sql-event-time-and-watermarks) of a table.

A [watermark](../../../_glossary.html#term-watermark) in Flink is used to track the progress of event time and provide a way to trigger time-based operations.

### Default watermark strategy¶

Confluent Cloud for Apache Flink provides a default watermark strategy for all tables, whether created automatically from a Kafka topic or from a CREATE TABLE statement.

The default watermark strategy is applied on the `$rowtime` system column.

Watermarks are calculated per Kafka partition, and at least 250 events are required per partition.

If a delay of longer than 7 days can occur, choose a custom watermark strategy.

Because the concrete implementation is provided by Confluent, you see only `WATERMARK FOR $rowtime AS SOURCE_WATERMARK()` in the declaration.

### Custom watermark strategies¶

You can replace the default strategy with a custom strategy at any time by using [ALTER TABLE](alter-table.html#flink-sql-alter-table).

### Watermark strategy reference¶

    WATERMARK FOR rowtime_column_name AS watermark_strategy_expression

The `rowtime_column_name` defines an existing column that is marked as the event-time attribute of the table. The column must be of type `TIMESTAMP(3)`, and it must be a top-level column in the schema.

The `watermark_strategy_expression` defines the watermark generation strategy. It allows arbitrary non-query expressions, including computed columns, to calculate the watermark. The expression return type must be `TIMESTAMP(3)`, which represents the timestamp since the Unix Epoch.

The returned watermark is emitted only if it’s non-null and its value is larger than the previously emitted local watermark, to respect the contract of ascending watermarks.

The watermark generation expression is evaluated by Flink SQL for every record. The framework emits the largest generated watermark periodically.

No new watermark is emitted if any of the following conditions apply.

* The current watermark is null.
* The current watermark is identical to the previous watermark.
* The value of the returned watermark is smaller than the value of the last emitted watermark.

When you use event-time semantics, your tables must contain an event-time attribute and watermarking strategy.

Flink SQL provides these watermark strategies.

* **Strictly ascending timestamps:** Emit a watermark of the maximum observed timestamp so far. Rows that have a timestamp larger than the max timestamp are not late.

        WATERMARK FOR rowtime_column AS rowtime_column

* **Ascending timestamps:** Emit a watermark of the maximum observed timestamp so far, minus _1_. Rows that have a timestamp larger than or equal to the max timestamp are not late.

        WATERMARK FOR rowtime_column AS rowtime_column - INTERVAL '0.001' SECOND

* **Bounded out-of-orderness timestamps:** Emit watermarks which are the maximum observed timestamp minus the specified delay.

        WATERMARK FOR rowtime_column AS rowtime_column - INTERVAL 'string' timeUnit

The following example shows a “5-seconds delayed” watermark strategy.

        WATERMARK FOR rowtime_column AS rowtime_column - INTERVAL '5' SECOND

Example

The following CREATE TABLE statement defines an `orders` table that has a rowtime column named `order_time` and a watermark strategy with a 5-second delay.

    CREATE TABLE orders (
        `user` BIGINT,
        `product` STRING,
        `order_time` TIMESTAMP(3),
        WATERMARK FOR `order_time` AS `order_time` - INTERVAL '5' SECOND
    );

### Progressive idleness detection¶

When a source does not receive any elements for a timeout time, which is specified by the `sql.tables.scan.idle-timeout` property, the source is marked as temporarily idle. This enables each downstream task to advance its watermark without the need to wait for watermarks from this source while it’s idle.

By default, Confluent Cloud for Apache Flink has progressive idleness detection that starts with an idle-timeout of 15 seconds, and increases to a maximum of 5 minutes over time.

You can disable idleness detection by setting the `sql.tables.scan.idle-timeout` property to `0`, or you can set a fixed idleness timeout with your desired value. When idleness detection is disabled, a single idle partition on any of the sources causes the watermarks to stop advancing. In turn, this causes operations that rely on watermarks to stop producing results. On the other hand, with idleness detection enabled, with either progressive idleness or a fixed value, the watermark advances unless all partitions of all sources are idle.

For more information, see the video, [How to Set Idle Timeouts](https://www.youtube.com/watch?v=YSIhM5-Sykw).

## CREATE TABLE AS SELECT (CTAS)¶

Tables can also be created and populated by the results of a query in one create-table-as-select (CTAS) statement. CTAS is the simplest and fastest way to create and insert data into a table with a single command.

The CTAS statement consists of two parts:

* The SELECT part can be any SELECT query supported by Flink SQL.
* The CREATE part takes the resulting schema from the SELECT part and creates the target table.

The following two code examples are equivalent.

    -- Equivalent to the following CREATE TABLE and INSERT INTO statements.
    CREATE TABLE my_ctas_table
    AS SELECT id, name, age FROM source_table WHERE mod(id, 10) = 0;

    -- These two statements are equivalent to the preceding CREATE TABLE AS statement.
    CREATE TABLE my_ctas_table (
        id BIGINT,
        name STRING,
        age INT
    );

    INSERT INTO my_ctas_table SELECT id, name, age FROM source_table WHERE mod(id, 10) = 0;

Similar to CREATE TABLE, CTAS requires all options of the target table to be specified in the WITH clause. The syntax is `CREATE TABLE t WITH (…) AS SELECT …`, for example:

    CREATE TABLE t WITH ('scan.startup.mode' = 'latest-offset') AS SELECT * FROM b;

### Specifying explicit columns¶

The CREATE part enables you to specify explicit columns. The resulting table schema contains the columns defined in the CREATE part first, followed by the columns from the SELECT part. Columns named in both parts retain the same column position as defined in the SELECT part.

You can also override the data type of SELECT columns if you specify it in the CREATE part.

    CREATE TABLE my_ctas_table (
        desc STRING,
        quantity DOUBLE,
        cost AS price * quantity,
        WATERMARK FOR order_time AS order_time - INTERVAL '5' SECOND,
    ) AS SELECT id, price, quantity, order_time FROM source_table;

### Primary keys and distribution strategies¶

The CREATE part enable you to specify primary keys and distribution strategies. Primary keys work only on NOT NULL columns. Currently, primary keys only allow you to define columns from the SELECT part, which may be NOT NULL.

The following two code examples are equivalent.

    -- Equivalent to the following CREATE TABLE and INSERT INTO statements.
    CREATE TABLE my_ctas_table (
        PRIMARY KEY (id) NOT ENFORCED
    ) DISTRIBUTED BY HASH(id) INTO 4 BUCKETS
    AS SELECT id, name FROM source_table;

    -- These two statements are equivalent to the preceding CREATE TABLE AS statement.
    CREATE TABLE my_ctas_table (
        id BIGINT NOT NULL PRIMARY KEY NOT ENFORCED,
        name STRING
    ) DISTRIBUTED BY HASH(id) INTO 4 BUCKETS;

    INSERT INTO my_ctas_table SELECT id, name FROM source_table;

## LIKE¶

The CREATE TABLE LIKE clause enables creating a new table with the same schema as an existing table. It is a combination of SQL features and can be used to extend or exclude certain parts of the original table. The clause must be defined at the top-level of a CREATE statement and applies to multiple parts of the table definition.

Use the LIKE options to control the merging logic of table features. You can control the merging behavior of:

* CONSTRAINTS - Constraints such as primary key. and unique keys.
* GENERATED - Computed columns.
* METADATA - Metadata columns.
* OPTIONS - Table options.
* PARTITIONS - Partition options.
* WATERMARKS - Watermark strategies.

with three different merging strategies:

* INCLUDING - Includes the feature of the source table and fails on duplicate entries, for example, if an option with the same key exists in both tables.
* EXCLUDING - Does not include the given feature of the source table.
* OVERWRITING - Includes the feature of the source table, overwrites duplicate entries of the source table with properties of the new table. For example, if an option with the same key exists in both tables, the option from the current statement is used.

Additionally, you can use the INCLUDING/EXCLUDING ALL option to specify what should be the strategy if no specific strategy is defined. For example, if you use EXCLUDING ALL INCLUDING WATERMARKS, only the watermarks are included from the source table.

If you provide no LIKE options, INCLUDING ALL OVERWRITING OPTIONS is used as a default.

### Example¶

The following CREATE TABLE statement defines a table named `t` that has 5 physical columns and three metadata columns.

    CREATE TABLE t (
      `user_id` BIGINT,
      `item_id` BIGINT,
      `price` DOUBLE,
      `behavior` STRING,
      `created_at` TIMESTAMP(3),
      `price_with_tax` AS `price` * 1.19,
      `event_time` TIMESTAMP_LTZ(3) METADATA FROM 'timestamp',
      `partition` BIGINT METADATA VIRTUAL,
      `offset` BIGINT METADATA VIRTUAL
    );

You can run the following CREATE TABLE LIKE statement to define table `t_derived`, which contains the physical and computed columns of `t`, drops the metadata and default watermark strategy, and applies a custom watermark strategy on `event_time`.

    CREATE TABLE t_derived (
        WATERMARK FOR `created_at` AS `created_at` - INTERVAL '5' SECOND
    )
    LIKE t (
        EXCLUDING WATERMARKS
        EXCLUDING METADATA
    );

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

* `fail`: Flink fails the statement.
* `ignore`: Flink ignores the error and continues processing with the next row.
* `log`: Flink sends the poison pill to the DLQ table and continues processing with the next row.

All Flink tables receive the `error-handling.mode` setting. If you don’t specify a value, the default is `fail`. You can override the setting for an existing table by using the [ALTER TABLE](alter-table.html#flink-sql-alter-table) statement. Only table-level overrides are supported. Per-statement overrides are not supported.

The following limitations apply:

* Only deserialization errors at the source are supported.
* Errors outside the source, for example, in windowed aggregations, are not handled.

### kafka.cleanup-policy¶

* Type: enum
* Default: `delete`

    'kafka.cleanup-policy' = [delete | compact | delete-compact]

Set the default cleanup policy for Kafka topic log segments beyond the retention window. Translates to the Kafka `log.cleanup.policy` property. For more information, see [Log Compaction](/kafka/design/log_compaction.html).

* `compact`: topic log is compacted periodically in the background by the log cleaner.
* `delete`: old log segments are discarded when their retention time or size limit is reached.
* `delete-compact`: compact the log and follow the retention time or size limit settings.

### kafka.consumer.isolation-level¶

* Type: enum
* Default: `read-committed`

    'kafka.consumer.isolation-level' = [read-committed | read-uncommitted]

Controls which transactional messages to read:

* `read-committed`: Only return messages from committed transactions. Any transactional messages from aborted or in-progress transactions are filtered out.
* `read-uncommitted`: Return all messages, including those from transactional messages that were aborted or are still in progress.

For more information, see [delivery guarantees and latency](../../concepts/delivery-guarantees.html#flink-sql-delivery-guarantees-latency).

### kafka.max-message-size¶

    'kafka.max-message-size' = MemorySize

Translates to the Kafka `max.message.bytes` property.

The default is _2097164_ bytes.

### kafka.producer.compression.type¶

* Type: enum
* Default: `none`

    'kafka.producer.compression.type' = [none | gzip | snappy | lz4 | zstd]

Translates to the Kafka `compression.type` property.

### kafka.retention.size¶

* Type: Integer
* Default: _0_

    'kafka.retention.size' = MemorySize

Translates to the Kafka `log.retention.bytes` property.

### kafka.retention.time¶

* Type: Duration
* Default: `7 days`

    'kafka.retention.time' = '<duration>'

Translates to the Kafka `log.retention.ms` property.

### key.fields-prefix¶

* Type: String
* Default: “”

Specify a custom prefix for all fields of the key format.

    'key.fields-prefix' = '<prefix-string>'

The `key.fields-prefix` property defines a custom prefix for all fields of the key format, which avoids name clashes with fields of the value format.

By default, the prefix is empty. If a custom prefix is defined, the table schema property works with prefixed names.

When constructing the data type of the key format, the prefix is removed, and the non-prefixed names are used within the key format.

This option requires that the value.fields-include property is set to `EXCEPT_KEY`.

The prefix for an inferred table is `key_`, for non-atomic Schema Registry types and fields that have a name.

### key.format¶

* Type: String
* Default: “avro-registry”

Specify the serialization format of the table’s key fields.

    'key.format' = '<key-format>'

These are the key formats for an inferred table:

* `raw` (if no Schema Registry entry)
* `avro-registry` (for AVRO Schema Registry entry)
* `json-registry` (for JSON Schema Registry entry)
* `proto-registry` (for Protobuf Schema Registry entry)

These are the key formats for a manually created table:

* `avro-registry` (for Avro Schema Registry entry)
* `json-registry` (for JSON Schema Registry entry)
* `proto-registry` (for Protobuf Schema Registry entry)

If no format is specified, Avro Schema Registry is used by default. This applies only if a primary or distribution key is defined.

The Schema Registry subject compatibility mode must be FULL or FULL_TRANSITIVE. For more information, see [Schema Evolution and Compatibility for Schema Registry on Confluent Cloud](../../../sr/fundamentals/schema-evolution.html#schema-evolution-and-compatibility).

### key.format.schema-context¶

* Type: String
* Default: (none)

Specify the Confluent Schema Registry Schema Context for the key format.

    'key.<format>.schema-context' = '<schema-context>'

Similar to value.format.schema-context, this option enables you to specify a schema context for the key format. It provides an independent scope in Schema Registry for key schemas.

### scan.bounded.mode¶

* Type: Enum
* Default: `unbounded`

Specify the bounded mode for the Kafka consumer.

    scan.bounded.mode = [latest-offset | timestamp | unbounded]

The following list shows the valid bounded mode values.

* `latest-offset`: bounded by latest offsets. This is evaluated at the start of consumption from a given partition.
* `timestamp`: bounded by a user-supplied timestamp.
* `unbounded`: table is unbounded.

If `scan.bounded.mode` isn’t set, the default is an unbounded table. For more information, see [Bounded and unbounded tables](../../concepts/overview.html#flink-sql-stream-processing-concepts-bounded-and-unbounded-tables).

If `timestamp` is specified, the scan.bounded.timestamp-millis config option is required to specify a specific bounded timestamp in milliseconds since the Unix epoch, `January 1, 1970 00:00:00.000 GMT`.

### scan.bounded.timestamp-millis¶

* Type: Long
* Default: (none)

End at the specified epoch timestamp (milliseconds) when the `timestamp` bounded mode is set in the scan.bounded.mode property.

    'scan.bounded.mode' = 'timestamp',
    'scan.bounded.timestamp-millis' = '<long-value>'

### scan.startup.mode¶

* Type: Enum
* Default: `earliest-offset`

The startup mode for Kafka consumers.

    'scan.startup.mode' = '<startup-mode>'

The following list shows the valid startup mode values.

* `earliest-offset`: start from the earliest offset possible.
* `latest-offset`: start from the latest offset.
* `timestamp`: start from the user-supplied timestamp for each partition.

The default is `earliest-offset`. This differs from the default in Apache Flink, which is `group-offsets`.

If `timestamp` is specified, the scan.startup.timestamp-millis config option is required, to define a specific startup timestamp in milliseconds since the Unix epoch, January 1, 1970 00:00:00.000 GMT.

### scan.startup.timestamp-millis¶

* Type: Long
* Default: (none)

Start from the specified Unix epoch timestamp (milliseconds) when the `timestamp` mode is set in the scan.startup.mode property.

    'scan.startup.mode' = 'timestamp',
    'scan.startup.timestamp-millis' = '<long-value>'

### value.fields-include¶

* Type: Enum
* Default: `except-key`

Specify a strategy for handling key columns in the data type of the value format.

    'value.fields-include' = [all, except-key]

If `all` is specified, all physical columns of the table schema are included in the value format, which means that key columns appear in the data type for both the key and value format.

### value.format¶

* Type: String
* Default: “avro-registry”

Specify the format for serializing and deserializing the value part of Kafka messages.

    'value.format' = '<format>'

These are the value formats for an inferred table:

* `raw` (if no Schema Registry entry)
* `avro-registry` (for Avro Schema Registry entry)
* `json-registry` (for JSON Schema Registry entry)
* `proto-registry` (for Protobuf Schema Registry entry)
* `avro-debezium-registry` (for Avro Debezium Schema Registry entry)
* `json-debezium-registry` (for JSON Debezium Schema Registry entry)
* `proto-debezium-registry` (for Protobuf Debezium Schema Registry entry)

These are the value formats for a manually created table:

* `avro-registry` (for Avro Schema Registry entry)
* `json-registry` (for JSON Schema Registry entry)
* `proto-registry` (for Protobuf Schema Registry entry)

If no format is specified, Avro Schema Registry is used by default.

### value.format.schema-context¶

* Type: String
* Default: (none)

Specify the Confluent Schema Registry Schema Context for the value format.

    'value.<format>.schema-context' = '<schema-context>'

A schema context represents an independent scope in Schema Registry and can be used to create separate “sub-registries” within one Schema Registry. Each schema context is an independent grouping of schema IDs and subject names, enabling the same schema ID in different contexts to represent completely different schemas.

## Inferred tables¶

Inferred tables are tables that have not been created by using a CREATE TABLE statement, but instead are automatically detected from information about existing Kafka topics and Schema Registry entries.

You can use the ALTER TABLE statement to [evolve schemas](alter-table.html#flink-sql-alter-table-examples) for inferred tables.

The following examples show output from the SHOW CREATE TABLE statement called on the resulting table.

### No key or value in Schema Registry¶

For an inferred table with no registered key or value schemas, SHOW CREATE TABLE returns the following output:

    CREATE TABLE `t_raw` (
      `key` VARBINARY(2147483647),
      `val` VARBINARY(2147483647)
    ) DISTRIBUTED BY HASH(`key`) INTO 2 BUCKETS
    WITH (
      'changelog.mode' = 'append',
      'connector' = 'confluent',
      'key.format' = 'raw',
      'value.format' = 'raw'
      ...
    )

Properties

* Key and value formats are raw (binary format) with BYTES.

* Following Kafka message semantics, both key and value support NULL as well, so the following code is valid:

        INSERT INTO t_raw (key, val) SELECT CAST(NULL AS BYTES), CAST(NULL AS BYTES);

### No key and but record value in Schema Registry¶

For the following value schema in Schema Registry:

    {
      "type": "record",
      "name": "TestRecord",
      "fields": [
        {
          "name": "i",
          "type": "int"
        },
        {
          "name": "s",
          "type": "string"
        }
      ]
    }

SHOW CREATE TABLE returns the following output:

    CREATE TABLE `t_raw_key` (
      `key` VARBINARY(2147483647),
      `i` INT NOT NULL,
      `s` VARCHAR(2147483647) NOT NULL
    ) DISTRIBUTED BY HASH(`key`) INTO 6 BUCKETS
    WITH (
      'changelog.mode' = 'append',
      'connector' = 'confluent',
      'key.format' = 'raw',
      'value.format' = 'avro-registry'
      ...
    )

Properties

* The key format is raw (binary format) with BYTES.

* Following Kafka message semantics, the key supports NULL as well, so the following code is valid:

        INSERT INTO t_raw_key SELECT CAST(NULL AS BYTES), 12, 'Bob';

### Atomic key and record value in Schema Registry¶

For the following key schema in Schema Registry:

    "int"

And for the following value schema in Schema Registry:

    {
      "type": "record",
      "name": "TestRecord",
      "fields": [
        {
          "name": "i",
          "type": "int"
        },
        {
          "name": "s",
          "type": "string"
        }
      ]
    }

SHOW CREATE TABLE returns the following output:

    CREATE TABLE `t_atomic_key` (
      `key` INT NOT NULL,
      `i` INT NOT NULL,
      `s` VARCHAR(2147483647) NOT NULL
    ) DISTRIBUTED BY HASH(`key`) INTO 2 BUCKETS
    WITH (
      'changelog.mode' = 'append',
      'connector' = 'confluent',
      'key.format' = 'avro-registry',
      'value.format' = 'avro-registry'
      ...
    )

Properties

* Schema Registry defines the column data type as INT NOT NULL.
* The column name, `key`, is used as the default, because Schema Registry doesn’t provide a column name.

### Overlapping names in key/value, no key in Schema Registry¶

For the following value schema in Schema Registry:

    {
      "type": "record",
      "name": "TestRecord",
      "fields": [
        {
          "name": "i",
          "type": "int"
        },
        {
          "name": "key",
          "type": "string"
        }
      ]
    }

SHOW CREATE TABLE returns the following output:

    CREATE TABLE `t_raw_disjoint` (
      `key_key` VARBINARY(2147483647),
      `i` INT NOT NULL,
      `key` VARCHAR(2147483647) NOT NULL
    ) DISTRIBUTED BY HASH(`key_key`) INTO 1 BUCKETS
    WITH (
      'changelog.mode' = 'append',
      'connector' = 'confluent',
      'key.fields-prefix' = 'key_',
      'key.format' = 'raw',
      'value.format' = 'avro-registry'
      ...
    )

Properties

* The Schema Registry value schema defines columns `i INT NOT NULL` and `key STRING`.
* The column name `key BYTES` is used as the default if no key is in Schema Registry.
* Because `key` would collide with value schema column, the `key_` prefix is added.

### Record key and record value in Schema Registry¶

For the following key schema in Schema Registry:

    {
      "type": "record",
      "name": "TestRecord",
      "fields": [
        {
          "name": "uid",
          "type": "int"
        }
      ]
    }

And for the following value schema in Schema Registry:

    {
      "type": "record",
      "name": "TestRecord",
      "fields": [
        {
          "name": "name",
          "type": "string"
        },
        {
          "name": "zip_code",
          "type": "string"
        }
      ]
    }

SHOW CREATE TABLE returns the following output:

    CREATE TABLE `t_sr_disjoint` (
      `uid` INT NOT NULL,
      `name` VARCHAR(2147483647) NOT NULL,
      `zip_code` VARCHAR(2147483647) NOT NULL
    ) DISTRIBUTED BY HASH(`uid`) INTO 1 BUCKETS
    WITH (
      'changelog.mode' = 'append',
      'connector' = 'confluent',
      'value.format' = 'avro-registry'
      ...
    )

Properties

* Schema Registry defines columns for both key and value.
* The column names of key and value are disjoint sets and don’t overlap.

### Record key and record value with overlap in Schema Registry¶

For the following key schema in Schema Registry:

    {
      "type": "record",
      "name": "TestRecord",
      "fields": [
        {
          "name": "uid",
          "type": "int"
        }
      ]
    }

And for the following value schema in Schema Registry:

    {
        "type": "record",
        "name": "TestRecord",
        "fields": [
          {
            "name": "uid",
            "type": "int"
          },{
            "name": "name",
            "type": "string"
          },
          {
            "name": "zip_code",
            "type": "string"
          }
        ]
      }

SHOW CREATE TABLE returns the following output:

    CREATE TABLE `t_sr_joint` (
      `uid` INT NOT NULL,
      `name` VARCHAR(2147483647) NOT NULL,
      `zip_code` VARCHAR(2147483647) NOT NULL
    ) DISTRIBUTED BY HASH(`uid`) INTO 1 BUCKETS
    WITH (
      'changelog.mode' = 'append',
      'connector' = 'confluent',
      'value.fields-include' = 'all',
      'value.format' = 'avro-registry'
      ...
    )

Properties

* Schema Registry defines columns for both key and value.
* The column names of key and value overlap on `uid`.
* `'value.fields-include' = 'all'` is set to exclude the key, because it is fully contained in the value.
* Detecting that key is fully contained in the value requires that _both field name and data type match completely, including nullability_ , and _all fields of the key_ are included in the value.

### Union types in Schema Registry¶

For the following value schema in Schema Registry:

    ["int", "string"]

SHOW CREATE TABLE returns the following output:

    CREATE TABLE `t_union` (
      `key` VARBINARY(2147483647),
      `int` INT,
      `string` VARCHAR(2147483647)
    )
    ...

For the following value schema in Schema Registry:

    [
      "string",
      {
        "type": "record",
        "name": "User",
        "fields": [
          {
            "name": "uid",
            "type": "int"
          },{
            "name": "name",
            "type": "string"
          }
        ]
      },
      {
        "type": "record",
        "name": "Address",
        "fields": [
          {
            "name": "zip_code",
            "type": "string"
          }
        ]
      }
    ]

SHOW CREATE TABLE returns the following output:

    CREATE TABLE `t_union` (
      `key` VARBINARY(2147483647),
      `string` VARCHAR(2147483647),
      `User` ROW<`uid` INT NOT NULL, `name` VARCHAR(2147483647) NOT NULL>,
      `Address` ROW<`zip_code` VARCHAR(2147483647) NOT NULL>
    )
    ...

Properties

* NULL and NOT NULL are inferred depending on whether a union contains NULL.
* Elements of a union are always NULL, because they need to be set to NULL when a different element is set.
* If a record defines a `namespace`, the field is prefixed with it, for example, `org.myorg.avro.User`.

### Multi-message protobuf schema in Schema Registry¶

For the following value schema in Schema Registry:

    syntax = "proto3";

    message Purchase {
       string item = 1;
       double amount = 2;
       string customer_id = 3;
    }

    message Pageview {
       string url = 1;
       bool is_special = 2;
       string customer_id = 3;
    }

SHOW CREATE TABLE returns the following output:

    CREATE TABLE `t` (
      `key` VARBINARY(2147483647),
      `Purchase` ROW<
          `item` VARCHAR(2147483647) NOT NULL,
          `amount` DOUBLE NOT NULL,
          `customer_id` VARCHAR(2147483647) NOT NULL
       >,
      `Pageview` ROW<
          `url` VARCHAR(2147483647) NOT NULL,
          `is_special` BOOLEAN NOT NULL,
          `customer_id` VARCHAR(2147483647) NOT NULL
       >
    )
    ...

For the following value schema in Schema Registry:

    syntax = "proto3";

    message Purchase {
       string item = 1;
       double amount = 2;
       string customer_id = 3;
       Pageview pageview = 4;
    }

    message Pageview {
       string url = 1;
       bool is_special = 2;
       string customer_id = 3;
    }

SHOW CREATE TABLE returns the following output:

    CREATE TABLE `t` (
      `key` VARBINARY(2147483647),
      `Purchase` ROW<
          `item` VARCHAR(2147483647) NOT NULL,
          `amount` DOUBLE NOT NULL,
          `customer_id` VARCHAR(2147483647) NOT NULL,
          `pageview` ROW<
             `url` VARCHAR(2147483647) NOT NULL,
             `is_special` BOOLEAN NOT NULL,
             `customer_id` VARCHAR(2147483647) NOT NULL
          >
       >,
      `Pageview` ROW<
          `url` VARCHAR(2147483647) NOT NULL,
          `is_special` BOOLEAN NOT NULL,
          `customer_id` VARCHAR(2147483647) NOT NULL
       >
    )
    ...

For the following value schema in Schema Registry:

    syntax = "proto3";

    message Purchase {
       string item = 1;
       double amount = 2;
       string customer_id = 3;
       Pageview pageview = 4;
       message Pageview {
          string url = 1;
          bool is_special = 2;
          string customer_id = 3;
       }
    }

SHOW CREATE TABLE returns the following output:

    CREATE TABLE `t` (
      `key` VARBINARY(2147483647),
      `item` VARCHAR(2147483647) NOT NULL,
      `amount` DOUBLE NOT NULL,
      `customer_id` VARCHAR(2147483647) NOT NULL,
      `pageview` ROW<
          `url` VARCHAR(2147483647) NOT NULL,
          `is_special` BOOLEAN NOT NULL,
          `customer_id` VARCHAR(2147483647) NOT NULL
       >
    )
    ...

### Debezium CDC format in Schema Registry¶

For a Debezium CDC format with the following value schema in Schema Registry:

    {
      "type": "record",
      "name": "Customer",
      "namespace": "io.debezium.data",
      "fields": [
        {
          "name": "before",
          "type": ["null", {
            "type": "record",
            "name": "Value",
            "fields": [
              {"name": "id", "type": "int"},
              {"name": "name", "type": "string"},
              {"name": "email", "type": "string"}
            ]
          }],
          "default": null
        },
        {
          "name": "after",
          "type": ["null", "Value"],
          "default": null
        },
        {
          "name": "source",
          "type": {
            "type": "record",
            "name": "Source",
            "fields": [
              {"name": "version", "type": "string"},
              {"name": "connector", "type": "string"},
              {"name": "name", "type": "string"},
              {"name": "ts_ms", "type": "long"},
              {"name": "db", "type": "string"},
              {"name": "schema", "type": "string"},
              {"name": "table", "type": "string"}
            ]
          }
        },
        {"name": "op", "type": "string"},
        {"name": "ts_ms", "type": ["null", "long"], "default": null},
        {"name": "transaction", "type": ["null", {
          "type": "record",
          "name": "Transaction",
          "fields": [
            {"name": "id", "type": "string"},
            {"name": "total_order", "type": "long"},
            {"name": "data_collection_order", "type": "long"}
          ]
        }], "default": null}
      ]
    }

SHOW CREATE TABLE returns the following output:

    CREATE TABLE `customer_changes` (
      `key` VARBINARY(2147483647),
       `id` INT NOT NULL,
       `name` VARCHAR(2147483647) NOT NULL,
       `email` VARCHAR(2147483647) NOT NULL
    )
    DISTRIBUTED BY HASH(`key`) INTO 6 BUCKETS
    WITH (
      'changelog.mode' = 'retract',
      'connector' = 'confluent',
      'key.format' = 'raw',
      'value.format' = 'avro-debezium-registry'
      ...
    )

Properties

* Flink detects the Debezium format automatically, based on the schema structure with `after`, `before`, and `op` fields.

* The table schema is inferred from the `after` schema, exposing only the actual data fields.

* **Automatic Debezium Envelope Detection** : For schemas created after May 19, 2025 at 09:00 UTC, Flink automatically detects Debezium envelopes and sets appropriate defaults:

  * `value.format` defaults to `*-debezium-registry` (instead of `*-registry`)
  * `changelog.mode` defaults to `retract` (instead of `append`)
  * Exception: If Kafka `cleanup.policy` is `compact`, `changelog.mode` is set to `upsert`
* The default `changelog.mode` is `retract`, which properly handles all CDC operations, including inserts, updates, and deletes.

* You can manually override the changelog mode if necessary:

        -- Change to upsert mode for primary key-based operations
        ALTER TABLE customer_changes SET ('changelog.mode' = 'upsert');

        -- Change to append mode (processes only inserts and updates)
        ALTER TABLE customer_changes SET ('changelog.mode' = 'append');

## Examples¶

The following examples show how to create Flink tables for frequently encountered scenarios.

### Minimal table¶

    CREATE TABLE t_minimal (s STRING);

Properties

* Append changelog mode.
* No Schema Registry key.
* Round robin distribution.
* 6 Kafka partitions.
* The `$rowtime` column and system watermark are added implicitly.

### Table with a primary key¶

Syntax

    CREATE TABLE t_pk (k INT PRIMARY KEY NOT ENFORCED, s STRING);

Properties

* Upsert changelog mode.
* The primary key defines an implicit DISTRIBUTED BY(k).
* `k` is the Schema Registry key.
* Hash distribution on `k`.
* The table has 6 Kafka partitions.
* `k` is declared as being unique, meaning no duplicate rows.
* `k` must not contain NULLs, so an implicit NOT NULL is added.
* The `$rowtime` column and system watermark are added implicitly.

### Table with a primary key in append mode¶

Syntax

    CREATE TABLE t_pk_append (k INT PRIMARY KEY NOT ENFORCED, s STRING)
      DISTRIBUTED INTO 4 BUCKETS
      WITH ('changelog.mode' = 'append');

Properties

* Append changelog mode.
* `k` is the Schema Registry key.
* Hash distribution on `k`.
* The table has 4 Kafka partitions.
* `k` is declared as being unique, meaning no duplicate rows.
* `k` must not contain NULLs, meaning implicit NOT NULL.
* The `$rowtime` column and system watermark are added implicitly.

### Table with hash distribution¶

Syntax

    CREATE TABLE t_dist (k INT, s STRING) DISTRIBUTED BY (k) INTO 4 BUCKETS;

Properties

* Append changelog mode.
* `k` is the Schema Registry key.
* Hash distribution on `k`.
* The table has 4 Kafka partitions.
* The `$rowtime` column and system watermark are added implicitly.

### Complex table with all concepts combined¶

Syntax

    CREATE TABLE t_complex (k1 INT, k2 INT, PRIMARY KEY (k1, k2) NOT ENFORCED, s STRING)
      COMMENT 'My complex table'
      DISTRIBUTED BY HASH(k1) INTO 4 BUCKETS
      WITH ('changelog.mode' = 'append');

Properties

* Append changelog mode.
* `k1` is the Schema Registry key.
* Hash distribution on `k1`.
* `k2` is treated as a value column and is stored in the value part of Schema Registry.
* The table has 4 Kafka partitions.
* `k1` and `k2` are declared as being unique, meaning no duplicates.
* `k` and `k2` must not contain NULLs, meaning implicit NOT NULL.
* The `$rowtime` column and system watermark are added implicitly.
* An additional comment is added.

### Table with overlapping names in key/value of Schema Registry but disjoint data¶

Syntax

    CREATE TABLE t_disjoint (from_key_k INT, k STRING)
      DISTRIBUTED BY (from_key_k)
      WITH ('key.fields-prefix' = 'from_key_');

Properties

* Append changelog mode.
* Hash distribution on `from_key_k`.
* The key prefix `from_key_` is defined and is stripped before storing the schema in Schema Registry.
  * Therefore, `k` is the Schema Registry key of type INT.
  * Also, `k` is the Schema Registry value of type STRING.
* Both key and value store disjoint data, so they can have different data types

### Create with overlapping names in key/value of Schema Registry but joint data¶

Syntax

    CREATE TABLE t_joint (k INT, v STRING)
      DISTRIBUTED BY (k)
      WITH ('value.fields-include' = 'all');

Properties

* Append changelog mode.
* Hash distribution on `k`.
* By default, the key is never included in the value in Schema Registry.
* By setting `'value.fields-include' = 'all'`, the value contains the full table schema
  * Therefore, `k` is the Schema Registry key.
  * Also, `k, v` is the Schema Registry value.
* The payload of `k` is stored twice in the Kafka message, because key and value store joint data and they have the same data type for `k`.

### Table with metadata columns for writing a Kafka message timestamp¶

Syntax

    CREATE TABLE t_metadata_write (name STRING, ts TIMESTAMP_LTZ(3) NOT NULL METADATA FROM 'timestamp')
      DISTRIBUTED INTO 1 BUCKETS;

Properties

* Adds the `ts` metadata column, which isn’t part of Schema Registry but instead is a pure Flink concept.
* In contrast with `$rowtime`, which is declared as a METADATA VIRTUAL column, `ts` is selected in a SELECT * statement and is writable.

The following examples show how to fill Kafka messages with an [instant](../datatypes.html#flink-sql-timestamp-comparison-timestamp-ltz).

    INSERT INTO t (ts, name) SELECT NOW(), 'Alice';
    INSERT INTO t (ts, name) SELECT TO_TIMESTAMP_LTZ(0, 3), 'Bob';
    SELECT $rowtime, * FROM t;

The Schema Registry subject compatibility mode must be FULL or FULL_TRANSITIVE. For more information, see [Schema Evolution and Compatibility for Schema Registry on Confluent Cloud](../../../sr/fundamentals/schema-evolution.html#schema-evolution-and-compatibility).

### Table with string key and value in Schema Registry¶

Syntax

    CREATE TABLE t_raw_string_key (key STRING, i INT)
      DISTRIBUTED BY (key)
      WITH ('key.format' = 'raw');

Properties

* Schema Registry is filled with a value subject containing `i`.
* The key columns are determined by the DISTRIBUTED BY clause.
* By default, Avro in Schema Registry would be used for the key, but the WITH clause overrides this to the `raw` format.

### Tables with cross-region schema sharing¶

  1. Create two Kafka clusters in different regions, for example, `eu-west-1` and `us-west-2`.

  2. Create two Flink compute pools in different regions, for example, `eu-west-1` and `us-west-2`.

  3. In the first region, run the following statement.

         CREATE TABLE t_shared_schema (key STRING, s STRING) DISTRIBUTED BY (key);

  4. In the second region, run the same statement.

         CREATE TABLE t_shared_schema (key STRING, s STRING) DISTRIBUTED BY (key);

Properties

* Schema Registry is shared across regions.
* The SQL metastore, Flink compute pools, and Kafka clusters are regional.
* Both tables in either region share the Schema Registry subjects `t_shared_schema-key` and `t_shared_schema-value`.

### Create with different changelog modes¶

There are three ways of storing events in a table’s log, this is, in the underlying Kafka topic.

append

* Every insertion event is an **immutable fact**.
* Every event is **insert-only**.
* Events can be distributed in a round-robin fashion across workers/shards because they are **unrelated**.

upsert

* Events are **related** using a primary key.
* Every event is either an **upsert or delete** event for a primary key.
* Events for the same primary key should land at the same worker/shard.

retract

* Every upsert event is a **fact that can be “undone”**.

* This means that every event is either an insertion or its retraction.

* So, **two events are related by all columns**. In other words, the entire row is the key.

For example, `+I['Bob', 42]` is related to `-D['Bob', 42]` and `+U['Alice', 13]` is related to `-U['Alice', 13]`.

* The **retract** mode is intermediate between the **append** and **upsert** modes.
* The **append** and **upsert** modes are natural to existing Kafka consumers and producers.
* Kafka compaction is a kind of **upsert**.

Start with a table created by the following statement.

    CREATE TABLE t_changelog_modes (i BIGINT);

Properties

* Confluent Cloud for Apache Flink always derives an appropriate changelog mode for the preceding declaration.
* If there is no primary key, **append** is the safest option, because it prevents users from pushing updates into a topic accidentally, and it has the best support of downstream consumers.

    -- works because the query is non-updating
    INSERT INTO t_changelog_modes SELECT 1;

    -- does not work because the query is updating, causing an error
    INSERT INTO t_changelog_modes SELECT COUNT(*) FROM (VALUES (1), (2), (3));

If you need updates, and if downstream consumers support it, for example, when the consumer is another Flink job, you can set the changelog mode to **retract**.

    ALTER TABLE t_changelog_modes SET ('changelog.mode' = 'retract');

Properties

* The table starts accepting retractions during INSERT INTO.
* Already existing records in the Kafka topic are treated as insertions.
* Newly added records receive a changeflag (+I, +U, -U, -D) in the Kafka message header.

Going back to **append** mode is possible, but retractions (-U, -D) appear as insertions, and the Kafka header metadata column reveals the changeflag.

    ALTER TABLE t_changelog_modes SET ('changelog.mode' = 'append');
    ALTER TABLE t_changelog_modes ADD headers MAP<BYTES, BYTES> METADATA VIRTUAL;

    -- Shows what is serialized internally
    SELECT i, headers FROM t_changelog_modes;

### Table with infinite retention time¶

    CREATE TABLE t_infinite_retention (i INT) WITH ('kafka.retention.time' = '0');

Properties

* By default, the retention time is 7 days, as in all other APIs.
* Flink doesn’t support `-1` for durations, so `0` means infinite retention time.
* Durations in Flink support `2 day` or `2 d` syntax, so it doesn’t need to be in milliseconds.
* If no unit is specified, the unit is milliseconds.
* The following units are supported:

    "d", "day", "h", "hour", "m", "min", "minute", "ms", "milli", "millisecond",
    "µs", "micro", "microsecond", "ns", "nano", "nanosecond"
