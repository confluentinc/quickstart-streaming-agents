---
document_id: flink_jobs_configure_metrics_chunk_1
source_file: flink_jobs_configure_metrics.md
source_url: https://docs.confluent.io/platform/current/flink/jobs/configure/metrics.html
title: Metrics with Confluent Manager for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Collect Metrics for Confluent Manager for Apache Flink¶

Apache Flink® provides a [metrics system](https://nightlies.apache.org/flink/flink-docs-release-1.18/docs/ops/metrics), which covers system metrics provided by the framework and user-defined metrics.

Metrics Reporters are used to make the metrics available from Flink to external systems. You can configure the metrics reporter with Flink configuration. See [the Flink metrics reporter documentation](https://nightlies.apache.org/flink/flink-docs-master/docs/deployment/metric_reporters/) for the full list of supported metrics reporters and how to configure them.

Confluent Manager for Apache Flink offers two ways of configuring the metric collection for your application.

## Option 1. Per application¶

The following example code shows a per-application configuration for metrics.

    ---
    apiVersion: cmf.confluent.io/v1
    kind: FlinkApplication
    metadata:
    name: basic-example
    spec:
    image: confluentinc/cp-flink:1.19.1-cp1
    flinkVersion: v1_19
    flinkConfiguration:
        taskmanager.numberOfTaskSlots: '1'
        # Use prometheus metric report
        metrics.reporter.prom.factory.class: org.apache.flink.metrics.prometheus.PrometheusReporterFactory
        metrics.reporter.prom.port: 9249-9250
    serviceAccount: flink
    # Custom logging configuration this application
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

## Option 2: The same metrics for every application in your environment¶

The following example code shows how to apply the same metrics setting to every application in your environment.

    ---
    name: default
    kubernetesNamespace: staging-shared
    flinkApplicationDefaults:
    metadata:
        annotations:
        fmc.platform.confluent.io/intra-cluster-ssl: 'false'
    spec:
        flinkConfiguration:
        # Use prometheus metric report for all applications in this environment
        metrics.reporter.prom.factory.class: org.apache.flink.metrics.prometheus.PrometheusReporterFactory
        metrics.reporter.prom.port: 9249-9250
        taskmanager.numberOfTaskSlots: '2'
        rest.profiling.enabled: 'true'

## Metrics in the Flink WebUI¶

Accessing the Flink WebUI enables you to observe your application’s live metrics by task. For more information, see [Access the Flink Web UI for the application](../../clients-api/cli.html#access-web-ui).

The following image shows an example of viewing metrics in the Flink WebUI.

[](../../../_images/cmf-metrics.png)
