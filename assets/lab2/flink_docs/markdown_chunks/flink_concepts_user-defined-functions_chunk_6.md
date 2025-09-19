---
document_id: flink_concepts_user-defined-functions_chunk_6
source_file: flink_concepts_user-defined-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/user-defined-functions.html
title: User-defined Functions in Confluent Cloud for Apache Flink
chunk_index: 6
total_chunks: 6
---

LOCALTIME * LOCALTIMESTAMP * NOW

## UDF regional availability¶

Flink UDFs are available in the following AWS regions.

  * ap-east-1
  * ap-northeast-2
  * ap-south-1
  * ap-southeast-1
  * ap-southeast-2
  * ca-central-1
  * eu-central-1
  * eu-central-2
  * eu-north-1
  * eu-west-1
  * eu-west-2
  * me-south-1
  * sa-east-1
  * us-east-1
  * us-east-2
  * us-west-2

Flink UDFs are available in the following Azure regions.

  * australiaeast
  * brazilsouth
  * centralindia
  * centralus
  * eastus
  * eastus2
  * francecentral
  * northeurope
  * southcentralus
  * southeastasia
  * spaincentral
  * uaenorth
  * uksouth
  * westeurope
  * westus2
  * westus3

## UDF limitations¶

User-defined functions have the following limitations.

  * Confluent CLI version 4.13.0 or later is required.
  * External network calls from UDFs are not supported.
  * JDK 17 is the latest supported Java version for uploaded JAR files.
  * Each Flink statement can have no more than 10 UDFs.
  * Each organization/cloud/region/environment can have no more than 100 Flink artifacts.
  * The size limit of each artifact is 100 MB.
  * Aggregates are not supported.
  * Table aggregates are not supported.
  * Temporary functions are not supported.
  * The ALTER FUNCTION statement is not supported.
  * UDFs can’t be used in combination with [MATCH_RECOGNIZE](../reference/queries/match_recognize.html#flink-sql-pattern-recognition).
  * Vararg functions are not supported.
  * User-defined structured types are not supported.
  * Python is not supported.
  * Both inputs and outputs of the UDF have a row-size limit of 4MB.
  * Custom type inference is not supported.
  * Constant expression reduction is not supported.
  * The UDF feature is optimized for streaming processing, so the initial query may be slow, but after the initial query, a UDF runs with low latency.

### File system access limitations¶

The file system is read-only in the runtime environment. UDFs can’t create, write, or modify files on the file system. This includes temporary files, model files, or any other file operations. Libraries that require file system write access, like those using JNI/native binaries that extract files from JARs, are not supported.

### JNI and native binary limitations¶

Libraries that use Java Native Interface (JNI) or require native binaries are not supported due to filesystem restrictions and potential architecture compatibility issues.

## UDF logging limitations¶

  * **Public Kafka destinations only:** Private networked cluster types aren’t supported as logging destinations.
  * **Log4j logging only:** External UDF loggers can be composed only with the Apache Log4j logging framework.
  * **Burst rate to 1000/s** : UDF logging supports up to 1000 log events per second for each UDF during a short burst of high activity. This helps to optimize performance and to reduce noise in logs. Events that exceed the maximum rate are dropped.
