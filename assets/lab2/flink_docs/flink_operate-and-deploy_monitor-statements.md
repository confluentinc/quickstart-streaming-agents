---
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/monitor-statements.html
title: Monitor and Manage Flink SQL Statements in Confluent Cloud for Apache Flink
hierarchy: ['operate-and-deploy', 'monitor-statements.html']
scraped_date: 2025-09-05T13:46:49.240407
---

# Monitor and Manage Flink SQL Statements in Confluent Cloud for Apache Flink¶

You start a stream-processing app on Confluent Cloud for Apache Flink® by running a [SQL statement](../concepts/statements.html#flink-sql-statements). Once a statement is running, you can monitor its progress by using the Confluent Cloud Console. Also, you can set up integrations with monitoring services like Prometheus and Datadog.

## View and monitor statements in Cloud Console¶

Cloud Console shows details about your statements on the **Flink** page.

  1. If you don’t have running statements currently, run a SQL query like [INSERT INTO FROM SELECT](../reference/queries/insert-into-from-select.html#flink-sql-insert-into-from-select-statement) in the Flink SQL shell or in a workspace.

  2. Log in to the [Confluent Cloud Console](https://confluent.cloud/login).

  3. Navigate to the [Environments](https://confluent.cloud/environments) page.

  4. Click the tile that has the environment where your Flink compute pools are provisioned.

  5. Click **Flink** , and in the **Flink** page, click **Flink statements**.

The **Statements** list opens.

  6. You can use the **Filter** options on the page to identify the statements you want to view.

  7. The following information is available in the **Flink** statements table to help you monitor your statements.

Field | Description  
---|---  
Flink Statement Name | The name of the statement. The name is populated automatically when a statement is submitted. You can set the name by using the [SET](../reference/statements/set.html#flink-sql-set-statement) command.  
Status | The statement status Represents what is currently happening with the statement. These are the status values:
     * **Pending** : The statement has been submitted and Flink is preparing to start running the statement.
     * **Running** : Flink is actively running the statement.
     * **Completed** : The statement has completed all of its work.
     * **Deleting** : The statement is being deleted.
     * **Failed** : The statement has encountered an error and is no longer running.
     * **Degraded** : The statement appears unhealthy, for example, no transactions have been committed for a long time, or the statement has frequently restarted recently.
     * **Stopping** : The statement is about to be stopped.
     * **Stopped** : The statement has been stopped and is no longer running.  
Statement Type | The type of SQL function that is used in the statement.  
Created | Indicates when the statement started running. If you stop and resume the statement, the Created date shows the date when the statement was first submitted.  
Messages Behind | The [Consumer Lag](../../monitoring/monitor-lag.html#cloud-monitoring-lag) of the statement. You are also shown an indicator of whether the back pressure is increasing, decreasing, or if the back pressure is being maintained at a stable rate. Ideally, the Messages Behind metric should be as close to zero as possible. A low, close-to-zero consumer lag is the best indicator that your statement is running smoothly and keeping up with all of its inputs. A growing consumer lag indicates there is a problem.  
Messages in | The count of Messages in per minute which represents the rate at which records are read. You also have a watermark for the messages read. The watermark displayed in the Flink statements table is the minimum watermark from the source(s) in the query.  
Messages out | The count of Messages out per minute which represents the rate at which records are written. You also have a watermark for the messages written. The watermark displayed in the Flink statements table is the minimum watermark from the sink(s) in the query.  
Account | The name of the user account or service account the statement is running with.  
  8. When you click on a particular statement a detailed side panel opens up. The panel provides detailed information on the statement at a more granular level, showing how messages are being read from sources and written to sinks. The watermarks for each individual source and sink table are shown in this panel along with the statement’s catalog, database, local time zone, and [Scaling status](../concepts/autopilot.html#flink-sql-autopilot) .

The **SQL Content** section shows the code used to generate the statement.

The panel also contains visual interactive graphs of statement’s performance over time. There are charts for **# Messages behind** , **Messages in per minute** , and **Messages out per minute**.

## Manage statements in Cloud Console¶

Cloud Console gives you actions to manage your statements on the **Flink** page.

  1. In the statement list, click the checkbox next to one of your statements to select it.

  2. Click **Actions**.

A menu opens, showing options for managing the statement’s status. You can select **Stop statement** , **Resume statement** , or **Delete statement**.

## Flink metrics integrations¶

Confluent Cloud for Apache Flink supports metrics integrations with services like Prometheus and Datadog.

  1. If you don’t have running statements currently, run a SQL query like [INSERT INTO FROM SELECT](../reference/queries/insert-into-from-select.html#flink-sql-insert-into-from-select-statement) in the Flink SQL shell or in a workspace.

  2. Log in to the [Confluent Cloud Console](https://confluent.cloud/login).

  3. Open the Administration menu ([](../../_images/ccloud-admin-menu-icon.png)) and select **Metrics** to open the **Metrics integration** page.

  4. In the **Explore available metrics** section, click the **Metric** dropdown.

  5. Scroll until you find the **Flink compute pool** and **Flink statement** metrics, for example, **Messages behind**. This list doesn’t include all available metrics. For a full list of available metrics, see [Metrics API Reference](https://api.telemetry.confluent.cloud/docs/descriptors/datasets/cloud).

  6. Click the **Resource** dropdown and select the corresponding compute pool or statement that you want to monitor.

A graph showing the most recent data for your selected Flink metric displays.

  7. Click **New integration** to export your metrics to a monitoring service. For more information, see [Integrate with third-party monitoring](../../monitoring/metrics-api.html#ccloud-integrate-with-3rd-party-monitoring).

## Error handling and recovery¶

Confluent Cloud for Apache Flink classifies exceptions that occur during the runtime of a statement into two categories: `USER` and `SYSTEM` exceptions.

  * **USER:** Exceptions are classified as `USER` if they fall into the user’s responsibility. Examples includes deserialization or arithmetic exceptions. Usually, the root cause is related to the data or the query. `USER` exceptions are forwarded to the user via the `Statement.status.statusDetails`.
  * **SYSTEM:** Exceptions are classified as `SYSTEM` if they fall into Confluent’s responsibility. Examples include exceptions during checkpointing or networking. Usually, the root cause is related to the infrastructure.

Furthermore, Confluent Cloud for Apache Flink classifies exceptions as “recoverable” (or “transient”) or “non-recoverable” (or “permanent”). `SYSTEM` exceptions are always classified as recoverable. Usually, `USER` exceptions are classified as non-recoverable. For example, a division-by-zero or a deserialization exception can’t be solved by restarting the underlying Flink job, because the same input message is replayed and leads to the same exception again.

Some `USER` exceptions are classified as recoverable, for example, the deletion of a statement’s input or output topic, or the deletion of the access rights to these topics.

If a non-recoverable exception occurs, the Flink statement moves into the `FAILED` state, and the underlying Flink job is cancelled. `FAILED` statements do not consume any CFUs. `FAILED` statements can be resumed, like `STOPPED` statements with exactly-once semantics, but in most cases, some change to the query or data is required so that the statement doesn’t transition immediately into the `FAILED` state again. For more information on the available options for evolving statements, see [Schema and Statement Evolution](../concepts/schema-statement-evolution.html#flink-sql-schema-and-statement-evolution).

Note

Confluent is actively working on additional options for handling non-recoverable exceptions, like skipping the offending message or sending it to a dead-letter-queue automatically. If you’re interested in providing feedback or feature requests, contact [Support](https://support.confluent.io/) or your account manager.

### Degraded statements¶

If a recoverable exception occurs, then the statement stays in the `RUNNING` state and the underlying Flink job is restarted. If the job is restarted repeatedly or has not recovered within 120 minutes (2 hours), the statement moves to the `DEGRADED` state. `DEGRADED` statements will continue to consume CFUs.

If the `DEGRADED` state is caused by a `USER` exception, then the error message is shown in `Statement.status.statusDetails`.

If no exception is shown in the `Statement.status.statusDetails`, then the `DEGRADED` state is caused by a `SYSTEM` exception. In this case, contact [Support](https://support.confluent.io/).

### Custom error handling rules¶

Confluent Cloud for Apache Flink supports custom error handling for deserialization errors using the [error-handling.mode](../reference/statements/create-table.html#flink-sql-create-table-with-error-handling-mode) table property. You can choose to fail, ignore, or log problematic records to a Dead Letter Queue (DLQ). When set to `log`, errors are sent to a DLQ table.

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

## Related content¶

  * Video: [How to work with a paused stream](https://www.youtube.com/watch?v=x_J2vdLCRuo)
  * [Statements](../concepts/statements.html#flink-sql-statements)
  * [Queries](../reference/queries/overview.html#flink-sql-queries)
  * [Flink SQL Shell Quick Start](../get-started/quick-start-shell.html#flink-sql-quick-start-shell)
  * [Flink SQL Shell](../reference/flink-sql-cli.html#flink-sql-confluent-cli)

Note

This website includes content developed at the [Apache Software Foundation](https://www.apache.org/) under the terms of the [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0.html).
