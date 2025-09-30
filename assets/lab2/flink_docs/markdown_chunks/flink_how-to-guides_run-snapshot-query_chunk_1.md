---
document_id: flink_how-to-guides_run-snapshot-query_chunk_1
source_file: flink_how-to-guides_run-snapshot-query.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/run-snapshot-query.html
title: Run a Snapshot Query with in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Run a Snapshot Query with Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® supports [snapshot queries](../concepts/snapshot-queries.html#flink-sql-snapshot-queries) that read data from a table at a specific point in time. In contrast with a streaming query, which runs continuously and returns results incrementally, a snapshot query runs, returns results, and then exits.

This guide shows how to run a snapshot query on a Flink table.

* Step 1: Create an example data stream
* Step 2: Run a snapshot query on the topic
* Step 3: Set the snapshot mode in SQL

Note

Snapshot query is an Early Access Program feature in Confluent Cloud for Apache Flink.

An Early Access feature is a component of Confluent Cloud introduced to gain feedback. This feature should be used only for evaluation and non-production testing purposes or to provide feedback to Confluent, particularly as it becomes more widely available in follow-on preview editions.

Early Access Program features are intended for evaluation use in development and testing environments only, and not for production use. Early Access Program features are provided: (a) without support; (b) “AS IS”; and (c) without indemnification, warranty, or condition of any kind. No service level commitment will apply to Early Access Program features. Early Access Program features are considered to be a Proof of Concept as defined in the Confluent Cloud Terms of Service. Confluent may discontinue providing preview releases of the Early Access Program features at any time in Confluent’s sole discretion.

## Prerequisites¶

* Access to Confluent Cloud.
* The OrganizationAdmin, EnvironmentAdmin, or FlinkAdmin role for creating compute pools, or the FlinkDeveloper role if you already have a compute pool. If you don’t have the appropriate role, contact your OrganizationAdmin or EnvironmentAdmin. For more information, see [Grant Role-Based Access in Confluent Cloud for Apache Flink](../operate-and-deploy/flink-rbac.html#flink-rbac).
* A provisioned Flink compute pool.

## Step 1: Create an example data stream¶

In this step, you create a Datagen source connector that produces a stream of data.

If you have a topic with data, you can skip this step and proceed to Step 2: Run a snapshot query on the topic.

  1. In the Confluent Cloud UI, go to the **Environments** page.

  2. Select the environment where you want to create the connector.

  3. In the **Overview** page, click the cluster that you want to use.

  4. In the navigation menu, click **Connectors**.

  5. Click **Add connector** , and in the **Connector Plugins** page, click **Sample Data**.

  6. In the **Launch Sample Data** dialog, click **Users** , and click **Launch**.

It may take a few minutes to create the connector.

## Step 2: Run a snapshot query on the topic¶

  1. In the navigation menu, click **Topics**.

  2. In the topics list, find the topic you want to query. If you created a Datagen source connector, the topic is named `sample_data_users`.

  3. Click the topic name to open the topic details page.

  4. Click **Query with Flink**.

A Flink workspace opens with a SQL editor that you can use to run a snapshot query.

  5. In the cell, find the **Mode** dropdown, which defaults to **Streaming**.

  6. Change the mode to **Snapshot** and click **Run**.

The query runs and returns all of the messages that have been produced to the topic at the current point in time.

## Step 3: Set the snapshot mode in SQL¶

You can set the snapshot mode in SQL by using the [SET](../reference/statements/set.html#flink-sql-set-statement-config-options) statement to assign the `sql.snapshot.mode` configuration option.

  1. In the cell, prepend the SELECT statement with the following SET statement:

         SET 'sql.snapshot.mode' = 'now';
         SELECT * FROM `<your-env>`.`<your-cluster>`.`sample_data_users`;

  2. Click **Run**.

The query runs and returns all of the messages that have been produced to the topic at the current point in time.
