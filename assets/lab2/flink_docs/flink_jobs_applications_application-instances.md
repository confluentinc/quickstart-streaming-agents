---
source_url: https://docs.confluent.io/platform/current/flink/jobs/applications/application-instances.html
title: Confluent Manager for Apache Flink Application Instances
hierarchy: ['platform', 'jobs', 'applications', 'application-instances.html']
scraped_date: 2025-09-05T13:52:46.073235
---

# Application Instances in Confluent Manager for Apache Flink¶

Flink application instances enable you to track the details of your deployed Flink application and any events associated with that running instance. Each application instance is tracked with a unique identifier (UID) and every time you change the specification for a Flink application, a new application instance, with a new UID, is created.

Flink application instances enable you to know more about your running Flink applications. You can:

  * Understand what the effective specification of a Flink application looks like, after the defaults from the Environment have been applied.
  * Understand what changes have been made to a Flink application over time
  * Correlate Flink applications with centralized logging systems. This enables you to determine the particular instance that produced a log event.
  * Use Flink applications for running finite streaming workloads (also called batch processing) on Confluent Platform for Apache Flink.

An application instance also tracks the status of the underlying Flink job.

Confluent Manager for Apache Flink provides REST APIs for interacting Flink application instances, and you can view application instances in the Confluent Control Center UI.

## Flink clusters and Flink application instances¶

The following image shows a Flink application that is configured with `upgradeMode=savepoint`. This configuration means that any change to a configuration value for that application requires a Flink savepoint, and a new application instance is created.

The transition from Cluster 1 to Cluster 2 is done when a savepoint on Cluster 1 is successfully created. Also, instances are not time-correlated with physical Flink clusters. In the image, you can see that Instance 1 and Instance 2 overlap from a time perspective, but the clusters associated with them do not overlap.

[](../../../_images/cpf-application-instances-ex.png)

You can check the currently deployed instance with the `FlinkApplication.status.currentDeployedInstanceName` field.

In the image, if Cluster 1 never manages to successfully stop with a savepoint, Instance 1 remains indefinitely in the `FlinkApplication.status.currentDeployedInstanceName = instance1` state, and Instance 2 won’t represent a physical cluster.

You could revert the Flink application to its previous state, making the upgrade of the cluster unnecessary. When you do this, Instance 3 is created (not shown in the image), but Cluster 1 still remains physically deployed, reporting its status to Instance 1 with the `FlinkApplication.status` property. After the user migrates their state off Cluster 1, there is a new instance (for example Instance 4) that represents the next cluster.

In summary, the following apply to application instances:

  * A Flink application instance is created for every Flink application spec change.
  * A Flink application will have at most one physical cluster deployed and have at most one Flink application name in its `FlinkApplication.status.currentDeployedInstanceName` property.
  * The status field of an application instance (`FlinkApplication.status`) tracks the `status.jobStatus.state` field. This field contains the last observed Flink job status provided by the Flink Kubernetes Operator (FKO) and reports if the last state of an instance was FAILED or FINISHED. This is particularly useful for tracking finite / batch jobs.

## Instances and logging¶

The instance name of a Flink application is provided on Kubernetes pods of a Flink cluster as an annotation. For example, an instance might be named `13e5e579-21e7-41e5-9259-aa32cf5e8ea8`, so all its pods will have this annotation: `platform.confluent.io/cmf-fa-instance: 13e5e579-21e7-41e5-9259-aa32cf5e8ea8`.

You can use these annotations to annotate log events from Flink clusters in your central logging system. This will allow you to easily filter for log events belonging to a specific instance. So you can correlate the evolution of Flink clusters to log events. If you want to see all log events from `platform.confluent.io/cmf-fa-instance == 13e5e579-21e7-41e5-9259-aa32cf5e8ea8`, you could apply that filter to your logs.

The number of instances CMF tracks is controlled by a configuration parameter, which defaults to 100 instances per Flink application.

## View application instances with Control Center¶

You can use Confluent Control Center to view details and the status of your Flink application instances.

Following is an example of application instances in Confluent Control Center:

[](../../../_images/cpf-applications.png)

For more information, see [Confluent Platform for Apache Flink in Control Center](/control-center/current/cmf.html).

## Application instance APIs¶

There are new REST API endpoints to support the use of Flink application instances.

### Get all application instances¶

The following call would return a list of all application instances in the environment:

`GET ``/applications/kafka-ingest/instances`¶

GET /cmf/api/v1/environments/aws-us-east-1-dev/applications/kafka-ingest/instances

A response might look like the following:

    GET /cmf/api/v1/environments/aws-us-east-1-dev/applications/kafka-ingest/instances
     ---
     {
       "pageable": {
         "page": 1,
         "size": 10,
         "sort": {
           "unsorted": true
         }
       },
       "metadata": {
         "size": 14
       },
       "items": [
         {
           "apiVersion":  "cmf.confluent.io/v1",
           "kind": "FlinkApplicationInstance",
           "metadata": {...},
           "spec": {...}
         },
         {...}
       ]
     }

### Get an application instance¶

You can get a specific application instance by its unique identifier (UID). This API will return the Flink application specification, with the current defaults from the environment applied, at the point in time when the instance was created. The response also contains metadata for `creationTimestamp` and `updateTimestamp`.

The following call would return the specified application instance in the environment:

`GET ``/environment/aws-us-east-1-dev/applications/kafka-ingest/instances/{instanceId}/`¶

A response might look like the following:

    GET /cmf/api/v1/environments/aws-us-east-1-dev/applications/kafka-ingest/instances/13e5e579-21e7-41e5-9259-aa32cf5e8ea8
    ---
    apiVersion: platform.confluent.io/v1
    kind: FlinkApplicationInstance
    metadata:
      name: 13e5e579-21e7-41e5-9259-aa32cf5e8ea8
      # The time when this instance has been created by the system
      creationTimestamp: 2025-03-26T21:17:22Z
      # The last time we've received a status for this instance
      updateTimestamp: 2025-03-27T04:58:46Z
    # The environment defaults merged with the FlinkApplication spec at instance creation time
    status:
      spec:
        flinkConfiguration:
          metrics.reporter.prom.factory.class: org.apache.flink.metrics.prometheus.PrometheusReporterFactory
          metrics.reporter.prom.port: 9249-9250
          taskmanager.numberOfTaskSlots: "1"
        flinkVersion: v1_19
        image: confluentinc/cp-flink:1.19.1-cp2
        podTemplate:
          metadata:
            annotations:
              platform.confluent.io/cmf-fa-instance: 13e5e579-21e7-41e5-9259-aa32cf5e8ea8
              platform.confluent.io/origin: flink
        job:
          args: []
          jarURI: local:///opt/flink/examples/streaming/StateMachineExample.jar
          parallelism: 1
          state: running # This is the desired state of the job, i.e you want your job to be running, if you want the job to stop, it would be suspended.
          # the only two state possible are running and suspended
          upgradeMode: stateless
      # Below fields track the last known state and job id of a particular instance
      # Returns some fields of the final observed jobStatus of the underlying
      # FlinkApplication
      jobStatus:
        # Flink job id inside the Flink cluster. Included as Flink metrics may contain this ID
        jobId: 8efa07007f025a3b9e937ff6e6ec317e
        # Exposed to track final status of (batch) jobs
        state: FINISHED
