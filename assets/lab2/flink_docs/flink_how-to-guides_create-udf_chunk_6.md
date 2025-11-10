---
document_id: flink_how-to-guides_create-udf_chunk_6
source_file: flink_how-to-guides_create-udf.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/create-udf.html
title: Create a User-Defined Function with Confluent Cloud for Apache Flink
chunk_index: 6
total_chunks: 7
---

steps in [Enable UDF Logging](enable-udf-logging.html#flink-sql-enable-udf-logging).

## Step 6: Delete the UDF¶

When you’re finished using the UDF, you can delete it from the current database.

You can use the Confluent Cloud Console, the Confluent CLI, the Confluent Terraform provider, or the REST API to delete your UDF.

### Drop the function¶

  1. Run the following statement to remove the `is_smaller` function from the current database.

         DROP FUNCTION is_smaller;

Your output should resemble:

         Function 'is_smaller' dropped.

Currently running statements are not affected and continue running.

  2. Exit the Flink shell.

         exit;

### Delete the JAR artifact¶

Confluent Cloud ConsoleConfluent CLITerraformREST API

  1. Navigate to the environment where your UDF is registered.
  2. Click **Flink** , and in the Flink page, click **Artifacts**.
  3. In the artifacts list, find the UDF you want to delete.
  4. In the **Actions** column, click the icon, and in the context menu, select **Delete artifact**.
  5. In the confirmation dialog, type “udf_example”, and click **Confirm**. The “Artifact deleted successfully” message appears.

  1. Run the following command to delete the artifact form the environment.

         confluent flink artifact delete \
         <artifact-id> \
         --cloud ${CLOUD_PROVIDER} \
         --region ${CLOUD_REGION}

You receive a warning about breaking Flink statements that use the artifact. Type “y” when you’re prompted to proceed.

Your output should resemble:

         Deleted Flink artifact "<artifact-id>".

You can delete a UDF by using the Confluent Terraform provider. For more information, see [confluent_flink_artifact Resource](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/resources/confluent_flink_artifact)

You can delete a UDF by sending a DELETE request to the [Delete Artifact endpoint](/cloud/current/api.html#tag/Flink-Artifacts-\(artifactv1\)/operation/deleteArtifactV1FlinkArtifact). For more information, see [Delete an artifact](../operate-and-deploy/flink-rest-api.html#flink-rest-api-delete-artifact).

## Implement a user-defined table function¶

In the previous steps, you implemented a UDF with a simple scalar function. Confluent Cloud for Apache Flink also supports [user-defined table functions (UDTFs)](../concepts/user-defined-functions.html#flink-sql-udfs-table-functions), which take multiple scalar values as input arguments and return multiple rows as output, instead of a single value.

The following steps show how to implement a simple UDTF, upload it to Confluent Cloud, and use it in a Flink SQL statement.

* Step 1: Build the uber jar
* Step 2: Upload the UDTF jar as a Flink artifact
* Step 3: Register the UDTF
* Step 4: Use the UDTF in a Flink SQL query

## Step 1: Build the uber jar¶

In this section, you compile a simple Java class, named `SplitFunction` into a jar file, similar to the previous section. The class is based on the `TableFunction` class in the Flink Table API. The `SplitFunction.java` class has an `eval` function that uses the Java `split` method to break up a string into words and returns the words as columns in a row.

  1. In the `example` directory, create a file named `SplitFunction.java`.

         touch example/SplitFunction.java

  2. Copy the following code into `SplitFunction.java`.

         package com.example.my;

         import org.apache.flink.table.annotation.DataTypeHint;
         import org.apache.flink.table.annotation.FunctionHint;
         import org.apache.flink.table.api.*;
         import org.apache.flink.table.functions.TableFunction;
         import org.apache.flink.types.Row;
         import static org.apache.flink.table.api.Expressions.*;

         @FunctionHint(output = @DataTypeHint("ROW<word STRING>"))
         public class SplitFunction extends TableFunction<Row> {

            public void eval(String str, String delimiter) {
               for (String s : str.split(delimiter)) {
                  // use collect(...) to emit a row
                  collect(Row.of(s));
               }
            }
         }

  3. Run the following command to build the jar file. You can use the POM file from the previous section.

         mvn clean package

  4. Run the following command to check the contents of your jar.

         jar -tf target/udf_example-1.0.jar | grep -i SplitFunction

Your output should resemble:

         com/example/my/SplitFunction.class
