---
document_id: flink_reference_queries_window-tvf_chunk_2
source_file: flink_reference_queries_window-tvf.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/window-tvf.html
title: SQL Windowing Table-Valued Functions in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 7
---

units are not currently supported.

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
    4d57c754-63e1-413a-8af8-768d54d128ee 3126
