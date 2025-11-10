---
document_id: flink_jobs_configure_logging_chunk_1
source_file: flink_jobs_configure_logging.md
source_url: https://docs.confluent.io/platform/current/flink/jobs/configure/logging.html
title: Logging with Confluent Manager for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Logging with Confluent Manager for Apache Flink¶

Confluent Manager for Apache Flink® exposes all Flink logging configurations (Logging) with the Application and Environment APIs. For more information, see [API reference](../../clients-api/rest.html#cmf-api-ref). Flink uses [Log4j 2](https://logging.apache.org/log4j/2.12.x/) configuration file, which you can use to define custom appenders for sending logs to a remote system or to define a log format compatible with your log ingestion system. When defining custom appenders, you should package a custom Docker image containing the required additional dependencies.

By default, Flink clusters deployed with CMF will log to standard out, which you can access from the pod logs or the Flink Web UI.

You can either choose to configure the logging behavior for a specific Application or per Environment. When you configure logging for an Environment, the same behavior is applied to all of the Applications it contains. A logging setting on an Environment takes precedence over the same setting at the Application level.

## Option 1: Configure Logging for an Application¶

The following code shows an example of configuration for an Application.

    ---
    apiVersion: cmf.confluent.io/v1
    kind: FlinkApplication
    metadata:
    name: basic-example
    spec:
    image: confluentinc/cp-flink:1.19.1-cp1
    flinkVersion: v1_19
    flinkConfiguration:
      taskmanager.numberOfTaskSlots: "1"
    serviceAccount: flink
    logConfiguration:
      log4j-console.properties: |+
        rootLogger.level = DEBUG
        rootLogger.appenderRef.file.ref = LogFile
    jobManager:
      resource:
      memory: 1048m
      cpu: 1
    taskManager:
      resource:
      memory: 1048m
      cpu: 1
    job:
      jarURI: local:///opt/flink/examples/streaming/StateMachineExample.jar
      state: running
      parallelism: 3
      upgradeMode: stateless

## Option 2: Configure Logging for an Environment¶

The following code shows an example of configuring logging at the Environment level:

    ---
    name: default
    kubernetesNamespace: staging-shared
    flinkApplicationDefaults:
    spec:
      # Custom logging configuration for all Applications in this environment
      logConfiguration:
      log4j-console.properties: |+
        rootLogger.level = DEBUG
        rootLogger.appenderRef.file.ref = LogFile
