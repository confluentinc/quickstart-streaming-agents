---
document_id: flink_reference_functions_datetime-functions_chunk_1
source_file: flink_reference_functions_datetime-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/datetime-functions.html
title: SQL Datetime Functions in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 6
---

# Datetime Functions in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides these built-in functions for handling date and time logic in SQL queries:

Date | Time | Timestamp | Utility
---|---|---|---
CURRENT_DATE | CONVERT_TZ | CURRENT_TIMESTAMP | CEIL
DATE_FORMAT | CURRENT_TIME | CURRENT_ROW_TIMESTAMP | CURRENT_WATERMARK
DATE | HOUR | LOCALTIMESTAMP | EXTRACT
DAYOFMONTH | LOCALTIME | TIMESTAMP | FLOOR
DAYOFWEEK | MINUTE | TO_TIMESTAMP | FROM_UNIXTIME
DAYOFYEAR | NOW | TO_TIMESTAMP_LTZ | INTERVAL
MONTH | SECOND | TIMESTAMPADD | SOURCE_WATERMARK
QUARTER | TIME | TIMESTAMPDIFF | OVERLAPS
TO_DATE |  | UNIX_TIMESTAMP |
WEEK |  | UNIX_TIMESTAMP |
YEAR |  |  |
