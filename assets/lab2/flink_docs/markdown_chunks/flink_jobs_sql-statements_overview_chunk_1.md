---
document_id: flink_jobs_sql-statements_overview_chunk_1
source_file: flink_jobs_sql-statements_overview.md
source_url: https://docs.confluent.io/platform/current/flink/jobs/sql-statements/overview.html
title: Deploy and Manage Statements in Confluent Manager for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Deploy and Manage Statements in Confluent Manager for Apache Flink¶

Statements are Confluent Manager for Apache Flink (CMF) resources that represent SQL queries, including their configuration, properties, and potential results. SQL queries must use the Flink SQL syntax. Statements are created within an [Environment](../../configure/environments.html#cmf-environments) and must be linked to a [Compute Pool](../../configure/compute-pools.html#cmf-compute-pools).

Important

Flink SQL support in is available as an open preview. A Preview feature is a feature that is being introduced to gain early feedback from developers. Preview features can be used for evaluation and non-production testing purposes or to provide feedback to Confluent. The warranty, SLA, and Support Services provisions of your agreement with Confluent do not apply to Preview features. Confluent may discontinue providing releases of Preview features at any time at Confluent’s’ sole discretion. Comments, questions, and suggestions related to preview features are encouraged and can be submitted to your account representative.

A Statement has access to all catalogs, databases, and tables that its Environment has access to. Environments can also set default Flink configuration properties, overriding those specified directly in the statement. The Compute Pool referenced by a Statement provides the specification and configuration of the Flink cluster responsible for executing the Statement’s SQL query.

There are three types of statements that are differently handled by CMF:

**Statements reading catalog metadata such as SHOW TABLES.**
     These statements are immediately executed by CMF without creating a Flink deployment. They are typically used in ad-hoc, interactive scenarios.
**Interactive SELECT statements.**
     These statements are executed on Flink clusters and collect results that can be retrieved from CMF via the Statement Results endpoint. SELECT statements are typically used in ad-hoc, interactive scenarios to explore data or develop production statements.
**Detached INSERT INTO statements.**
     These statements are executed on Flink clusters and write results into a table (backed by a Kafka topic). INSERT INTO statements are typically used to deploy data pipeline jobs in production scenarios.

See the following topics to learn more about working with Statements:

  * [Create Statements](create-statements.html#flink-sql-statements-create)
  * [Manage Statements](manage-statements.html#flink-sql-statements-manage)
  * [Use the Interactive CLI SQL Shell](use-interactive-shell.html#flink-sql-statements-interactive-cli)
  * [Features & Support](features-support.html#flink-sql-features-support)
