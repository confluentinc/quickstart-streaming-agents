---
document_id: flink_reference_queries_window-tvf_chunk_6
source_file: flink_reference_queries_window-tvf.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/window-tvf.html
title: SQL Windowing Table-Valued Functions in Confluent Cloud for Apache Flink
chunk_index: 6
total_chunks: 7
---

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
