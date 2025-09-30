---
document_id: flink_jobs_applications_events_chunk_1
source_file: flink_jobs_applications_events.md
source_url: https://docs.confluent.io/platform/current/flink/jobs/applications/events.html
title: Confluent Manager for Apache Flink Events
chunk_index: 1
total_chunks: 1
---

# Events in Confluent Manager for Apache Flink¶

Apache Flink® Application Events are a new feature in Confluent Manager for Apache Flink® (CMF) that enables you to track the state of your Flink applications and clusters. Events provide insight into changes that occur within a Flink application. Flink events tell you:

  * The time an event occurred.
  * The Flink application instance that the event is associated with.
  * What changes to the Flink application resource occurred.
  * The status of the Flink cluster.

Events help you to understand the status of your Flink clusters, without examining the Kubernetes cluster or using the Flink Web Interface.

By default, a maximum of 100 events per Flink application is stored, meaning you see the 100 most recent events. This number is configurable with the `cmf.application-events.max-events-per-application` property. In addition, when a Flink application is deleted, all events associated with that application are deleted as well.

Note that if you are using RBAC, you must have View permissions on the Flink application to view its events.

## Tracked events¶

You can use CMF to track the following events.

**CMF Status** :

  * Flink application resource creation.
  * Flink application resource updated.

**Cluster status**. Tracked from `status.lifecycleState` of the FlinkApplication:

  * CREATED: The resource was created in Kubernetes but not yet handled by the operator.
  * SUSPENDED: The (job) resource has been suspended.
  * UPGRADING: The resource is suspended before upgrading to a new spec.
  * DEPLOYED: The resource is deployed/submitted to Kubernetes, but it’s not yet considered to be stable and might be rolled back in the future.
  * STABLE: The resource deployment is considered to be stable and won’t be rolled back. This means the Flink cluster is healthy.
  * ROLLING_BACK: The resource is being rolled back to the last stable spec.
  * ROLLED_BACK: The resource is deployed with the last stable spec.
  * FAILED: The job terminally failed.

**Flink Job status** :

  * Any change to the Flink job status. Tracked from the `FlinkApplication.status.jobStatus.state`.

** Flink Exceptions**: Any exception causing a restart of a Flink job will be tracked as an event.

## View events with Control Center¶

You can view events in the Confluent Control Center UI. The **Events** page displays a list of events associated with your Flink applications. Following is an example of Events in Confluent Control Center:

[](../../../_images/cpf-c3-event-logs.png)

## Get events with an API¶

You can also use the Events REST API to determine the status of your Flink applications and clusters. For example, you can use the following command to get a list of events for a specific Flink application:

`GET ``/cmf/api/v1alpha1/environments/dev-east/applications/fraud-detection/events`¶

An example response might look like the following:

    {
      "pageable": null,
      "metadata": {
        "size": 3
      },
      "items": [
        {
          "apiVersion": "cmf.confluent.io/v1alpha1",
          "kind": "FlinkApplicationEvent",
          "metadata": {
            "name": "77d37980-4798-437b-8850-1ecd6b612ade",
            "uid": "77d37980-4798-437b-8850-1ecd6b612ade",
            "creationTimestamp": "2025-06-18T11:16:38.061Z",
            "flinkApplicationInstance": "9f118068-3855-4442-919f-2007338a88b2",
            "labels": null,
            "annotations": null
          },
          "status": {
            "message": "Flink job status changed to RECONCILING",
            "type": "JOB_STATUS",
            "data": {
              "newStatus": "RECONCILING"
            }
          }
        },
        {
          "apiVersion": "cmf.confluent.io/v1alpha1",
          "kind": "FlinkApplicationEvent",
          "metadata": {
            "name": "e66b2e16-b833-4350-8e18-8f51dd148f28",
            "uid": "e66b2e16-b833-4350-8e18-8f51dd148f28",
            "creationTimestamp": "2025-06-18T11:16:36.434Z",
            "flinkApplicationInstance": null,
            "labels": null,
            "annotations": null
          },
          "status": {
            "message": "Flink cluster status changed to CREATED",
            "type": "CLUSTER_STATUS",
            "data": {
              "newStatus": "CREATED"
            }
          }
        },
        {
          "apiVersion": "cmf.confluent.io/v1alpha1",
          "kind": "FlinkApplicationEvent",
          "metadata": {
            "name": "27102d2e-18f1-4135-a49e-62bd423c5023",
            "uid": "27102d2e-18f1-4135-a49e-62bd423c5023",
            "creationTimestamp": "2025-06-18T11:16:35.435Z",
            "flinkApplicationInstance": null,
            "labels": null,
            "annotations": null
          },
          "status": {
            "message": "FlinkApplication created",
            "type": "CMF_STATUS",
            "data": null
          }
        }
      ]
    }
