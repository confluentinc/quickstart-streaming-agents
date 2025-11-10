---
document_id: flink_reference_functions_table-api-functions_chunk_1
source_file: flink_reference_functions_table-api-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/table-api-functions.html
title: Table API functions in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 4
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
