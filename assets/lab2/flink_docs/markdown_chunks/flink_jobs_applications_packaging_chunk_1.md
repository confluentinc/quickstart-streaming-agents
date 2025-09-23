---
document_id: flink_jobs_applications_packaging_chunk_1
source_file: flink_jobs_applications_packaging.md
source_url: https://docs.confluent.io/platform/current/flink/jobs/applications/packaging.html
title: How to Package a Flink Job with Confluent Manager for Apache Flink
chunk_index: 1
total_chunks: 2
---

# How to Package a Flink Job for Confluent Manager for Apache Flink¶

This topic walks you through configuring your project for packaging with Confluent Manager for Apache Flink.

## Prerequisites¶

* Confluent Manager for Apache Flink installed using Helm. For installation instructions, see [Install Confluent Manager for Apache Flink with Helm](../../installation/helm.html#install-cmf-helm).
* A Flink project configured with Maven. For more information, see [configuration overview](https://nightlies.apache.org/flink/flink-docs-release-1.19/docs/dev/configuration/overview/) and [Maven configuration](https://nightlies.apache.org/flink/flink-docs-release-1.19/docs/dev/configuration/maven/).

## Set up the project configuration¶

The Flink [configuration overview](https://nightlies.apache.org/flink/flink-docs-release-1.19/docs/dev/configuration/overview/) provides instructions on how to configure your project. Follow the linked instructions to create a Flink project for Maven. For more on configuring your project with Maven, see [Maven configuration](https://nightlies.apache.org/flink/flink-docs-release-1.19/docs/dev/configuration/maven/).

To use the Flink dependencies that are provided as part of Confluent Platform for Apache Flink®, you need to add the Confluent Maven repository and change the Maven group ID and version for supported components in the POM file for your project.

  1. Add the Confluent Platform for Apache Flink Maven repository to the `pom.xml` file like shown in the following code:

         <repositories>
           <repository>
             <id>cp-flink-releases</id>
             <url>https://packages.confluent.io/maven</url>
             <releases>
               <enabled>true</enabled>
             </releases>
             <snapshots>
               <enabled>false</enabled>
             </snapshots>
           </repository>
         </repositories>

  2. Replace the Maven group IDs and versions.

In the `dependency` section of the `pom.xml` file, change the group ID to `io.confluent.flink` and update the version for each supported component like the following code:

         <dependency>
           <groupId>io.confluent.flink</groupId>
           <artifactId>flink-streaming-java</artifactId>
           <version>1.19.1-cp2</version>
         </dependency>

After you have changed these settings, your project will use Confluent Platform for Apache Flink.
