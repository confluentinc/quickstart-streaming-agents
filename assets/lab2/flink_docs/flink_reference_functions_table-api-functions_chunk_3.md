---
document_id: flink_reference_functions_table-api-functions_chunk_3
source_file: flink_reference_functions_table-api-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/table-api-functions.html
title: Table API functions in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 4
---

## Table interface: API extensions¶

  * [Table.addColumns(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#addColumns-org.apache.flink.table.expressions.Expression...-)
  * [Table.addOrReplaceColumns(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#addOrReplaceColumns-org.apache.flink.table.expressions.Expression...-)
  * [Table.dropColumns(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#dropColumns-org.apache.flink.table.expressions.Expression...-)
  * [Table.execute()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Executable.html#execute--)
  * [Table.explain()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Explainable.html#explain-org.apache.flink.table.api.ExplainDetail...-)
  * [Table.getResolvedSchema()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#getResolvedSchema--)
  * [Table.map(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#map-org.apache.flink.table.expressions.Expression-)
  * [Table.printExplain()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Explainable.html#printExplain-org.apache.flink.table.api.ExplainDetail...-)
  * [Table.printSchema()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#printSchema--)
  * [Table.renameColumns(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#renameColumns-org.apache.flink.table.expressions.Expression...-)

## TablePipeline interface¶

  * [TablePipeline.execute()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Executable.html#execute--)
  * [TablePipeline.explain()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Explainable.html#explain-org.apache.flink.table.api.ExplainDetail...-)
  * [TablePipeline.printExplain()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Explainable.html#printExplain-org.apache.flink.table.api.ExplainDetail...-)

## StatementSet interface¶

  * [StatementSet.add(TablePipeline)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/StatementSet.html#add-org.apache.flink.table.api.TablePipeline-)
  * [StatementSet.addInsert(String, Table)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/StatementSet.html#addInsert-java.lang.String-org.apache.flink.table.api.Table-)
  * [StatementSet.addInsertSql(String)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/StatementSet.html#addInsertSql-java.lang.String-)
  * [StatementSet.execute()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Executable.html#execute--)
  * [StatementSet.explain()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Explainable.html#explain-org.apache.flink.table.api.ExplainDetail...-)

## TableResult interface¶

  * [TableResult.await(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableResult.html#await--)
  * [TableResult.collect()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableResult.html#collect--)
  * [TableResult.getJobClient().cancel()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableResult.html#getJobClient--)
  * [TableResult.getResolvedSchema()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableResult.html#getResolvedSchema--)
  * [TableResult.print()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableResult.html#print--)

## TableConfig class¶

  * [TableConfig.set(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableConfig.html#set-org.apache.flink.configuration.ConfigOption-T-)

## Expressions class¶

  * [Expressions.*](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Expressions.html) (except for `call()`)
