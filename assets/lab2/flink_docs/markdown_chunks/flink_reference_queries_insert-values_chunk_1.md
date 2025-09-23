---
document_id: flink_reference_queries_insert-values_chunk_1
source_file: flink_reference_queries_insert-values.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/insert-values.html
title: SQL INSERT VALUES Statement in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# INSERT VALUES Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables inserting data directly into a Flink SQL table.

## Syntax¶

    [EXECUTE] INSERT { INTO | OVERWRITE } [catalog_name.][database_name.]table_name VALUES
      (value1 [, value2, ...])
      [, (value3 [, value4, ...])]

## Description¶

Insert data into a table.

Use the INSERT VALUES statement to insert one or more rows into a table by specifying the value for each column.

For example, the following statement inserts a single row into a table named `orders` that has four columns.

    INSERT INTO orders VALUES (1, 1001, '2023-02-24', 50.0);

You can insert multiple rows by using a comma-separated list of values.

    INSERT INTO orders VALUES
      (1, 1001, '2023-02-24', 50.0),
      (2, 1002, '2023-02-25', 60.0),
      (3, 1003, '2023-02-26', 70.0);

## Example¶

In the Flink SQL shell or in a Cloud Console workspace, run the following commands to see an example of the INSERT VALUES statement.

  1. Create a users table.

         -- Create a users table.
         CREATE TABLE users (
           user_id STRING,
           registertime BIGINT,
           gender STRING,
           regionid STRING
         );

  2. Insert rows into the `users` table.

         -- Populate the table with mock users data.
         INSERT INTO users VALUES
           ('Thomas A. Anderson', 1677260724, 'male', 'Region_4'),
           ('Trinity', 1677260733, 'female', 'Region_4'),
           ('Morpheus', 1677260742, 'male', 'Region_8'),
           ('Dozer', 1677260823, 'male', 'Region_1'),
           ('Agent Smith', 1677260955, 'male', 'Region_0'),
           ('Persephone', 1677260901, 'female', 'Region_2'),
           ('Niobe', 1677260921, 'female', 'Region_3'),
           ('Zee', 1677260922, 'female', 'Region_5');

  3. Inspect the inserted rows.

         SELECT * FROM users;

Your output should resemble:

         user_id            registertime gender regionid
         Thomas A. Anderson 1677260724   male   Region_4
         Trinity            1677260733   female Region_4
         Morpheus           1677260742   male   Region_8
         Dozer              1677260823   male   Region_1
         Agent Smith        1677260955   male   Region_0
         Persephone         1677260901   female Region_2
         Niobe              1677260921   female Region_3
         Zee                1677260922   female Region_5
