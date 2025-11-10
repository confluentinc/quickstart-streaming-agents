---
document_id: flink_reference_queries_window-topn_chunk_2
source_file: flink_reference_queries_window-topn.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/window-topn.html
title: SQL Window Top-N Queries in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 2
---

optimizer can’t translate the query.

## Examples¶

The following examples show Window Top-N aggregations over [example data streams](../example-data.html#flink-sql-example-data) that you can experiment with.

Note

To show the behavior of windowing more clearly in the following examples, `TIMESTAMP(3)` values may be simplified so that trailing zeroes aren’t shown. For example, `2020-04-15 08:05:00.000` may be shown as `2020-04-15 08:05`. Columns may be hidden intentionally to enhance the readability of the content.

### Window Top-N follows after Window Aggregation¶

The following example shows how to calculate Top 3 customers who have the highest order value for every tumbling 10 minutes window.

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

    SELECT *
      FROM (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY window_start, window_end ORDER BY price DESC) as rownum
        FROM (
          SELECT window_start, window_end, customer_id, SUM(price) as price, COUNT(*) as cnt
          FROM TABLE(
            TUMBLE(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '10' MINUTES))
          GROUP BY window_start, window_end, customer_id
        )
      ) WHERE rownum <= 3;

    window_start      window_end       customer_id price   cnt rownum
    2023-11-02 17:50  2023-11-02 18:00 3084        1523.75 18  1
    2023-11-02 17:50  2023-11-02 18:00 3092        1487.32 15  2
    2023-11-02 17:50  2023-11-02 18:00 3082        1452.18 17  3
    2023-11-02 18:00  2023-11-02 18:10 3095        1698.50 20  1
    2023-11-02 18:00  2023-11-02 18:10 3088        1645.23 19  2
    2023-11-02 18:00  2023-11-02 18:10 3079        1589.75 16  3

### Window Top-N follows after Windowing TVF¶

The following example shows how to calculate Top 3 customers which have the highest order value for every tumbling 10 minutes window.

    SELECT *
      FROM (
        SELECT $rowtime, price, product_id, customer_id, window_start, window_end, ROW_NUMBER() OVER (PARTITION BY window_start, window_end ORDER BY price DESC) as rownum
        FROM TABLE(
                    TUMBLE(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '10' MINUTES))
      ) WHERE rownum <= 3;

    $rowtime            price product_id customer_id window_start        window_end          rownum
    2023-11-05 19:35:38 99.53 1382       3120        2023-11-05 19:30    2023-11-05 19:40    1
    2023-11-05 19:35:39 99.04 1216       3204        2023-11-05 19:30    2023-11-05 19:40    2
    2023-11-05 19:35:32 98.95 1364       3114        2023-11-05 19:30    2023-11-05 19:40    3
    2023-11-05 19:42:41 97.75 1295       3187        2023-11-05 19:40    2023-11-05 19:50    1
    2023-11-05 19:41:53 97.30 1428       3256        2023-11-05 19:40    2023-11-05 19:50    2
    2023-11-05 19:43:17 96.80 1173       3092        2023-11-05 19:40    2023-11-05 19:50    3
