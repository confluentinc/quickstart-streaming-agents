---
document_id: flink_reference_example-data_chunk_1
source_file: flink_reference_example-data.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/example-data.html
title: Example Data Streams in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 3
---

# Example Data Streams in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides an Examples catalog that has mock data streams you can use for experimenting with Flink SQL queries.

* The `examples` catalog is available in all environments.
* All example tables have `$rowtime` available as a system column. The `SOURCE_WATERMARK()` strategy for example tables is different than the `SOURCE_WATERMARK()` strategy Kafka-based tables. For the example tables, the `SOURCE_WATAERMARK()` corresponds to the maximum timestamp seen to this point.
* You can use example data in Flink workspaces, Flink shell, Terraform, and all other clients.
* Example data is read-only, so you can’t use INSERT INTO/ALTER/DROP/CREATE statements on these tables, the database, or the catalog.
* SHOW statements work for the database, catalog, and tables.
* SHOW CREATE TABLE works for the example tables.

## Publish to a Kafka topic¶

You can publish any of the example streams to a Kafka topic by creating a Flink table and populating it with the [INSERT INTO FROM SELECT](queries/insert-into-from-select.html#flink-sql-insert-into-from-select-statement) statement. Confluent Cloud for Apache Flink creates a Kafka topic automatically for the table.

  1. Run the following statements to create and populate a `customers_source` table with the `examples.marketplace.customers` stream.

         CREATE TABLE customers_source (
           customer_id INT,
           name STRING,
           address STRING,
           postcode STRING,
           city STRING,
           email STRING,
           PRIMARY KEY (customer_id) NOT ENFORCED
         );

         INSERT INTO customers_source(
           customer_id,
           name,
           address,
           postcode,
           city,
           email
         )
         SELECT * FROM examples.marketplace.customers;

  2. Run the following statement to inspect the `customers_source` table:

         SELECT * FROM customers_source;

Your output should resemble:

         customer_id name                  address                postcode city               email
         3172        Roseanna Bode         6744 Kacy Bypass       22635    Margarettborough   rico.zboncak@yahoo.com
         3055        Josiah Morissette PhD 61799 Friesen Islands  14194    North Abbybury     thomas.dach@gmail.com
         3177        Buddy Hill            6836 Graham Street     72767    South Earnest      enoch.turcotte@hotmail.com
         ...

  3. Navigate to the [Environments](https://confluent.cloud/environments) page, and in the navigation menu, click **Data portal**.

  4. In the **Data portal** page, click the dropdown menu and select the environment for your workspace.

  5. In the **Recently created** section, find your **customers_source** topic and click it to open the details pane.

  6. Click **View all messages** to open the **Message viewer** on the `customers_source` topic.

  7. Observe the example data from the `examples.marketplace.customers` flowing into the Kafka topic.

Important

The INSERT INTO statement runs continuously until you stop it manually. Free resources in your compute pool by deleting the long-running statement when you’re done.
