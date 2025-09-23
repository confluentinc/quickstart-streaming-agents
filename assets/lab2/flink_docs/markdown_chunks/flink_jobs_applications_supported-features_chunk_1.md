---
document_id: flink_jobs_applications_supported-features_chunk_1
source_file: flink_jobs_applications_supported-features.md
source_url: https://docs.confluent.io/platform/current/flink/jobs/applications/supported-features.html
title: Confluent Platform for Apache Flink Features and Support
chunk_index: 1
total_chunks: 1
---

# Confluent Platform for Apache Flink Features and Support¶

Confluent Platform for Apache Flink® is compatible with Apache Flink. The following sections list all components that are supported by Confluent. Only configurations related to the listed components are supported. Other configurations or custom configurations are not supported.

For requirement and compatibility details, see [Confluent Platform for Apache Flink](../../../installation/versions-interoperability.html#cp-af-compat).

## Core components¶

The following core components are supported with Confluent Platform for Apache Flink:

* Runtime
* REST API
* Web UI
* Flink CLI

## State backends¶

The following state backends are supported with Confluent Platform for Apache Flink:

* [RocksDB](https://github.com/facebook/rocksdb/wiki) \- recommended as the default state backend.
* Memory - recommended for small state.

## FileSystem implementations¶

The following `FileSystem` implementations are supported with Confluent Platform for Apache Flink:

* AWS S3 - includes Presto and Hadoop variants
* Azure blob storage
* Google Cloud cloud storage

## Data formats¶

The following data formats are supported with Confluent Platform for Apache Flink:

* Avro
* Avro (CSR)
* CSV
* ORC
* Parquet
* Protobuf
* JSON
* Debezium JSON
* Debezium Avro

## Flink APIs, libraries and metadata catalogs¶

The following table lists [Flink APIs](../../concepts/flink.html#af-apis) and their Confluent Platform for Apache Flink support.

Important

Confluent offers support only for the APIs, libraries and components of Flink listed on this page. Code implemented by the customer (“customer code”) and code embedded into Flink is not supported. This also includes other open-source code parts of open-source Apache Flink or other open-source projects. For example, using an open-source Flink connector is not supported by Confluent and is considered customer code.

Flink Component | Supported by Confluent | Notes
---|---|---
Flink SQL | Yes, but supported only as part of a packaged JAR application based on the `TableEnvironment` interface. | SQL Shell and SQL gateway are not currently supported.
Table API - Java | Yes | Python for this API not currently supported.
DataStream API - Java | Yes | Python for this API not currently supported.
DataSet API | No | Deprecated in Apache Flink and not supported in Confluent Platform for Apache Flink.

In addition:

* Libraries: Complex Event Processing (CEP) is the only library supported with Confluent Platform for Apache Flink, for use with SQL. PyFlink, Flink ML, Stateful Functions and Queryable State are not supported.
* Catalogs: `GenericInMemoryCatalog` and `JdbcCatalog` are supported with Confluent Platform for Apache Flink. Hive not currently supported.

Note that Confluent only offers support for the APIs, libraries and components of Flink listed on this page. Code implemented by the customer (“customer code”), also when embedded into Flink, will not be supported. This also includes other open source code part of open-source Apache Flink or other open source projects. For example using an open source Flink connector not supported by Confluent, will be considered customer code.

## Connectors¶

All Flink connectors are compatible with Confluent Platform for Apache Flink. However, professional support is limited to the connectors listed in the following table:

Connector | Supported by Confluent | Distribution channel | Notes
---|---|---|---
Kafka Source and Sink connectors | Yes | [Maven via packages.confluent.io](https://packages.confluent.io/maven/io/confluent/flink/flink-connector-kafka/) | This includes: Table API Upsert Kafka connector, Datastream API Kafka connector, and the Datastream API Dynamic Kafka connector. Java and SQL support only. Bundle with your user code JAR.
FileSystem Source and Sink | Yes | [Maven via packages.confluent.io](https://packages.confluent.io/maven/io/confluent/flink/) | Java and SQL support only. Additional support charges apply. Not bundled with the Confluent Docker image.
JDBC | Yes | [Maven via packages.confluent.io](https://packages.confluent.io/maven/io/confluent/flink/) | Java and SQL support only.
CDC Source | Yes | [Maven via packages.confluent.io](https://packages.confluent.io/maven/io/confluent/flink/) | Databases: DB2, MySQL, Oracle, Postgres, SQLServer. Java and SQL support only.
All other connectors | No | Apache Flink | No additional connectors are currently supported.

additional connectors are currently supported.

## Deployment and monitoring¶

Note the following about deploying Flink jobs with Confluent Platform for Apache Flink:

* Confluent Platform for Apache Flink supports Application Mode only.
* Confluent Platform for Apache Flink supports high-availability deployment via Kubernetes. The default mode to deploy with Kubernetes is native. This is the only Confluent-supported deployment solution for Confluent Platform for Apache Flink.
* ZooKeeper is not supported.
* The following metrics reporters are supported with Confluent Platform for Apache Flink:
  * Datadog
  * Prometheus
  * InfluxDB
  * JMX
  * Statsd
  * Graphite
