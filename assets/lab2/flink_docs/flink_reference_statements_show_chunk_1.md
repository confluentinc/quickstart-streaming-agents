---
document_id: flink_reference_statements_show_chunk_1
source_file: flink_reference_statements_show.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/show.html
title: SQL SHOW Statements in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 5
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
