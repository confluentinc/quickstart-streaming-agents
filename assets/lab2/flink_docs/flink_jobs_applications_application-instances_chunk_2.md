---
document_id: flink_jobs_applications_application-instances_chunk_2
source_file: flink_jobs_applications_application-instances.md
source_url: https://docs.confluent.io/platform/current/flink/jobs/applications/application-instances.html
title: Confluent Manager for Apache Flink Application Instances
chunk_index: 2
total_chunks: 2
---

Apache Flink in Control Center](/control-center/current/cmf.html).

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
