---
document_id: flink_how-to-guides_create-udf_chunk_2
source_file: flink_how-to-guides_create-udf.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/create-udf.html
title: Create a User-Defined Function with Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 7
---

1.19.x of `flink-table-api-java` are supported.

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
                           new Size("X-Small",
