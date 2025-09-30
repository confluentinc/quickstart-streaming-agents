---
document_id: flink_reference_functions_model-inference-functions_chunk_2
source_file: flink_reference_functions_model-inference-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/model-inference-functions.html
title: AI Model Inference and Machine Learning Functions in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 8
---

60, 'max_parallelism', 20, 'retry_count', 5]));

## ML_DETECT_ANOMALIES¶

Identify outliers in a data stream.

Syntax

    ML_DETECT_ANOMALIES(
     data_column,
     timestamp_column,
     JSON_OBJECT('p' VALUE 1, 'q' VALUE 1, 'd' VALUE 1, 'minTrainingSize' VALUE 10));

Description

The ML_DETECT_ANOMALIES function uses an [ARIMA model](../../../ai/builtin-functions/detect-anomalies.html#flink-sql-detect-anomalies-arima-model) to identify outliers in time-series data.

Your data must include:

  * A timestamp column.
  * A target column representing some quantity of interest at each timestamp.

For more information, see [Detect Anomalies in Data](../../../ai/builtin-functions/detect-anomalies.html#flink-sql-detect-anomalies).

Parameters
    For anomaly detection parameters, see [ARIMA model parameters](../../../ai/builtin-functions/detect-anomalies.html#flink-sql-detect-anomalies-arima-model-parameters).
Example

    SELECT
        ML_DETECT_ANOMALIES(
         total_orderunits,
         summed_ts,
         JSON_OBJECT('p' VALUE 1, 'q' VALUE 1, 'd' VALUE 1, 'minTrainingSize' VALUE 10))
        OVER (
            ORDER BY summed_ts
            RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS anomalies
    FROM test_table;
