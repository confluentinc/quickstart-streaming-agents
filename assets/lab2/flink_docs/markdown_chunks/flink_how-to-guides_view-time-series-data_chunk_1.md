---
document_id: flink_how-to-guides_view-time-series-data_chunk_1
source_file: flink_how-to-guides_view-time-series-data.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/view-time-series-data.html
title: View Time Series Data in Confluent Cloud
chunk_index: 1
total_chunks: 1
---

# View Time Series Data with Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables visualizing time-series data in real time. The output of certain SQL statements render as time-series charts. Whenever a statement’s output has at least one time column, and at least one numeric column, it is charted automatically in a time-series graph when you toggle to chart mode.

You can further customize charts by user interactions: you can choose a different x-axis column, add multiple series, change the chart’s time granularity, and filter the overall time range.

## Prerequisites¶

  * Access to Confluent Cloud.
  * The OrganizationAdmin, EnvironmentAdmin, or FlinkAdmin role for creating compute pools, or the FlinkDeveloper role if you already have a compute pool. If you don’t have the appropriate role, contact your OrganizationAdmin or EnvironmentAdmin. For more information, see [Grant Role-Based Access in Confluent Cloud for Apache Flink](../operate-and-deploy/flink-rbac.html#flink-rbac).
  * A provisioned Flink compute pool.

## Step 1: Open a workspace¶

  1. Log in to Confluent Cloud Console at <https://confluent.cloud/login>.
  2. Open a Flink workspace.
  3. Use the **Catalog** and **Database** dropdown controls to select the **examples** catalog and the **marketplace** database.

## Step 2: Generate time-series data¶

Run the following statement to generate three time-series signals.

    SELECT $rowtime AS row_timestamp,
       RAND() * 0.10 * SIN(0.10 * UNIX_TIMESTAMP() + 0) AS series1,
       RAND() * 0.10 * SIN(0.10 * UNIX_TIMESTAMP() + 1.1e3) AS series2,
       RAND() * 0.03 * SIN(0.10 * UNIX_TIMESTAMP() + 1.2e3) AS series3
    FROM orders;

## Step 3: View time-series data¶

  1. Click the time-series toggle ([](../../_images/flink-workspace-time-series-toggle.png)) to open the time-series visualizer.

Your output should resemble:

[](../../_images/flink-workspace-time-series.png)

The upper pane shows the **series1** signal.

The lower pane enables scrolling through the data as it streams through the visualizer.

  2. On the right side of the lower pane, click [](../../_images/flink-workspace-nav-window-size.png) and drag it to the left. On the left side of the lower pane, click [](../../_images/flink-workspace-nav-window-size.png) and drag it to the right.

These gestures define the width of the view window that displays in the upper pane.

  3. Click [](../../_images/flink-workspace-nav-window-move.png) and drag it to the right.

The view in the upper pane adjusts to display the data within the window.

As data continues to stream, the window in the lower pane moves to the left, while the display in the upper pane remains centered on the data selected in the window.

  4. Double-click [](../../_images/flink-workspace-nav-window-move.png) to reset the view.

  5. Click **Add Column** , and in the context menu, select **series2** and **series3** to display the other signals.

  6. Click [](../../_images/flink-workspace-time-series-download.png) to download the current visualization as a PNG file.

  7. Click the time-series toggle ([](../../_images/flink-workspace-time-series-toggle.png)) to close the visualizer.
