---
document_id: flink_reference_statements_show_chunk_5
source_file: flink_reference_statements_show.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/show.html
title: SQL SHOW Statements in Confluent Cloud for Apache Flink
chunk_index: 5
total_chunks: 5
---

both for reading and writing.

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
