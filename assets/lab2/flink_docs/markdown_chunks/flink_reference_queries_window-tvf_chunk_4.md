---
document_id: flink_reference_queries_window-tvf_chunk_4
source_file: flink_reference_queries_window-tvf.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/window-tvf.html
title: SQL Windowing Table-Valued Functions in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 7
---

4d86db03-a573-4fc2-9699-85455331a7c4 3023        1346       85.45 2023-11-02 19:24:46 2023-11-02 19:15:00 2023-11-02 19:25:00 2023-11-02 19:24:59.999
    d1460cf7-9472-45e0-9c2d-40537c9f34c0 3114        1333       49.56 2023-11-02 19:24:47 2023-11-02 19:20:00 2023-11-02 19:30:00 2023-11-02 19:29:59.999
    d1460cf7-9472-45e0-9c2d-40537c9f34c0 3114        1333       49.56 2023-11-02 19:24:47 2023-11-02 19:15:00 2023-11-02 19:25:00 2023-11-02 19:24:59.999
    e38984d8-5683-4e55-9f7a-e43350de7c3d 3024        1402       90.75 2023-11-02 19:24:47 2023-11-02 19:20:00 2023-11-02 19:30:00 2023-11-02 19:29:59.999
    e38984d8-5683-4e55-9f7a-e43350de7c3d 3024        1402       90.75 2023-11-02 19:24:47 2023-11-02 19:15:00 2023-11-02 19:25:00 2023-11-02 19:24:59.999

The following query computes the sum of the `price` column in the `orders` table within hopping windows that have a 5-minute slide and 10-minute size.

    -- apply aggregation on the hopping windowed table
    SELECT window_start, window_end, SUM(price) as `sum`
      FROM TABLE(
        HOP(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '5' MINUTES, INTERVAL '10' MINUTES))
      GROUP BY window_start, window_end;

The output resembles:

    window_start        window_end          sum
    2023-11-02 11:10:00 2023-11-02 11:20:00 296049.38
    2023-11-02 11:15:00 2023-11-02 11:25:00 1122455.07
    2023-11-02 11:20:00 2023-11-02 11:30:00 1648270.20
    2023-11-02 11:25:00 2023-11-02 11:35:00 2143271.00
    2023-11-02 11:30:00 2023-11-02 11:40:00 2701592.45
    2023-11-02 11:35:00 2023-11-02 11:45:00 3214376.78

### CUMULATE¶

Cumulating windows are useful in some scenarios, such as tumbling windows with early firing in a fixed window interval. For example, a daily dashboard might display cumulative unique views (UVs) from 00:00 to every minute, and the UV at 10:00 might represent the total number of UVs from 00:00 to 10:00. This can be implemented easily and efficiently by `CUMULATE` windowing.

The `CUMULATE` function assigns elements to windows that cover rows within an initial interval of a specified step size, and it expands by one more step size, keeping the window start fixed, for every step, until the maximum window size is reached.

`CUMULATE` function windows all have the same window start but add a step size to each window until the max value is reached, so the window size is always changing, and the windows overlap. When the max value is reached, the window start is advanced to the end of the last window, and the size resets to the step size. In comparison, `TUMBLE` function windows all have the same size, the step size, and do not overlap.

[](../../../_images/flink-cumulating-windows.png)

For example, you could have a cumulating window with a 1-hour step and 1-day maximum size, and you will get these windows for every day:

* `[00:00, 01:00)`
* `[00:00, 02:00)`
* `[00:00, 03:00)` …
* `[00:00, 24:00)`

The `CUMULATE` function assigns windows based on a time attribute column.

* In streaming mode, the time attribute field must be an [event time attribute](../../concepts/timely-stream-processing.html#flink-sql-time-attributes).
* In batch mode, the time attribute field of window table function must be an attribute of type `TIMESTAMP` or `TIMESTAMP_LTZ`.

The return value of `CUMULATE` is a new relation that includes all columns of the original relation, as well as an additional 3 columns named `window_start`, `window_end`, and `window_time` to indicate the assigned window. The original time attribute, `timecol`, is a regular timestamp column after window TVF.

The `CUMULATE` takes four required parameters and one optional parameter:

    CUMULATE(TABLE data, DESCRIPTOR(timecol), step, size)

* `data`: is a table parameter that can be any relation with an time attribute column.
* `timecol`: is a column descriptor indicating which time attributes column of data should be mapped to cumulating windows.
* `step`: is a duration specifying the increased window size between the end of sequential cumulating windows.
* `size`: is a duration specifying the max width of the cumulating windows. `size` must be an integral multiple of `step`.
* `offset`: is an optional parameter to specify the offset which window start would be shifted by.

The following queries return all rows in the `orders` table in CUMULATE windows that have a 2-minute step and 10-minute size.

    SELECT * FROM TABLE(
        CUMULATE(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '2' MINUTES, INTERVAL '10' MINUTES));

    -- or with the named params
    -- note: the DATA param must be the first
    SELECT * FROM TABLE(
        CUMULATE(
          DATA => TABLE `examples`.`marketplace`.`orders`,
          TIMECOL => DESCRIPTOR($rowtime),
          STEP => INTERVAL '2' MINUTES,
          SIZE => INTERVAL '10' MINUTES));
