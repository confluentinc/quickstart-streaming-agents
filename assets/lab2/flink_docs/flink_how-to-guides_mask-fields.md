---
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/mask-fields.html
title: Mask Fields in a Table with Confluent Cloud for Apache Flink
hierarchy: ['how-to-guides', 'mask-fields.html']
scraped_date: 2025-09-05T13:47:41.945755
---

# Mask Fields in a Table with Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables generating a topic that contains masked fields from an input topic with only a few clicks.

In this guide, you create a Flink table and apply the Mask Fields action to generate a topic that has user names masked out, by using a preconfigured regular expression. The Mask Fields action creates a Flink SQL statement for you, but no knowledge of Flink SQL is required to use it.

This guide shows the following steps:

  * Step 1: Inspect the example stream
  * Step 2: Create a source table
  * Step 3: Apply the Mask Fields action
  * Step 4: Inspect the output table
  * Step 5: Stop the persistent query

## Prerequisites¶

  * Access to Confluent Cloud.
  * The OrganizationAdmin, EnvironmentAdmin, or FlinkAdmin role for creating compute pools, or the FlinkDeveloper role if you already have a compute pool. If you don’t have the appropriate role, contact your OrganizationAdmin or EnvironmentAdmin. For more information, see [Grant Role-Based Access in Confluent Cloud for Apache Flink](../operate-and-deploy/flink-rbac.html#flink-rbac).
  * A provisioned Flink compute pool.

## Step 1: Inspect the example stream¶

In this step, you query the read-only `customers` table in the `examples.marketplace` database to inspect the stream for fields that you can mask.

  1. Log in to Confluent Cloud and navigate to your Flink workspace.

  2. In the **Use catalog** dropdown, select your environment.

  3. In the **Use database** dropdown, select your Kafka cluster.

  4. Run the following statement to inspect the example `customers` stream.
         
         SELECT * FROM examples.marketplace.customers;

Your output should resemble:
         
         customer_id name                  address                  postcode city              email
         3134        Dr. Andrew Terry      45488 Eileen Walk        78690    Latoyiaberg       romaine.lynch@hotmail.com
         3243        Miss Shelby Lueilwitz 199 Bernardina Brook     79991    Johnburgh         dominick.oconner@hotmail.c…
         3027        Korey Hand            655 Murray Turnpike      08917    Port Sukshire     karlyn.ziemann@yahoo.com
         ...

## Step 2: Create a source table¶

In the step, you create a `customers_source` table for the data from the example `customers` stream. You use the [INSERT INTO FROM SELECT](../reference/queries/insert-into-from-select.html#flink-sql-insert-into-from-select-statement) statement to populate the table with streaming data.

  1. Run the following statement to register the `customers_source` table. Confluent Cloud for Apache Flink creates a backing Kafka topic that has the same name automatically.
         
         -- Register a customers source table.
         CREATE TABLE customers_source (
           customer_id INT NOT NULL,
           name STRING,
           address STRING,
           postcode STRING,
           city STRING,
           email STRING,
           PRIMARY KEY(`customer_id`) NOT ENFORCED
         );

  2. Run the following statement to populate the `customers_source` table with data from the example `customers` stream.
         
         -- Persistent query to stream data from
         -- the customers example stream to the
         -- customers_source table.
         INSERT INTO customers_source(
           customer_id,
           name,
           address,
           postcode,
           city,
           email
           )
         SELECT customer_id, name, address, postcode, city, email FROM examples.marketplace.customers;

  3. Run the following statement to inspect the `customers_source` table.
         
         SELECT * FROM customers_source;

Your output should resemble:
         
         customer_id name                  address                  postcode city              email
         3088        Phil Grimes          07738 Zieme Court        84845    Port Dillontown     garnett.abernathy@hotmail.com
         3022        Jeana Gaylord        021 Morgan Drives        35160    West Celena         emile.daniel@gmail.com
         3097        Lily Ryan            671 Logan Throughway     58261    Dickinsonburgh      ivory.lockman@gmail.com
         ...

## Step 3: Apply the Mask Fields action¶

In the previous step, you created a Flink table that had rows with customer names, which might be confidential data. In this step, you apply the Mask Fields action to create an output table that has the contents of the `name` field masked.

  1. Navigate to the [Environments](https://confluent.cloud/environments) page, and in the navigation menu, click **Data portal**.

  2. In the **Data portal** page, click the dropdown menu and select the environment for your workspace.

  3. In the **Recently created** section, find your **customers_source** topic and click it to open the details pane.

  4. Click **Actions** , and in the Actions list, click **Mask fields** to open the **Mask fields** dialog.

  5. In the **Field to mask** dropdown, select **name**.

  6. In the **Regex for name** dropdown, select **Word characters**.

  7. In the **Runtime configuration** section, either select an existing service account or create a new service account for the current action.

Note

The service you select must have the EnvironmentAdmin role to create topics, schemas, and run Flink statements.

  8. Optionally, click the **Show SQL** toggle to view the statements that the action will run.

The code resembles:
         
         CREATE TABLE `<your-environment>`.`<your-kafka-cluster>`.`customers_source_mask`
           LIKE `<your-environment>`.`<your-kafka-cluster>`.`customers_source`
         
         INSERT INTO `<your-environment>`.`<your-kafka-cluster>`.`customers_source_mask` SELECT
           `customer_id`,
           REGEXP_REPLACE(`name`, '(\w)', '*') as `name`,
           address,
           postcode,
           city,
           email
         FROM `<your-environment>`.`<your-kafka-cluster>`.`customers_source`;

  9. Click **Confirm**.

The action runs the CREATE TABLE and INSERT INTO statements. These statements register the `customers_source_mask` table and populate it with rows from the `customers_source` table. The strings in the `name` column are masked by the [REGEXP_REPLACE](../reference/functions/string-functions.html#flink-sql-regexp-replace-function) function.

## Step 4: Inspect the output table¶

The statements that were generated by the Mask Fields action created an output table named `customers_source_mask`. In this step, you query the output table to see the masked field values.

  * Return to your workspace and run the following command to inspect the `customers_source_mask` output table.
        
        SELECT * FROM customers_source_mask;

Your output should resemble:
        
        customer_id name                 address                postcode city              email
        3104        **** *** ******      342 Odis Hollow        27615    West Florentino   bryce.hodkiewicz@hotmail.c…
        3058        **** ******* ******  33569 Turner Glens     14107    Schummchester     sarah.roob@yahoo.com
        3138        **** ****** ******** 944 Elden Walks        39293    New Ernestbury    velvet.volkman@gmail.com
        ...

## Step 5: Stop the persistent query¶

The INSERT INTO statement that was created by the Mask Fields action runs continuously until you stop it manually. Free resources in your compute pool by deleting the long-running statement.

  1. Navigate to the **Flink** page in your environment and click **Flink statements**.
  2. In the statements list, find the statement that has a status of **Running**.
  3. In the **Actions** column, click **…** and select **Delete statement**.
  4. In the **Confirm statement deletion** dialog, copy and paste the statement name and click **Confirm**.

## Related content¶

  * Flink action: [Deduplicate Rows in a Table](deduplicate-rows.html#flink-sql-deduplicate-topic-action)
  * Flink action: [Transform a Topic](transform-topic.html#flink-sql-transform-topic-action)
  * Flink action: [Create an Embedding](../../ai/embeddings/embedding-action.html#flink-sql-embedding-action)
  * [Aggregate a Stream in a Tumbling Window](aggregate-tumbling-window.html#flink-sql-aggregate-tumbling-window)
  * [Compare Current and Previous Values in a Data Stream](compare-current-and-previous-values.html#flink-sql-compare-current-and-previous-values)
  * [Convert the Serialization Format of a Topic](convert-serialization-format.html#flink-sql-convert-format)

Note

This website includes content developed at the [Apache Software Foundation](https://www.apache.org/) under the terms of the [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0.html).
