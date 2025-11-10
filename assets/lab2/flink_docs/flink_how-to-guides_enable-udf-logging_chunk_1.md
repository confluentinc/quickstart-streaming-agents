---
document_id: flink_how-to-guides_enable-udf-logging_chunk_1
source_file: flink_how-to-guides_enable-udf-logging.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/enable-udf-logging.html
title: Enable Logging in a User Defined Function with Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 3
---

# Enable Logging in a User Defined Function for Confluent Cloud for Apache Flink¶

Note

User-Defined Function (UDF) logging support is an Early Access Program feature in Confluent Cloud. This feature should be used only for evaluation and non-production testing purposes or to provide feedback to Confluent, particularly as it becomes more widely available in follow-on preview editions. To participate in this Early Access Program, contact your Confluent account manager.

Early Access Program features are intended for evaluation use in development and testing environments only, and not for production use. Early Access Program features are provided: (a) without support; (b) “AS IS”; and (c) without indemnification, warranty, or condition of any kind. No service level commitment will apply to Early Access Program features. Early Access Program features are considered to be a Proof of Concept as defined in the Confluent Cloud Terms of Service. Confluent may discontinue providing preview releases of the Early Access Program features at any time in Confluent’s sole discretion.

When you create a user defined function (UDF) with Confluent Cloud for Apache Flink®, you have the option of enabling logging to an Apache Kafka® topic to help with monitoring and debugging.

In this topic, you perform the following steps.

* Step 1: Enable the UDF log for an environment and region
* Step 2: Implement logging code
* View logged events
* Manage your UDF logs

For more information on creating UDFs, see [Create a User Defined Function](create-udf.html#flink-sql-create-udf).

## Limitations¶

For limitations related to logs, see [UDF logging limitations](../concepts/user-defined-functions.html#flink-sql-udfs-logging-limitations).

## Prerequisites¶

You need the following prerequisites to use Confluent Cloud for Apache Flink.

* Access to Confluent Cloud.

* The organization ID, environment ID, and compute pool ID for your organization.

* The OrganizationAdmin, EnvironmentAdmin, or FlinkAdmin role for creating compute pools, or the FlinkDeveloper role if you already have a compute pool. If you don’t have the appropriate role, reach out to your OrganizationAdmin or EnvironmentAdmin.

* The Confluent CLI. To use the Flink SQL shell, update to the latest version of the Confluent CLI by running the following command:

        confluent update --yes

If you used homebrew to install the Confluent CLI, update the CLI by using the `brew upgrade` command, instead of `confluent update`.

For more information, see [Confluent CLI](https://docs.confluent.io/confluent-cli/current/overview.html).

* A provisioned Flink compute pool in Confluent Cloud.

* Apache Maven software project management tool (see [Installing Apache Maven](https://maven.apache.org/install.html))

* Java 11 to Java 17

* Sufficient permissions to upload and invoke UDFs in Confluent Cloud. For more information, see [Flink RBAC](../operate-and-deploy/flink-rbac.html#flink-rbac).

* Sufficient permissions to enable UDF logging. For more information, see [RBAC for UDF Logging](../operate-and-deploy/flink-rbac.html#flink-rbac-udf-logging).

* Flink versions 1.18.x and 1.19.x of `flink-table-api-java` are supported.

* Confluent CLI version 4.13.0 or later

* A Kafka topic that receives the log output
