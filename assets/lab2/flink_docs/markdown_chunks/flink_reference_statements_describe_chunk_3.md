---
document_id: flink_reference_statements_describe_chunk_3
source_file: flink_reference_statements_describe.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/describe.html
title: SQL DESCRIBE Statement in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 3
---

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
