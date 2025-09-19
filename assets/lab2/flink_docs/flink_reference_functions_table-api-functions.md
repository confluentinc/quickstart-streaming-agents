---
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/table-api-functions.html
title: Table API functions in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'functions', 'table-api-functions.html']
scraped_date: 2025-09-05T13:48:16.449254
---

# Table API in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® supports programming applications with the Table API. For more information, see the [Table API Overview](../table-api.html#flink-table-api). To get started with programming a streaming data application with the Table API, see the [Java Table API Quick Start](../../get-started/quick-start-java-table-api.html#flink-java-table-api-quick-start).

Confluent Cloud for Apache Flink supports the following Table API functions.

  * TableEnvironment interface
  * Table interface: SQL equivalents
  * Table interface: API extensions
  * TablePipeline interface
  * StatementSet interface
  * TableResult interface
  * TableConfig class
  * TableConfig class
  * Confluent
  * Others

## TableEnvironment interface¶

  * [TableEnvironment.createStatementSet()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableEnvironment.html#createStatementSet--)
  * [TableEnvironment.createTable(String, TableDescriptor)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableEnvironment.html#createTable-java.lang.String-org.apache.flink.table.api.TableDescriptor-)
  * [TableEnvironment.executeSql(String)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableEnvironment.html#executeSql-java.lang.String-)
  * [TableEnvironment.explainSql(String)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableEnvironment.html#explainSql-java.lang.String-org.apache.flink.table.api.ExplainDetail...-)
  * [TableEnvironment.from(String)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableEnvironment.html#from-java.lang.String-)
  * [TableEnvironment.fromValues(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableEnvironment.html#fromValues-org.apache.flink.table.types.AbstractDataType-org.apache.flink.table.expressions.Expression...-)
  * [TableEnvironment.getConfig()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableEnvironment.html#getConfig--)
  * [TableEnvironment.getCurrentCatalog()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableEnvironment.html#getCurrentCatalog--)
  * [TableEnvironment.getCurrentDatabase()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableEnvironment.html#getCurrentDatabase--)
  * [TableEnvironment.listCatalogs()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableEnvironment.html#listCatalogs--)
  * [TableEnvironment.listDatabases()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableEnvironment.html#listDatabases--)
  * [TableEnvironment.listFunctions()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableEnvironment.html#listFunctions--)
  * [TableEnvironment.listTables()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableEnvironment.html#listTables--)
  * [TableEnvironment.listTables(String, String)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableEnvironment.html#listTables-java.lang.String-java.lang.String-)
  * [TableEnvironment.listViews()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableEnvironment.html#listViews--)
  * [TableEnvironment.sqlQuery(String)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableEnvironment.html#sqlQuery-java.lang.String-)
  * [TableEnvironment.useCatalog(String)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableEnvironment.html#useCatalog-java.lang.String-)
  * [TableEnvironment.useDatabase(String)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableEnvironment.html#useDatabase-java.lang.String-)

## Table interface: SQL equivalents¶

  * [Table.as(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#as-java.lang.String-java.lang.String...-)
  * [Table.distinct()](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#distinct--)
  * [Table.executeInsert(String)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#executeInsert-java.lang.String-)
  * [Table.fetch(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#fetch-int-)
  * [Table.filter(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#filter-org.apache.flink.table.expressions.Expression-)
  * [Table.fullOuterJoin(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#fullOuterJoin-org.apache.flink.table.api.Table-org.apache.flink.table.expressions.Expression-)
  * [Table.groupBy(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#groupBy-org.apache.flink.table.expressions.Expression...-)
  * [Table.insertInto(String)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#insertInto-java.lang.String-)
  * [Table.intersect(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#intersect-org.apache.flink.table.api.Table-)
  * [Table.intersectAll(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#intersectAll-org.apache.flink.table.api.Table-)
  * [Table.join(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#join-org.apache.flink.table.api.Table-)
  * [Table.leftOuterJoin(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#leftOuterJoin-org.apache.flink.table.api.Table-)
  * [Table.limit(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#limit-int-)
  * [Table.minus(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#minus-org.apache.flink.table.api.Table-)
  * [Table.minusAll(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#minusAll-org.apache.flink.table.api.Table-)
  * [Table.offset(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#offset-int-)
  * [Table.orderBy(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#orderBy-org.apache.flink.table.expressions.Expression...-)
  * [Table.rightOuterJoin(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#rightOuterJoin-org.apache.flink.table.api.Table-org.apache.flink.table.expressions.Expression-)
  * [Table.select(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#select-org.apache.flink.table.expressions.Expression...-)
  * [Table.union(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#union-org.apache.flink.table.api.Table-)
  * [Table.unionAll(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#unionAll-org.apache.flink.table.api.Table-)
  * [Table.where(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#where-org.apache.flink.table.expressions.Expression-)
  * [Table.window(…)](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Table.html#window-org.apache.flink.table.api.GroupWindow-)

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

## Others¶

  * [FormatDescriptor.*](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/FormatDescriptor.html)
  * [TableDescriptor.*](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/TableDescriptor.html)
  * [Over.*](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Over.html)
  * [Session.*](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/gateway/service/session/Session.html)
  * [Slide.*](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Slide.html)
  * [Tumble.*](https://nightlies.apache.org/flink/flink-docs-release-1.20/api/java/org/apache/flink/table/api/Tumble.html)

## Confluent¶

Confluent adds the following classes for more convenience:

  * ConfluentSettings.*
  * ConfluentTools.*
  * ConfluentTableDescriptor.*

