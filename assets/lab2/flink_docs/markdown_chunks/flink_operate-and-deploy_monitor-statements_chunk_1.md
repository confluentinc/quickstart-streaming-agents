---
document_id: flink_operate-and-deploy_monitor-statements_chunk_1
source_file: flink_operate-and-deploy_monitor-statements.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/monitor-statements.html
title: Monitor and Manage Flink SQL Statements in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 3
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
