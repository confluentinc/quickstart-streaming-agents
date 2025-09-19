---
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/show.html
title: SQL SHOW Statements in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'statements', 'show.html']
scraped_date: 2025-09-05T13:48:33.853474
---

# SHOW Statements in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables listing catalogs, which map to Confluent Cloud environments, databases, which map to Apache Kafka® clusters, and other available Flink resources, like AI models, UDFs, connections, and tables.

Confluent Cloud for Apache Flink supports these SHOW statements.

SHOW CATALOGS | SHOW CONNECTIONS  
---|---  
SHOW CREATE MODEL | SHOW CURRENT CATALOG  
SHOW CREATE TABLE | SHOW CURRENT DATABASE  
SHOW DATABASES | SHOW JOBS  
SHOW FUNCTIONS | SHOW MODELS  
SHOW TABLES |   
  
## SHOW CATALOGS¶

Syntax

    SHOW CATALOGS;

Description
    Show all catalogs. Confluent Cloud for Apache Flink maps Flink catalogs to environments.
Example

    SHOW CATALOGS;

Your output should resemble:

    +-------------------------+------------+
    |      catalog name       | catalog id |
    +-------------------------+------------+
    | my_environment          | env-12abcz |
    | example-streams-env     | env-23xjoo |
    | quickstart-env          | env-9wg8ny |
    | default                 | env-t12345 |
    +-------------------------+------------+

Run the [USE CATALOG statement](use-catalog.html#flink-sql-use-catalog-statement) to set the current Flink catalog (Confluent Cloud environment).

    USE CATALOG my_environment;

Your output should resemble:

    +---------------------+----------------+
    |         Key         |      Value     |
    +---------------------+----------------+
    | sql.current-catalog | my_environment |
    +---------------------+----------------+

## SHOW CONNECTIONS¶

Syntax

    SHOW CONNECTIONS [LIKE <sql-like-pattern>];

Description
    Show all connections.
Example

    SHOW CONNECTIONS;
    
    -- with name filter
    SHOW CONNECTIONS LIKE 'sql%';

Your output should resemble:

    +-------------------------+
    |          Name           |
    +-------------------------+
    | azure-openai-connection |
    | deepwiki-mcp-connection |
    | demo-day-mcp-connection |
    | mcp-connection          |
    +-------------------------+

## SHOW CURRENT CATALOG¶

Syntax

    SHOW CURRENT CATALOG;

Description
    Show the current catalog.
Example

    SHOW CURRENT CATALOG;

Your output should resemble:

    +----------------------+
    | current catalog name |
    +----------------------+
    | my_environment       |
    +----------------------+

## SHOW DATABASES¶

Syntax

    SHOW DATABASES;

Description
    Show all databases in the current catalog. Confluent Cloud for Apache Flink maps Flink databases to Kafka clusters.
Example

    SHOW DATABASES;

Your output should resemble:

    +---------------+-------------+
    | database name | database id |
    +---------------+-------------+
    | cluster_0     | lkc-r289m7  |
    +---------------+-------------+

Run the [USE statement](use-database.html#flink-sql-use-database-statement) to set the current database (Kafka cluster).

    USE cluster_0;

Your output should resemble:

    +----------------------+-----------+
    |         Key          |   Value   |
    +----------------------+-----------+
    | sql.current-database | cluster_0 |
    +----------------------+-----------+

## SHOW CURRENT DATABASE¶

Syntax

    SHOW CURRENT DATABASE;

Description
    Show the current database. Confluent Cloud for Apache Flink maps Flink databases to Kafka clusters.
Example

    SHOW CURRENT DATABASE;

Your output should resemble:

    +-----------------------+
    | current database name |
    +-----------------------+
    | cluster_0             |
    +-----------------------+

## SHOW TABLES¶

Syntax

    SHOW TABLES [ [catalog_name.]database_name ] [ [NOT] LIKE <sql_like_pattern> ]

Description

Show all tables for the current database. You can filter the output of SHOW TABLES by using the LIKE clause with an optional matching pattern.

The optional LIKE clause shows all tables with names that match `<sql_like_pattern>`.

The syntax of the SQL pattern in a `LIKE` clause is the same as in the `MySQL` dialect.

  * `%` matches any number of characters, including zero characters. Use the backslash character to escape the `%` character: `\%` matches one `%` character.
  * `_` matches exactly one character. Use the backslash character to escape the `_` character: `\_` matches one `_` character.

Example

Create two tables in the current catalog: `flights` and `orders`.

    -- Create a flights table.
    CREATE TABLE flights (
      flight_id STRING,
      origin STRING,
      destination STRING
    );

    -- Create an orders table.
    CREATE TABLE orders (
      user_id BIGINT NOT NULL,
      product_id STRING,
      amount INT
    );

Show all tables in the current database that are similar to the specified SQL pattern.

    SHOW TABLES LIKE 'f%';

Your output should resemble:

    +------------+
    | table name |
    +------------+
    | flights    |
    +------------+

Show all tables in the given database that are not similar to the specified SQL pattern.

    SHOW TABLES NOT LIKE 'f%';

Your output should resemble:

    +------------+
    | table name |
    +------------+
    | orders     |
    +------------+

Show all tables in the current database.

    SHOW TABLES;

    +------------+
    | table name |
    +------------+
    | flights    |
    | orders     |
    +------------+

## SHOW CREATE TABLE¶

Syntax

    SHOW CREATE TABLE [catalog_name.][db_name.]table_name;

Description
    Show details about the specified table.
Example

    SHOW CREATE TABLE flights;

Your output should resemble:

    +-----------------------------------------------------------+
    |                     SHOW CREATE TABLE                     |
    +-----------------------------------------------------------+
    | CREATE TABLE `my_environment`.`cluster_0`.`flights` (     |
    |   `flight_id` VARCHAR(2147483647),                        |
    |   `origin` VARCHAR(2147483647),                           |
    |   `destination` VARCHAR(2147483647)                       |
    | ) WITH (                                                  |
    |   'changelog.mode' = 'append',                            |
    |   'connector' = 'confluent',                              |
    |   'kafka.cleanup-policy' = 'delete',                      |
    |   'kafka.max-message-size' = '2097164 bytes',             |
    |   'kafka.partitions' = '6',                               |
    |   'kafka.retention.size' = '0 bytes',                     |
    |   'kafka.retention.time' = '604800000 ms',                |
    |   'scan.bounded.mode' = 'unbounded',                      |
    |   'scan.startup.mode' = 'earliest-offset',                |
    |   'value.format' = 'avro-registry'                        |
    | )                                                         |
    |                                                           |
    +-----------------------------------------------------------+

### Inferred Tables¶

Inferred tables are tables that have not been created with CREATE TABLE but are detected automatically by using information about existing topics and Schema Registry entries.

The following examples show SHOW CREATE TABLE called on the resulting table.

#### No key and no value in Schema Registry¶

SHOW CREATE TABLE returns:

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
    );

Properties

  * Key and value formats are raw (binary format) with BYTES

  * Following Kafka message semantics, both key and value support NULL as well, so the following statement is supported:
        
        INSERT INTO t_raw (key, val) SELECT CAST(NULL AS BYTES), CAST(NULL AS BYTES);

#### No key and but record value in Schema Registry¶

Given the following value in Schema Registry:

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

SHOW CREATE TABLE returns:

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

  * Key format is raw (binary format) with BYTES

  * Following Kafka message semantics, key supports NULL as well. So this is possible: so the following statement is supported:
        
        INSERT INTO t_raw_key SELECT CAST(NULL AS BYTES), 12, 'Bob';

#### Atomic key and record value in Schema Registry¶

Given the following key and value in Schema Registry:

    "int"

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

SHOW CREATE TABLE returns:

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

  * Schema Registry defines column data type INT NOT NULL.
  * The column name `key` is used as a default, because Schema Registry doesn’t provide a column name.

#### Overlapping names in key/value, no key in Schema Registry¶

Given the following value in Schema Registry:

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

SHOW CREATE TABLE returns:

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

  * Schema Registry value defines columns INT NOT NULL and `key STRING`
  * The column name `key BYTES` is used as a default if no key is in Schema Registry
  * Because `key` would collide with value column, `key_` prefix is added

#### Record key and record value in Schema Registry¶

Given the following key and value in Schema Registry:

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

SHOW CREATE TABLE returns:

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

#### Record key and record value with overlap in Schema Registry¶

Given the following key and value in Schema Registry:

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

SHOW CREATE TABLE returns:

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
  * `'value.fields-include' = 'all'` is set to exclude the key because it is fully contained in the value.

### Inferred tables schema evolution¶

#### Schema Registry columns overlap with computed/metadata columns¶

Given the following value in Schema Registry:

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

Evolve the table by adding metadata:

    ALTER TABLE t_metadata_overlap ADD `timestamp` TIMESTAMP_LTZ(3) NOT NULL METADATA;

Evolve the table by adding an optional schema column:

    {
      "type": "record",
      "name": "TestRecord",
      "fields": [
         {
            "name": "uid",
            "type": "int"
         },
         {
            "name": "timestamp",
            "type": ["null", "string"],
            "default": null
         }
      ]
    }

SHOW CREATE TABLE shows:

    CREATE TABLE t_metadata_overlap` (
      `key` VARBINARY(2147483647),
      `uid` INT NOT NULL,
      `timestamp` TIMESTAMP(3) WITH LOCAL TIME ZONE NOT NULL METADATA
    ) DISTRIBUTED BY HASH(`key`) INTO 6 BUCKETS
    WITH (
      ...
    )

Properties

  * Schema Registry says there is a timestamp physical column, but Flink says there is timestamp metadata column.

  * In this case, metadata columns and computed columns have precedence, so Flink removes the physical column from the schema.

  * Given that Flink advertises FULL_TRANSITIVE mode, queries still work, and the physical column is set to NULL in the payload:
        
        INSERT INTO t_metadata_overlap
          SELECT CAST(NULL AS BYTES), 42, TO_TIMESTAMP_LTZ(0, 3);
        
        SELECT * FROM t_metadata_overlap;

Evolve the table by renaming metadata:

    ALTER TABLE t_metadata_overlap DROP `timestamp`;
    
    ALTER TABLE t_metadata_overlap
      ADD message_timestamp TIMESTAMP_LTZ(3) METADATA FROM 'timestamp';

SHOW CREATE TABLE shows:

    CREATE TABLE `t_metadata_overlap` (
      `key` VARBINARY(2147483647),
      `uid` INT NOT NULL,
      `timestamp` VARCHAR(2147483647),
      `message_timestamp` TIMESTAMP(3) WITH LOCAL TIME ZONE METADATA FROM 'timestamp'
    ) DISTRIBUTED BY HASH(`key`) INTO 6 BUCKETS
    WITH (
      ...
    )

Properties

  * Now, both physical and metadata column show up and can be accessed both for reading and writing.

## SHOW JOBS¶

Syntax

    SHOW JOBS;

Description
    Show the status of all statements in the current catalog/environment.
Example

    SHOW JOBS;

Your output should resemble:

    +----------------------------------+-----------+------------------+--------------+------------------+------------------+
    |               Name               |   Phase   |    Statement     | Compute Pool |  Creation Time   |      Detail      |
    +----------------------------------+-----------+------------------+--------------+------------------+------------------+
    | 0fb72c57-8e3d-4614               | COMPLETED | CREATE TABLE ... | lfcp-8m03rm  | 2024-01-23 13... | Table 'flight... |
    | 8567b0eb-fabd-4cb8               | COMPLETED | CREATE TABLE ... | lfcp-8m03rm  | 2024-01-23 13... | Table 'orders... |
    | 4cd171ca-77db-48ce               | COMPLETED | SHOW TABLES L... | lfcp-8m03rm  | 2024-01-23 13... |                  |
    | 291eb50b-965c-4a53               | COMPLETED | SHOW TABLES N... | lfcp-8m03rm  | 2024-01-23 13... |                  |
    | 7a30e70a-36af-41f4               | COMPLETED | SHOW TABLES;     | lfcp-8m03rm  | 2024-01-23 13... |                  |
    +----------------------------------+-----------+------------------+--------------+------------------+------------------+

## SHOW FUNCTIONS¶

Syntax

    SHOW [USER] FUNCTIONS;

Description

Show all functions including system functions and user-defined functions in the current catalog and current database. Both system and catalog functions are returned.

The `USER` option shows only user-defined functions in the current catalog and current database.

Functions of internal modules are shown if your Organization is in the allow-list, for example, OLTP functions.

For convenience, SHOW FUNCITONS also shows functions with special syntax or keywords that don’t follow a traditional functional-style syntax, like `FUNC(arg0)`. For example, `||` (string concatenation) or `IS BETWEEN`.

Example

    SHOW FUNCTIONS;

Your output should resemble:

    +------------------------+
    |     function name      |
    +------------------------+
    | %                      |
    | *                      |
    | +                      |
    | -                      |
    | /                      |
    | <                      |
    | <=                     |
    | <>                     |
    | =                      |
    | >                      |
    | >=                     |
    | ABS                    |
    | ACOS                   |
    | AND                    |
    | ARRAY                  |
    | ARRAY_CONTAINS         |
    | ASCII                  |
    | ASIN                   |
    | ATAN                   |
    | ATAN2                  |
    | AVG                    |
    ...

## SHOW MODELS¶

Syntax

    SHOW MODELS [ ( FROM | IN ) [catalog_name.]database_name ]
    [ [NOT] LIKE <sql_like_pattern> ];

Description

Show all AI models that are registered in the current Flink environment.

To register an AI model, run the [CREATE MODEL](create-model.html#flink-sql-create-model) statement.

Example

    SHOW MODELS;

Your output should resemble:

    +----------------+
    |   Model Name   |
    +----------------+
    |   demo_model   |
    +----------------+

## SHOW CREATE MODEL¶

Syntax

    SHOW CREATE MODEL <model-name>;

Description

Show details about the specified AI inference model.

This command is useful for understanding the configuration and options that were set when the model was created with the [CREATE MODEL](create-model.html#flink-sql-create-model) statement.

Example

For an example AWS Bedrock model named “bedrock_embed”, the following statement might display the shown output.

    SHOW CREATE MODEL bedrock_embed;
    
    -- Example SHOW CREATE MODEL output:
    CREATE MODEL `model-testing`.`virtual_topic_GCP`.`bedrock_embed`
    INPUT (`text` VARCHAR(2147483647))
    OUTPUT (`response` ARRAY<FLOAT>)
    WITH (
      'BEDROCK.CONNECTION' = 'bedrock-connection-hao',
      'BEDROCK.INPUT_FORMAT' = 'AMAZON-TITAN-EMBED',
      'PROVIDER' = 'bedrock',
      'TASK' = 'text_generation'
    );

