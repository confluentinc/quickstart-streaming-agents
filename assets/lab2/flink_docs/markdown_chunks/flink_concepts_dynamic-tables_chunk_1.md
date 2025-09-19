---
document_id: flink_concepts_dynamic-tables_chunk_1
source_file: flink_concepts_dynamic-tables.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/dynamic-tables.html
title: Tables and Topics in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 2
---

# Tables and Topics in Confluent Cloud for Apache Flink¶

Apache Flink® and the Table API use the concept of dynamic tables to facilitate the manipulation and processing of streaming data. Dynamic tables represent an abstraction for working with both batch and streaming data in a unified manner, offering a flexible and expressive way to define, modify, and query structured data. In contrast to the static tables that represent batch data, dynamic tables change over time. But like static batch tables, systems can execute queries over dynamic tables.

Confluent Cloud for Apache Flink® implements ANSI-Standard SQL and has the familiar concepts of catalogs, databases, and tables. Confluent Cloud maps a Flink catalog to an environment and _vice-versa_. Similarly, Flink databases and tables are mapped to Apache Kafka® clusters and topics. For more information, see [Metadata mapping between Kafka cluster, topics, schemas, and Flink](../overview.html#ccloud-flink-overview-metadata-mapping).
