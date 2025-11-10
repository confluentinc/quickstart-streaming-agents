---
document_id: flink_reference_statements_describe_chunk_2
source_file: flink_reference_statements_describe.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/describe.html
title: SQL DESCRIBE Statement in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 3
---

Type *Endpoint* Comment

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
