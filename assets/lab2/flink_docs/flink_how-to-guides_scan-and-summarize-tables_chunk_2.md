---
document_id: flink_how-to-guides_scan-and-summarize-tables_chunk_2
source_file: flink_how-to-guides_scan-and-summarize-tables.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/scan-and-summarize-tables.html
title: Scan and Summarize Flink Tables in Confluent Cloud
chunk_index: 2
total_chunks: 2
---

reset the rows to unsorted.

## Apply a filter¶

Any column that has numerical or datetime data is filterable. Filters apply across all columns in the table.

Filters apply only in the graphical display and don’t affect the underlying data stream.

  1. Hover over the leftmost bar in the **price** chart.

The cursor changes to a **+** target, and a summary of the rows represented by the bar appears in a popup.

  2. Click-drag, or _brush_ the cursor over the first three bars in the **price** chart.

[](../../_images/flink-workspace-filter-prices.png)

A filter is applied to the price data, so only the rows with prices that fall within the selected range are displayed. This filter shows the orders for the least expensive products.

When a filter is applied, the unfiltered data is shown in gray.

Above the charts, the current filter is displayed and if you click on it you will see (and be able to adjust) its settings.

  3. You can apply more than one filter. In the **customer_id** chart, brush the first three bars.

A filter is applied to the customer data. In conjunction with the filter you applied already to the price data, the displayed rows show the least expensive products ordered by customers with IDs between 3000 and 3029, inclusive.

Click **x** in the filters to clear them.

## View changes over time¶

[](../../_images/flink-sparkline-time-series.png)

If your data contains a datetime column then each numerical column, along with distribution, will have the option to show the average value over time. If the data is filtered then the unfiltered average value is also shown for context. You can hover over the chart for exact values.
