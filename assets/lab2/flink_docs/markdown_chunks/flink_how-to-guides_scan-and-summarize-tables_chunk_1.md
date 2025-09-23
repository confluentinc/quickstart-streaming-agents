---
document_id: flink_how-to-guides_scan-and-summarize-tables_chunk_1
source_file: flink_how-to-guides_scan-and-summarize-tables.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/scan-and-summarize-tables.html
title: Scan and Summarize Flink Tables in Confluent Cloud
chunk_index: 1
total_chunks: 2
---

# Scan and Summarize Tables with Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides graphical tools in your workspaces that enable scanning and summarizing data visually in Flink tables. Distributions of values for each column in a table are shown in embedded charts, or _sparklines_. You can highlight values in one chart to filter corresponding values in all columns, revealing connections and relationships in your data.

[](../../_images/flink-dex-visual-grid.gif)

## Overview¶

When you explore data in a table, you frequently want to find a row (scan), or you may want to understand the shape of the data (summarize).

### Scan¶

Cloud Console workspaces provide a search box that enables scanning the data for particular rows. For example, if you’re interested in the orders that are placed by a particular customer, you can enter the customer’s ID in the search box to scan the table for relevant rows.

### Summarize¶

In a Cloud Console workspace, when you run a Flink SQL statement that returns a table, sparklines are displayed automatically and show the distribution of distinct values in each column. These charts update automatically as new rows arrive from the data stream.

The workspace enables filtering rows by interacting with these charts. For example, in an `orders` table, you can apply a filter that shows only rows for low-price items and compare these results with another filter that shows high-price items to see if there’s a different distribution of items between the price ranges.

## Explore example data¶

  1. Log in to the Confluent Cloud Console and navigate to an environment that hosts Flink SQL.

  2. In the navigation menu, click **Stream processing** to open the **Stream processing** page.

  3. If you have a workspace set up already, click its tile, or click **Create workspace** to create a new one.

  4. In the workspace, use the **Catalog** and **Database** dropdown controls to select the **examples** catalog and the **marketplace** database.

  5. Run the following statement to query the **orders** stream for all rows.

         SELECT * FROM orders;

Your output should resemble:

[](../../_images/flink-workspace-visual-grid.png)

At the top of each column, a chart is displayed. The charts update as new rows stream into the query results. Each chart shows the distribution of distinct values in the column, for strings, booleans, numbers, and categories. An icon displays the data type of the column. Also, the arrow icon enables sorting rows by the column values.

At the bottom of each column, aggregated values are displayed that summarize aspects of the data in the column, like the count of rows and the number of distinct values, or _cardinality_. For columns with numerical values, you can see statistics, like the average, minimum, and maximum values.

The number of rows displayed is limited to 5000 or to the LIMIT value you specify in your query. For example, the following statement limits the query result to 50 rows.

         SELECT * FROM orders LIMIT 50;

  6. At the bottom of the **price** column, change the dropdown control from **Count** to **Average**.

The average value of the most recent prices displays and updates as new rows arrive.

Select other statistics for prices, like **Max** and **Min**.

## Search for values¶

The search box enables finding values across all columns in the currently displayed result set.

The search box doesn’t filter the data. It’s useful for scanning for a particular row or narrowing the results down to a particular row.

  1. In the search box, type “3000”.

All rows that have a **customer_id** value of `3000` are displayed, which enables viewing all orders from this customer.

Click **x** in the search to clear it.

  2. In the search box, type “1000”.

All rows that have a **product_id** value of `1000` are displayed, which enables viewing all orders for this product.

Click **x** in the search box to clear it.

  3. In the search box, type “3050”, and in the **price** column, click the double-arrow icon.

All rows for customer `3050` are displayed, and the rows are sorted by price, from lowest to highest.

  4. In the **price** column, click the arrow icon.

All rows for customer `3050` are displayed, and the rows are sorted by price, from highest to lowest.

Click **x** in the search box to clear it, and click the arrow icon in the **price** column to reset the rows to unsorted.
