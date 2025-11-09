---
document_id: flink_reference_functions_table-api-functions_chunk_2
source_file: flink_reference_functions_table-api-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/table-api-functions.html
title: Table API functions in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 4
---

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
