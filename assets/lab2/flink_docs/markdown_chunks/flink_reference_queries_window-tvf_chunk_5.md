---
document_id: flink_reference_queries_window-tvf_chunk_5
source_file: flink_reference_queries_window-tvf.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/window-tvf.html
title: SQL Windowing Table-Valued Functions in Confluent Cloud for Apache Flink
chunk_index: 5
total_chunks: 7
---

The output resembles:

    order_id                             customer_id product_id price $rowtime            window_start        window_end          window_time
    2572a2e0-2ba2-4947-8926-e70e31b68df3 3239        1015       13.59 2023-11-02 19:27:39 2023-11-02 19:20:00 2023-11-02 19:28:00 2023-11-02 19:27:59.999
    2572a2e0-2ba2-4947-8926-e70e31b68df3 3239        1015       13.59 2023-11-02 19:27:39 2023-11-02 19:20:00 2023-11-02 19:30:00 2023-11-02 19:29:59.999
    7f791e40-a524-4a9b-bb0d-35a2c1b5a7c4 3102        1374       93.59 2023-11-02 19:27:39 2023-11-02 19:20:00 2023-11-02 19:28:00 2023-11-02 19:27:59.999
    7f791e40-a524-4a9b-bb0d-35a2c1b5a7c4 3102        1374       93.59 2023-11-02 19:27:39 2023-11-02 19:20:00 2023-11-02 19:30:00 2023-11-02 19:29:59.999
    47e70310-8fa4-4568-b521-7e2b68b06634 3026        1142       58.26 2023-11-02 19:27:39 2023-11-02 19:20:00 2023-11-02 19:28:00 2023-11-02 19:27:59.999
    47e70310-8fa4-4568-b521-7e2b68b06634 3026        1142       58.26 2023-11-02 19:27:39 2023-11-02 19:20:00 2023-11-02 19:30:00 2023-11-02 19:29:59.999
    fe1b440e-dc75-4092-be11-8e1c3afe55c7 3106        1057       11.37 2023-11-02 19:27:39 2023-11-02 19:20:00 2023-11-02 19:28:00 2023-11-02 19:27:59.999
    fe1b440e-dc75-4092-be11-8e1c3afe55c7 3106        1057       11.37 2023-11-02 19:27:39 2023-11-02 19:20:00 2023-11-02 19:30:00 2023-11-02 19:29:59.999
    6668e4dc-d574-44db-8f0f-2b8e1b1f3c2e 3061        1049       26.20 2023-11-02 19:27:39 2023-11-02 19:20:00 2023-11-02 19:28:00 2023-11-02 19:27:59.999
    6668e4dc-d574-44db-8f0f-2b8e1b1f3c2e 3061        1049       26.20 2023-11-02 19:27:39 2023-11-02 19:20:00 2023-11-02 19:30:00 2023-11-02 19:29:59.999

The following query computes the sum of the `price` column in the `orders` table within CUMULATE windows that have a 2-minute step and 10-minute size.

    -- apply aggregation on the cumulating windowed table
    SELECT window_start, window_end, SUM(price) as `sum`
      FROM TABLE(
        CUMULATE(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '2' MINUTES, INTERVAL '10' MINUTES))
      GROUP BY window_start, window_end;

The output resembles:

    window_start            window_end              sum
    2023-11-02 12:40:00.000 2023-11-02 12:46:00.000 327376.23
    2023-11-02 12:40:00.000 2023-11-02 12:48:00.000 661272.70
    2023-11-02 12:40:00.000 2023-11-02 12:50:00.000 989294.13
    2023-11-02 12:50:00.000 2023-11-02 12:52:00.000 1316596.58
    2023-11-02 12:50:00.000 2023-11-02 12:54:00.000 1648097.20
    2023-11-02 12:50:00.000 2023-11-02 12:56:00.000 1977881.53
    2023-11-02 12:50:00.000 2023-11-02 12:58:00.000 2304080.32
    2023-11-02 12:50:00.000 2023-11-02 13:00:00.000 2636795.56

### SESSION¶

The `SESSION` function groups elements by sessions of activity. Unlike `TUMBLE` and `HOP` windows, session windows do not overlap and do not have a fixed start and end time. Instead, a session window closes when it doesn’t receive elements for a certain period of time, that is, when a gap of inactivity occurs. A session window is configured with a static session gap that defines the duration of inactivity. When this period expires, the current session closes and subsequent elements are assigned to a new session window.

For example, you could have windows with a gap of 1 minute. With this configuration, when the interval between two events is less than 1 minute, these events are grouped into the same session window. If there is no data for 1 minute following the latest event, then this session window closes and is sent downstream. Subsequent events are assigned to a new session window.

The `SESSION` function assigns windows that cover rows based on a time attribute.

  * In streaming mode, the time attribute field must be an [event time attribute](../../concepts/timely-stream-processing.html#flink-sql-time-attributes).
  * `SESSION` Window TVF is not supported in batch mode.

The return value of `SESSION` is a new relation that includes all columns of the original relation, as well as three additional columns named `window_start`, `window_end`, and `window_time` to indicate the assigned window. The original time attribute `timecol` becomes a regular timestamp column after the windowing TVF.

The `SESSION` function takes three required parameters and one optional parameter:

    SESSION(TABLE data [PARTITION BY(keycols, ...)], DESCRIPTOR(timecol), gap)

  * `data`: is a table parameter that can be any relation with a time attribute column.
  * `keycols`: is a column or set of columns indicating which columns should be used to partition the data prior to session windows.
  * `timecol`: is a column descriptor indicating which time attribute column of data should be mapped to session windows.
  * `gap`: is the maximum interval in timestamp for two events to be considered part of the same session window.
