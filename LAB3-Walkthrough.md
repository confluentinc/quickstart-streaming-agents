# Lab3: Anomaly Detection Walkthrough

In this lab, we show how to use the built-in Flink AI function, `ML_DETECT_ANOMALIES` to quickly identify unexpected surges or variances in real-time data streams. A common design pattern is for organizations to use anomaly detection  as a trigger that kicks off a streaming agent, enabling it to take action given some change in the data.

Read the [blog post](https://docs.confluent.io/cloud/current/ai/builtin-functions/detect-anomalies.html) and view the [documentation](https://docs.confluent.io/cloud/current/flink/reference/functions/model-inference-functions.html#flink-sql-ml-anomaly-detect-function) for more details about how it works..

```sql
CREATE TABLE `ride_requests` (
  `request_id` VARCHAR(2147483647) NOT NULL,
  `customer_email` VARCHAR(2147483647) NOT NULL,
  `pickup_zone` VARCHAR(2147483647) NOT NULL,
  `drop_off_zone` VARCHAR(2147483647) NOT NULL,
  `price` DOUBLE NOT NULL,
  `number_of_passengers` INT NOT NULL,
  `request_ts` TIMESTAMP(3) WITH LOCAL TIME ZONE NOT NULL,
  WATERMARK FOR `request_ts` AS `request_ts` - INTERVAL '5' SECOND
);
```

## Prerequisites

- Run `uv run deploy` to deploy Lab3 (see [main README](./README.md))

## Generate Data

To begin generating data in real-time, make sure Docker Desktop is running, then execute the following command to begin generating data:
```sh
uv run deploy lab3_datagen
```

Running this command populates two tables with real-time data:
- `ride_requests` - Boat rideshare request stream. Includes 24 hours of historical data as well as new orders continuously streaming in.
- `vessel_catalog` - inventory of boats in the New Orleans area, including their availability to pick up riders, capacity, and current location.

## Detect Anomalies with `ML_DETECT_ANOMALIES`

First, run the following command:

```sql
ALTER TABLE ride_requests
MODIFY (WATERMARK FOR request_ts AS request_ts - INTERVAL '5' SECOND);
```

Then:

```sql
CREATE TABLE anomalies_detected_per_zone AS
WITH windowed_traffic AS (
    SELECT 
        window_start,
        window_end,
        window_time,
        pickup_zone,
        COUNT(*) AS request_count,
        SUM(number_of_passengers) AS total_passengers,
        SUM(CAST(price AS DECIMAL(10, 2))) AS total_revenue
    FROM TABLE(
        TUMBLE(TABLE ride_requests, DESCRIPTOR(request_ts), INTERVAL '5' MINUTE)
    )
    GROUP BY window_start, window_end, window_time, pickup_zone
),
anomaly_detection AS (
    SELECT 
        pickup_zone,
        window_time,
        request_count,
        total_passengers,
        total_revenue,
        ML_DETECT_ANOMALIES(
            CAST(request_count AS DOUBLE),
            window_time,
            JSON_OBJECT(
                'minTrainingSize' VALUE 287,
                'maxTrainingSize' VALUE 7000,
                'confidencePercentage' VALUE 99.0,
                'enableStl' VALUE FALSE           
            )
        ) OVER (
            PARTITION BY pickup_zone
            ORDER BY window_time 
            RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS anomaly_result
    FROM windowed_traffic
)
SELECT 
    pickup_zone,
    window_time,
    request_count,
    total_passengers,
    total_revenue,
    CAST(ROUND(anomaly_result.forecast_value) AS BIGINT) AS expected_requests,
    anomaly_result.upper_bound AS upper_bound,
    anomaly_result.lower_bound AS lower_bound,
    anomaly_result.is_anomaly AS is_surge
FROM anomaly_detection
WHERE anomaly_result.is_anomaly = true 
  AND request_count > anomaly_result.upper_bound;
```

Remember to keep the data generation you started with `uv run lab3_datagen` going. Then, to view detected anomalies, simply run:

```sql
SELECT * FROM `anomalies_detected_per_zone
```