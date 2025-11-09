---
document_id: flink_how-to-guides_transform-topic_chunk_1
source_file: flink_how-to-guides_transform-topic.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/transform-topic.html
title: Transform a Topic with Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 2
---

# Transform a Topic with Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables generating a transformed topic from an input topic’s properties, like partition count, key, serialization format, and field names, with only a few clicks.

In this guide, you create a Flink table and apply a transformation that creates an output topic with these changes:

* Rename a field
* Specify a bucket key
* Change the key and value serialization format
* Specify a different partition count

The Transform Topic action creates a Flink SQL statement for you, but no knowledge of Flink SQL is required to use it.

This guide shows the following steps:

* Step 1: Create a users table
* Step 2: Apply the Transform Topic action
* Step 3: Inspect the transformed topic

## Prerequisites¶

* Access to Confluent Cloud.
* The OrganizationAdmin, EnvironmentAdmin, or FlinkAdmin role for creating compute pools, or the FlinkDeveloper role if you already have a compute pool. If you don’t have the appropriate role, contact your OrganizationAdmin or EnvironmentAdmin. For more information, see [Grant Role-Based Access in Confluent Cloud for Apache Flink](../operate-and-deploy/flink-rbac.html#flink-rbac).
* A provisioned Flink compute pool.

## Step 1: Create a users table¶

  1. Log in to Confluent Cloud and navigate to your Flink workspace.

  2. Run the following statement to create a `users` table.

         -- Create a users table.
         CREATE TABLE users (
           user_id STRING,
           registertime BIGINT,
           gender STRING,
           regionid STRING
         );

  3. Insert rows with mock data into the `users` table.

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

  4. Inspect the inserted rows.

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
