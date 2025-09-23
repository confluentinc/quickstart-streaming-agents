---
source_url: https://docs.confluent.io/platform/current/flink/jobs/applications/packaging.html
title: How to Package a Flink Job with Confluent Manager for Apache Flink
hierarchy: ['platform', 'jobs', 'applications', 'packaging.html']
scraped_date: 2025-09-05T13:52:50.350030
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

## Deploy your Flink Application with CMF¶

After you have developed your Flink application locally, you should have produced a jar archive that includes your Flink applications. For more information, see [Packaging your Application](https://nightlies.apache.org/flink/flink-docs-release-1.19/docs/dev/configuration/maven/#packaging-the-application) in the Flink documentation.

Following are some different packaging options.

### Package with a custom docker image¶

Packaging a Flink job with a customer docker image that contains the Flink jar is recommended when you have the infrastructure in place for building docker images in a build pipeline. The custom docker image should be based on the [confluentinc/cp-flink:1.19.1-cp2](https://hub.docker.com/layers/confluentinc/cp-flink/1.19.1-cp2/images/sha256-ba85f2a20f2151e9f254ac0b315d8c70acb364c808041dc24c75886c0c0444bc) image found on Docker Hub.

Example for Dockerfile:

    FROM confluentinc/cp-flink:1.19.1-cp2
    COPY target/application.jar /opt/flink/usrlib/application.jar
    COPY target/flink-connector-files-1.19.1.jar /opt/flink/usrlib/flink-connector-files-1.19.1.jar

Build the docker image, for example using this command:

    mkdir target
    cd target
    # you can also add additional dependencies to the image
    wget https://repo1.maven.org/maven2/org/apache/flink/flink-connector-files/1.19.1/flink-connector-files-1.19.1.jar
    # and the actual application jar
    wget -O application.jar https://repo1.maven.org/maven2/org/apache/flink/flink-examples-streaming/1.19.1/flink-examples-streaming-1.19.1.jar
    cd ..
    docker build -t image-with-application:1.19.1-cp2 .

Define the FlinkApplication like this:

    ---
    apiVersion: cmf.confluent.io/v1
    kind: FlinkApplication
    metadata:
      name: basic-example
    spec:
      image: image-with-application:1.19.1-cp2
      flinkVersion: v1_19
      flinkConfiguration:
        taskmanager.numberOfTaskSlots: '1'
      serviceAccount: flink
      jobManager:
        resource:
          memory: 1024m
          cpu: 1
      taskManager:
        resource:
          memory: 1024m
          cpu: 1
      job:
        # Jar is already part of the image and is immediately referenceable
        jarURI: local:///opt/flink/usrlib/application.jar
        entryClass: org.apache.flink.streaming.examples.windowing.TopSpeedWindowing
        state: running
        parallelism: 1
        upgradeMode: stateless

### Package with a side-car container¶

In this option you package with a side-car container that downloads the application jar before starting the Flink container.

Use this approach when the application jars are located in remote storage, like an Amazon Web Services S3 bucket.

For example:

    ...
    apiVersion: cmf.confluent.io/v1
    kind: FlinkApplication
    metadata:
      name: sidecar-example
    spec:
      image: confluentinc/cp-flink:1.19.1-cp2
      flinkVersion: v1_19
      flinkConfiguration:
        taskmanager.numberOfTaskSlots: "1"
      serviceAccount: flink
      podTemplate:
        spec:
          # Define volume where the init container will place the application jar
          containers:
            - name: flink-main-container
              volumeMounts:
                - mountPath: /opt/flink/downloads
                  name: downloads
          volumes:
            - name: downloads
              emptyDir: {}
          # Define init containers on all pods
          initContainers:
            - name: artifact-fetcher
              image: registry.access.redhat.com/ubi8/toolbox:latest
              volumeMounts:
                - mountPath: /opt/flink/downloads
                  name: downloads
              command:
                - /bin/sh
                - -c
                - wget -O /opt/flink/downloads/flink-examples-streaming.jar https://repo1.maven.org/maven2/org/apache/flink/flink-examples-streaming/1.19.1/flink-examples-streaming-1.19.1.jar
      jobManager:
        resource:
          memory: 1024m
          cpu: 1
      taskManager:
        resource:
          memory: 1024m
          cpu: 1
      job:
        jarURI: local:///opt/flink/downloads/flink-examples-streaming.jar
        entryClass: org.apache.flink.streaming.examples.statemachine.StateMachineExample
        state: running
        parallelism: 1
        upgradeMode: stateless

## Submit the application definition¶

To run your Flink application with CMF you need to make the jar available to the Flink clusters. After you package the application, you can use the CLI to submit your Flink application definition.

For example:

    confluent flink application create --environment <env-name> <appliction-definition>
