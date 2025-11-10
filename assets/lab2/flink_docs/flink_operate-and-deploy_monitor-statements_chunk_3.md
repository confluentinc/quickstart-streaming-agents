---
document_id: flink_operate-and-deploy_monitor-statements_chunk_3
source_file: flink_operate-and-deploy_monitor-statements.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/monitor-statements.html
title: Monitor and Manage Flink SQL Statements in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 3
---

sent to a DLQ table.

## Notifications¶

Confluent Cloud for Apache Flink integrates with [Notifications for Confluent Cloud](../../monitoring/configure-notifications.html#ccloud-notifications). The following notifications are available for Flink statements. They apply only to background Data Manipulation Language (DML) statements like INSERT INTO, EXECUTE STATEMENT SET, or CREATE TABLE AS.

* **Statement failure** : This notification is triggered when a statement transitions from `RUNNING` to `FAILED`. A statement transitions to `FAILED` on exceptions that Confluent classifies as `USER`, as opposed to `SYSTEM` exceptions.
* **Statement degraded** : This notification triggered when a statement transitions from `RUNNING` to `DEGRADED`.
* **Statement stuck in pending** : This notification is triggered when a newly submitted statement stays in `PENDING` for a long time. The time period for a statement to be considered stuck in the `PENDING` state depends on the cloud provider that’s running your Flink statements:
  * AWS: 10 minutes
  * Azure: 30 minutes
  * Google Cloud: 10 minutes
* **Statement auto-stopped** : This notification is triggered when a statement moves into `STOPPED` because the compute pool it is using was deleted by a user.

## Best practices for alerting¶

Use the [Metrics API](../../monitoring/metrics-api.html#metrics-api) and [Notifications for Confluent Cloud](../../monitoring/configure-notifications.html#ccloud-notifications) to monitor your compute pools and statements over time. You should monitor and configure alerts for the following conditions:

* Per compute pool

  * Alert on exhausted compute pools by comparing the current CFUs (`io.confluent.flink/compute_pool_utilization/current_cfus`) to the maximum CFUs of the pool (`io.confluent.flink/compute_pool_utilization/cfu_limit`).
  * **Flink statement stuck in pending** notifications also indicate compute-pool exhaustion.
* Per statement

  * Alert on statement failures (see Notifications)
  * Alert on Statement degradation (see Notifications)
  * Alert on a increase of “Messages Behind”/”Consumer Lag” (metric name: `io.confluent.flink/pending_records`) over an extended period of time, for example > 10 minutes; your mileage may vary. Note that Confluent Cloud for Apache Flink does not appear as a consumer in the regular consumer lag monitoring feature in Confluent Cloud, because it uses the `assign()` method.
  * (Optional) Alert on an increase of the difference between the output (`io.confluent.flink/current_output_watermark_ms`) and input watermark (`io.confluent.flink/current_input_watermark_ms`). The input watermark corresponds to the time up to which the input data is complete, and the output watermark corresponds to the time up to which the output data is complete. This difference can be considered as a measure of the amount of data that’s currently “in-flight”. Depending on the logic of the statement, different patterns are expected. For example, for a tumbling event-time window, expect an increasing difference until the window is fired, at which point the difference drops to zero and starts increasing again.

## Statement logging¶

Confluent Cloud for Apache Flink supports event logging for statements in Confluent Cloud Console.

The following screenshot shows the event log for a statement that failed due to a division by zero error. The event log is available in the **Logs** tab of the statement details page.

[](../../_images/flink-statement-logging-page-showing-error.png)

The statement event log page provides logs for the following events:

* Changes of lifecycle, for example, **PENDING** or **RUNNING**. For more information, see [Statement lifecycle](../concepts/statements.html#flink-sql-statements-lifecycle).
* Scaling status changes, for example, **OK** or **Pending Scale Up**. For more information, see [Scaling status](../concepts/autopilot.html#flink-sql-autopilot).
* Errors and warnings.

The Cloud Console enables the following operations:

* **Search** : Search for specific log messages. Wildcards are supported.
* **Time range** : Select the time range for the log events.
* **Log level** : Filter logs events by severity: Error, Warning, Info.
* **Chart** : View the log events in a chart.
* **Download** : Download log events as a CSV or JSON file.
