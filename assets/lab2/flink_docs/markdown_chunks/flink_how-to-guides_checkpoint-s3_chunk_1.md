---
document_id: flink_how-to-guides_checkpoint-s3_chunk_1
source_file: flink_how-to-guides_checkpoint-s3.md
source_url: https://docs.confluent.io/platform/current/flink/how-to-guides/checkpoint-s3.html
title: Enable checkpointing to S3
chunk_index: 1
total_chunks: 1
---

# How to Set Up Checkpointing to AWS S3 with Confluent Manager for Apache Flink¶

This guide shows how to set up checkpointing for a Flink application using Confluent Manager for Apache Flink. This example shows how to set up checkpointing to AWS S3. The steps are mostly the same for other cloud providers, but this example is specific to AWS S3.

## Overview of steps¶

Use the following steps to set up checkpointing.

  1. Enable the S3 filesystem plugin for Flink. Do this by setting the `ENABLE_BUILT_IN_PLUGINS` environment variable using a `spec.podTemplate` format for all the pods in the Flink cluster. Make sure to use the correct version in the plugin jar name.
  2. Set the S3 credentials in the Flink configuration. The following example shows the `s3.access-key: your-access-key` and `s3.secret-key: your-secret-key` settings. The [Apache Flink docs](https://nightlies.apache.org/flink/flink-docs-release-1.19/docs/deployment/filesystems/s3/#configure-access-credentials) provide other ways to set the credentials.
  3. Enable checkpointing by setting the `state.checkpoints.dir` to the location on the S3 bucket where you want the checkpoints to be saved.

## Example¶

Implementing the previous steps should result in a `FlinkApplication` specification as follows:

    apiVersion: cmf.confluent.io/v1
    kind: FlinkApplication
    metadata:
      name: checkpointing-example
    spec:
      image: confluentinc/cp-flink:1.19.2-cp1
      flinkVersion: v1_19
      flinkConfiguration:
        taskmanager.numberOfTaskSlots: '1'
        # Set the S3 credentials
        s3.access-key: your-access-key
        s3.secret-key: your-secret-key
        # Enable checkpointing to S3
        state.checkpoints.dir: s3://your-bucket/flink-checkpoints/
      serviceAccount: flink
      podTemplate:
        spec:
          containers:
            - name: flink-main-container
              env:
                - name: ENABLE_BUILT_IN_PLUGINS
                  value: "flink-s3-fs-hadoop-1.19.2-cp1.jar"
      jobManager:
        resource:
          memory: 1024m
          cpu: 1
      taskManager:
        resource:
          memory: 1024m
          cpu: 1
      job:
        jarURI: local:///opt/flink/examples/streaming/StateMachineExample.jar
        state: running
        parallelism: 1
