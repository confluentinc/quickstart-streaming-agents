---
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/window-tvf.html
title: SQL Windowing Table-Valued Functions in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'queries', 'window-tvf.html']
scraped_date: 2025-09-05T13:49:32.078618
---

# Windowing Table-Valued Functions (Windowing TVFs) in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides several window table-valued functions (TVFs) for dividing the elements of a table into windows.

## Description¶

Windows are central to processing infinite streams. Windows split the stream into “buckets” of finite size, over which you can apply computations. This document focuses on how windowing is performed in Confluent Cloud for Apache Flink and how you can benefit from windowed functions.

Flink provides several window table-valued functions (TVF) to divide the elements of your table into windows, including:

  * Tumble Windows
  * Hop Windows
  * Cumulate Windows
  * Session Windows (not supported in batch mode)

Note that each element can logically belong to more than one window, depending on the windowing table-valued function you use. For example, HOP windowing creates overlapping windows in which a single element can be assigned to multiple windows.

Windowing TVFs are Flink-defined Polymorphic Table Functions (abbreviated PTF). PTF is part of the [SQL 2016 standard](https://www.iso.org/standard/78938.html), a special table-function, but can have a table as a parameter. PTF is a powerful feature to change the shape of a table. Because PTFs are used semantically like tables, their invocation occurs in a `FROM` clause of a `SELECT` statement.

These are frequently-used computations based on windowing TVF:

  * [Window Aggregation](window-aggregation.html#flink-sql-window-aggregation)
  * [Window TopN](window-topn.html#flink-sql-window-top-n)
  * [Window Join](window-join.html#flink-sql-window-join)
  * [Window Deduplication](window-deduplication.html#flink-sql-window-deduplication)

## Window functions¶

Flink provides 4 built-in windowing TVFs: `TUMBLE`, `HOP`, `CUMULATE` and `SESSION`. The return value of windowing TVF is a new relation that includes all columns of original relation as well as additional 3 columns named “window_start”, “window_end”, “window_time” to indicate the assigned window.

  * In streaming mode, the “window_time” field is a [time attribute](../../concepts/timely-stream-processing.html#flink-sql-time-attributes) of the window.
  * In batch mode, the “window_time” field is an attribute of type `TIMESTAMP` or `TIMESTAMP_LTZ` based on input time field type.

The “window_time” field can be used in subsequent time-based operations, for example, another windowing TVF, [interval-join](joins.html#flink-sql-interval-joins), or [over aggregation](over-aggregation.html#flink-sql-over-aggregation). The value of `window_time` always equal to `window_end - 1ms`.

## Window alignment¶

Time-based window boundaries align with clock seconds, minutes, hours, and days. For example, assume that you have events with these timestamps (in UTC):

  * 00:59:00.000
  * 00:59:30.000
  * 01:00:15.000

If you put these events into hour-long tumbling windows, the first two land in the window for `00:00:00-00:59:59.999`, and the third event lands in the following hour.

## Supported time units¶

Window TVFs support the following [time units](../functions/datetime-functions.html#flink-sql-time-interval-and-point-unit-specifiers):

  * SECOND
  * MINUTE
  * HOUR
  * DAY

MONTH and YEAR time units are not currently supported.

## Examples¶

The following examples show Window TVFs over [example data streams](../example-data.html#flink-sql-example-data) that you can experiment with.

Note

To show the behavior of windowing more clearly in the following examples, `TIMESTAMP(3)` values may be simplified so that trailing zeroes aren’t shown. For example, `2020-04-15 08:05:00.000` may be shown as `2020-04-15 08:05`. Columns may be hidden intentionally to enhance the readability of the content.

### TUMBLE¶

The `TUMBLE` function assigns each element to a window of specified window size. Tumbling windows have a fixed size and do not overlap. For example, suppose you specify a tumbling window with a size of 5 minutes. In that case, Flink will evaluate the current window, and a new window started every five minutes, as illustrated by the following figure.

[](../../../_images/flink-tumbling-windows.png)

The `TUMBLE` function assigns a window for each row of a relation based on a time attribute field.

  * In streaming mode, the time attribute field must be an [event time attribute](../../concepts/timely-stream-processing.html#flink-sql-time-attributes).
  * In batch mode, the time attribute field of window table function must be an attribute of type `TIMESTAMP` or `TIMESTAMP_LTZ`.

The return value of `TUMBLE` is a new relation that includes all columns of the original relation, as well as an additional 3 columns named `window_start`, `window_end`, and `window_time` to indicate the assigned window. The original time attribute, `timecol` is a regular timestamp column after windowing TVF.

The `TUMBLE` function takes three required parameters and one optional parameter:

    TUMBLE(TABLE data, DESCRIPTOR(timecol), size [, offset ])

  * `data`: is a table parameter that can be any relation with a time attribute column.
  * `timecol`: is a column descriptor indicating which time attributes column of data should be mapped to tumbling windows.
  * `size`: is a duration specifying the width of the tumbling windows.
  * `offset`: is an optional parameter to specify the offset which window start would be shifted by.

Here is an example invocation on the `orders` table:

    DESCRIBE `examples`.`marketplace`.`orders`;

The output resembles:

    +--------------+-----------+----------+---------------+
       | Column Name  | Data Type | Nullable |    Extras     |
       +--------------+-----------+----------+---------------+
       | order_id     | STRING    | NOT NULL |               |
       | customer_id  | INT       | NOT NULL |               |
       | product_id   | STRING    | NOT NULL |               |
       | price        | DOUBLE    | NOT NULL |               |
       +--------------+-----------+----------+---------------+

The following query returns all rows in the `orders` table.

    SELECT * FROM `examples`.`marketplace`.`orders`;

The output resembles:

    order_id                             customer_id  product_id price
    d770a538-a70c-4de6-9d06-e6c16c5bef5a 3075         1379       32.21
    787ee1f4-d0d0-4c39-bdb9-44dc2d203d55 3028         1335       34.74
    7ab7ce23-5f61-4398-afad-b1e3f548fee3 3148         1045       69.26
    6fea712c-9454-497e-8038-ebaf6dfc7a17 3247         1390       67.26
    dc9daf5e-98d5-4bcd-8839-251fed13b75e 3167         1309       12.04
    ab3151d0-2950-49cd-9783-016ccc6a3281 3105         1094       21.52
    d27ca945-3cff-48a4-afcc-7b17446aa95d 3168         1250       99.95

The following queries return all rows in the `orders` table in 10-minute tumbling windows.

    SELECT * FROM TABLE(
       TUMBLE(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '10' MINUTES))
    
    -- or with the named params
    -- note: the DATA param must be the first
    SELECT * FROM TABLE(
       TUMBLE(
         DATA => TABLE `examples`.`marketplace`.`orders`,
         TIMECOL => DESCRIPTOR($rowtime),
         SIZE => INTERVAL '10' MINUTES));

The output resembles:

    order_id                             customer_id product_id price $rowtime            window_start        window_end          window_time
    e69058b5-7ed9-44fa-86ff-4d6f8baff028 3145        1488       63.94 2023-11-02 13:20:27 2023-11-02 13:20:00 2023-11-02 13:30:00 2023-11-02 13:29:59.999
    92e81cc4-93c4-488b-9386-ae9300d7cd21 3223        1328       29.37 2023-11-02 13:20:27 2023-11-02 13:20:00 2023-11-02 13:30:00 2023-11-02 13:29:59.999
    7ca2ddaa-dd5e-41dc-ac47-c9aa7477d913 3223        1402       49.78 2023-11-02 13:20:27 2023-11-02 13:20:00 2023-11-02 13:30:00 2023-11-02 13:29:59.999
    84efa0d0-7157-4cd3-a893-e7d2780cefdd 3076        1321       47.38 2023-11-02 13:20:27 2023-11-02 13:20:00 2023-11-02 13:30:00 2023-11-02 13:29:59.999
    d72a37d2-ef15-4740-8ae8-1199ddf84ea9 3211        1234       56.27 2023-11-02 13:20:27 2023-11-02 13:20:00 2023-11-02 13:30:00 2023-11-02 13:29:59.999
    4d57c754-63e1-413a-8af8-768d54d128ee 3126        1223       21.52 2023-11-02 13:20:27 2023-11-02 13:20:00 2023-11-02 13:30:00 2023-11-02 13:29:59.999
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

The following query returns all columns from the `orders` table within SESSION windows that have a 1-minute gap, partitioned by `product_id`:

    SELECT * FROM TABLE(
      SESSION(TABLE `examples`.`marketplace`.`orders` PARTITION BY product_id, DESCRIPTOR($rowtime), INTERVAL '1' MINUTES));
    
    -- or with the named params
    -- note: the DATA param must be the first
    SELECT * FROM TABLE(
        SESSION(
          DATA => TABLE `examples`.`marketplace`.`orders` PARTITION BY product_id,
          TIMECOL => DESCRIPTOR($rowtime),
          GAP => INTERVAL '1' MINUTES));

The output resembles:

    order_id                             customer_id product_id price     $rowtime                window_start         window_end           window_time
    d7ef1f9a-4f5f-406e-bbad-25db521c38bf 3068        1234       17.08     2023-11-02T19:43:58.626Z 2023-11-02 21:43:58.626 2023-11-02 21:44:58.626 2023-11-02T19:44:58.625Z
    804f0c86-a59a-4425-a293-b28bafaa9674 3071        1332       48.12     2023-11-02T19:44:00.506Z 2023-11-02 21:44:00.506 2023-11-02 21:45:00.506 2023-11-02T19:45:00.505Z
    61ea63e3-f040-4501-b78e-8db1fdcf45fc 3179        1267       12.35     2023-11-02T19:43:58.405Z 2023-11-02 21:43:58.405 2023-11-02 21:45:07.925 2023-11-02T19:45:07.924Z
    b70ba5bc-428c-41d7-b8fc-8014dd3fd429 3234        1267       40.81     2023-11-02T19:44:00.365Z 2023-11-02 21:43:58.405 2023-11-02 21:45:07.925 2023-11-02T19:45:07.924Z
    37688f8c-65ee-4e27-a567-4890e6c7663b 3179        1267       98.17     2023-11-02T19:44:07.925Z 2023-11-02 21:43:58.405 2023-11-02 21:45:07.925 2023-11-02T19:45:07.924Z
    4cfa0cc6-881a-43b3-bb34-1746c3b93094 3077        1047       16.78     2023-11-02T19:44:01.985Z 2023-11-02 21:44:01.985 2023-11-02 21:45:23.285 2023-11-02T19:45:23.284Z
    e007ce6e-5a76-4390-8fb3-50f46025b965 3095        1047       77.48     2023-11-02T19:44:11.365Z 2023-11-02 21:44:01.985 2023-11-02 21:45:23.285 2023-11-02T19:45:23.284Z
    487a0248-a534-489e-bbc5-733e87d19cc7 3200        1047       47.86     2023-11-02T19:44:23.285Z 2023-11-02 21:44:01.985 2023-11-02 21:45:23.285 2023-11-02T19:45:23.284Z
    4dd1ab51-8ca4-4de6-9f79-bb2ad7ab2498 3043        1235       36.5      2023-11-02T19:43:57.785Z 2023-11-02 21:43:57.785 2023-11-02 21:45:24.625 2023-11-02T19:45:24.624Z
    bb524ec6-1b21-40f1-8c54-3aac7b454c5b 3232        1235       36.98     2023-11-02T19:44:07.265Z 2023-11-02 21:43:57.785 2023-11-02 21:45:24.625 2023-11-02T19:45:24.624Z
    9c218c8a-1566-4982-9640-a0deb9ac203c 3065        1235       30.17     2023-11-02T19:44:16.966Z 2023-11-02 21:43:57.785 2023-11-02 21:45:24.625 2023-11-02T19:45:24.624Z
    6623c41b-04fa-4df0-a312-45b6dfcdc639 3143        1235       12.2      2023-11-02T19:44:24.625Z 2023-11-02 21:43:57.785 2023-11-02 21:45:24.625 2023-11-02T19:45:24.624Z

The following query computes the sum of the `price` column in the `orders` table within SESSION windows that have a 5-minute gap.

    SELECT window_start, window_end, customer_id, SUM(price) as `sum`
      FROM TABLE(
        SESSION(TABLE `examples`.`marketplace`.`orders` PARTITION BY customer_id, DESCRIPTOR($rowtime), INTERVAL '1' MINUTES))
      GROUP BY window_start, window_end, customer_id;

The output resembles:

    window_start        window_end          sum
    2023-11-02 12:40:00 2023-11-02 12:46:00 327376.23
    2023-11-02 12:40:00 2023-11-02 12:48:00 661272.70
    2023-11-02 12:40:00 2023-11-02 12:50:00 989294.13
    2023-11-02 12:50:00 2023-11-02 12:52:00 1316596.58
    2023-11-02 12:50:00 2023-11-02 12:54:00 1648097.20
    2023-11-02 12:50:00 2023-11-02 12:56:00 1977881.53
    2023-11-02 12:50:00 2023-11-02 12:58:00 2304080.32
    2023-11-02 12:50:00 2023-11-02 13:00:00 2636795.56

## Window Offset¶

`Offset` is an optional parameter that you can use to change the window assignment. It can be a positive duration or a negative duration. The default value for a window offset is 0. The same record may be assigned to a different window if set to a different offset value.

For example, which window would a record be assigned to if it has a timestamp of `2021-06-30 00:00:00`, for a Tumble window with 10 MINUTE as size?

  * If the `offset` is `-16 MINUTE`, the record assigns to window [`2021-06-29 23:44:00`, `2021-06-29 23:54:00`].
  * If the `offset` is `-6 MINUTE`, the record assigns to window [`2021-06-29 23:54:00`, `2021-06-30 00:04:00`].
  * If the `offset` is `-4 MINUTE`, the record assigns to window [`2021-06-29 23:56:00`, `2021-06-30 00:06:00`].
  * If the `offset` is `0`, the record assigns to window [`2021-06-30 00:00:00`, `2021-06-30 00:10:00`].
  * If the `offset` is `4 MINUTE`, the record assigns to window [`2021-06-30 00:04:00`, `2021-06-30 00:14:00`].
  * If the `offset` is `6 MINUTE`, the record assigns to window [`2021-06-30 00:06:00`, `2021-06-30 00:16:00`].
  * If the `offset` is `16 MINUTE`, the record assigns to window [`2021-06-30 00:16:00`, `2021-06-30 00:26:00`].

Note

The effect of window offset is only for updating window assignment. It has no effect on Watermark.

### Examples¶

The following SQL examples show how to use `offset` in a tumbling window.

    SELECT * FROM TABLE(
       TUMBLE(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '10' MINUTES, INTERVAL '1' MINUTES));
    
    -- or with the named params
    -- note: the DATA param must be the first
    SELECT * FROM TABLE(
       TUMBLE(
         DATA => TABLE `examples`.`marketplace`.`orders`,
         TIMECOL => DESCRIPTOR($rowtime),
         SIZE => INTERVAL '10' MINUTES,
         OFFSET => INTERVAL '1' MINUTES));

The output resembles:

    order_id                             customer_id product_id price $rowtime            window_start        window_end          window_time
    0932497b-a3c2-4f80-9b1f-9d099b091696 3063        1035       75.85 2023-11-02 19:29:51 2023-11-02 19:21:00 2023-11-02 19:31:00 2023-11-02 19:30:59.999
    20f4529c-9c86-4a54-8c38-f6c3caa1d7b8 3131        1207       89.00 2023-11-02 19:29:51 2023-11-02 19:21:00 2023-11-02 19:31:00 2023-11-02 19:30:59.999
    cbda6c08-e0c7-41cb-ae04-c50f5b1f5e3c 3074        1312       63.71 2023-11-02 19:29:51 2023-11-02 19:21:00 2023-11-02 19:31:00 2023-11-02 19:30:59.999
    d049ed28-cbbb-479b-8df6-8c637c1b68f5 3006        1201       72.14 2023-11-02 19:29:51 2023-11-02 19:21:00 2023-11-02 19:31:00 2023-11-02 19:30:59.999
    63b6f2ef-c0e9-4737-ab81-f5acb93e4a64 3182        1346       76.18 2023-11-02 19:29:51 2023-11-02 19:21:00 2023-11-02 19:31:00 2023-11-02 19:30:59.999
    00c088db-9cb7-4128-a4fd-4e06c0e95f7a 3198        1166       63.49 2023-11-02 19:29:51 2023-11-02 19:21:00 2023-11-02 19:31:00 2023-11-02 19:30:59.999
    b9ca292e-635a-4ef7-a6ee-bcf099df7c1b 3236        1462       69.13 2023-11-02 19:29:51 2023-11-02 19:21:00 2023-11-02 19:31:00 2023-11-02 19:30:59.999
    3299fd08-264e-4e49-8bb9-82cae18c5d7c 3058        1226       59.53 2023-11-02 19:29:51 2023-11-02 19:21:00 2023-11-02 19:31:00 2023-11-02 19:30:59.999
    45878388-7cb3-409d-91a4-8ef1f02c8576 3028        1228       16.63 2023-11-02 19:29:51 2023-11-02 19:21:00 2023-11-02 19:31:00 2023-11-02 19:30:59.999
    c2fef024-c0c2-4c0f-9880-bc423d1c2db6 3219        1071       80.66 2023-11-02 19:29:51 2023-11-02 19:21:00 2023-11-02 19:31:00 2023-11-02 19:30:59.999

The following query computes the sum of the `price` column in the `orders` table within 10-minute tumbling windows that have an offset of 1 minute.

    -- apply aggregation on the tumbling windowed table
    SELECT window_start, window_end, SUM(price) as `sum`
      FROM TABLE(
        TUMBLE(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '10' MINUTES, INTERVAL '1' MINUTES))
      GROUP BY window_start, window_end;

The output resembles:

    window_start        window_end          sum
    2023-11-02 19:21:00 2023-11-02 19:31:00 7285.64
    2023-11-02 19:22:00 2023-11-02 19:32:00 6932.18
    2023-11-02 19:23:00 2023-11-02 19:33:00 7104.53
    2023-11-02 19:24:00 2023-11-02 19:34:00 7456.92
    2023-11-02 19:25:00 2023-11-02 19:35:00 7198.75
    2023-11-02 19:26:00 2023-11-02 19:36:00 6875.39
    2023-11-02 19:27:00 2023-11-02 19:37:00 7312.87
    2023-11-02 19:28:00 2023-11-02 19:38:00 7089.26
    2023-11-02 19:29:00 2023-11-02 19:39:00 7401.58
    2023-11-02 19:30:00 2023-11-02 19:40:00 7156.43

## Related content¶

  * Course: [Window Aggregations](https://developer.confluent.io/courses/flink-sql/window-aggregations/)
  * Confluent Developer: [How to create cumulating windows](https://developer.confluent.io/tutorials/create-cumulating-windows/flinksql.html)
  * [Top-N Queries](topn.html#flink-sql-top-n)
  * [Window Top-N Queries](window-topn.html#flink-sql-window-top-n)

Note

This website includes content developed at the [Apache Software Foundation](https://www.apache.org/) under the terms of the [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0.html).
