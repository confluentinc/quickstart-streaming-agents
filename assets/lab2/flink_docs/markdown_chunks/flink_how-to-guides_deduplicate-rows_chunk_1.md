---
document_id: flink_how-to-guides_deduplicate-rows_chunk_1
source_file: flink_how-to-guides_deduplicate-rows.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/deduplicate-rows.html
title: Deduplicate Rows in a Table with Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 2
---

# Deduplicate Rows in a Table with Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables generating a table that contains only unique records from an input table with only a few clicks.

In this guide, you create a Flink table and apply the Deduplicate Rows action to generate a topic that has only unique records, by using a [deduplication statement](../reference/queries/deduplication.html#flink-sql-deduplication). The Deduplicate Rows action creates a Flink SQL statement for you, but no knowledge of Flink SQL is required to use it.

This guide shows the following steps:

* Step 1: Create a users table
* Step 2: Apply the Deduplicate Topic action
* Step 3: Inspect the output table

## Prerequisites¶

* Access to Confluent Cloud.
* The OrganizationAdmin, EnvironmentAdmin, or FlinkAdmin role for creating compute pools, or the FlinkDeveloper role if you already have a compute pool. If you don’t have the appropriate role, contact your OrganizationAdmin or EnvironmentAdmin. For more information, see [Grant Role-Based Access in Confluent Cloud for Apache Flink](../operate-and-deploy/flink-rbac.html#flink-rbac).
* A provisioned Flink compute pool.

## Step 1: Create a users table¶

Before you can deduplicate rows, you need a table with sample data that contains duplicates. In this step, you create a simple `users` table and populate it with mock records, some of which are duplicated intentionally.

  1. Log in to Confluent Cloud and navigate to your Flink workspace.

  2. Run the following statement to create a `users` table.

         CREATE TABLE users (
           user_id STRING NOT NULL,
           registertime BIGINT,
           gender STRING,
           regionid STRING
         );

  3. Insert rows with mock data into the `users` table.

         INSERT INTO users VALUES
           ('Thomas A. Anderson', 1677260724, 'male', 'Region_4'),
           ('Thomas A. Anderson', 1677260724, 'male', 'Region_4'),
           ('Trinity', 1677260733, 'female', 'Region_4'),
           ('Trinity', 1677260733, 'female', 'Region_4'),
           ('Morpheus', 1677260742, 'male', 'Region_8'),
           ('Morpheus', 1677260742, 'male', 'Region_8'),
           ('Dozer', 1677260823, 'male', 'Region_1'),
           ('Agent Smith', 1677260955, 'male', 'Region_0'),
           ('Persephone', 1677260901, 'female', 'Region_2'),
           ('Niobe', 1677260921, 'female', 'Region_3'),
           ('Niobe', 1677260921, 'female', 'Region_3'),
           ('Niobe', 1677260921, 'female', 'Region_3'),
           ('Zee', 1677260922, 'female', 'Region_5');

  4. Inspect the inserted rows.

         SELECT * FROM users;

Your output should resemble:

         user_id            registertime gender regionid
         Thomas A. Anderson 1677260724   male   Region_4
         Thomas A. Anderson 1677260724   male   Region_4
         Trinity            1677260733   female Region_4
         Trinity            1677260733   female Region_4
         Morpheus           1677260742   male   Region_8
         Morpheus           1677260742   male   Region_8
         Dozer              1677260823   male   Region_1
         Agent Smith        1677260955   male   Region_0
         Persephone         1677260901   female Region_2
         Niobe              1677260921   female Region_3
         Niobe              1677260921   female Region_3
         Niobe              1677260921   female Region_3
         Zee                1677260922   female Region_5
