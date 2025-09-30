---
document_id: flink_how-to-guides_create-udf_chunk_1
source_file: flink_how-to-guides_create-udf.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/create-udf.html
title: Create a User-Defined Function with Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 7
---

# Create a User-Defined Function with Confluent Cloud for Apache Flink¶

A [user-defined function (UDF)](../concepts/user-defined-functions.html#flink-sql-udfs) extends the capabilities of Confluent Cloud for Apache Flink® and enables you to implement custom logic beyond what is supported by SQL. For example, you can implement functions like encoding and decoding a string, performing geospatial calculations, encrypting and decrypting fields, or reusing an existing library or code from a third-party supplier.

Confluent Cloud for Apache Flink supports UDFs written in Java. Package your custom function and its dependencies into a JAR file and upload it as an artifact to Confluent Cloud. Register the function in a Flink database by using the [CREATE FUNCTION](../reference/statements/create-function.html#flink-sql-create-function) statement, and invoke your UDF in Flink SQL or the [Table API](../reference/table-api.html#flink-table-api). Confluent Cloud provides the infrastructure to run your code.

For a list of cloud service providers and regions that support UDFs, see [UDF regional availability](../concepts/user-defined-functions.html#flink-sql-udfs-availability).

The following steps show how to implement a simple [user-defined scalar function](../concepts/user-defined-functions.html#flink-sql-udfs-scalar-functions), upload it to Confluent Cloud, and use it in a Flink SQL statement.

* Step 1: Build the uber jar
* Step 2: Upload the jar as a Flink artifact
* Step 3: Register the UDF
* Step 4: Use the UDF in a Flink SQL query
* Step 5: Implement UDF logging (optional)
* Step 6: Delete the UDF

After you build and run the scalar function, try building a table function.

For more code examples, see [Flink UDF Java Examples](https://github.com/confluentinc/flink-udf-java-examples).

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

* If using the Table API only, Flink versions 1.18.x and 1.19.x of `flink-table-api-java` are supported.
