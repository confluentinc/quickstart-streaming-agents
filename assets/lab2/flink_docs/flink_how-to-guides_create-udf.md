---
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/create-udf.html
title: Create a User-Defined Function with Confluent Cloud for Apache Flink
hierarchy: ['how-to-guides', 'create-udf.html']
scraped_date: 2025-09-05T13:47:33.077855
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

## Step 1: Build the uber jar¶

In this section, you compile a simple Java class, named `TShirtSizingIsSmaller` into a jar file. The project is based on the `ScalarFunction` class in the Flink Table API. The `TShirtSizingIsSmaller.java` class has an `eval` function that compares two T-shirt sizes and returns the smaller size.

  1. Copy the following project object model into a file named pom.xml.

Important

You can’t use your own Flink-related jars. If you package Flink core dependencies as part of the jar, you may break the dependency.

Also, this example shows how to capture all dependencies greedily, possibly including more than needed. As an alternative, you can optimize on artifact size by listing all dependencies and including their transitive dependencies.

pom.xml
         
         <?xml version="1.0" encoding="UTF-8"?>
         <project xmlns="http://maven.apache.org/POM/4.0.0"
                  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                  xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
             <modelVersion>4.0.0</modelVersion>
         
             <groupId>example</groupId>
             <artifactId>udf_example</artifactId>
             <version>1.0</version>
         
             <properties>
                 <maven.compiler.source>11</maven.compiler.source>
                 <maven.compiler.target>11</maven.compiler.target>
                 <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
             </properties>
         
             <dependencies>
                 <dependency>
                     <groupId>org.apache.flink</groupId>
                     <artifactId>flink-table-api-java</artifactId>
                     <version>1.18.1</version>
                     <scope>provided</scope>
                 </dependency>
         
                 <!-- Dependencies -->
         
             </dependencies>
         
             <build>
                 <sourceDirectory>./example</sourceDirectory>
                 <plugins>
                     <plugin>
                         <groupId>org.apache.maven.plugins</groupId>
                         <artifactId>maven-shade-plugin</artifactId>
                         <version>3.6.0</version>
                         <configuration>
                             <artifactSet>
                                 <includes>
                                     <!-- Include all UDF dependencies and their transitive dependencies here. -->
                                     <!-- This example shows how to capture all of them greedily. -->
                                     <include>*:*</include>
                                 </includes>
                             </artifactSet>
                             <filters>
                                 <filter>
                                     <artifact>*</artifact>
                                     <excludes>
                                         <!-- Do not copy the signatures in the META-INF folder.
                                         Otherwise, this might cause SecurityExceptions when using the JAR. -->
                                         <exclude>META-INF/*.SF</exclude>
                                         <exclude>META-INF/*.DSA</exclude>
                                         <exclude>META-INF/*.RSA</exclude>
                                     </excludes>
                                 </filter>
                             </filters>
                         </configuration>
                         <executions>
                             <execution>
                                 <phase>package</phase>
                                 <goals>
                                     <goal>shade</goal>
                                 </goals>
                             </execution>
                         </executions>
                     </plugin>
                 </plugins>
             </build>
         </project>

  2. Create a directory named “example”.
         
         mkdir example

  3. In the `example` directory, create a file named `TShirtSizingIsSmaller.java`.
         
         touch example/TShirtSizingIsSmaller.java

  4. Copy the following code into `TShirtSizingIsSmaller.java`.
         
         package com.example.my;
         
         import org.apache.flink.table.functions.ScalarFunction;
         
         import java.util.Arrays;
         import java.util.List;
         import java.util.stream.IntStream;
         
         /** TShirt sizing function for demo. */
         public class TShirtSizingIsSmaller extends ScalarFunction {
            public static final String NAME = "IS_SMALLER";
         
            private static final List<Size> ORDERED_SIZES =
                     Arrays.asList(
                           new Size("X-Small", "XS"),
                           new Size("Small", "S"),
                           new Size("Medium", "M"),
                           new Size("Large", "L"),
                           new Size("X-Large", "XL"),
                           new Size("XX-Large", "XXL"));
         
            public boolean eval(String shirt1, String shirt2) {
               int size1 = findSize(shirt1);
               int size2 = findSize(shirt2);
               // If either can't be found just say false rather than throw an error
               if (size1 == -1 || size2 == -1) {
                     return false;
               }
               return size1 < size2;
            }
         
            private int findSize(String shirt) {
               return IntStream.range(0, ORDERED_SIZES.size())
                        .filter(
                                 i -> {
                                    Size s = ORDERED_SIZES.get(i);
                                    return s.name.equalsIgnoreCase(shirt)
                                             || s.abbreviation.equalsIgnoreCase(shirt);
                                 })
                        .findFirst()
                        .orElse(-1);
            }
         
            private static class Size {
               private final String name;
               private final String abbreviation;
         
               public Size(String name, String abbreviation) {
                     this.name = name;
                     this.abbreviation = abbreviation;
               }
            }
         }

  5. Run the following command to build the jar file.
         
         mvn clean package

  6. Run the following command to check the contents of your jar.
         
         jar -tf target/udf_example-1.0.jar | grep -i TShirtSizingIsSmaller

Your output should resemble:
         
         com/example/my/TShirtSizingIsSmaller$Size.class
         com/example/my/TShirtSizingIsSmaller.class

## Step 2: Upload the jar as a Flink artifact¶

You can use the Confluent Cloud Console, the Confluent CLI, or the REST API to upload your UDF.

Confluent Cloud ConsoleConfluent CLIREST API

  1. Log in to Confluent Cloud and navigate to your Flink workspace.
  2. Navigate to the environment where you want to run the UDF.
  3. Click **Flink** , in the Flink page, click **Artifacts**.
  4. Click **Upload artifact** to open the upload pane.
  5. In the **Cloud provider** dropdown, select **AWS** , and in the **Region** dropdown, select the cloud region.
  6. Click **Upload your JAR file** and navigate to the location of your JAR file, which in the current example is `target/udf_example-1.0.jar`.
  7. When your JAR file is uploaded, it appears in the **Artifacts** list. In the list, click the row for your UDF artifact to open the details pane.

  1. Log in to Confluent Cloud.
         
         confluent login --organization-id ${ORG_ID} --prompt

  2. Run the following command to upload the jar to Confluent Cloud.
         
         confluent flink artifact create udf_example \
         --artifact-file target/udf_example-1.0.jar \
         --cloud ${CLOUD_PROVIDER} \
         --region ${CLOUD_REGION} \
         --environment ${ENV_ID}

Your output should resemble:
         
         +--------------------+-------------+
         | ID                 | cfa-ldxmro  |
         | Name               | udf_example |
         | Version            | ver-81vxm5  |
         | Cloud              | aws         |
         | Region             | us-east-1   |
         | Environment        | env-z3q9rd  |
         | Content Format     | JAR         |
         | Description        |             |
         | Documentation Link |             |
         +--------------------+-------------+

Note the artifact ID and version of your UDTF, which in this example are `cfa-ldxmro` and `ver-81vxm5`, because you use them later to register the UDTF in Flink SQL and to manage it.

  3. Run the following command to view all of the available UDFs.
         
         confluent flink artifact list \
         --cloud ${CLOUD_PROVIDER} \
         --region ${CLOUD_REGION}

Your output should resemble:
         
         ID     |    Name     | Cloud |  Region   | Environment
         -------------+-------------+-------+-----------+--------------
         cfa-ldxmro | udf_example | AWS   | us-east-1 | env-z3q9rd

  4. Run the following command to view the details of your UDF. You can use the artifact ID from the previous step or the artifact name to specify your UDF.
         
         # use the artifact ID
         confluent flink artifact describe \
         cfa-ldxmro \
         --cloud ${CLOUD_PROVIDER} \
         --region ${CLOUD_REGION}
         
         # use the artifact name
         confluent flink artifact describe \
         udf_example \
         --cloud ${CLOUD_PROVIDER} \
         --region ${CLOUD_REGION}

Your output should resemble:
         
         +--------------------+-------------+
         | ID                 | cfa-ldxmro  |
         | Name               | udf_example |
         | Version            | ver-81vxm5  |
         | Cloud              | aws         |
         | Region             | us-east-1   |
         | Environment        | env-z3q9rd  |
         | Content Format     | JAR         |
         | Description        |             |
         | Documentation Link |             |
         +--------------------+-------------+

You can upload your JAR file by requesting a presigned upload URL, then uploading the file by using the presigned URL information. For more information, see [Create a Flink artifact](../operate-and-deploy/flink-rest-api.html#flink-rest-api-create-artifact).

## Step 3: Register the UDF¶

UDFs are registered inside a Flink database, which means that you must specify the Confluent Cloud environment (Flink catalog) and Kafka cluster (Flink database) where you want to use the UDF.

You can use the Confluent Cloud Console, the Confluent CLI, the Confluent Terraform provider, or the REST API to register your UDF.

Confluent Cloud ConsoleConfluent CLITerraformREST API

  1. In the Flink page, click **Compute pools**.
  2. In the tile for the compute pool where you want to run the UDF, click **Open SQL workspace**.
  3. In the **Use catalog** dropdown, select the environment where you want to run the UDF.
  4. In the **Use database** dropdown, select Kafka cluster that you want to run the UDF.

  1. Run the following command to start the Flink shell.
         
         confluent flink shell --environment ${ENV_ID} --compute-pool ${COMPUTE_POOL_ID}

  2. Run the following statements to specify the catalog and database.
         
         -- Specify your catalog. This example uses the default.
         USE CATALOG default;

Your output should resemble:
         
         +---------------------+---------+
         |         Key         |  Value  |
         +---------------------+---------+
         | sql.current-catalog | default |
         +---------------------+---------+

Specify the database you want to use, for example, `cluster_0`.
         
         -- Specify your database. This example uses cluster_0.
         USE cluster_0;

Your output should resemble:
         
         +----------------------+-----------+
         |         Key          |   Value   |
         +----------------------+-----------+
         | sql.current-database | cluster_0 |
         +----------------------+-----------+

You can register a previously uploaded UDF by using the Confluent Terraform provider. For more information, see [confluent_flink_artifact Resource](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/resources/confluent_flink_artifact)

You can register a UDF by sending a POST request to the [Create Artifact endpoint](/cloud/current/api.html#tag/Flink-Artifacts-\(artifactv1\)/operation/createArtifactV1FlinkArtifact). For more information, see [Create a Flink artifact](../operate-and-deploy/flink-rest-api.html#flink-rest-api-create-artifact).

  * In Cloud Console or the Confluent CLI, run the [CREATE FUNCTION](../reference/statements/create-function.html#flink-sql-create-function) statement to register your UDF in the current catalog and database. Substitute your UDF’s value for `<artifact-id>`.
        
        CREATE FUNCTION is_smaller
          AS 'com.example.my.TShirtSizingIsSmaller'
          USING JAR 'confluent-artifact://<artifact-id>';

Your output should resemble:
        
        Function 'is_smaller' created.

## Step 4: Use the UDF in a Flink SQL query¶

Once it is registered, your UDF is available to use in queries.

  1. Run the following statement to view the UDFs in the current database.
         
         SHOW USER FUNCTIONS;

Your output should resemble:
         
         +---------------+
         | function name |
         +---------------+
         | is_smaller    |
         +---------------+

  2. Run the following statement to create a `sizes` table.
         
         CREATE TABLE sizes (
           `size_1` STRING,
           `size_2` STRING
         );

  3. Run the following statement to populate the `sizes` table with values.
         
         INSERT INTO sizes VALUES
           ('XL', 'L'),
           ('small', 'L'),
           ('M', 'L'),
           ('XXL', 'XL');

  4. Run the following statement to view the rows in the `sizes` table.
         
         SELECT * FROM sizes;

Your output should resemble:
         
         size_1 size_2
         XL     L
         small  L
         M      L
         XXL    XL

  5. Run the following statement to execute the `is_smaller` function on the data in the `sizes` table.
         
         SELECT size_1, size_2, is_smaller (size_1, size_2)
           AS is_smaller
           FROM sizes;

Your output should resemble:
         
         size_1 size_2 is_smaller
         XL     L      FALSE
         small  L      TRUE
         M      L      TRUE
         XXL    XL     FALSE

## Step 5: Implement UDF logging (optional)¶

If you want to log UDF status messages to a Kafka topic, follow the steps in [Enable UDF Logging](enable-udf-logging.html#flink-sql-enable-udf-logging).

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

## Step 2: Upload the UDTF jar as a Flink artifact¶

Confluent Cloud ConsoleConfluent CLI

  1. Log in to Confluent Cloud and navigate to your Flink workspace.
  2. Navigate to the environment where you want to run the UDF.
  3. Click **Flink** , in the Flink page, click **Artifacts**.
  4. Click **Upload artifact** to open the upload pane.
  5. In the **Cloud provider** dropdown, select **AWS** , and in the **Region** dropdown, select the cloud region.
  6. Click **Upload your JAR file** and navigate to the location of your JAR file, which in the current example is `target/udf_example-1.0.jar`.
  7. When your JAR file is uploaded, it appears in the **Artifacts** list. In the list, click the row for your UDF artifact to open the details pane.

  1. Log in to Confluent Cloud.
         
         confluent login --organization-id ${ORG_ID} --prompt

  2. Run the following command to upload the jar to Confluent Cloud.
         
         confluent flink artifact create udf_table_example \
         --artifact-file target/udf_example-1.0.jar \
         --cloud ${CLOUD_PROVIDER} \
         --region ${CLOUD_REGION} \
         --environment ${ENV_ID}

Your output should resemble:
         
         +--------------------+-------------------+
         | ID                 | cfa-l5xp82        |
         | Name               | udf_table_example |
         | Version            | ver-0x37m2        |
         | Cloud              | aws               |
         | Region             | us-east-1         |
         | Environment        | env-z3q9rd        |
         | Content Format     | JAR               |
         | Description        |                   |
         | Documentation Link |                   |
         +--------------------+-------------------+

Note the artifact ID and version of your UDTF, which in this example are `cfa-l5xp82` and `ver-0x37m2`, because you use them later to register the UDTF in Flink SQL and to manage it.

## Step 3: Register the UDTF¶

  1. In the Flink shell or the Cloud Console, specify the catalog and database (environment and cluster) where you want to use the UDTF, as you did in the previous section.

  2. Run the [CREATE FUNCTION](../reference/statements/create-function.html#flink-sql-create-function) statement to register your UDTF in the current catalog and database. Substitute your UDTF’s value for `<artifact-id>`.
         
         CREATE FUNCTION split_string
           AS 'com.example.my.SplitFunction'
           USING JAR 'confluent-artifact://<artifact-id>';

Your output should resemble:
         
         Function 'split_string' created.

## Step 4: Use the UDTF in a Flink SQL query¶

Once it is registered, your UDTF is available to use in queries.

  1. Run the following statement to view the UDFs in the current database.
         
         SHOW USER FUNCTIONS;

Your output should resemble:
         
         +---------------+
         | Function Name |
         +---------------+
         | split_string  |
         +---------------+

  2. Run the following statement to execute the `split_string` function.
         
         SELECT * FROM (VALUES 'A;B', 'C;D;E;F') as T(f), LATERAL TABLE(split_string(f, ';'))

Your output should resemble:
         
         f        word
         A;B      A
         A;B      B
         C;D;E;F  C
         C;D;E;F  D
         C;D;E;F  E
         C;D;E;F  F

  3. When you’re done with the example UDTF, drop the function and delete the JAR artifact as you did in Step 6: Delete the UDF.

