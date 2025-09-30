---
document_id: flink_configure_compute-pools_chunk_1
source_file: flink_configure_compute-pools.md
source_url: https://docs.confluent.io/platform/current/flink/configure/compute-pools.html
title: Manage Compute Pools in Confluent Manager for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Manage Compute Pools in Confluent Manager for Apache Flink¶

A Compute Pool in Confluent Manager for Apache Flink® (CMF) is any of the compute resources that are used to execute a SQL statement. Each statement must reference a Compute Pool and the Compute Pool’s resource definition is used as a template for the Flink cluster that is started to run the statement. This topic describes how to create and manage Compute Pools in CMF.

Important

Flink SQL support in is available as an open preview. A Preview feature is a feature that is being introduced to gain early feedback from developers. Preview features can be used for evaluation and non-production testing purposes or to provide feedback to Confluent. The warranty, SLA, and Support Services provisions of your agreement with Confluent do not apply to Preview features. Confluent may discontinue providing releases of Preview features at any time at Confluent’s’ sole discretion. Comments, questions, and suggestions related to preview features are encouraged and can be submitted to your account representative.

## Create a Compute Pool¶

An environment can have multiple Compute Pools. Each statement is associated with exactly one Compute Pool. Following is an example Compute Pool resource definition:

    {
      "apiVersion": "cmf.confluent.io/v1",
      "kind": "ComputePool",
      "metadata": {
        "name": "pool"
      },
      "spec": {
        "type": "DEDICATED",
        "clusterSpec": {
          "flinkVersion": "v1_19",
          "image": "confluentinc/cp-flink-sql:1.19-cp1",
          "flinkConfiguration": {
            "pipeline.operator-chaining.enabled": "false",
            "execution.checkpointing.interval": "10s"
          },
          "taskManager": {
            "resource": {
              "cpu": 1.0,
              "memory": "1024m"
            }
          },
          "jobManager": {
            "resource": {
              "cpu": 0.5,
              "memory": "1024m"
            }
          }
        }
      }
    }

Currently, only one type of Compute Pool is supported. The `DEDICATED` Compute Pool type means that each statement is executed on a dedicated Flink cluster, in application mode. The `clusterSpec` field contains the definition of a Flink Kubernetes Deployment (similar to the definition of a CMF Flink Application). You can specify resources for JobManager and TaskManagers as well as Flink configuration. The Flink configuration is passed to the JobManager and TaskManager processes during start-up.

There are a few fields that must not be specified for Compute Pools because they are automatically managed by CMF:

  * **serviceAccount** : CMF uses a dedicated Kubernetes service account to deploy statements
  * **job** : most properties of the job spec are automatically set by CMF, including `jarURI`, `entryClass`, `args`, `parallelism`, and `state`.

CMF also creates two volumes and volume mounts to pass information from CMF to the Flink cluster that you should not interfere with:

  * volume: `statement-plan-volume`, mount path: `/opt/flink/statement`
  * volume: `statement-encryption-volume`, mount path: `/opt/flink/statement-secret`

The `image` field must be set to a `confluentinc/cp-flink-sql` image (or an image that uses the `cp-flink-sql` image as base image). CMF expects the image to contain a specific Flink job JAR and certain dependencies to be present.

The next sections describe the commands create a Compute Pool in the `env-1` environment.

## Use the Confluent CLI to create a Compute Pool¶

The following command creates a Compute Pool in the `env-1` environment using the Confluent CLI:

    confluent --environment env-1 flink compute-pool create /path/to/compute-pool.json

## Use the REST API to create a Compute Pool¶

The following curl command creates a Compute Pool in the `env-1` environment using the REST API:

    curl -v -H "Content-Type: application/json" \
     -X POST http://cmf:8080/cmf/api/v1/environments/env-1/compute-pools \
     -d @/path/to/compute-pool.json

## Delete a Compute Pool¶

A Compute Pool can only be deleted if there are no more statements referencing it. The deletion can be done with the Confluent CLI or the REST API.

## Use the Confluent CLI to delete a Compute Pool¶

The following command creates a Compute Pool in the `env-1` environment using the Confluent CLI:

    confluent --environment env-1 flink compute-pool delete pool

## Use the REST API to delete a Compute Pool¶

The following curl command deletes a Compute Pool in the `env-1` environment using the REST API:

    curl -v -H "Content-Type: application/json" \
     -X DELETE http://cmf:8080/cmf/api/v1/environments/env-1/compute-pools/pool
