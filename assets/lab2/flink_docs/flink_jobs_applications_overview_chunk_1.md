---
document_id: flink_jobs_applications_overview_chunk_1
source_file: flink_jobs_applications_overview.md
source_url: https://docs.confluent.io/platform/current/flink/jobs/applications/overview.html
title: Confluent Manager for Apache Flink Applications
chunk_index: 1
total_chunks: 1
---

# Deploy and Manage Confluent Manager for Apache Flink Applications¶

Confluent Manager for Apache Flink® defines a Flink application resource, which closely mirrors a Apache Flink [FlinkDeployment](https://nightlies.apache.org/flink/flink-kubernetes-operator-docs-release-1.12/docs/custom-resource/reference/) in structure and purpose. A Flink application exists to provide Confluent customers with strong compatibility guarantees to make sure Flink Applications won’t break with future version upgrades. Confluent might provide additional features in the Flink Application abstraction. FlinkDeployment is exposed as Kubernetes Custom Resource (CR), and a FlinkApplication exhibits the same principles, but it is only available as a CR when used with CFK. In CMF, it is exposed via a REST API, C3 and the confluent cli. A Custom Resource is an extension of the Kubernetes API and provides a way to define new object types.

A Flink application enables you to define and manage Flink clusters using Confluent Manager for Apache Flink (CMF). It describes the desired state of a Flink application, including configurations for the job manager, task manager, and job specifications, and exposes the actual status of the application (which is a Flink cluster).

After CMF is installed and running, it will continuously watch Flink applications. To learn more about CMF, see [Confluent Manager for Apache Flink](../../concepts/cmf.html#cmf). To install CMF, see [Install Confluent Manager for Apache Flink with Helm](../../installation/helm.html#install-cmf-helm)

## Running and suspending a Flink application¶

A Flink application controls the physical deployment of the underlying Flink application:

  * Running: A Flink application in the desired job state `running`, it is deployed according its specified configuration. When there are no errors, the Flink cluster associated with the Flink application consumes the configured amount of physical resources (such as CPU and memory).
  * Suspended: A Flink application in `suspended` desired state is inactive. When there are no errors, the Flink cluster associated with the Flink application consumes no physical resources (such as CPU and memory). Depending on the configured `upgradeMode`, the state of a `suspended` Flink Flink application will be preserved and restored upon a transition back into `running` state.

## Relationship to Environment¶

When you deploy a Flink application with CMF, CMF manages the life-cycle of the Flink job that contains it with an [Environment](../../configure/environments.html#cmf-environments).

The Environment controls the Kubernetes namespace in which the Flink job is deployed.

In addition, the Environment sets configuration options that take precedence over the configuration options specified in the Flink application.

## Isolation between applications¶

Each Flink application is executed in a Flink cluster. This deployment mode isolates each Flink application at the process level. When a Flink application is in a `running` state, the physical resources (such as CPU and memory) are exclusively allocated to the respective Flink application.

## Flink application definition example¶

Flink application objects are defined in YAML or JSON. A Flink application definition might look like the following:

YAMLJSON

The following shows a YAML example of a Flink application definition.

    apiVersion: cmf.confluent.io/v1
    kind: FlinkApplication
    metadata:
      name: curl-example
    spec:
      image: confluentinc/cp-flink:1.19.1-cp2
      flinkVersion: v1_19
      flinkConfiguration:
        taskmanager.numberOfTaskSlots: "1"
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
        jarURI: local:///opt/flink/examples/streaming/StateMachineExample.jar
        state: running
        parallelism: 1
        upgradeMode: stateless

    {
      "apiVersion": "cmf.confluent.io/v1",
      "kind": "FlinkApplication",
      "metadata": {
        "name": "curl-example"
      },
      "spec": {
        "image": "confluentinc/cp-flink:1.19.1-cp2",
        "flinkVersion": "v1_19",
        "flinkConfiguration": {
          "taskmanager.numberOfTaskSlots": "1"
        },
        "serviceAccount": "flink",
        "jobManager": {
          "resource": {
            "memory": "1024m",
            "cpu": 1
          }
        },
        "taskManager": {
          "resource": {
            "memory": "1024m",
            "cpu": 1
          }
        },
        "job": {
          "jarURI": "local:///opt/flink/examples/streaming/StateMachineExample.jar",
          "state": "running",
          "parallelism": 1,
          "upgradeMode": "stateless"
        }
      }
    }

"upgradeMode": "stateless" } } }

## Manage applications¶

You can use these tools to create and manage Flink applications.

The [REST APIs](../../clients-api/rest.html#af-rest-api) to manage Flink application instances are declarative, which makes it easy to integrate with external tooling such as CI/CD systems, and they fully describe the desired configuration.

  * [REST APIs for Confluent Manager for Apache Flink](../../clients-api/rest.html#af-rest-api)
  * [Confluent CLI reference](/confluent-cli/current/command-reference/flink/index.html)
  * [Confluent for Kubernetes](../../clients-api/flink-cfk.html#cmf-cfk)
