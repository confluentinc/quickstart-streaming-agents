---
document_id: flink_operate-and-deploy_monitor-statements_chunk_2
source_file: flink_operate-and-deploy_monitor-statements.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/monitor-statements.html
title: Monitor and Manage Flink SQL Statements in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 3
---

statement** , or **Delete statement**.

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
