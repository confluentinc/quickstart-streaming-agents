---
document_id: flink_reference_queries_window-tvf_chunk_7
source_file: flink_reference_queries_window-tvf.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/window-tvf.html
title: SQL Windowing Table-Valued Functions in Confluent Cloud for Apache Flink
chunk_index: 7
total_chunks: 7
---

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
