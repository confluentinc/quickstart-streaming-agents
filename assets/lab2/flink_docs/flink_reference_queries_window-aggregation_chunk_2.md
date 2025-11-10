---
document_id: flink_reference_queries_window-aggregation_chunk_2
source_file: flink_reference_queries_window-aggregation.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/window-aggregation.html
title: SQL Window Aggregation Queries in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 3
---

not supported in batch mode.

## Examples¶

The following examples show Window aggregations over [example data streams](../example-data.html#flink-sql-example-data) that you can experiment with.

Note

To show the behavior of windowing more clearly in the following examples, `TIMESTAMP(3)` values may be simplified so that trailing zeroes aren’t shown. For example, `2020-04-15 08:05:00.000` may be shown as `2020-04-15 08:05`. Columns may be hidden intentionally to enhance the readability of the content.

Here are some examples for `TUMBLE`, `HOP`, `CUMULATE` and `SESSION` window aggregations.

    DESCRIBE `examples`.`marketplace`.`orders`;

    +--------------+-----------+----------+---------------+
    | Column Name  | Data Type | Nullable |    Extras     |
    +--------------+-----------+----------+---------------+
    | order_id     | STRING    | NOT NULL |               |
    | customer_id  | INT       | NOT NULL |               |
    | product_id   | STRING    | NOT NULL |               |
    | price        | DOUBLE    | NOT NULL |               |
    +--------------+-----------+----------+---------------+

    SELECT * FROM `examples`.`marketplace`.`orders`;

    order_id                             customer_id  product_id price
    d770a538-a70c-4de6-9d06-e6c16c5bef5a 3075         1379       32.21
    787ee1f4-d0d0-4c39-bdb9-44dc2d203d55 3028         1335       34.74
    7ab7ce23-5f61-4398-afad-b1e3f548fee3 3148         1045       69.26
    6fea712c-9454-497e-8038-ebaf6dfc7a17 3247         1390       67.26
    dc9daf5e-98d5-4bcd-8839-251fed13b75e 3167         1309       12.04
    ab3151d0-2950-49cd-9783-016ccc6a3281 3105         1094       21.52
    d27ca945-3cff-48a4-afcc-7b17446aa95d 3168         1250       99.95

    -- apply aggregation on the tumbling windowed table
    SELECT window_start, window_end, SUM(price) as `sum`
      FROM TABLE(
        TUMBLE(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '10' MINUTES))
      GROUP BY window_start, window_end;

    window_start        window_end          sum
    2023-11-02 10:40:00 2023-11-02 10:50:00 258484.93
    2023-11-02 10:50:00 2023-11-02 11:00:00 287632.15
    2023-11-02 11:00:00 2023-11-02 11:10:00 271945.78
    2023-11-02 11:10:00 2023-11-02 11:20:00 315207.46
    2023-11-02 11:20:00 2023-11-02 11:30:00 342618.92
    2023-11-02 11:30:00 2023-11-02 11:40:00 329754.31

    -- apply aggregation on the hopping windowed table
    SELECT window_start, window_end, SUM(price) as `sum`
      FROM TABLE(
        HOP(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '5' MINUTES, INTERVAL '10' MINUTES))
      GROUP BY window_start, window_end;

    window_start        window_end          sum
    2023-11-02 11:10:00 2023-11-02 11:20:00 296049.38
    2023-11-02 11:15:00 2023-11-02 11:25:00 1122455.07
    2023-11-02 11:20:00 2023-11-02 11:30:00 1648270.20
    2023-11-02 11:25:00 2023-11-02 11:35:00 2143271.00
    2023-11-02 11:30:00 2023-11-02 11:40:00 2701592.45
    2023-11-02 11:35:00 2023-11-02 11:45:00 3214376.78

    -- apply aggregation on the cumulating windowed table
    SELECT window_start, window_end, SUM(price) as `sum`
      FROM TABLE(
        CUMULATE(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '2' MINUTES, INTERVAL '10' MINUTES))
      GROUP BY window_start, window_end;

    window_start            window_end              sum
    2023-11-02 12:40:00.000 2023-11-02 12:46:00.000 327376.23
    2023-11-02 12:40:00.000 2023-11-02 12:48:00.000 661272.70
    2023-11-02 12:40:00.000 2023-11-02 12:50:00.000 989294.13
    2023-11-02 12:50:00.000 2023-11-02 12:52:00.000 1316596.58
    2023-11-02 12:50:00.000 2023-11-02 12:54:00.000 1648097.20
    2023-11-02 12:50:00.000 2023-11-02 12:56:00.000 1977881.53
    2023-11-02 12:50:00.000 2023-11-02 12:58:00.000 2304080.32
    2023-11-02 12:50:00.000 2023-11-02 13:00:00.000 2636795.56

    -- apply aggregation on the session windowed table
    SELECT window_start, window_end, customer_id, SUM(price) as `sum`
      FROM TABLE(
        SESSION(TABLE `examples`.`marketplace`.`orders` PARTITION BY customer_id, DESCRIPTOR($rowtime), INTERVAL '1' MINUTES))
      GROUP BY window_start, window_end, customer_id;

    window_start        window_end          sum
    2023-11-02 12:40:00 2023-11-02 12:46:00 327376.23
    2023-11-02 12:40:00 2023-11-02 12:48:00 661272.70
    2023-11-02 12:40:00 2023-11-02 12:50:00 989294.13
    2023-11-02 12:50:00 2023-11-02 12:52:00 1316596.58
    2023-11-02 12:50:00 2023-11-02 12:54:00 1648097.20
    2023-11-02 12:50:00 2023-11-02 12:56:00 1977881.53
    2023-11-02 12:50:00 2023-11-02 12:58:00 2304080.32
    2023-11-02 12:50:00 2023-11-02 13:00:00 2636795.56
