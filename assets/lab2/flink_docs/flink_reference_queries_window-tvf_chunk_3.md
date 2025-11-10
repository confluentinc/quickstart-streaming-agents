---
document_id: flink_reference_queries_window-tvf_chunk_3
source_file: flink_reference_queries_window-tvf.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/window-tvf.html
title: SQL Windowing Table-Valued Functions in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 7
---

1223       21.52 2023-11-02 13:20:27 2023-11-02 13:20:00 2023-11-02 13:30:00 2023-11-02 13:29:59.999
    80f9fe0b-3e5d-4c25-aa6e-0b3dacfa36de 3087        1393       70.26 2023-11-02 13:20:27 2023-11-02 13:20:00 2023-11-02 13:30:00 2023-11-02 13:29:59.999
    ea733533-1516-41b6-b5e3-cadcb6f71529 3079        1488       17.55 2023-11-02 13:20:27 2023-11-02 13:20:00 2023-11-02 13:30:00 2023-11-02 13:29:59.999
    cef1cd9f-379e-4791-8a0d-69eec8adae35 3211        1293       91.20 2023-11-02 13:20:27 2023-11-02 13:20:00 2023-11-02 13:30:00 2023-11-02 13:29:59.999

The following query computes the sum of the `price` column in the `orders` table within 10-minute tumbling windows.

    -- apply aggregation on the tumbling windowed table
    SELECT window_start, window_end, SUM(price) as `sum`
      FROM TABLE(
        TUMBLE(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '10' MINUTES))
      GROUP BY window_start, window_end;

The output resembles:

    window_start        window_end          sum
    2023-11-02 10:40:00 2023-11-02 10:50:00 258484.93
    2023-11-02 10:50:00 2023-11-02 11:00:00 287632.15
    2023-11-02 11:00:00 2023-11-02 11:10:00 271945.78
    2023-11-02 11:10:00 2023-11-02 11:20:00 315207.46
    2023-11-02 11:20:00 2023-11-02 11:30:00 342618.92
    2023-11-02 11:30:00 2023-11-02 11:40:00 329754.31

### HOP¶

The `HOP` function assigns elements to windows of fixed length. Like a `TUMBLE` windowing function, the size of the windows is configured by the window size parameter. An additional window slide parameter controls how frequently a hopping window is started. Hence, hopping windows can be overlapping if the slide is smaller than the window size. In this case, elements are assigned to multiple windows. Hopping windows are also known as “sliding windows”.

For example, you could have windows of size 10 minutes that slides by 5 minutes. With this, you get every 5 minutes a window that contains the events that arrived during the last 10 minutes, as depicted by the following figure.

[](../../../_images/flink-hopping-windows.png)

The `HOP` function assigns windows that cover rows within the interval of size and shifting every slide based on a time attribute field.

* In streaming mode, the time attribute field must be an [event time attribute](../../concepts/timely-stream-processing.html#flink-sql-time-attributes).
* In batch mode, the time attribute field of window table function must be an attribute of type `TIMESTAMP` or `TIMESTAMP_LTZ`.

The return value of `HOP` is a new relation that includes all columns of the original relation as well as an additional 3 columns named `window_start`, `window_end`, and `window_time` to indicate the assigned window. The original time attribute, `timecol`, is a regular timestamp column after windowing TVF.

The `HOP` takes four required parameters and one optional parameter:

    HOP(TABLE data, DESCRIPTOR(timecol), slide, size [, offset ])

* `data`: is a table parameter that can be any relation with an time attribute column.
* `timecol`: is a column descriptor indicating which time attributes column of data should be mapped to hopping windows.
* `slide`: is a duration specifying the duration between the start of sequential hopping windows
* `size`: is a duration specifying the width of the hopping windows.
* `offset`: is an optional parameter to specify the offset which window start would be shifted by.

The following queries return all rows in the `orders` table in hopping windows with a 5-minute slide and 10-minute size.

    SELECT * FROM TABLE(
        HOP(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '5' MINUTES, INTERVAL '10' MINUTES))

    -- or with the named params
    -- note: the DATA param must be the first
    SELECT * FROM TABLE(
        HOP(
          DATA => TABLE `examples`.`marketplace`.`orders`,
          TIMECOL => DESCRIPTOR($rowtime),
          SLIDE => INTERVAL '5' MINUTES,
          SIZE => INTERVAL '10' MINUTES));

The output resembles:

    order_id                             customer_id product_id price $rowtime            window_start        window_end          window_time
    10ae1386-496e-4c6c-9436-7f7e2e7a59f9 3160        1015       26.20 2023-11-02 19:24:46 2023-11-02 19:20:00 2023-11-02 19:30:00 2023-11-02 19:29:59.999
    10ae1386-496e-4c6c-9436-7f7e2e7a59f9 3160        1015       26.20 2023-11-02 19:24:46 2023-11-02 19:15:00 2023-11-02 19:25:00 2023-11-02 19:24:59.999
    66ecb3b3-7a3d-43ac-b3a2-4c35e06a8d7c 3046        1081       20.24 2023-11-02 19:24:46 2023-11-02 19:20:00 2023-11-02 19:30:00 2023-11-02 19:29:59.999
    66ecb3b3-7a3d-43ac-b3a2-4c35e06a8d7c 3046        1081       20.24 2023-11-02 19:24:46 2023-11-02 19:15:00 2023-11-02 19:25:00 2023-11-02 19:24:59.999
    4d86db03-a573-4fc2-9699-85455331a7c4 3023        1346       85.45 2023-11-02 19:24:46 2023-11-02 19:20:00 2023-11-02 19:30:00 2023-11-02 19:29:59.999
