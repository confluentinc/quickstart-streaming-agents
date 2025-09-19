---
source_url: https://docs.confluent.io/cloud/current/flink/get-started/quick-start-java-table-api.html
title: Java Table API Quick Start on Confluent Cloud for Apache Flink
hierarchy: ['get-started', 'quick-start-java-table-api.html']
scraped_date: 2025-09-05T13:45:59.122237
---

# Java Table API Quick Start on Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® supports programming applications with the Table API. Confluent provides a plugin for running applications that use the Table API on Confluent Cloud.

For more information, see [Table API](../reference/table-api.html#flink-table-api).

For code examples, see [Java Examples for Table API on Confluent Cloud](https://github.com/confluentinc/flink-table-api-java-examples).

For a Confluent Developer course, see [Apache Flink Table API: Processing Data Streams in Java](https://developer.confluent.io/courses/flink-table-api-java/exercise-connecting-to-confluent-cloud/).

Note

The Flink Table API is available for preview.

A Preview feature is a Confluent Cloud component that is being introduced to gain early feedback from developers. Preview features can be used for evaluation and non-production testing purposes or to provide feedback to Confluent. The warranty, SLA, and Support Services provisions of your agreement with Confluent do not apply to Preview features. Confluent may discontinue providing preview releases of the Preview features at any time in Confluent’s’ sole discretion.

Comments, questions, and suggestions related to the Table API are encouraged and can be submitted through the [established channels](../get-help.html#ccloud-flink-help).

## Prerequisites¶

  * Access to Confluent Cloud
  * A [compute pool](../operate-and-deploy/create-compute-pool.html#flink-sql-manage-compute-pool) in Confluent Cloud
  * A Apache Kafka® [cluster](../../clusters/create-cluster.html#cloud-create-cluster), if you want to run examples that store data in Kafka
  * Java version 11 or later
  * Maven (see [Installing Apache Maven](https://maven.apache.org/install.html))

To run Table API and Flink SQL programs, you must generate an API key that’s specific to the Flink environment. Also, you need Confluent Cloud account details, like your organization and environment identifiers.

  * **Flink API Key:** Follow the steps in [Generate a Flink API key](../operate-and-deploy/flink-rest-api.html#flink-rest-api-generate-api-key). For convenience, assign your Flink key and secret to the FLINK_API_KEY and FLINK_API_SECRET environment variables.
  * **Organization ID:** The identifier your organization, for example, `b0b421724-4586-4a07-b787-d0bb5aacbf87`. For convenience, assign your organization identifier to the ORG_ID environment variable.
  * **Environment ID:** The identifier of the environment where your Flink SQL statements run, for example, `env-z3y2x1`. For convenience, assign your environment identifier to the ENV_ID environment variable.
  * **Cloud provider name:** The name of the cloud provider where your cluster runs, for example, `aws`. To see the available providers, run the `confluent flink region list` command. For convenience, assign your cloud provider to the CLOUD_PROVIDER environment variable.
  * **Cloud region:** The name of the region where your cluster runs, for example, `us-east-1`. To see the available regions, run the `confluent flink region list` command. For convenience, assign your cloud region to the CLOUD_REGION environment variable.

    export CLOUD_PROVIDER="aws"
    export CLOUD_REGION="us-east-1"
    export FLINK_API_KEY="<your-flink-api-key>"
    export FLINK_API_SECRET="<your-flink-api-secret>"
    export ORG_ID="<your-organization-id>"
    export ENV_ID="<your-environment-id>"
    export COMPUTE_POOL_ID="<your-compute-pool-id>"

## Compile and run a Table API program¶

The following code example shows how to run a “Hello World” statement and how to query an example data stream.

  1. Copy the following project object model (POM) into a file named pom.xml.

pom.xml
         
         <project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
             <modelVersion>4.0.0</modelVersion>
         
             <groupId>example</groupId>
             <artifactId>flink-table-api-java-hello-world</artifactId>
             <version>1.0</version>
             <packaging>jar</packaging>
         
             <name>Apache Flink® Table API Java Hello World Example on Confluent Cloud</name>
         
             <properties>
                 <flink.version>1.20.0</flink.version>
                 <confluent-plugin.version>1.20-42</confluent-plugin.version>
                 <target.java.version>11</target.java.version>
                 <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
                 <maven.compiler.source>${target.java.version}</maven.compiler.source>
                 <maven.compiler.target>${target.java.version}</maven.compiler.target>
                 <log4j.version>2.17.1</log4j.version>
             </properties>
         
             <repositories>
                 <repository>
                     <id>confluent</id>
                     <url>https://packages.confluent.io/maven/</url>
                 </repository>
                 <repository>
                     <id>apache.snapshots</id>
                     <name>Apache Development Snapshot Repository</name>
                     <url>https://repository.apache.org/content/repositories/snapshots/</url>
                     <releases>
                         <enabled>false</enabled>
                     </releases>
                     <snapshots>
                         <enabled>true</enabled>
                     </snapshots>
                 </repository>
             </repositories>
         
             <dependencies>
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
         
                 <!-- Add logging framework, to produce console output when running in the IDE. -->
                 <!-- These dependencies are excluded from the application JAR by default. -->
                 <dependency>
                     <groupId>org.apache.logging.log4j</groupId>
                     <artifactId>log4j-slf4j-impl</artifactId>
                     <version>${log4j.version}</version>
                     <scope>runtime</scope>
                 </dependency>
                 <dependency>
                     <groupId>org.apache.logging.log4j</groupId>
                     <artifactId>log4j-api</artifactId>
                     <version>${log4j.version}</version>
                     <scope>runtime</scope>
                 </dependency>
                 <dependency>
                     <groupId>org.apache.logging.log4j</groupId>
                     <artifactId>log4j-core</artifactId>
                     <version>${log4j.version}</version>
                     <scope>runtime</scope>
                 </dependency>
             </dependencies>
         
             <build>
             <sourceDirectory>./example</sourceDirectory>
                 <plugins>
         
                     <!-- Java Compiler -->
                     <plugin>
                         <groupId>org.apache.maven.plugins</groupId>
                         <artifactId>maven-compiler-plugin</artifactId>
                         <version>3.10.1</version>
                         <configuration>
                             <source>${target.java.version}</source>
                             <target>${target.java.version}</target>
                         </configuration>
                     </plugin>
         
                     <!-- We use the maven-shade plugin to create a fat jar that contains all necessary dependencies. -->
                     <!-- Change the value of <mainClass>...</mainClass> if your program entry point changes. -->
                     <plugin>
                         <groupId>org.apache.maven.plugins</groupId>
                         <artifactId>maven-shade-plugin</artifactId>
                         <version>3.4.1</version>
                         <executions>
                             <!-- Run shade goal on package phase -->
                             <execution>
                                 <phase>package</phase>
                                 <goals>
                                     <goal>shade</goal>
                                 </goals>
                                 <configuration>
                                     <artifactSet>
                                         <excludes>
                                             <exclude>org.apache.flink:flink-shaded-force-shading</exclude>
                                             <exclude>com.google.code.findbugs:jsr305</exclude>
                                         </excludes>
                                     </artifactSet>
                                     <filters>
                                         <filter>
                                             <!-- Do not copy the signatures in the META-INF folder.
                                             Otherwise, this might cause SecurityExceptions when using the JAR. -->
                                             <artifact>*:*</artifact>
                                             <excludes>
                                                 <exclude>META-INF/*.SF</exclude>
                                                 <exclude>META-INF/*.DSA</exclude>
                                                 <exclude>META-INF/*.RSA</exclude>
                                             </excludes>
                                         </filter>
                                     </filters>
                                     <transformers>
                                         <transformer
                                                 implementation="org.apache.maven.plugins.shade.resource.ServicesResourceTransformer"/>
                                         <transformer
                                                 implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
                                             <mainClass>example.hello_table_api</mainClass>
                                         </transformer>
                                     </transformers>
                                 </configuration>
                             </execution>
                         </executions>
                     </plugin>
                 </plugins>
         
                 <pluginManagement>
                     <plugins>
         
                         <!-- This improves the out-of-the-box experience in Eclipse by resolving some warnings. -->
                         <plugin>
                             <groupId>org.eclipse.m2e</groupId>
                             <artifactId>lifecycle-mapping</artifactId>
                             <version>1.0.0</version>
                             <configuration>
                                 <lifecycleMappingMetadata>
                                     <pluginExecutions>
                                         <pluginExecution>
                                             <pluginExecutionFilter>
                                                 <groupId>org.apache.maven.plugins</groupId>
                                                 <artifactId>maven-shade-plugin</artifactId>
                                                 <versionRange>[3.1.1,)</versionRange>
                                                 <goals>
                                                     <goal>shade</goal>
                                                 </goals>
                                             </pluginExecutionFilter>
                                             <action>
                                                 <ignore/>
                                             </action>
                                         </pluginExecution>
                                         <pluginExecution>
                                             <pluginExecutionFilter>
                                                 <groupId>org.apache.maven.plugins</groupId>
                                                 <artifactId>maven-compiler-plugin</artifactId>
                                                 <versionRange>[3.1,)</versionRange>
                                                 <goals>
                                                     <goal>testCompile</goal>
                                                     <goal>compile</goal>
                                                 </goals>
                                             </pluginExecutionFilter>
                                             <action>
                                                 <ignore/>
                                             </action>
                                         </pluginExecution>
                                     </pluginExecutions>
                                 </lifecycleMappingMetadata>
                             </configuration>
                         </plugin>
                     </plugins>
                 </pluginManagement>
             </build>
         </project>

  2. Create a directory named “example”.
         
         mkdir example

  3. Create a file named `hello_table_api.java` in the `example` directory.
         
         touch example/hello_table_api.java

  4. Copy the following code into `hello_table_api.java`.
         
         package example;
         import io.confluent.flink.plugin.ConfluentSettings;
         import io.confluent.flink.plugin.ConfluentTools;
         import org.apache.flink.table.api.EnvironmentSettings;
         import org.apache.flink.table.api.Table;
         import org.apache.flink.table.api.TableEnvironment;
         import org.apache.flink.types.Row;
         import java.util.List;
         
         /**
          * A table program example to get started with the Apache Flink® Table API.
          *
          * <p>It executes two foreground statements in Confluent Cloud. The results of both statements are
          * printed to the console.
          */
         public class hello_table_api {
         
             // All logic is defined in a main() method. It can run both in an IDE or CI/CD system.
             public static void main(String[] args) {
         
                 // Set up connection properties to Confluent Cloud.
                 // Use the fromGlobalVariables() method if you assigned environment variables.
                 // EnvironmentSettings settings = ConfluentSettings.fromGlobalVariables();
         
                 // Use the fromArgs(args) method if you want to run with command-line arguments.
                 EnvironmentSettings settings = ConfluentSettings.fromArgs(args);
         
                 // Initialize the session context to get started.
                 TableEnvironment env = TableEnvironment.create(settings);
         
                 System.out.println("Running with printing...");
         
                 // The Table API centers on 'Table' objects, which help in defining data pipelines
                 // fluently. You can define pipelines fully programmatically.
                 Table table = env.fromValues("Hello world!");
         
                 // Also, You can define pipelines with embedded Flink SQL.
                 // Table table = env.sqlQuery("SELECT 'Hello world!'");
         
                 // Once the pipeline is defined, execute it on Confluent Cloud.
                 // If no target table has been defined, results are streamed back and can be printed
                 // locally. This can be useful for development and debugging.
                 table.execute().print();
         
                 System.out.println("Running with collecting...");
         
                 // Results can be collected locally and accessed individually.
                 // This can be useful for testing.
                 Table moreHellos = env.fromValues("Hello Bob", "Hello Alice", "Hello Peter").as("greeting");
                 List<Row> rows = ConfluentTools.collectChangelog(moreHellos, 10);
                 rows.forEach(
                         r -> {
                             String column = r.getFieldAs("greeting");
                             System.out.println("Greeting: " + column);
                         });
             }
         }

  5. Run the following command to build the jar file.
         
         mvn clean package

  6. Run the jar. If you assigned your cloud configuration to the environment variables specified in the Prerequisites section, and you used the `fromGlobalVariables` method in the `hello_table_api` code, you don’t need to provide the command-line options.
         
         java -jar target/flink-table-api-java-hello-world-1.0.jar \
           --cloud aws \
           --region us-east-1 \
           --flink-api-key key \
           --flink-api-secret secret \
           --organization-id b0b21724-4586-4a07-b787-d0bb5aacbf87 \
           --environment-id env-z3y2x1 \
           --compute-pool-id lfcp-8m03rm

Your output should resemble:
         
         Running with printing...
         +----+--------------------------------+
         | op |                             f0 |
         +----+--------------------------------+
         | +I |                   Hello world! |
         +----+--------------------------------+
         1 row in set
         Running with collecting...
         Greeting: Hello Bob
         Greeting: Hello Alice
         Greeting: Hello Peter

