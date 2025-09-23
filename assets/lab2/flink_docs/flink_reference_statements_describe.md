---
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/describe.html
title: SQL DESCRIBE Statement in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'statements', 'describe.html']
scraped_date: 2025-09-05T13:48:49.088304
---

# DESCRIBE Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables viewing the schema of an Apache Kafka® topic. Also, you can view details of an AI model, function, or connection.

## Syntax¶

    -- View table details.
    { DESCRIBE | DESC } [EXTENDED] [catalog_name.][db_name.]table_name

    -- View model details.
    { DESCRIBE | DESC } MODEL [[catalogname].[database_name]].model_name

    -- View function details.
    { DESCRIBE | DESC } FUNCTION [EXTENDED] [catalog_name.][db_name.]function_name

    -- View connection details.
    { DESCRIBE | DESC } CONNECTION [catalog_name.][db_name.]connection_name

## Description¶

The DESCRIBE statement shows the following properties of a table:

  * Columns and their data type, including nullability constraints
  * Primary keys
  * Bucket keys, i.e., keys of distribution
  * Implicit NOT NULL for primary key columns
  * Custom [watermark](../../../_glossary.html#term-watermark)

The DESCRIBE EXTENDED statement shows all of the properties from the DESCRIBE statement and also shows system columns, like `$rowtime`, including the system watermark.

The DESCRIBE MODEL statement shows the following properties of an AI model:

  * Input format
  * Output format
  * Model version
  * isDefault version (yes or no)

The DESCRIBE FUNCTION statement shows the following properties of a function:

  * System function (yes or no)
  * Temporary (yes or no)
  * Class name
  * Function language
  * Plugin ID
  * Version ID
  * Argument types
  * Return type

The DESCRIBE FUNCTION EXTENDED statement shows all of the properties from the DESCRIBE FUNCTION statement and also shows the following properties:

  * Kind i.e. SCALAR, TABLE, or AGGREGATE
  * Requirements e.g an aggregate function that can only be applied in an OVER window
  * Deterministic (yes or no)
  * Constant folding (yes or no)
  * Signature

The DESCRIBE CONNECTION statement shows the following properties of a connection:

  * Name
  * Type
  * Endpoint
  * Comment

## Examples¶

### Tables¶

In the Flink SQL shell or in a Cloud Console workspace, run the following commands to see an example of the DESCRIBE statement.

  1. Create a table.

         CREATE TABLE orders (
           `user` BIGINT NOT NULL,
           product STRING,
           amount INT,
           ts TIMESTAMP(3),
           PRIMARY KEY(`user`) NOT ENFORCED
         );

Your output should resemble:

         [INFO] Execute statement succeed.

  2. View the table’s schema.

         DESCRIBE orders;

Your output should resemble:

         +-------------+--------------+----------+-------------------------+
         | Column Name |  Data Type   | Nullable |         Extras          |
         +-------------+--------------+----------+-------------------------+
         | user        | BIGINT       | NOT NULL | PRIMARY KEY, BUCKET KEY |
         | product     | STRING       | NULL     |                         |
         | amount      | INT          | NULL     |                         |
         | ts          | TIMESTAMP(3) | NULL     |                         |
         +-------------+--------------+----------+-------------------------+

  3. View the table’s schema and system columns.

         DESCRIBE EXTENDED orders;

Your output should resemble:

         +-------------+----------------------------+----------+-----------------------------------------------------+---------+
         | Column Name |         Data Type          | Nullable |                       Extras                        | Comment |
         +-------------+----------------------------+----------+-----------------------------------------------------+---------+
         | user        | BIGINT                     | NOT NULL | PRIMARY KEY, BUCKET KEY                             |         |
         | product     | STRING                     | NULL     |                                                     |         |
         | amount      | INT                        | NULL     |                                                     |         |
         | ts          | TIMESTAMP(3)               | NULL     |                                                     |         |
         | $rowtime    | TIMESTAMP_LTZ(3) *ROWTIME* | NOT NULL | METADATA VIRTUAL, WATERMARK AS `SOURCE_WATERMARK`() | SYSTEM  |
         +-------------+----------------------------+----------+-----------------------------------------------------+---------+

### Models¶

If you have an AI model registered in the Flink environment, you can view its details and creation options by using the DESCRIBE MODEL statement.

The following code example shows how to view the default model version:

    DESCRIBE MODEL `my-model`;

Your output should resemble:

    +-----------------------+---------------------------+---------------------------+---------+
    |        Inputs         |          Outputs          |          Options          | Comment |
    +-----------------------+---------------------------+---------------------------+---------+
    | (                     | (                         | {                         |         |
    |   `credit_limit` INT, |   `predicted_default` INT |   AZUREML.API_KEY=******, |         |
    |   `age` INT           | )                         |   AZUREML.ENDPOINT=h...   |         |
    | )                     |                           |                           |         |
    +-----------------------+---------------------------+---------------------------+---------+

The following code example shows how to view a specific model version:

    DESCRIBE MODEL `my-model$2`;

Your output should resemble:

    +-----------+------------------+-----------------------+---------------------------+--------------------+---------+
    | VersionId | IsDefaultVersion |        Inputs         |          Outputs          |      Options       | Comment |
    +-----------+------------------+-----------------------+---------------------------+--------------------+---------+
    | 2         | true             | (                     | (                         | {                  |         |
    |           |                  |   `credit_limit` INT, |   `predicted_default` INT |   AZUREML.API_K... |         |
    |           |                  |   `age` INT           | )                         |                    |         |
    |           |                  | )                     |                           |                    |         |
    +-----------+------------------+-----------------------+---------------------------+--------------------+---------+

The following code example shows how to view all model versions:

    DESCRIBE MODEL `my-model$all`;

Your output should resemble:

    +-----------+------------------+-----------------------+---------------------------+--------------------+---------+
    | VersionId | IsDefaultVersion |        Inputs         |          Outputs          |      Options       | Comment |
    +-----------+------------------+-----------------------+---------------------------+--------------------+---------+
    | 1         | true             | (                     | (                         | {                  |         |
    |           |                  |   `credit_limit` INT, |   `predicted_default` INT |   AZUREML.API_K... |         |
    |           |                  |   `age` INT           | )                         |                    |         |
    |           |                  | )                     |                           |                    |         |
    | 2         | false            | (                     | (                         | {                  |         |
    |           |                  |   `credit_limit` INT, |   `predicted_default` INT |   AZUREML.API_K... |         |
    |           |                  |   `age` INT           | )                         |                    |         |
    |           |                  | )                     |                           |                    |         |
    +-----------+------------------+-----------------------+---------------------------+--------------------+---------+

For more information, see [Model versioning](create-model.html#flink-sql-create-model-input-model-versioning).

### Functions¶

You can view the details of any system functions or registered user-defined functions in the Flink environment, by using the DESCRIBE FUNCTION statement.

The following code example shows how to describe a system function:

    DESCRIBE FUNCTION `SUM`;

Your output should resemble:

    +-----------------+------------+
    |       info name | info value |
    +-----------------+------------+
    | system function |       true |
    |       temporary |      false |
    +-----------------+------------+

View more details about the system function definition.

    DESCRIBE FUNCTION EXTENDED `SUM`;

Your output should resemble:

    +------------------+----------------+
    |        info name |     info value |
    +------------------+----------------+
    |  system function |           true |
    |        temporary |          false |
    |             kind |      AGGREGATE |
    |     requirements |             [] |
    |    deterministic |           true |
    | constant folding |           true |
    |        signature | SUM(<NUMERIC>) |
    +------------------+----------------+

Here is what describing a user-defined function looks like

    DESCRIBE FUNCTION `MyUpperCaseUdf`;

Your output should resemble:

    +-------------------+----------------------+
    |         info name |           info value |
    +-------------------+----------------------+
    |   system function |                false |
    |         temporary |                 true |
    |        class name | org.example.UpperUDF |
    | function language |                 JAVA |
    |         plugin id |              ccp-xyz |
    |        version id |              ver-123 |
    |    argument types |                [str] |
    |       return type |                  str |
    +-------------------+----------------------+

View more details about the user-defined function definition.

    DESCRIBE FUNCTION EXTENDED `MyUpperCaseUdf`;

Your output should resemble:

    +-------------------+-------------------------------+
    |         info name |                    info value |
    +-------------------+-------------------------------+
    |   system function |                         false |
    |         temporary |                          true |
    |        class name |          org.example.UpperUDF |
    | function language |                          JAVA |
    |              kind |                        SCALAR |
    |      requirements |                            [] |
    |     deterministic |                          true |
    |  constant folding |                          true |
    |         signature | cat.db.MyUpperCaseUdf(STRING) |
    |         plugin id |                       ccp-xyz |
    |        version id |                       ver-123 |
    |    argument types |                         [str] |
    |       return type |                           str |
    +-------------------+-------------------------------+

### Connections¶

You can view the details of any connection in the Flink environment by using the DESCRIBE CONNECTION statement.

The following code example shows how to describe an example connection named `azure-openai-connection`.

    DESCRIBE CONNECTION `azure-openai-connection`;

Your output should resemble:

    +-------------------------+-------------+-----------------------------------------------------------------------+---------+
    |          Name           |    Type     |                              Endpoint                                 | Comment |
    +-------------------------+-------------+-----------------------------------------------------------------------+---------+
    | azure-openai-connection | AZUREOPENAI | https://<your-project>.openai.azure.com/openai/deployments/matrix-... |         |
    +-------------------------+-------------+-----------------------------------------------------------------------+---------+
