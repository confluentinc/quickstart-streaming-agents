---
document_id: flink_reference_table-api_chunk_1
source_file: flink_reference_table-api.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/table-api.html
title: Table API on Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 5
---

# Table API on Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® supports programming applications with the Table API in Java and Python. Confluent provides a plugin for running applications that use the Table API on Confluent Cloud.

The Table API enables a programmatic way of developing, testing, and submitting Flink pipelines for processing data streams. Streams can be finite or infinite, with insert-only or changelog data. Changelog data enables handling Change Data Capture (CDC) events.

To use the Table API, you work with tables that change over time, a concept inspired by relational databases. A Table program is a declarative and structured graph of transformations. The Table API is inspired by SQL and complements it with additional tools for manipulating real-time data. You can use both Flink SQL and the Table API in your applications.

A table program has these characteristics:

* Runs in a regular `main()` method (Java)
* Uses Flink APIs
* Communicates with Confluent Cloud by using REST requests, for example, [Statements endpoint](/cloud/current/api.html#tag/Statements-\(sqlv1\)/operation/createSqlv1Statement).

For a list of Table API functions supported by Confluent Cloud for Apache Flink, see [Table API functions](functions/table-api-functions.html#flink-table-api-functions).

For a list of Table API limitations in Confluent Cloud for Apache Flink, see Known limitations.

Use the Confluent for VS Code extension to generate a new Flink Table API project that interacts with your Confluent Cloud resources. This option is ideal if you’re learning about the Table API.

For more information see [Confluent for VS Code for Confluent Cloud](../../client-apps/vs-code-extension.html#cc-vscode-extension).

Note

The Flink Table API is available for preview.

A Preview feature is a Confluent Cloud component that is being introduced to gain early feedback from developers. Preview features can be used for evaluation and non-production testing purposes or to provide feedback to Confluent. The warranty, SLA, and Support Services provisions of your agreement with Confluent do not apply to Preview features. Confluent may discontinue providing preview releases of the Preview features at any time in Confluent’s’ sole discretion.

Comments, questions, and suggestions related to the Table API are encouraged and can be submitted through the [established channels](../get-help.html#ccloud-flink-help).

## Add the Table API to an existing Java project¶

To add the Table API to an existing project, include the following dependencies in the `<dependencies>` section of your pom.xml file.

    <!-- Apache Flink dependencies -->
    <dependency>
       <groupId>org.apache.flink</groupId>
       <artifactId>flink-table-api-java</artifactId>
       <version>${flink.version}</version>
    </dependency>

    <!-- Confluent Flink Table API Java plugin -->
    <dependency>
       <groupId>io.confluent.flink</groupId>
       <artifactId>confluent-flink-table-api-java-plugin</artifactId>
       <version>${confluent-plugin.version}</version>
    </dependency>
