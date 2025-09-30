---
document_id: flink_how-to-guides_mask-fields_chunk_1
source_file: flink_how-to-guides_mask-fields.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/mask-fields.html
title: Mask Fields in a Table with Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 2
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
